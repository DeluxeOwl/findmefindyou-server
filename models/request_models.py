from pydantic import BaseModel


class AccountReq(BaseModel):
    display_name: str
    unique_key: str


class FriendCoordReq(BaseModel):
    friend_name: str
