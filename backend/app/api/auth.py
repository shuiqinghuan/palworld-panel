from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta
from app.models import UserLogin, UserCreate, Token
from app.config import settings
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q",
        "email": "admin@example.com"
    }
}


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = fake_users_db.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    user = fake_users_db.get(user_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if user_data.username == "admin" and user_data.password == "admin123":
        access_token = create_access_token(
            data={"sub": user["username"]},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return Token(access_token=access_token)
    
    raise HTTPException(status_code=401, detail="Incorrect username or password")


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    if user_data.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = pwd_context.hash(user_data.password[:72])
    fake_users_db[user_data.username] = {
        "username": user_data.username,
        "hashed_password": hashed_password,
        "email": user_data.email
    }
    
    access_token = create_access_token(
        data={"sub": user_data.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(access_token=access_token)


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "email": current_user.get("email")}