from fastapi import APIRouter, HTTPException, Depends
import aiosqlite
from models.schemas import UserLogin, UserRegister, UserResponse, TokenResponse
from utils.auth_utils import hash_password, verify_password, create_access_token, get_current_user
from config import DB_PATH

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE username = ?", (user_data.username,)
        )
        user = await cursor.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    user = dict(user)
    if not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token({"user_id": user["id"], "role": user["role"]})

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user["id"],
            username=user["username"],
            name=user["name"],
            role=user["role"],
            class_name=user.get("class_name"),
            major=user.get("major"),
            created_at=user.get("created_at", "")
        )
    )

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    async with aiosqlite.connect(DB_PATH) as db:
        
        cursor = await db.execute(
            "SELECT id FROM users WHERE username = ?", (user_data.username,)
        )
        if await cursor.fetchone():
            raise HTTPException(status_code=400, detail="用户名已存在")

        pwd_hash = hash_password(user_data.password)
        cursor = await db.execute(
            "INSERT INTO users (username, name, password_hash, role, class_name, major) VALUES (?, ?, ?, ?, ?, ?)",
            (user_data.username, user_data.name, pwd_hash, user_data.role,
             user_data.class_name, user_data.major)
        )
        await db.commit()
        user_id = cursor.lastrowid

        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = dict(await cursor.fetchone())

    return UserResponse(
        id=user["id"],
        username=user["username"],
        name=user["name"],
        role=user["role"],
        class_name=user.get("class_name"),
        major=user.get("major"),
        created_at=user.get("created_at", "")
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        name=current_user["name"],
        role=current_user["role"],
        class_name=current_user.get("class_name"),
        major=current_user.get("major"),
        created_at=current_user.get("created_at", "")
    )
