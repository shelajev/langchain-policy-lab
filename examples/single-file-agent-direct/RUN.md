# Run the unchanged app

Host steps below are NOT RUN here. Review ACCESS.md and every command before approving.
Keep these control files outside workspace/. Use a fresh sandbox name; inspect inherited policy and existing credentials first.
No generated mixin is needed. An allow list does not cancel broader host/org grants.

## 1. Host: existing credential and environment

```bash
sbx secret set google --sandbox single-file-agent-kit
sbx env plan ./sbxenv.yaml
sbx env create ./sbxenv.yaml
sbx policy ls
```

# UNVERIFIED: whether this host's shell composition requests additional binding approval. Stop for host review; no global binding is generated.

## 2. Host: scoped bootstrap and runtime policy

```bash
sbx policy allow network --sandbox single-file-agent-kit files.pythonhosted.org
sbx policy allow network --sandbox single-file-agent-kit generativelanguage.googleapis.com
sbx policy allow network --sandbox single-file-agent-kit github.com
sbx policy allow network --sandbox single-file-agent-kit pypi.org
sbx policy allow network --sandbox single-file-agent-kit release-assets.githubusercontent.com
sbx policy deny network --sandbox single-file-agent-kit example.com
sbx env exec ./sbxenv.yaml -- pwd
sbx env exec -i ./sbxenv.yaml -- sh < setup-deps.sh
```

Setup runs only inside the sandbox, from its mounted workspace; verify pwd and the expected pyproject.toml first.
The reviewed setup script checks uv's release hash and runs uv sync --locked. Package build hooks may execute inside the sandbox.

## 3. Host: remove temporary grants

```bash
sbx policy rm network --sandbox single-file-agent-kit --resource github.com
sbx policy rm network --sandbox single-file-agent-kit --resource release-assets.githubusercontent.com
sbx policy rm network --sandbox single-file-agent-kit --resource pypi.org
sbx policy rm network --sandbox single-file-agent-kit --resource files.pythonhosted.org
sbx policy ls
```

Inspect effective policy. Do not claim other hosts are denied if inherited rules allow them.

## 4. Host: execute inside the sandbox

```bash
sbx env exec ./sbxenv.yaml -- .venv/bin/python agent.py
```

For an interactive shell use `sbx env run ./sbxenv.yaml`; inside it activate `.venv/bin/activate`, then run `python agent.py`.
Approve model cost/data separately. This command is live unless your app selects its fake-model option.

## 5. Host: denied operation and origin control

```bash
sbx env exec ./sbxenv.yaml -- python3 -c "import urllib.request; urllib.request.urlopen('https://example.com', timeout=10)"
sbx policy log
```

Expect a policy rejection for example.com, not merely a DNS/TLS/timeout error. Compare an approved host-side origin reachability check and inspect the policy log.
Check `.env` and private/ are absent without printing secrets. Build/container checks do not prove this SBX boundary.

## 6. Host: cleanup

```bash
sbx env rm ./sbxenv.yaml
```

Review leftover sandbox-scoped policy/secret entries and remove only this run's entries. Cloud has no host mount; use an approved kit/bake transfer and separate cloud credentials/policy.
