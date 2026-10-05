from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.auth import create_access_token, get_current_user, get_password_hash, verify_password
from app.backend.memory.db import get_pg_connection

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    user_id: str
    username: str

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    # Check if username exists
    async with get_pg_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id FROM users WHERE username = %s", (user.username,))
            if await cur.fetchone():
                raise HTTPException(status_code=400, detail="Username already registered")
            
            # Insert new user
            hashed_pw = get_password_hash(user.password)
            await cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                (user.username, hashed_pw)
            )
            user_id = (await cur.fetchone())[0]
            await conn.commit()
            
    # Create token
    access_token = create_access_token(data={"sub": str(user_id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    async with get_pg_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (form_data.username,))
            user_record = await cur.fetchone()
            
    if not user_record or not verify_password(form_data.password, user_record[1]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": str(user_record[0])})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(user_id: str = Depends(get_current_user)):
    async with get_pg_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
            record = await cur.fetchone()
            
    if not record:
        raise HTTPException(status_code=404, detail="User not found")
        
    return UserResponse(user_id=user_id, username=record[0])
