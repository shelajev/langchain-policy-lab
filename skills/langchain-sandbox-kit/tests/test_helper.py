import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sbx_helper", SKILL / "scripts/sbx_langchain_kit.py")
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)
ROOT = SKILL.parents[1]
CANARY = "TEST_ONLY_PRIVATE_CANARY_4728c2bd"


class HelperTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.project = self.base / "project"
        (self.project / "src/demo").mkdir(parents=True)
        (self.project / "src/demo/app.py").write_text('import os\nurl = os.environ.get("DEMO_URL")\n')
        (self.project / "pyproject.toml").write_text('[project]\nname="demo"\nversion="0.1.0"\ndependencies=["langchain-openai==1.0.0"]\n')
        (self.project / "uv.lock").write_text('version=1\n[[package]]\nname="langchain-openai"\nversion="1.0.0"\nsource={registry="https://pypi.org/simple"}\nwheels=[{url="https://files.pythonhosted.org/demo.whl",hash="sha256:' + "a" * 64 + '"}]\n')
        (self.project / ".python-version").write_text("3.13.7\n")
        self.output = self.base / "kit"
        self.answers_path = self.base / "answers.json"

    def report(self):
        return HELPER.inspect(self.project, "src/demo/app.py")[0]

    def answers(self):
        answers = {"name": "demo", "launch": "python -m demo.app", "dataPaths": [],
                   "decisions": {finding["id"]: {"action": "out-of-scope", "reason": "Not required for this test"}
                                 for finding in self.report()["findings"]}}
        self.answers_path.write_text(json.dumps(answers))
        return answers

    def generate(self, force=False):
        return HELPER.generate(self.project, "src/demo/app.py", self.answers_path, self.output, force)

    def assert_refused(self, callback, code=3):
        with self.assertRaises(HELPER.Refusal) as refusal:
            callback()
        self.assertEqual(refusal.exception.code, code)

    def test_inspect_provider_and_never_execute_input(self):
        marker = self.base / "executed"
        with (self.project / "src/demo/app.py").open("a") as stream:
            stream.write(f'from pathlib import Path\nPath({str(marker)!r}).touch()\n')
        report = self.report()
        self.assertFalse(marker.exists())
        self.assertTrue(any(finding["value"] == "api.openai.com" for finding in report["findings"]))
        self.assertTrue(all("line" in finding and "confidence" in finding for finding in report["findings"]))
        self.answers()
        self.generate()
        self.assertFalse(marker.exists())

    def test_secret_files_and_ignore_rules_never_enter_context(self):
        (self.project / ".env").write_text(CANARY)
        (self.project / "id_rsa").write_text(CANARY)
        (self.project / "private").mkdir()
        (self.project / "private/payload.py").write_text(CANARY)
        (self.project / ".gitignore").write_text("src/demo/ignored.py\n")
        (self.project / "src/demo/ignored.py").write_text(CANARY)
        (self.project / ".dockerignore").write_text("!**\n")
        self.answers()
        self.generate()
        for path in self.output.rglob("*"):
            if path.is_file():
                self.assertNotIn(CANARY.encode(), path.read_bytes())
        self.assertFalse((self.output / "app/.env").exists())
        self.assertFalse((self.output / "app/private").exists())
        self.assertTrue((self.output / ".dockerignore").read_text().startswith("**\n!app/"))
        self.assertNotIn(CANARY, json.dumps(self.report()))

    def test_secret_literal_redacted_and_refused(self):
        token = "sk-" + "testSecretThatMustNeverBePrinted123456"
        (self.project / "src/demo/app.py").write_text(f'key = "{token}"\n')
        self.assertNotIn(token, json.dumps(self.report()))
        self.answers()
        self.assert_refused(self.generate)

    def test_structured_fake_output_is_not_an_entropy_secret(self):
        (self.project / "src/demo/app.py").write_text('response = \'{"category":"technical","ticket_id":"T-101"}\'\n')
        self.assertFalse(any(item["kind"] == "secret-like" for item in self.report()["findings"]))
        self.answers()
        self.generate()

    def test_syntax_binary_size_and_depth_findings(self):
        (self.project / "src/demo/bad.py").write_text("def (:\n")
        (self.project / "src/demo/binary.py").write_bytes(b"\xff")
        (self.project / "src/demo/big.py").write_bytes(b"a" * (HELPER.MAX_SIZE + 1))
        deep = self.project.joinpath(*(["deep"] * 22))
        deep.mkdir(parents=True)
        (deep / "app.py").write_text("pass")
        kinds = {finding["kind"] for finding in self.report()["findings"]}
        self.assertTrue({"unparseable", "oversized", "depth-limit"} <= kinds)
        self.answers()
        self.assert_refused(self.generate)

    def test_symlink_and_outside_entrypoint(self):
        outside = self.base / "outside.py"
        outside.write_text(CANARY)
        (self.project / "src/demo/link.py").symlink_to(outside)
        self.assertNotIn(CANARY, json.dumps(self.report()))
        self.assertTrue(any(finding["kind"] == "symlink-skipped" for finding in self.report()["findings"]))
        self.assert_refused(lambda: HELPER.inspect(self.project, "../outside.py"))
        self.assert_refused(lambda: HELPER.inspect(self.project, str(outside)))
        self.answers()
        self.assert_refused(self.generate)

    def test_bad_answers_paths_and_lifecycle(self):
        for change in ({"dataPaths": ["../private"]}, {"lifecycle": {}}, {"sbx@1": {}}, {"launch": "python -m demo.app; touch pwn"}):
            answers = self.answers()
            answers.update(change)
            self.answers_path.write_text(json.dumps(answers))
            self.assert_refused(self.generate)

    def test_missing_lock_missing_dependency_unhashed_lock(self):
        self.answers()
        lock = (self.project / "uv.lock").read_bytes()
        (self.project / "uv.lock").unlink()
        self.assert_refused(self.generate)
        (self.project / "uv.lock").write_bytes(lock.replace(b"langchain-openai", b"different-package"))
        self.assert_refused(self.generate)
        (self.project / "uv.lock").write_bytes(lock.replace(b"sha256:", b"unhashed:"))
        self.assert_refused(self.generate)

    def test_dynamic_url_needs_answer_and_exact_host(self):
        (self.project / "src/demo/app.py").write_text('client.get(url)\n')
        self.answers_path.write_text('{"name":"demo","decisions":{}}')
        self.assert_refused(self.generate, 2)
        answers = self.answers()
        question = next(finding for finding in self.report()["findings"] if finding["kind"] == "dynamic-url")
        answers["decisions"][question["id"]] = {"action": "allow", "reason": "User chose a status service"}
        self.answers_path.write_text(json.dumps(answers))
        self.assert_refused(self.generate, 2)
        answers["decisions"][question["id"]]["hosts"] = ["*.example.com"]
        self.answers_path.write_text(json.dumps(answers))
        self.assert_refused(self.generate)
        answers["decisions"][question["id"]]["allowBroad"] = True
        self.answers_path.write_text(json.dumps(answers))
        self.generate()
        self.assertIn("explicitly authorized", (self.output / "PERMISSIONS.md").read_text())

    def test_no_implicit_grants_and_mixin_ownership(self):
        self.answers()
        self.generate()
        descriptor = (self.output / "demo.yaml").read_text()
        self.assertIn("kind: mixin", descriptor)
        self.assertIn("allow: []", descriptor)
        self.assertNotIn("credential@1", descriptor)
        self.assertNotIn("sbx@1", descriptor)
        recipe = (self.output / "demo.dockerfile").read_text()
        for forbidden in ("ENTRYPOINT", "CMD", "USER"):
            self.assertNotIn(forbidden, recipe)
        self.assertNotIn("workspace:", (self.output / "sbxenv.cloud.yaml").read_text())

    def test_explicit_provider_credential_request(self):
        answers = self.answers()
        question = next(finding for finding in self.report()["findings"] if finding["kind"] == "provider-package")
        answers["decisions"][question["id"]] = {"action": "allow", "reason": "Explicit model use", "credential": "openai"}
        self.answers_path.write_text(json.dumps(answers))
        self.generate()
        descriptor = (self.output / "demo.yaml").read_text()
        self.assertIn("phase: runtime", descriptor)
        self.assertIn("proxyManaged: true", descriptor)
        self.assertIn('allow: ["api.openai.com"]', descriptor)

    def test_provider_host_deny_cannot_be_overridden_by_package_allow(self):
        answers = self.answers()
        for finding in self.report()["findings"]:
            if finding["kind"] == "provider-package":
                answers["decisions"][finding["id"]] = {"action": "allow", "reason": "Provider requested"}
            if finding["kind"] == "provider-host":
                answers["decisions"][finding["id"]] = {"action": "deny", "reason": "Host explicitly refused"}
        self.answers_path.write_text(json.dumps(answers))
        self.assert_refused(self.generate)

    def test_force_refuses_manual_edits_and_unknown_files(self):
        self.answers()
        self.generate()
        self.assert_refused(self.generate, 4)
        self.generate(force=True)
        (self.output / "personal.txt").write_text("keep")
        self.assert_refused(lambda: self.generate(force=True), 4)
        (self.output / "personal.txt").unlink()
        (self.output / "demo.yaml").write_text("edited")
        self.assert_refused(lambda: self.generate(force=True), 4)
        self.assertEqual((self.output / "demo.yaml").read_text(), "edited")

    def test_force_preserves_unowned_empty_directories(self):
        self.answers()
        self.generate()
        (self.output / "personal").mkdir()
        self.assert_refused(lambda: self.generate(force=True), 4)
        self.assertTrue((self.output / "personal").is_dir())

    def test_requirements_inspection_before_lock_setup(self):
        (self.project / "requirements.txt").write_text("langchain-anthropic==1.0.0\n")
        self.assertTrue(any(item["value"] == "api.anthropic.com" for item in self.report()["findings"]))

    def test_force_refuses_symlinks(self):
        self.answers()
        self.generate()
        target = self.output / "demo.yaml"
        target.unlink()
        target.symlink_to(self.project / "pyproject.toml")
        self.assert_refused(lambda: self.generate(force=True), 4)

    def test_output_cannot_overlap_input(self):
        self.answers()
        for output in (self.project, self.project / "kit", self.base):
            self.output = output
            self.assert_refused(self.generate, 4)

    def test_output_cannot_overlap_excluded_ancestor(self):
        self.answers()
        self.output = self.base / "private/kit"
        self.assert_refused(self.generate, 4)

    def test_inputs_unchanged_and_manifest_hashes(self):
        before = self.report()["inputHashes"]
        self.answers()
        manifest = self.generate()
        self.assertEqual(before, self.report()["inputHashes"])
        for filename, expected in manifest["outputHashes"].items():
            self.assertEqual(hashlib.sha256((self.output / filename).read_bytes()).hexdigest(), expected)

    def test_single_file_without_restructuring(self):
        original = b'import os\nfrom langchain.chat_models import init_chat_model\nmodel = os.environ.get("MODEL")\n'
        (self.project / "agent.py").write_bytes(original)
        report = HELPER.inspect(self.project, "agent.py")[0]
        answers = self.answers()
        answers["decisions"] = {finding["id"]: {"action": "deny", "reason": "Test"} for finding in report["findings"]}
        answers["launch"] = "python agent.py"
        self.answers_path.write_text(json.dumps(answers))
        HELPER.generate(self.project, "agent.py", self.answers_path, self.output)
        self.assertEqual((self.output / "app/agent.py").read_bytes(), original)
        self.assertEqual((self.project / "agent.py").read_bytes(), original)
        self.assertIn("python agent.py", (self.output / "demo-context.md").read_text())

    def test_cli_exit_codes(self):
        self.answers()
        command = [sys.executable, str(SKILL / "scripts/sbx_langchain_kit.py"), "generate", "--project", str(self.project),
                   "--entrypoint", "src/demo/app.py", "--answers", str(self.answers_path), "--out", str(self.output)]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 4)
        self.answers_path.write_text("not JSON")
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 3)

    @unittest.skipUnless((ROOT / "examples/ticket-triage-kit").is_dir(), "repository golden fixture not present")
    def test_golden(self):
        HELPER.generate(ROOT / "examples/ticket-triage", "src/ticket_triage/app.py",
                        ROOT / "examples/ticket-triage.answers.json", self.output)
        golden = ROOT / "examples/ticket-triage-kit"
        expected = {path.relative_to(golden).as_posix(): path.read_bytes() for path in golden.rglob("*") if path.is_file()}
        actual = {path.relative_to(self.output).as_posix(): path.read_bytes() for path in self.output.rglob("*") if path.is_file()}
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
