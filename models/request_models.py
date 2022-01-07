from pydantic import BaseModel
from typing import Optional


class AccountReq(BaseModel):
    display_name: str
    unique_key: str


class FriendCoordReq(BaseModel):
    friend_name: str
    start_date: Optional[str]
    end_date: Optional[str]


class FriendAddDeleteReq(BaseModel):
    friend_name: str


class RecoverAccReq(BaseModel):
    unique_key: str


class AcceptDeclineFriendReq(BaseModel):
    friend_name: str
    action: str


class UploadCoordReq(BaseModel):
    timestamp: str
    latitude: float
    longitude: float
