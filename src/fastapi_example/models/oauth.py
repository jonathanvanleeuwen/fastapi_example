from pydantic import BaseModel


class InputData(BaseModel):
    A: float
    B: float


class AuthorizationRequest(BaseModel):
    redirect_uri: str


class TokenRequest(BaseModel):
    code: str
    redirect_uri: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
