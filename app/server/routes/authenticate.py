from fastapi import APIRouter, Depends, HTTPException, status

from server.schemas.token import Token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt


from server.cruds.user import (
    get_user_by_username,
    verify_password
)

from server.routes.user import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, get_db

router = APIRouter()


def authenticate_user(username:str, password: str, db:Session):
    # Get user from db by username
    user = get_user_by_username(db, username)
    # Check for existing of user
    if not user:
        return False
    # Check correction entered password of user and actual password
    if not verify_password(password, user.password):
        return False
    # Return user from database
    return user

def create_access_token(data:dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp':expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub':user.username},
        expires_delta = access_token_expires
    )
    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }