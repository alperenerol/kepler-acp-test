"""Tests for keplertool.core: greet and add."""

import pytest

from keplertool.core import add, greet


class TestGreet:
    def test_greet_success_message(self):
        assert greet("Alice") == "Hello, Alice!"

    def test_greet_strips_surrounding_whitespace(self):
        assert greet("  Bob  ") == "Hello, Bob!"

    def test_greet_returns_str(self):
        assert isinstance(greet("World"), str)

    def test_greet_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            greet("")

    def test_greet_whitespace_only_raises_value_error(self):
        with pytest.raises(ValueError):
            greet("   \t  ")


class TestAdd:
    def test_add_normal(self):
        assert add(2, 3) == 5

    def test_add_zero(self):
        assert add(0, 0) == 0

    def test_add_negative(self):
        assert add(-1, 1) == 0
        assert add(-2, -3) == -5

    def test_add_large_integers(self):
        big = 10**18
        assert add(big, big) == 2 * big

    def test_add_returns_int(self):
        assert isinstance(add(1, 2), int)
