# Requests, not grants

| Package | Suggested host | Service | Environment name | Header |
| --- | --- | --- | --- | --- |
| langchain-google-genai | generativelanguage.googleapis.com | google | GOOGLE_API_KEY (GEMINI_API_KEY alias) | x-goog-api-key |
| langchain-openai | api.openai.com | openai | OPENAI_API_KEY | Authorization: Bearer |
| langchain-anthropic | api.anthropic.com | anthropic | ANTHROPIC_API_KEY | x-api-key |
| langsmith | api.smith.langchain.com | none built in (helper refuses a credential) | LANGSMITH_API_KEY | x-api-key |
| langchain-community / unknown integration | unknown; ask developer | unknown | ask for names only | unknown |
| httpx / requests | literal hosts are evidence, dynamic URLs need answers | none by default | no automatic secret request | none |

## Provider mappings and manual review

The **Service** column is the service name accepted by `sbx secret set` and
written into the kit's `credential@1` request. Current `sbx secret set --help`
lists `anthropic`, `google`, and `openai` among its built-in services (there is
no `gemini` service name). It also lists `groq`, `mistral`, `openrouter`, and
`xai`, but the helper has no reviewed LangChain mapping for them, so package
those manually with their documented host, header, and environment variable.

Having a package installed in `pyproject.toml` is not proof that the app uses
it or should be granted network access for it. Custom provider endpoints,
regional services, OpenAI-compatible gateways, and tracing integrations often
use different hosts and headers; ask the developer rather than broadening hosts
or assuming API compatibility.

## How the mixin composes onto `shell`

The generated **mixin** adds `/opt/NAME/app`, `/opt/NAME/venv`, and environment
configuration, while Docker's built-in `shell` agent is the **workload** that
owns the container entrypoint, identity, and `sbx@1`. There is no mixin
lifecycle hook. Because the mixin appends to `ENV PATH` after the workload's
`PATH`, plain `python` inside the sandbox still points to the workload's system
Python without the app's packages; always run the app with
`/opt/NAME/venv/bin/python`.

`agent-context@1` uses `contentFile` to provide run instructions to a coding
agent, not to execute a launch command automatically. With the `shell` workload
there is no coding agent to read it; the human runs `RUN.md`'s commands.

## Network and credential boundaries

`network-policy@1` requests runtime host allow and deny entries. No install-phase
network grant is requested because `uv sync --locked` downloads packages during
the image build, before runtime provisioning. Do not mix `@1` and `@2`
capabilities in one composition. `@2` can restrict HTTP methods and paths (with
target runtime enforcement needing direct verification), whereas this helper
intentionally uses `@1` host-only semantics. Keep in mind that adding an allow
request in a kit does not make the effective composed sandbox policy exclusive:
other host or organization policy grants can widen access, while explicit
denies win.

The Gemini mapping sets the placeholder in `GOOGLE_API_KEY`; it does not set
`GEMINI_API_KEY` as a second placeholder.

`credential@1` is scoped per `(service, phase)`, configured here for runtime
only and marked optional so fake or offline app modes work without a bound key.
With `proxyManaged: true`, the real API key stays outside the container at the
proxy boundary. Inside the sandbox, the app sees a placeholder value in its
environment variable (separate from whatever credentials your coding agent uses
on the host), and outbound headers are rewritten with the real key only on
requests to the exact allowed provider domain. A host-side binding via
`sbx secret set` is required to resolve the service; exporting an environment
variable in your host shell alone does nothing. Even with proxy-managed
credentials, the app controls what it sends to that allowed service and can
still spend money or transmit data.

Authoritative specification: `github.com/docker/sandbox-kit-spec` at
`a1d110de252bcc3cb2fa6d47fe37137a1a328b97` (build/TCK pin), compared with HEAD
`e223cd4c52be3407ffecb5208777289c07583360` on 2026-10-16. Read
`docs/spec/capabilities/com.docker.sandbox/{network-policy@1,credential@1}.md`
and `skills/create-kit-v3/SKILL.md` in that upstream repository for the normative
rules, and see `docs.docker.com/reference/cli/sbx/env/` for Docker CLI details.
