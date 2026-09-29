"""Tests for keplertool.cli: argparse CLI with greet/add subcommands.

Happy paths and errors are exercised through monkeypatched sys.argv; streams
are captured with capsys. Error paths must print nothing on stdout.
"""

import sys

import pytest

from keplertool.cli import main


def run_cli(monkeypatch, *argv):
    """Patch sys.argv and invoke main() through its default argv path."""
    monkeypatch.setattr(sys, "argv", ["keplertool", *argv])
    return main()


class TestGreetSubcommand:
    def test_greet_happy_path(self, monkeypatch, capsys):
        code = run_cli(monkeypatch, "greet", "Alice")
        captured = capsys.readouterr()
        assert code == 0
        assert captured.out == "Hello, Alice!\n"
        assert captured.err == ""

    def test_greet_blank_input_nonzero_exit_no_stdout(self, monkeypatch, capsys):
        code = run_cli(monkeypatch, "greet", "   ")
        captured = capsys.readouterr()
        assert code != 0
        assert captured.out == ""
        assert captured.err != ""

    def test_greet_missing_name_argparse_error_exit_2(self, monkeypatch, capsys):
        with pytest.raises(SystemExit) as excinfo:
            run_cli(monkeypatch, "greet")
        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert captured.out == ""


class TestAddSubcommand:
    def test_add_happy_path(self, monkeypatch, capsys):
        code = run_cli(monkeypatch, "add", "1", "--b", "2")
        captured = capsys.readouterr()
        assert code == 0
        assert captured.out == "3\n"
        assert captured.err == ""

    def test_add_short_option_b(self, monkeypatch, capsys):
        code = run_cli(monkeypatch, "add", "1", "-b", "2")
        captured = capsys.readouterr()
        assert code == 0
        assert captured.out == "3\n"

    def test_add_missing_b_exits_2(self, monkeypatch, capsys):
        with pytest.raises(SystemExit) as excinfo:
            run_cli(monkeypatch, "add", "1")
        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert captured.out == ""

    def test_add_missing_positional_a_exits_2(self, monkeypatch, capsys):
        with pytest.raises(SystemExit) as excinfo:
            run_cli(monkeypatch, "add", "--b", "2")
        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert captured.out == ""


class TestCliRouting:
    def test_no_subcommand_exits_2(self, monkeypatch, capsys):
        with pytest.raises(SystemExit) as excinfo:
            run_cli(monkeypatch)
        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert captured.out == ""

    def test_unknown_subcommand_exits_2(self, monkeypatch, capsys):
        with pytest.raises(SystemExit) as excinfo:
            run_cli(monkeypatch, "frobnicate")
        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert captured.out == ""
