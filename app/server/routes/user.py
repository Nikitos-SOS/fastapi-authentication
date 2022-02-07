from fastapi import APIRouter,  Depends, HTTPException, status



from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from numpy import deprecate

from sqlalchemy.orm import Session
from server.database import SessionLocal, engine
from server.cruds.user import (
    get_all_users,
    get_user_by_id,
    get_user_by_username,
    create_user,
)
from server.schemas.user import (
    BaseUser,
    UserCreate,
    User
)
from server.schemas.token import (
    TokenData
)

from server.models.user import Base

Base.metadata.create_all(bind=engine)

SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(token: str = Depends(oauth2_scheme), db:Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username:str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    user = User(id = user.id, username = user.username, is_active = user.is_active)
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):

    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

router = APIRouter()

@router.get('/all')
def get_all_users_data( skip: int = 0, limit: int = 100, db:Session = Depends(get_db) ):
    return get_all_users(db, skip, limit)

@router.post('/')
def create_user_data(user:UserCreate, db:Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if db_user:
        return HTTPException(404, 'Usernme already registered')
    return create_user(db, user)

@router.get('/{id}')
def get_user_data_by_id(id:int, db:Session = Depends(get_db)):
    return get_user_by_id(db, id)

@router.get('/get/{username}',response_model=User)
def get_user_data_by_username(username:str, db:Session = Depends(get_db)):
    user =  get_user_by_username(db, username)
    return User(username = user.username, id = user.id, is_active = user.is_active)

@router.get('/me/')
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

