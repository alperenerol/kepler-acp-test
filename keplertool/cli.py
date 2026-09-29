"""Command-line interface for keplertool.

Two subcommands:

    keplertool greet Alice      -> prints ``Hello, Alice!`` (exit 0)
    keplertool add 1 --b 2      -> prints ``3`` (exit 0)

``--b``/``-b`` is required for ``add``; missing or invalid values are
argparse errors (exit 2). Blank greet input is a deterministic non-zero
runtime error (exit 3). Errors never print to stdout — a single explanatory
line goes to stderr.
"""

import argparse
import sys

from keplertool.core import add, greet


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="keplertool",
        description="keplertool command-line tool",
    )
    subparsers = parser.add_subparsers(dest="command")

    p_greet = subparsers.add_parser("greet", help="Print a greeting")
    p_greet.add_argument("name", help="Name to greet")

    p_add = subparsers.add_parser("add", help="Add two integers")
    p_add.add_argument("a", help="First integer")
    p_add.add_argument(
        "--b",
        "-b",
        required=True,
        help="Second integer (required)",
    )
    return parser


def main(argv=None):
    """Run the CLI. Returns int exit code (2 on usage errors, 3 on runtime errors)."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "greet":
        try:
            message = greet(args.name)
        except ValueError:
            print("keplertool greet: name is blank", file=sys.stderr)
            return 3
        print(message)
        return 0

    if args.command == "add":
        try:
            a = int(args.a)
            b = int(args.b)
        except ValueError:
            print("keplertool add: arguments must be integers", file=sys.stderr)
            return 2
        print(add(a, b))
        return 0

    # No subcommand given: standard argparse usage error (SystemExit, code 2).
    parser.error("the following arguments are required: command")
