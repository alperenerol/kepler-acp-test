#!/usr/bin/env python3
"""verify_all.py — one-shot repo verification harness (stdlib only, no pytest).

Runs, in order:
  1. every standalone unittest file matching tests/test_*.py (via python3),
  2. doc checks: every .md under docs/ (recursive) plus top-level README.md,
     SECURITY.md and TERMS.md must contain >= 1 fenced bash code block, and
     the marker '##### Do Not' must appear exactly once in SECURITY.md and
     nowhere in any other markdown file.

Prints 'PASS: <relative-path>' / 'FAIL: <relative-path>' per file and one
final 'TOTAL: <n> passed, <f> failed' line (when doc violations exist, a
'TOTAL: <n> doc violations' line precedes it). Exits 0 only when every
check passed (n > 0, f == 0, doc violations == 0); otherwise exits 1.
'-h' / '--help' prints usage and exits 0.
"""

import argparse
import os
import re
import subprocess
import sys

# Repo root derived from this file's own location (no hardcoded absolute
# paths). Runtime checks verify the invocation directory (see _resolve_root);
# ROOT is kept for integrators and tools that import this module.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR_NAME = "tests"
PYTHON = sys.executable or "python3"
TEST_TIMEOUT_SECONDS = 120
MARKER = "##### Do Not"
GUARD_ENV_VAR = "WS3_VERIFY_ALL_TESTS_RUNNING"
USAGE = (
    "usage: verify_all.py [-h | --help]\n"
    "\n"
    "Runs every standalone unittest file under tests/ (pattern test_*.py)\n"
    "and then checks the docs: every .md under docs/ (recursive) plus\n"
    "top-level README.md, SECURITY.md and TERMS.md must contain at least one\n"
    "fenced bash code block, and the marker '##### Do Not' must appear\n"
    "exactly once in SECURITY.md and zero times in every other markdown\n"
    "file. Prints PASS/FAIL per file and a final TOTAL line.\n"
    "\n"
    "options:\n"
    "  -h, --help  show this help message and exit\n"
)


def run_doc_checks(root):
    """Print PASS/FAIL per markdown file; return (passed, violations)."""
    passed = 0
    violations = 0
    for rel in _doc_paths(root):
        text = _load_md_text(rel, root)
        ok = True
        if text is None:
            ok = False
        else:
            has_bash = _has_bash_fence(text)
            count = text.count(MARKER)
            if rel == "SECURITY.md":
                if not has_bash or count != 1:
                    ok = False
            elif not has_bash or count != 0:
                ok = False
        if ok:
            passed += 1
            print("PASS: " + rel)
        else:
            violations += 1
            print("FAIL: " + rel)
    return passed, violations


def _run_test_files(root):
    """Run tests/test_*.py files standalone under Python; return (passed, failed, found)."""
    results = []
    found = False
    for path in _iter_test_files(root):
        found = True
        if not _is_unittest_file(path):
            continue
        results.append(_run_test_file(path, root))
    passed = sum(1 for ok in results if ok)
    failed = len(results) - passed
    if not found:
        print("FAIL: no test files found under tests/")
    elif not results:
        print("FAIL: no runnable unittest files under tests/")
    return passed, failed, found


def _resolve_root():
    """The directory the verifier was launched from — always.

    The cwd IS the repo under verification: integrators and our subprocess
    tests run tools/verify_all.py from the worktree/sandbox root they want
    checked. A directory with no tests/ and no markdown simply falls out of
    the checks as 'FAIL: no test files found' + 'TOTAL: 0 passed' (exit 1),
    which is also the missing/broken-repo contract path.
    """
    return os.path.abspath(os.getcwd())


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if any(arg in ("-h", "--help") for arg in argv):
        print(USAGE)
        return 0
    parser = argparse.ArgumentParser(add_help=False)
    parser.parse_args(argv)  # unknown args -> usage error (exit 2)

    root = _resolve_root()

    passed, failed, found = _run_test_files(root)
    doc_ok, doc_violations = run_doc_checks(root)

    total = passed + doc_ok
    failed_total = failed + doc_violations
    # Spec 5b asks for a doc-violations total; spec 5c fixes the FINAL line
    # as 'TOTAL: <n> passed, <f> failed' — so the doc line is printed first.
    if doc_violations > 0:
        print("TOTAL: {} doc violations".format(doc_violations))
    print("TOTAL: {} passed, {} failed".format(total, failed_total))
    if failed_total > 0:
        return 1
    if not found or (passed + failed) == 0 or passed == 0:
        return 1
    return 0


# ---------------------------------------------------------------------------
# internals
# ---------------------------------------------------------------------------


def _doc_paths(root):
    docs_dir = os.path.join(root, "docs")
    if os.path.isdir(docs_dir):
        for dirpath, dirnames, filenames in os.walk(docs_dir):
            dirnames.sort()
            for filename in sorted(filenames):
                if filename.endswith(".md"):
                    yield os.path.relpath(
                        os.path.join(dirpath, filename), root
                    ).replace(os.sep, "/")
    for name in ("README.md", "SECURITY.md", "TERMS.md"):
        if os.path.isfile(os.path.join(root, name)):
            yield name


def _load_md_text(rel, root):
    abspath = os.path.join(root, *rel.split("/"))
    try:
        with open(abspath, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return None


def _has_bash_fence(text):
    """True if the file has a fenced block whose info string contains 'bash'."""
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if not in_fence:
            if stripped.startswith("```"):
                if re.search(r"\bbash\b", stripped):
                    return True
                in_fence = True
        elif stripped.startswith("```"):
            in_fence = False
    return False


def _iter_test_files(root):
    tests_dir = os.path.join(root, TEST_DIR_NAME)
    if not os.path.isdir(tests_dir):
        return
    for name in sorted(os.listdir(tests_dir)):
        if name.startswith("test_") and name.endswith(".py"):
            yield os.path.join(tests_dir, name)


def _is_unittest_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            source = handle.read()
    except OSError:
        return False
    return "import unittest" in source or "from unittest import" in source


def _run_test_file(path, root):
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    env = os.environ.copy()
    env.setdefault(GUARD_ENV_VAR, "1")
    try:
        proc = subprocess.run(
            [PYTHON, os.path.abspath(path)],
            cwd=root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=TEST_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        print("FAIL: " + rel)
        sys.stderr.write("{}: launch failed: {}\n".format(rel, exc))
        return False
    if proc.returncode == 0:
        print("PASS: " + rel)
        return True
    print("FAIL: " + rel)
    err = (proc.stderr or proc.stdout or "").strip()
    if err:
        tail = "\n".join(err.splitlines()[-15:])
        sys.stderr.write("{}: test output (tail):\n{}\n".format(rel, tail))
    return False


if __name__ == "__main__":
    sys.exit(main())
