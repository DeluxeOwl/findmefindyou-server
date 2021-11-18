from pydantic import BaseModel


class AccountReq(BaseModel):
    display_name: str
    unique_key: str
