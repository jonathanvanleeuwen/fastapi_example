import pytest

from fastapi_example.workers.math_operations import (
    add_numbers,
    divide_numbers,
    multiply_numbers,
    subtract_numbers,
)


def test_add_numbers():
    assert add_numbers(5, 3) == 8
    assert add_numbers(-5, 3) == -2
    assert add_numbers(0, 0) == 0
    assert add_numbers(1.5, 2.5) == 4.0


def test_subtract_numbers():
    assert subtract_numbers(5, 3) == 2
    assert subtract_numbers(3, 5) == -2
    assert subtract_numbers(0, 0) == 0
    assert subtract_numbers(10.5, 5.5) == 5.0


def test_multiply_numbers():
    assert multiply_numbers(5, 3) == 15
    assert multiply_numbers(-5, 3) == -15
    assert multiply_numbers(0, 100) == 0
    assert multiply_numbers(2.5, 4) == 10.0


def test_divide_numbers():
    assert divide_numbers(10, 2) == 5
    assert divide_numbers(15, 3) == 5
    assert divide_numbers(7, 2) == 3.5
    assert divide_numbers(-10, 2) == -5


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide_numbers(10, 0)
