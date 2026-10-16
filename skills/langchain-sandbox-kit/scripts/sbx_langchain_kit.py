#!/usr/bin/env python3
"""Static inspection and reviewable v3 packaging; never executes project input."""

import argparse
import ast
import fnmatch
import hashlib
import ipaddress
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
import tomllib
from urllib.parse import urlsplit


VERSION = "1.0.0"
FRONTEND = "docker/sandbox-kit:3@sha256:e6a397771e865625047cf84256a914c7974b3e749d858259b5bc9c653ddb6f0d"
BASE = "ghcr.io/astral-sh/uv:0.9.26-bookworm-slim@sha256:85c530098e4db6143cf1b63d1634a9150210a3f98690b3eb6e9fa6515bc60954"
SHELL = "docker/sbx-kit-shell:1.0.0@sha256:367c9a4b3fd550f777e1d57cc53550afb4a1385055d79111acf6f996272ff6de"
PROVIDERS = {
    "langchain-google-genai": ("generativelanguage.googleapis.com", "gemini", "GOOGLE_API_KEY", "x-goog-api-key", "%s"),
    "langchain-openai": ("api.openai.com", "openai", "OPENAI_API_KEY", "Authorization", "Bearer %s"),
    "langchain-anthropic": ("api.anthropic.com", "anthropic", "ANTHROPIC_API_KEY", "x-api-key", "%s"),
    "langsmith": ("api.smith.langchain.com", "langsmith", "LANGSMITH_API_KEY", "x-api-key", "%s"),
}
HARD_DIRS = {".git", ".venv", "__pycache__", "private", ".pytest_cache", ".claude", ".codex"}
HARD_FILES = ("*.pem", "*.key", "id_*", ".netrc", ".npmrc", ".pypirc", "credentials*", "secrets*")
SAFE_PATH = re.compile(r"[A-Za-z0-9_./-]+\Z")
SAFE_ENV = re.compile(r"[A-Z][A-Z0-9_]{0,100}\Z")
MAX_SIZE = 1024 * 1024


class Refusal(Exception):
    def __init__(self, message, code=3):
        self.code = code
        super().__init__(message)


def digest(content):
    return hashlib.sha256(content).hexdigest()


