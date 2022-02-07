from pydantic import BaseModel
from typing import List, Optional

class BaseUser(BaseModel):
    username:str

class UserCreate(BaseUser):
    password:str

    class Config:
        schema_extra = {
            'example':{
                'username': 'username',
                'password': 'password'
            }
        }

class User(BaseUser):
    id: int
    is_active: bool

class UserInDB(User):
    password: str