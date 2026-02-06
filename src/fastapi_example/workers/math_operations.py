import logging

logger = logging.getLogger(__name__)


def add_numbers(a: float, b: float) -> float:
    result = a + b
    logger.debug("Adding %s + %s = %s", a, b, result)
    return result


def subtract_numbers(a: float, b: float) -> float:
    result = a - b
    logger.debug("Subtracting %s - %s = %s", a, b, result)
    return result


def multiply_numbers(a: float, b: float) -> float:
    result = a * b
    logger.debug("Multiplying %s * %s = %s", a, b, result)
    return result


def divide_numbers(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    result = a / b
    logger.debug("Dividing %s / %s = %s", a, b, result)
    return result
