import logging

from fastapi import APIRouter, HTTPException, Request, status

from fastapi_example.models.input import InputData
from fastapi_example.workers.math_operations import (
    add_numbers,
    divide_numbers,
    multiply_numbers,
    subtract_numbers,
)

logger = logging.getLogger(__name__)

math_router = APIRouter(tags=["math"], prefix="/math")


@math_router.post("/add", status_code=200)
def add(input_data: InputData, request: Request) -> dict:
    user_info = request.state.user_info
    user = user_info.get("sub")
    logger.debug("User %s requesting add operation", user)
    result = add_numbers(input_data.A, input_data.B)
    return {"operation": "add", "a": input_data.A, "b": input_data.B, "result": result}


@math_router.post("/subtract", status_code=200)
def subtract(input_data: InputData, request: Request) -> dict:
    user_info = request.state.user_info
    user = user_info.get("sub")
    logger.debug("User %s requesting subtract operation", user)
    result = subtract_numbers(input_data.A, input_data.B)
    return {
        "operation": "subtract",
        "a": input_data.A,
        "b": input_data.B,
        "result": result,
    }


@math_router.post("/multiply", status_code=200)
def multiply(input_data: InputData, request: Request) -> dict:
    user_info = request.state.user_info
    user = user_info.get("sub")
    logger.debug("User %s requesting multiply operation", user)
    result = multiply_numbers(input_data.A, input_data.B)
    return {
        "operation": "multiply",
        "a": input_data.A,
        "b": input_data.B,
        "result": result,
    }


@math_router.post("/divide", status_code=200)
def divide(input_data: InputData, request: Request) -> dict:
    user_info = request.state.user_info
    user = user_info.get("sub")
    logger.debug("User %s requesting divide operation", user)
    try:
        result = divide_numbers(input_data.A, input_data.B)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    return {
        "operation": "divide",
        "a": input_data.A,
        "b": input_data.B,
        "result": result,
    }
