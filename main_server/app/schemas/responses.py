from pydantic import BaseModel, ConfigDict, EmailStr
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

class DatasetInfo(BaseResponse):
    name: str
    size: int
    host: str
    created_at_server: datetime
    created_at_host: datetime
    last_read: datetime
    last_modified: datetime
    frequency_of_use_in_month: int
