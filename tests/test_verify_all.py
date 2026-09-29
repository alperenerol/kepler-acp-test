#!/usr/bin/env python3
"""Subprocess tests for tools/verify_all.py.

Runnable under pytest AND standalone (``python3 tests/test_verify_all.py``)
since tools/verify_all.py executes every tests/test_*.py file standalone.

Each verify_all subprocess runs with HOME pointed at a fresh writable temp
dir, so the script must not depend on the caller's real HOME.
"""

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFY_SCRIPT = os.path.join(ROOT, "tools", "verify_all.py")
PYTHON = sys.executable or "python3"

# Recursion guard: when a verify_all run (ours or a nested one) executes this
# test file, child verify_all subprocesses are launched with this variable set
# so the nested execution of this file skips its tests instead of forking
# another generation of verifiers.
GUARD_ENV_VAR = "WS3_VERIFY_ALL_TESTS_RUNNING"


def _write(path, text):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def _import_verify_ns():
    """Load tools/verify_all.py as a module namespace without running main()."""
    import runpy

    return runpy.run_path(VERIFY_SCRIPT, run_name="ws3_verify_all_under_test")


def _call_main(ns, argv):
    """Invoke the verifier's main() with stdout captured; returns (code, out).

    Catches SystemExit so both the argparse --help path (SystemExit 0) and the
    failure path (SystemExit 1) can be inspected.
    """
    buf = io.StringIO()
    code = None
    outcome = None
    with contextlib.redirect_stdout(buf):
        try:
            outcome = ns["main"](list(argv))
        except SystemExit as exc:
            code = exc.code
    return outcome, code, buf.getvalue()


def _make_repo(tmp_parent, files):
    """Create a fresh fake repo dir from a {relpath: text} mapping."""
    repo = tempfile.mkdtemp(prefix="repo_", dir=tmp_parent)
    for relpath, text in files.items():
        _write(os.path.join(repo, relpath), text)
    return repo


def _run_verify(repo, args=(), script=None):
    env = os.environ.copy()
    env["HOME"] = tempfile.mkdtemp(prefix="vhome_")
    env[GUARD_ENV_VAR] = "1"
    return subprocess.run(
        [PYTHON, script or VERIFY_SCRIPT, *args],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )


PASSING_TEST_FILE = (
    "#!/usr/bin/env python3\n"
    "import unittest\n"
    "\n"
    "\n"
    "class Ok(unittest.TestCase):\n"
    "    def test_passes(self):\n"
    "        self.assertTrue(True)\n"
    "\n"
    "\n"
    "if __name__ == \"__main__\":\n"
    "    unittest.main()\n"
)

FAILING_TEST_FILE = (
    "#!/usr/bin/env python3\n"
    "import unittest\n"
    "\n"
    "\n"
    "class Bad(unittest.TestCase):\n"
    "    def test_fails(self):\n"
    "        self.fail(\"boom\")\n"
    "\n"
    "\n"
    "if __name__ == \"__main__\":\n"
    "    unittest.main()\n"
)

GOOD_README = "# demo\n\nA short description.\n\n```bash\nkeplertool --help\n```\n"


class VerifyAllTests(unittest.TestCase):
    def setUp(self):
        if os.environ.get(GUARD_ENV_VAR) == "1":
            self.skipTest("recursion guard: nested verify_all execution")
        self.tmp_parent = tempfile.mkdtemp(prefix="ws3tmp_")
        self.addCleanup(shutil.rmtree, self.tmp_parent, True)

    def test_help_flag_exits_zero(self):
        repo = _make_repo(self.tmp_parent, {})
        try:
            result = _run_verify(repo, ["--help"])
            self.assertEqual(result.returncode, 0)
            self.assertIn("usage", result.stdout.lower())
        finally:
            shutil.rmtree(repo, True)

    def test_help_h_exits_zero(self):
        repo = _make_repo(self.tmp_parent, {})
        result = _run_verify(repo, ["-h"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        shutil.rmtree(repo, True)

    def test_clean_repo_exits_zero_and_reports(self):
        repo = _make_repo(
            self.tmp_parent,
            {"tests/test_ok.py": PASSING_TEST_FILE, "README.md": GOOD_README},
        )
        result = _run_verify(repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: tests/test_ok.py", result.stdout)
        self.assertIn("PASS: README.md", result.stdout)
        last = result.stdout.strip().splitlines()[-1]
        self.assertEqual(last, "TOTAL: 2 passed, 0 failed")
        shutil.rmtree(repo, True)

    def test_failing_test_file_exits_1(self):
        repo = _make_repo(
            self.tmp_parent,
            {
                "tests/test_ok.py": PASSING_TEST_FILE,
                "tests/test_bad.py": FAILING_TEST_FILE,
                "README.md": GOOD_README,
            },
        )
        result = _run_verify(repo)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("PASS: tests/test_ok.py", result.stdout)
        self.assertIn("FAIL: tests/test_bad.py", result.stdout)
        last = result.stdout.strip().splitlines()[-1]
        self.assertEqual(last, "TOTAL: 2 passed, 1 failed")
        shutil.rmtree(repo, True)

    def test_docs_without_bash_fence_exit_1(self):
        repo = _make_repo(
            self.tmp_parent,
            {
                "tests/test_ok.py": PASSING_TEST_FILE,
                "README.md": GOOD_README,
                "docs/plan.md": "# plan\n\nno fenced code block here\n",
            },
        )
        result = _run_verify(repo)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL: docs/plan.md", result.stdout)
        self.assertIn("1 doc violation", result.stdout)
        shutil.rmtree(repo, True)

    def test_missing_verify_script_exits_nonzero(self):
        # In a bare repo there is no tools/verify_all.py at all: launching it
        # must fail without producing a zero exit status.
        repo = _make_repo(self.tmp_parent, {})
        result = _run_verify(repo, script=os.path.join(repo, "tools", "verify_all.py"))
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        shutil.rmtree(repo, True)

    def test_unit_help_branch_exits_0(self):
        self.assertTrue(os.path.isfile(VERIFY_SCRIPT), "tools/verify_all.py missing")
        ns = _import_verify_ns()
        # main() returns the exit code; only argparse paths raise SystemExit.
        outcome, exc_code, out = _call_main(ns, ["--help"])
        self.assertIsNone(exc_code)
        self.assertEqual(outcome, 0)
        self.assertIn("usage", out.lower())

    def test_unit_missing_script_branch_exits_1(self):
        if not os.path.isfile(VERIFY_SCRIPT):
            self.skipTest("tools/verify_all.py not built yet (RED phase)")
        # Break BOTH resolution candidates: run from a dir without
        # tools/verify_all.py and patch the module ROOT to another one, so
        # the no-repo branch fails loudly regardless of the real repo state.
        ns = _import_verify_ns()
        original_cwd = os.getcwd()
        fake_cwd = tempfile.mkdtemp(prefix="no_tools_cwd_")
        fake_root = tempfile.mkdtemp(prefix="no_tools_root_")
        self.addCleanup(shutil.rmtree, fake_cwd, True)
        self.addCleanup(shutil.rmtree, fake_root, True)
        self.addCleanup(os.chdir, original_cwd)
        os.chdir(fake_cwd)
        patched = dict(ns)
        patched["ROOT"] = fake_root
        with unittest.mock.patch.dict(ns, patched):
            outcome, _, _ = _call_main(ns, [])
        self.assertEqual(outcome, 1)


if __name__ == "__main__":
    unittest.main()
