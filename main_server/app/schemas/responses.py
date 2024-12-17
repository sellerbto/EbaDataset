from typing import Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl
from datetime import datetime

class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AccessTokenResponse(BaseResponse):
    token_type: str = "Bearer"
    access_token: str
    expires_at: int
    refresh_token: str
    refresh_token_expires_at: int

class UserResponse(BaseResponse):
    user_id: str
    email: EmailStr

class LinkResponse(BaseResponse):
    url: HttpUrl
    name: str
    description: str

class DatasetInfo(BaseResponse):
    id: int
    file_path: str
    size: int
    host: str
    created_at_server: Optional[datetime] = None
    created_at_host: Optional[datetime] = None
    last_read: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    frequency_of_use_in_month: Optional[int] = None

class DatasetsSummary(BaseModel):
    name: str
    description: str
    datasets_infos: List[DatasetInfo]
