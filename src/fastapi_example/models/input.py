from pydantic import BaseModel, Field


class InputData(BaseModel):
    A: float = Field(description="The first numeric value")
    B: float = Field(description="The second numeric value")
