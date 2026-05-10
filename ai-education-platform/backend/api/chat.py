from fastapi import APIRouter, HTTPException, Depends
import aiosqlite
import json
from datetime import datetime
from utils.auth_utils import get_current_user

router = APIRouter()
DB_PATH = "education.db"

@router.post("/send-message")
async def send_message(
    message: dict,
    current_user: dict = Depends(get_current_user)
):
    content = message.get("content", "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="消息内容不能为空")

    receiver_id = message.get("receiver_id")
    group_id = message.get("group_id")
    msg_type = message.get("msg_type", "text")

    if not receiver_id and not group_id:
        raise HTTPException(status_code=400, detail="请指定接收者或群组")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            (
                current_user["id"],
                receiver_id,
                group_id,
                content,
                msg_type,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        await db.commit()
        return {"message": "发送成功", "id": cursor.lastrowid}

@router.get("/messages/{user_id}")
async def get_messages(user_id: int, current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            (current_user["id"], user_id, user_id, current_user["id"])
        )
        messages = await cursor.fetchall()
        return [dict(m) for m in messages]

@router.get("/groups")
async def get_groups(current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            (f'%"{current_user["id"]}%"',)
        )
        groups = await cursor.fetchall()
        result = []
        for g in groups:
            g = dict(g)
            g["members"] = json.loads(g["members"]) if g["members"] else []
            result.append(g)
        return result

@router.post("/create-group")
async def create_group(
    group_data: dict,
    current_user: dict = Depends(get_current_user)
):
    name = group_data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="群组名称不能为空")

    course_id = group_data.get("course_id")
    members = group_data.get("members", [])
    if current_user["id"] not in members:
        members.append(current_user["id"])

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            (name, course_id, json.dumps(members))
        )
        await db.commit()
        return {"message": "群组创建成功", "group_id": cursor.lastrowid}

@router.get("/group-messages/{group_id}")
async def get_group_messages(group_id: int, current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("SELECT members FROM chat_groups WHERE id = ?", (group_id,))
        group = await cursor.fetchone()
        if not group:
            raise HTTPException(status_code=404, detail="群组不存在")

        members = json.loads(group["members"]) if group["members"] else []
        if current_user["id"] not in members:
            raise HTTPException(status_code=403, detail="您不在此群组中")

        cursor = await db.execute(
            (group_id,)
        )
        messages = await cursor.fetchall()
        return [dict(m) for m in messages]

@router.get("/contacts")
async def get_contacts(current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            "SELECT id, name, role, class_name FROM users WHERE id != ? ORDER BY name",
            (current_user["id"],)
        )
        contacts = await cursor.fetchall()
        return [dict(c) for c in contacts]