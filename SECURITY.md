# Security Policy

## Responsible disclosure

Found a security issue in `kepler-acp-test` or in one of its example CLI
tools? Please do not open a public issue with exploitation details.

- Report privately to the maintainers first (open a minimal issue without
  reproduction details, or contact the team directly) and allow a reasonable
  window for a fix before publishing anything.
- Include the affected component, the impact, and the minimal steps needed to
  understand the problem — enough for triage, no weaponized detail.
- Never test against systems you do not own or do not have explicit,
  written permission to test.

## Local development good practice

`kepler-acp-test` is a local example/playground repository. Keep your
environment boring and safe:

- Use a dedicated virtual environment; install only what the README lists.
- Never commit secrets, tokens, or `.env` files; keep credentials out of
  shell history and out of example outputs.
- Run the CLI tools against throwaway data, not against real user files or
  production systems.
- Prefer the least privilege available: no admin shells, no global config
  rewrites, no network calls you cannot explain.

### Local development: Do

- Read `README.md` and `docs/cli_usage.md` before running anything.
- Verify the whole repo after every change:

```bash
python3 tools/verify_all.py
```

- Keep commits small and described accurately.

##### Do Not

- do not commit generated artifacts, caches, or editor state.
- do not run the example tools with elevated privileges.
- do not disable or weaken the verification harness to make a run pass.
- do not publish internal endpoints, keys, or seed data anywhere public.
