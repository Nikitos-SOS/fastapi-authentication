from sqlalchemy.orm import Session
from passlib.context import CryptContext


# from server.routes.user import get_password_hash

from server.models.user import User
from server.schemas.user import (

    UserCreate,
  
)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Get hash of password
def get_password_hash(password):
    return pwd_context.hash(password)

# Verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


    

def get_user_by_id(db:Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db:Session, username:str):
    return db.query(User).filter(User.username == username).first()

def get_all_users(db:Session, skip:int = 0, limit:int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db:Session, user:UserCreate):
    
    db_user = User(username = user.username, password = get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

