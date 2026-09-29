"""Core helpers for keplertool: greeting and integer addition."""


def greet(name: str) -> str:
    """Return ``Hello, <name>!`` for the cleaned name.

    Surrounding whitespace is stripped; if nothing remains after stripping,
    a ValueError is raised.
    """
    clean = name.strip()
    if not clean:
        raise ValueError("name is empty")
    return f"Hello, {clean}!"


def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b
