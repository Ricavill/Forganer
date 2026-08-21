from pydantic import BaseModel, EmailStr


class UserSignUp(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    last_name: str
    email: EmailStr

    model_config = {"from_attributes": True}
