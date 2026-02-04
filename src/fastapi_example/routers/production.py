import logging

from fastapi import APIRouter, Depends

from fastapi_example.auth.authentication import get_current_user
from fastapi_example.models.input import InputData

logger = logging.getLogger(__name__)

fastapi_router = APIRouter(tags=["fastapi_example"], prefix="/fastapi_example")


@fastapi_router.post(
    "/example",
    operation_id="fastapi_example",
    status_code=200,
)
def analysis(input_data: InputData, user: str = Depends(get_current_user)) -> dict:
    logger.debug("User %s", user)
    logger.debug("Input data %s", input_data)
    return {"result": input_data.A + input_data.B}
