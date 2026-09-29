# kepler-acp-test

`kepler-acp-test` is a Python CLI example suite: a small playground of
command-line tools (`keplertool` and friends) kept in monorepo-style layout
for exercising docs, tests, and verification tooling.

## Layout

- `keplertool/` — the `keplertool` command-line application.
- `reporting/` — reporting helpers that consume CLI output.
- `tests/` — standalone `unittest` test files (run directly with `python3`).
- `docs/` — manuals and usage guides.
- `tools/verify_all.py` — one-shot verification harness (tests + docs).

## Quick start

Check out the repository, then introspect the CLI to see what it offers:

```bash
keplertool --help
```

## Verify everything

From the repository root, run `python3 tools/verify_all.py`.

It executes every standalone test file under `tests/`, then checks the
documentation (every markdown file must expose a fenced bash block, and the
security marker rules must hold), ending with a `TOTAL:` summary line.

## Notes

- Python 3.9-compatible, standard library only.
- `SECURITY.md` documents responsible disclosure and local development best
  practices. `TERMS.md` defines the vocabulary used across the docs.