def encoded(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def relative(value):
    if not isinstance(value, str) or not SAFE_PATH.fullmatch(value):
        raise Refusal("unsafe relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value in ("", "."):
        raise Refusal("path must stay inside project")
    return path.as_posix()


def hard_excluded(path):
    parts = PurePosixPath(path).parts
    return any(part in HARD_DIRS or any(fnmatch.fnmatchcase(part, pattern) for pattern in HARD_FILES)
               or (part.startswith(".env") and part != ".env.example") for part in parts)


def secret_like(value):
    if re.search(r"(?:sk-[A-Za-z0-9_-]{12,}|AIza[A-Za-z0-9_-]{15,}|-----BEGIN .*PRIVATE KEY)", value):
        return True
    return (len(value) >= 32 and len(set(value)) >= 18 and bool(re.fullmatch(r"[A-Za-z0-9_+/=-]+", value))
            and not re.fullmatch(r"[a-fA-F0-9]+", value)
            and not re.fullmatch(r"[A-Z][A-Z0-9_]*", value)
            and not value.startswith(("http://", "https://")) and not any(char.isspace() for char in value)
            and not re.fullmatch(r"[a-zA-Z_]+(?:\.[a-zA-Z_]+)+", value))


def ignore_match(path, pattern):
    pattern = pattern.lstrip("/")
    if pattern.endswith("/"):
        base = pattern.rstrip("/")
        return any(fnmatch.fnmatchcase("/".join(PurePosixPath(path).parts[:index]), base)
                   for index in range(1, len(PurePosixPath(path).parts) + 1)) or base in PurePosixPath(path).parts
    return fnmatch.fnmatchcase(path, pattern) or ("/" not in pattern and any(
        fnmatch.fnmatchcase(part, pattern) for part in PurePosixPath(path).parts))


def inventory(project):
    if project.is_symlink() or not project.is_dir():
        raise Refusal("project must be a real directory")
    project = project.resolve()
    rules = []
    for filename in (".gitignore", ".dockerignore"):
        path = project / filename
        if path.is_symlink():
            raise Refusal("ignore file must not be a symlink")
        if path.exists():
            if path.stat().st_size > MAX_SIZE:
                raise Refusal("ignore file is oversized")
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except UnicodeError:
                raise Refusal("ignore file must be UTF-8")
            rules.append(lines)
    files, excluded, issues = {}, {".env (always)", "private/ (always)", "key and credential files (always)"}, []
    visited = 0

    def walk(directory, depth):
        nonlocal visited
        if depth > 20:
            issues.append(("depth-limit", "input", 0))
            return
        for item in sorted(os.scandir(directory), key=lambda item: item.name):
            visited += 1
            if visited > 5000:
                raise Refusal("project exceeds 5000 entries")
            path = Path(item.path).relative_to(project).as_posix()
            if not SAFE_PATH.fullmatch(path):
                issues.append(("unsafe-filename", "input", 0))
                continue
            if item.is_symlink():
                issues.append(("symlink-skipped", path, 0))
                continue
            ignored = hard_excluded(path)
            for group in rules:
                group_ignored = False
                for rule in group:
                    rule = rule.strip()
                    if not rule or rule.startswith("#"):
                        continue
                    negate = rule.startswith("!")
                    if ignore_match(path, rule[1:] if negate else rule):
                        group_ignored = not negate
                ignored = ignored or group_ignored
            if ignored:
                excluded.add(path)
            elif item.is_dir(follow_symlinks=False):
                walk(item.path, depth + 1)
            elif item.is_file(follow_symlinks=False):
                if item.stat(follow_symlinks=False).st_size > MAX_SIZE:
                    issues.append(("oversized", path, 0))
                else:
                    files[path] = Path(item.path).read_bytes()
            else:
                issues.append(("nonregular-skipped", path, 0))
    walk(project, 0)
    return files, sorted(excluded), issues


def inspect(project, entrypoint):
    entrypoint = relative(entrypoint)
    files, excluded, issues = inventory(project)
    if entrypoint not in files:
        raise Refusal("entrypoint missing, excluded, or symlinked")
    findings = []

    def add(kind, filename, line=0, value="", confidence="unresolved"):
        finding = {"kind": kind, "file": filename, "line": line, "value": value, "confidence": confidence}
        finding["id"] = digest(encoded(finding).encode())[:16]
        if finding not in findings:
            findings.append(finding)

    def package_finding(name, filename, line):
        name = name.lower().replace("_", "-")
        if name in PROVIDERS or name.startswith("langchain-") or name in ("httpx", "requests"):
            add("provider-package" if name in PROVIDERS else "dependency", filename, line, name, "declared")
            if name in PROVIDERS:
                provider = PROVIDERS[name]
                add("provider-host", filename, line, provider[0], "inferred")
                add("env-name", filename, line, provider[2], "inferred")
                if name == "langchain-google-genai":
                    add("env-name", filename, line, "GEMINI_API_KEY", "inferred")

    for kind, filename, line in issues:
        add(kind, filename, line)
    for filename, raw in sorted(files.items()):
        if filename.endswith(".py"):
            try:
                tree = ast.parse(raw.decode("utf-8"))
            except (UnicodeError, SyntaxError, ValueError, RecursionError):
                add("unparseable", filename)
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if secret_like(node.value):
                        add("secret-like", filename, node.lineno, "redacted secret-like literal")
                    elif node.value.startswith(("https://", "http://")):
                        try:
                            host = urlsplit(node.value).hostname
                            if host and re.fullmatch(r"[A-Za-z0-9.-]+", host):
                                add("literal-host", filename, node.lineno, host.lower(), "declared")
                        except ValueError:
                            add("dynamic-url", filename, node.lineno)
                    elif SAFE_ENV.fullmatch(node.value):
                        add("env-name", filename, node.lineno, node.value)
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                    for name in names:
                        if name.split(".")[0] in ("subprocess", "socket"):
                            add("process-or-socket", filename, node.lineno, name.split(".")[0])
                        if name.startswith("langchain_") and name.split(".")[0] not in (
                            "langchain_core", "langchain_google_genai", "langchain_openai", "langchain_anthropic"):
                            add("unknown-integration", filename, node.lineno, name.split(".")[0])
                if isinstance(node, ast.Call):
                    name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
                    if name in ("get", "post", "request", "fetch_status") and node.args and not isinstance(node.args[0], ast.Constant):
                        add("dynamic-url", filename, node.lineno)
                    if name in ("open", "read_text", "read_bytes"):
                        add("file-read", filename, node.lineno, "developer must confirm data paths")
        elif filename in ("pyproject.toml", "uv.lock", ".python-version") or filename.endswith(".json"):
            try:
                text = raw.decode("utf-8")
            except UnicodeError:
                add("unparseable", filename)
                continue
            if filename == "pyproject.toml":
                try:
                    config = tomllib.loads(text)
                    dependencies = config.get("project", {}).get("dependencies", [])
                    for dependency in dependencies:
                        name = re.split(r"[<=>\[ ;]", dependency)[0].lower().replace("_", "-")
                        line = next((index for index, content in enumerate(text.splitlines(), 1) if dependency in content), 0)
                        package_finding(name, filename, line)
                except (tomllib.TOMLDecodeError, TypeError):
                    add("unparseable", filename)
            for index, line in enumerate(text.splitlines(), 1):
                if re.search(r"sk-[A-Za-z0-9_-]{12,}|AIza[A-Za-z0-9_-]{15,}|-----BEGIN .*PRIVATE KEY", line):
                    add("secret-like", filename, index, "redacted secret-like literal")
        elif fnmatch.fnmatchcase(PurePosixPath(filename).name, "requirements*.txt"):
            try:
                for line, dependency in enumerate(raw.decode("utf-8").splitlines(), 1):
                    match = re.match(r"([A-Za-z0-9_-]+)(?:[<>=;\[ ]|$)", dependency.strip())
                    if match:
                        package_finding(match[1], filename, line)
            except UnicodeError:
                add("unparseable", filename)
        elif filename not in ("README.md", ".gitignore", ".dockerignore", ".env.example"):
            try:
                raw.decode("utf-8")
            except UnicodeError:
                add("unparseable", filename)
    missing_lock_files = sorted({"pyproject.toml", "uv.lock", ".python-version"} - files.keys())
    if missing_lock_files:
        add("lock-setup", entrypoint, value="Create reviewed dependency metadata with normal uv tooling before generation: " + ", ".join(missing_lock_files))
    if any(item["kind"] == "env-name" and "TRACING" in item["value"] for item in findings):
        add("optional-tracing", entrypoint, value="LangSmith: api.smith.langchain.com; LANGSMITH_API_KEY (off unless explicitly enabled)", confidence="inferred")
    add("scope-confirmation", entrypoint, value="Static inspection cannot prove complete permissions; confirm model, files, tracing and runtime resources")
    findings.sort(key=lambda finding: (finding["file"], finding["line"], finding["kind"], finding["value"]))
    return {"helperVersion": VERSION, "entrypoint": entrypoint, "findings": findings,
            "questions": [{"id": finding["id"], "question": f"{finding['kind']}: {finding['value'] or 'inspect this location'}; allow with reason, deny, or out-of-scope?",
                           "evidence": f"{finding['file']}:{finding['line']}"} for finding in findings],
            "excluded": excluded, "inputHashes": {name: digest(raw) for name, raw in sorted(files.items())}}, files


def validate_lock(files):
    if not {"pyproject.toml", "uv.lock", ".python-version"} <= files.keys():
        raise Refusal("require pyproject.toml, uv.lock and .python-version; run uv lock yourself")
    try:
        project = tomllib.loads(files["pyproject.toml"].decode())
        lock = tomllib.loads(files["uv.lock"].decode())
    except (UnicodeError, tomllib.TOMLDecodeError):
        raise Refusal("invalid project or lock; run uv lock yourself")
    python = files[".python-version"].decode().strip()
    if not re.fullmatch(r"3\.\d+\.\d+", python):
        raise Refusal("pin an exact Python 3 version in .python-version")
    if project.get("tool", {}).get("uv", {}).get("sources"):
        raise Refusal("custom uv sources require manual review; not supported")
    packages = lock.get("package", [])
    locked = {(package.get("name"), package.get("version")) for package in packages}
    for dependency in project.get("project", {}).get("dependencies", []):
        match = re.fullmatch(r"([A-Za-z0-9_-]+)==([A-Za-z0-9.]+)", dependency)
        if not match or (match[1].lower().replace("_", "-"), match[2]) not in locked:
            raise Refusal("direct dependencies must be exactly pinned and present in uv.lock; run uv lock yourself")
    for package in packages:
        source = package.get("source", {})
        if "registry" in source:
            artifacts = package.get("wheels", []) + ([package["sdist"]] if "sdist" in package else [])
            if not artifacts or any(not re.fullmatch(r"sha256:[0-9a-f]{64}", artifact.get("hash", "")) for artifact in artifacts):
                raise Refusal("lock contains unhashed artifacts")
            if source["registry"] != "https://pypi.org/simple" or any(
                urlsplit(artifact.get("url", "")).hostname != "files.pythonhosted.org" for artifact in artifacts
            ):
                raise Refusal("custom dependency endpoint requires manual review")
        elif source != {"editable": "."} and source != {"virtual": "."}:
            raise Refusal("non-registry dependency requires manual review")
    return python


def validate_host(host, broad, reason):
    if not isinstance(host, str) or not re.fullmatch(r"[a-z0-9.*-]+", host) or ".." in host or host.startswith("-"):
        raise Refusal("host must be a lowercase hostname, not a URL")
    try:
        ipaddress.ip_address(host)
        is_ip = True
    except ValueError:
        is_ip = False
    if ("*" in host or is_ip) and not (broad is True and reason.strip()):
        raise Refusal("wildcard/IP requires allowBroad true with reason")


def permissions(report, answers, allowed, denied):
    rows = ["# Permission review", "", "Capabilities are host requests, not grants. Review the target runtime's effective composition.",
            "", "| Resource | Decision | Reason / source |", "| --- | --- | --- |"]
    for finding in report["findings"]:
        answer = answers["decisions"][finding["id"]]
        text = f"{finding['value'] or finding['kind']} ({finding['file']}:{finding['line']})"
        rows.append(f"| {text} | {answer['action']} | {answer['reason'].replace('|', '/').replace(chr(10), ' ')} |")
    rows += ["", f"Runtime allow: {', '.join(allowed) or '(none)'}. Runtime deny: {', '.join(denied) or '(none)' }.",
             "", "Excluded by policy: .env/.env.* (except .env.example), private/, VCS/venv/cache directories, keys and credential files; additional project ignore rules apply.", "",
             "Broad/IP access: " + ("explicitly authorized; review carefully" if any(item.get("allowBroad") for item in answers["decisions"].values()) else "none"),
             "", "## Launch ownership", "", "This is a mixin, not a workload. The pinned shell workload owns entrypoint, user and sbx@1.",
             "Run the command in the context file with sbx env exec after environment creation.",
             f"Launch from /opt/{answers['name']}/app: `{answers['launch']}`.",
             "", "## What this does not protect", "", "Static inspection is incomplete. Denied/out-of-scope findings are not proof of absence.",
             "No install-phase network is requested; image builds still download locked dependencies.",
             "Other kits and host policy affect the effective boundary. Allowed services can incur costs, store data or have side effects.",
             "Isolation does not solve prompt injection or answer correctness. Cloud needs separate secrets and policy; no host workspace mount is included.",
             "Build/TCK/container checks are not local or cloud SBX runtime confinement evidence."]
    return "\n".join(rows) + "\n"


def generate(project, entrypoint, answers_path, output, force=False):
    report, files = inspect(project, entrypoint)
    python = validate_lock(files)
    if answers_path.is_symlink() or answers_path.stat().st_size > MAX_SIZE:
        raise Refusal("unsafe answers file")
    answers_raw = answers_path.read_bytes()
    try:
        answers = json.loads(answers_raw)
    except (ValueError, UnicodeError):
        raise Refusal("invalid answers JSON")
    if not isinstance(answers, dict) or set(answers) - {"name", "decisions", "dataPaths", "launch", "acknowledgeSecrets"}:
        raise Refusal("unknown answers field; mixin lifecycle and sbx@1 are forbidden")
    name = answers.get("name", "")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,40}", name):
        raise Refusal("name must be lowercase-kebab")
    decisions = answers.get("decisions", {})
    if not isinstance(decisions, dict):
        raise Refusal("decisions must be an object")
    allowed, denied, credentials = set(), set(), set()
    for finding in report["findings"]:
        answer = decisions.get(finding["id"])
        if not isinstance(answer, dict) or answer.get("action") not in ("allow", "deny", "out-of-scope") or not isinstance(answer.get("reason"), str) or not answer["reason"].strip():
            raise Refusal("needs answers: explicit decision and reason for " + finding["id"], 2)
        if set(answer) - {"action", "reason", "hosts", "credential", "allowBroad"}:
            raise Refusal("unknown decision field")
        if secret_like(answer["reason"]) or re.search(r"sk-[\w-]{12,}|AIza[\w-]{15,}", answer["reason"]):
            raise Refusal("secret-like answer reason")
        if finding["kind"] == "secret-like":
            raise Refusal("remove secret-like literals from source before packaging (acknowledgement is not permission to bake secrets)")
        if finding["kind"] in ("unparseable", "oversized", "depth-limit", "unsafe-filename", "symlink-skipped", "nonregular-skipped"):
            raise Refusal("incomplete or unsafe input; resolve inspection findings first")
        hosts = answer.get("hosts", [])
        if not isinstance(hosts, list):
            raise Refusal("hosts must be a list")
        provider = PROVIDERS.get(finding["value"]) if finding["kind"] == "provider-package" else None
        if not hosts and provider:
            hosts = [provider[0]]
        if not hosts and finding["kind"] in ("literal-host", "provider-host"):
            hosts = [finding["value"]]
        if answer["action"] == "allow" and finding["kind"] == "dynamic-url" and not hosts:
            raise Refusal("dynamic URL needs exact hosts", 2)
        for host in hosts:
            validate_host(host, answer.get("allowBroad"), answer["reason"])
            if answer["action"] == "allow":
                allowed.add(host)
            elif answer["action"] == "deny":
                denied.add(host)
        if answer.get("credential"):
            if not provider or answer["action"] != "allow" or answer["credential"] != provider[1] or provider[0] not in hosts:
                raise Refusal("credential must match an explicitly allowed provider host")
            credentials.add(provider)
    if set(decisions) != {finding["id"] for finding in report["findings"]}:
        raise Refusal("stale/extra decisions; inspect again", 2)
    allowed, denied = sorted(allowed), sorted(denied)
    if set(allowed) & set(denied):
        raise Refusal("contradictory allow/deny decisions")
    paths = answers.get("dataPaths", [])
    if not isinstance(paths, list):
        raise Refusal("dataPaths must be a list")
    paths = [relative(path) for path in paths]
    if any(hard_excluded(path) for path in paths):
        raise Refusal("excluded data path")
    selected = {filename: raw for filename, raw in files.items() if filename in ("pyproject.toml", "uv.lock", ".python-version")
                or ("/" not in filename and filename.endswith(".py"))
                or filename.startswith("src/") or any(filename == path or filename.startswith(path + "/") for path in paths)}
    if entrypoint not in selected:
        raise Refusal("entrypoint must be a root Python file or under src/")
    for path in paths:
        if not any(filename == path or filename.startswith(path + "/") for filename in selected):
            raise Refusal("data path missing or excluded")
    launch = answers.get("launch", "")
    if not isinstance(launch, str) or not re.fullmatch(r"python (?:-m [a-zA-Z_][a-zA-Z0-9_.]*|[A-Za-z0-9_/-]+\.py)(?: [A-Za-z0-9_./=-]+)*", launch) or ".." in launch:
        raise Refusal("launch must be a simple reviewed python command without shell syntax")
    if not launch.startswith("python -m ") and launch.split()[1] != entrypoint:
        raise Refusal("script launch must name the inspected entrypoint")
    for raw in selected.values():
        text = raw.decode("utf-8")
        if re.search(r"sk-[\w-]{12,}|AIza[\w-]{15,}|-----BEGIN .*PRIVATE KEY", text):
            raise Refusal("build context contains a secret-like literal")
    output = Path(os.path.abspath(output))
    project = project.resolve()
    if output.is_symlink() or any(parent.is_symlink() for parent in output.parents):
        raise Refusal("output must not be symlinked", 4)
    if output == project or output.is_relative_to(project) or project.is_relative_to(output) or hard_excluded(output.as_posix()):
        raise Refusal("output must be outside project and excluded paths", 4)
    template_root = Path(__file__).resolve().parents[1] / "templates"
    descriptor = (template_root / "descriptor.txt").read_text().replace("@FRONTEND@", FRONTEND).replace("@NAME@", name)
    descriptor += f"  - type: com.docker.sandbox/network-policy@1\n    config:\n      runtime:\n        allow: {json.dumps(allowed)}\n        deny: {json.dumps(denied)}\n"
    for host, service, env, header, format_value in sorted(credentials):
        descriptor += ("  - type: com.docker.sandbox/credential@1\n    optional: true\n    config:\n"
                       f"      service: {service}\n      phase: runtime\n      apiKey:\n        name: {env}\n        proxyManaged: true\n"
                       f"        inject:\n          - domain: {host}\n            header: {header}\n            format: {json.dumps(format_value)}\n")
    recipe = (template_root / "dockerfile.txt").read_text().replace("@BASE@", BASE).replace("@NAME@", name).replace("@PYTHON@", python)
    context = f"# {name}\n\nRun inside the composed sandbox:\n\n    cd /opt/{name}/app && {launch}\n\nThe workload owns launch and identity. See PERMISSIONS.md before granting capabilities.\n"
    environment = (template_root / "sbxenv.txt").read_text().replace("@NAME@", name).replace("@SHELL@", SHELL)
    outputs = {f"{name}.yaml": descriptor.encode(), f"{name}.dockerfile": recipe.encode(),
               f"{name}-context.md": context.encode(), "sbxenv.local.yaml": (environment + "workspace: .\n").encode(),
               "sbxenv.cloud.yaml": environment.encode(), "PERMISSIONS.md": permissions(report, answers, allowed, denied).encode()}
    outputs.update({"app/" + filename: raw for filename, raw in selected.items()})
    outputs[".dockerignore"] = ("**\n" + "\n".join("!" + filename for filename in sorted(outputs) if filename.startswith("app/"))
                                 + f"\n!{name}-context.md\n").encode()
    manifest = {"helperVersion": VERSION, "name": name, "entrypoint": entrypoint,
                "inputHashes": report["inputHashes"], "answersHash": digest(answers_raw),
                "outputHashes": {filename: digest(raw) for filename, raw in sorted(outputs.items())}}
    outputs["kit-manifest.json"] = encoded(manifest).encode()
    existing = set()
    if output.exists():
        if not output.is_dir():
            raise Refusal("output is not a directory", 4)
        existing = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file() or path.is_symlink()}
        if any(output.iterdir()):
            if not force:
                raise Refusal("output exists; review before --force", 4)
            try:
                if any(path.is_symlink() for path in output.rglob("*")):
                    raise ValueError()
                if (output / "kit-manifest.json").stat().st_size > MAX_SIZE:
                    raise ValueError()
                old = json.loads((output / "kit-manifest.json").read_text())
                old_hashes = old["outputHashes"]
                if old["helperVersion"] != VERSION or not isinstance(old_hashes, dict):
                    raise ValueError()
                if existing != set(old_hashes) | {"kit-manifest.json"}:
                    raise ValueError()
                expected_directories = {parent.as_posix() for filename in old_hashes for parent in PurePosixPath(relative(filename)).parents if parent.as_posix() != "."}
                actual_directories = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_dir()}
                if actual_directories != expected_directories:
                    raise ValueError()
                for filename, expected in old_hashes.items():
                    if digest((output / relative(filename)).read_bytes()) != expected:
                        raise ValueError()
            except (OSError, ValueError, KeyError, TypeError, Refusal):
                raise Refusal("output has changed or unowned files; refusing overwrite", 4)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".kit-", dir=output.parent))
    backup = None
    try:
        for filename, raw in outputs.items():
            path = temporary / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        if output.exists():
            backup = Path(tempfile.mkdtemp(prefix=".kit-backup-", dir=output.parent))
            backup.rmdir()
            output.rename(backup)
        try:
            temporary.rename(output)
        except OSError:
            if backup:
                backup.rename(output)
                backup = None
            raise
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
        if backup:
            shutil.rmtree(backup)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "generate"):
        subparser = subcommands.add_parser(command)
        subparser.add_argument("--project", type=Path, required=True)
        subparser.add_argument("--entrypoint", required=True)
        if command == "inspect":
            subparser.add_argument("--json", type=Path)
        else:
            subparser.add_argument("--answers", type=Path, required=True)
            subparser.add_argument("--out", type=Path, required=True)
            subparser.add_argument("--force", action="store_true")
    explanation = subcommands.add_parser("explain")
    explanation.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            report, files = inspect(args.project, args.entrypoint)
            if args.json:
                if args.json.exists() or args.json.is_symlink() or args.json.resolve().is_relative_to(args.project.resolve()):
                    raise Refusal("JSON output must be new and outside the project", 4)
                args.json.write_text(encoded(report))
                print("# Inspection\n\n" + "\n".join(f"- {item['id']}: {item['question']} ({item['evidence']})" for item in report["questions"]))
            else:
                print(encoded(report), end="")
        elif args.command == "generate":
            generate(args.project, args.entrypoint, args.answers, args.out, args.force)
            print("generated reviewable mixin; no capabilities granted or runtime started")
        else:
            if args.manifest.is_symlink():
                raise Refusal("manifest must not be a symlink")
            manifest = json.loads(args.manifest.read_text())
            summary = args.manifest.parent / "PERMISSIONS.md"
            if summary.is_symlink() or digest(summary.read_bytes()) != manifest["outputHashes"]["PERMISSIONS.md"]:
                raise Refusal("permission summary changed")
            print(summary.read_text(), end="")
    except Refusal as error:
        print(str(error), file=sys.stderr)
        return error.code
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        print("invalid or unreadable input; no runtime started", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
