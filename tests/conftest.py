# Empty conftest.py at the repo root: pytest's prepend import mode adds this
# directory to sys.path when loading it, so tests can `import keplertool`
# regardless of how pytest is invoked (python -m pytest, bare pytest, or a
# different working directory).
