# kepler-acp-test

Three small Python CLI modules written end to end by three parallel AI agents, integrated by a fourth. Not a product: it is the artifact of an orchestration experiment, kept public because the story is the point.

**Read the full writeup with screenshots and timings:** [`alperenerol/kepler-acp-writeup`](https://github.com/alperenerol/kepler-acp-writeup)

## What this is

One Hermes Agent session (GitKraken Kepler, custom ACP agent) acted as a lead: it split a tiny objective into three workstream tasks, started a coding agent session per workstream in an isolated git worktree, then merged the results back. No code in this repository was written by a human.

| Workstream | Branch | Delivers |
|---|---|---|
| WS1 | `kepler/task-d0561e1a` | `keplertool/` core CLI (`greet`, `add`), argparse, `pyproject.toml` |
| WS2 | `kepler/task-1cdb0bbd` | `reporting/` JSON report module: `load_events`, `aggregate`, `format_summary` |
| WS3 | `kepler/task-8b095751` | `docs/` manuals, `SECURITY.md`, `TERMS.md`, `tools/verify_all.py` self-verification harness |

Each workstream committed to its own branch; the lead then merged all three, resolved the `README.md` conflict, and added two integration fixes.Git history preserves the whole structure (3 work commits + 2 cleanup + 3 merges + 2 fixes).

## Try it

Requires Python 3.9+ (standard library only).

```bash
git clone https://github.com/alperenerol/kepler-acp-test.git
cd kepler-acp-test

python3 -m keplertool.cli greet Alper     # Hello, Alper!
python3 -m keplertool.cli add 2 --b 3     # 5
```

```bash
python3 -m unittest discover -s tests -q   # combined test suite
python3 tools/verify_all.py                # WS3 harness: tests + doc checks
```

## Verify

```bash
python3 -m unittest discover -s tests -q   # combined test suite
python3 tools/verify_all.py                # WS3 harness: tests + doc checks
```

Both were run green at integration time: 51 tests passed, harness 5/5 PASS, exit 0.

## Layout

- `keplertool/` — core CLI application (WS1)
- `reporting/` — reporting helpers that consume CLI output (WS2)
- `tests/` — test suites for all modules
- `docs/` — `cli_usage.md` manual (WS3)
- `tools/verify_all.py` — one-shot verification harness: every standalone test file plus documentation checks (fenced bash blocks present; the security marker rule enforced globally)
- `SECURITY.md`, `TERMS.md` — agent-authored governance stubs (WS3)

## Notes

- The quirky, deliberately over-strict doc checks in `verify_all.py` (bash fences everywhere, a security marker counted globally) are the agents' own doing; they make the "docs must stay in sync" constraint machine-checkable.
- `SECURITY.md` documents responsible disclosure and local development; `TERMS.md` defines vocabulary used across the docs, because three separate writers otherwise drift apart.
