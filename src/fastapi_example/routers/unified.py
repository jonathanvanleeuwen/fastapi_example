import logging

from fastapi import APIRouter, Request

from fastapi_example.models.input import InputData
from fastapi_example.workers import (
    add_numbers,
    divide_numbers,
    multiply_numbers,
    subtract_numbers,
)

logger = logging.getLogger(__name__)

# This router accepts BOTH OAuth and API key authentication
unified_router = APIRouter(tags=["unified_auth"], prefix="/api")


@unified_router.post("/add", operation_id="unified_add_numbers", status_code=200)
def add(input_data: InputData, request: Request) -> dict:
    user_info = request.state.user_info
    user = user_info.get("sub")
    auth_type = user_info.get("auth_type")
    logger.debug(f"User {user} (auth: {auth_type}) requesting add operation")
    result = add_numbers(input_data.A, input_data.B)
    return {
        "operation": "add",
        "a": input_data.A,
        "b": input_data.B,
        "result": result,
        "user": user,
        "auth_type": auth_type,
    }


@unified_router.post(
    "/subtract", operation_id="unified_subtract_numbers", status_code=200
)
def subtract(input_data: InputData, request: Request) -> dict:
    user_info = request.state.user_info
    user = user_info.get("sub")
    auth_type = user_info.get("auth_type")
    logger.debug(f"User {user} (auth: {auth_type}) requesting subtract operation")
    result = subtract_numbers(input_data.A, input_data.B)
    return {
        "operation": "subtract",
        "a": input_data.A,
        "b": input_data.B,
        "result": result,
        "user": user,
        "auth_type": auth_type,
    }


@unified_router.post(
    "/multiply", operation_id="unified_multiply_numbers", status_code=200
)
def multiply(input_data: InputData, request: Request) -> dict:
    user_info = request.state.user_info
    user = user_info.get("sub")
    auth_type = user_info.get("auth_type")
    logger.debug(f"User {user} (auth: {auth_type}) requesting multiply operation")
    result = multiply_numbers(input_data.A, input_data.B)
    return {
        "operation": "multiply",
        "a": input_data.A,
        "b": input_data.B,
        "result": result,
        "user": user,
        "auth_type": auth_type,
    }


@unified_router.post("/divide", operation_id="unified_divide_numbers", status_code=200)
def divide(input_data: InputData, request: Request) -> dict:
    user_info = request.state.user_info
    user = user_info.get("sub")
    auth_type = user_info.get("auth_type")
    logger.debug(f"User {user} (auth: {auth_type}) requesting divide operation")
    result = divide_numbers(input_data.A, input_data.B)
    return {
        "operation": "divide",
        "a": input_data.A,
        "b": input_data.B,
        "result": result,
        "user": user,
        "auth_type": auth_type,
    }
