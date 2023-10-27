from pydantic import BaseModel, Field, EmailStr


class TweetSchema(BaseModel):
    id: int = Field(default=None)
    content: str = Field(default=None)


class UserSchema(BaseModel):
    id: int = Field(default=None)
    fullname: str = Field(default=None)
    username: str = Field(default=None)
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)


# class UserLoginSchema(BaseModel):
#     username: str = Field(default=None)
#     # email: EmailStr = Field(default=None)
#     password: str = Field(default=None)


class TokenSchema(BaseModel):
    access_token: str = Field(default=None)
    token_type: str = Field(default=None)
