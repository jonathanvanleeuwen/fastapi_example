from pydantic import BaseModel


class InputData(BaseModel):
    A: float
    B: float
