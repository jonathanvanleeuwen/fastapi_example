import logging

from fastapi import APIRouter, Request

from fastapi_example.models.input import InputData
from fastapi_example.workers import add_numbers

logger = logging.getLogger(__name__)


fastapi_test_router = APIRouter(
    tags=["fastapi_example_test"], prefix="/fastapi_example_test"
)


@fastapi_test_router.post("/test", operation_id="test_endpoint", status_code=200)
def test_endpoint(input_data: InputData, request: Request) -> dict:
    user_info = request.state.user_info
    user = user_info.get("sub")
    logger.debug(f"Test endpoint called by user {user}")
    result = add_numbers(input_data.A, input_data.B)
    return {"test_mode": True, "result": result}
