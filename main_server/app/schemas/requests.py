from datetime import datetime

from pydantic import BaseModel, EmailStr


class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class UserUpdatePasswordRequest(BaseRequest):
    password: str


class UserCreateRequest(BaseRequest):
    email: EmailStr
    password: str


class ClientRequest(BaseRequest):
    hostname: str
    age: float
    access_rights: str
    last_access_date: datetime
    last_modification_date: datetime

