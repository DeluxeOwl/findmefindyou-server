from pydantic import BaseModel
from typing import Optional


class AccountReq(BaseModel):
    display_name: str
    unique_key: str


class DateStartEndReq(BaseModel):
    start_date: Optional[str]
    end_date: Optional[str]


class FriendCoordReq(DateStartEndReq):
    friend_name: str


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
