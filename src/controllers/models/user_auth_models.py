from pydantic import BaseModel


class CreateNewAccount(BaseModel):
    user_id: str
    nickname: str
    password: str


class Login(BaseModel):
    user_id: str
    password: str
