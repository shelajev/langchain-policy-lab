# Requests, not grants

| Package | Suggested host | Service | Environment name | Header |
| --- | --- | --- | --- | --- |
| langchain-google-genai | generativelanguage.googleapis.com | gemini | GOOGLE_API_KEY (GEMINI_API_KEY alias) | x-goog-api-key |
| langchain-openai | api.openai.com | openai | OPENAI_API_KEY | Authorization: Bearer |
| langchain-anthropic | api.anthropic.com | anthropic | ANTHROPIC_API_KEY | x-api-key |
| langsmith | api.smith.langchain.com | langsmith | LANGSMITH_API_KEY | x-api-key |
| langchain-community / unknown integration | unknown; ask developer | unknown | ask for names only | unknown |
| httpx / requests | literal hosts are evidence, dynamic URLs need answers | none by default | no automatic secret request | none |

Installed packages are not proof of use or permission. Custom provider endpoints,
regional services and tracing may need different hosts; ask rather than broaden.

The generated **mixin** adds files and environment; the pinned shell **workload**
owns entrypoint, identity and `sbx@1`. There is no mixin lifecycle hook.
`agent-context@1` uses `contentFile` for run instructions, not a launch command.
`network-policy@1` requests runtime host allow/deny. No install-phase grant is
requested. Image-build dependency downloads happen before runtime provisioning.
Do not mix @1 and @2 in one composition. @2 can restrict methods/paths but target
runtime enforcement must be tested. This helper chooses @1 host-only semantics.

`credential@1` is per (service, phase), here runtime only and optional so fake
mode needs no secret. With `proxyManaged: true`, the real key stays at the
boundary; a sentinel satisfies the SDK's environment lookup and outbound
headers are rewritten only for the exact allowed provider domain. A host-side
binding must resolve the service; setting a host env var alone is not a binding.
The app still controls allowed-service requests and can spend money/send data.

Authoritative specification: github.com/docker/sandbox-kit-spec at
`a1d110de252bcc3cb2fa6d47fe37137a1a328b97` (build/TCK pin), compared with HEAD
`e223cd4c52be3407ffecb5208777289c07583360` on 2026-10-16. Read
`docs/spec/capabilities/com.docker.sandbox/{network-policy@1,credential@1}.md`
and `skills/create-kit-v3/SKILL.md` in that upstream repository for the normative
rules. Docker CLI docs: docs.docker.com/reference/cli/sbx/env/.
