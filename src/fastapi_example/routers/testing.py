import logging

from fastapi import APIRouter, Depends

from fastapi_example.auth.authentication import get_current_user
from fastapi_example.models.input import InputData

logger = logging.getLogger(__name__)


fastapi_test_router = APIRouter(
    tags=["fastapi_example_test"], prefix="/fastapi_example_test"
)


@fastapi_test_router.post(
    "/example",
    operation_id="test_fastapi_example",
    status_code=200,
)
def analysis(input_data: InputData, user: str = Depends(get_current_user)) -> dict:
    logger.debug("User %s", user)
    logger.debug("Input data %s", input_data)
    return {"results": 4}
