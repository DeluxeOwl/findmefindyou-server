from pydantic import BaseModel


class AccountReq(BaseModel):
    display_name: str
    unique_key: str


# TODO: add optional fields: starting time and end time
# validate that starting time is no more than one week ago
class FriendCoordReq(BaseModel):
    friend_name: str


class FriendDeleteReq(BaseModel):
    friend_name: str
