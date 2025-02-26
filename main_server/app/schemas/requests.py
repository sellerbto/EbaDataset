from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr, HttpUrl


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


class DaemonClientRequest(BaseRequest):
    dataset_general_info_id: int
    hostname: str
    file_path: str
    age: datetime
    access_rights: str
    last_access_date: datetime
    last_modification_date: datetime
    size: int


class LinkDescriptionUpdateRequest(BaseModel):
    url: HttpUrl
    name: Optional[str] = None
    description: Optional[str] = None


class DatasetInfoUpdateRequest(BaseRequest):
    id: int
    name: str
    description: str


class DatasetInfoCreateRequest(BaseRequest):
    name: str
    description: Optional[str] = None