# TERMS

Glossary for `kepler-acp-test` — the vocabulary used across the docs and
tooling in this repository.

## event

An **event** is a single observable action occurring in or around a CLI tool
invocation: a command start, a parsed argument, a produced line of output, an
error, or a finished run. Events are the raw material everything else in this
repository reasons about; they are emitted by the tools and consumed by the
reporting helpers.

## summary

A **summary** is an aggregated view over a set of events: counts, totals,
success/failure splits, or other rollups produced after a run completes. In
this repository a summary is what `reporting/` builds from tool events, and
what `tools/verify_all.py` prints at the end of a run (its `TOTAL:` line is a
summary of the verification results). A summary is always derived from
events, never collected on its own.

## CLI

A **CLI** (command-line interface) is a program operated from a shell by
passing a command name plus flags and arguments — the interface style every
tool in this repository follows. The primary example here is `keplertool`,
whose keyboard-free interface looks like this:

```bash
python3 tools/verify_all.py
```

CLIs are composable: they read stdin, write stdout, and signal success or
failure through their exit code, which is what makes them easy to script and
verify automatically.
