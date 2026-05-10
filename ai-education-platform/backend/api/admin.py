from fastapi import APIRouter, HTTPException, Depends
import aiosqlite
import psutil
import os
from datetime import datetime
from utils.auth_utils import get_current_user

router = APIRouter()
DB_PATH = "education.db"

def require_admin(current_user: dict):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")

@router.get("/server-status")
async def get_server_status(current_user: dict = Depends(get_current_user)):
    require_admin(current_user)

    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count()
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": memory.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "percent": round(disk.percent, 1)
        },
        "uptime_hours": round((datetime.now().timestamp() - psutil.boot_time()) / 3600, 1),
        "status": "healthy" if cpu_percent < 80 and memory.percent < 85 else "warning"
    }

@router.get("/bug-reports")
async def get_bug_reports(current_user: dict = Depends(get_current_user)):
    require_admin(current_user)

    return [
        {
            "id": 1,
            "title": "签到页面偶尔显示空白",
            "severity": "medium",
            "status": "open",
            "reported_by": "教师反馈",
            "created_at": "2024-12-15 10:30:00",
            "description": "在高并发签到时，签到页面偶尔出现白屏，刷新后恢复"
        },
        {
            "id": 2,
            "title": "作业提交后状态未更新",
            "severity": "low",
            "status": "fixed",
            "reported_by": "学生反馈",
            "created_at": "2024-12-14 16:20:00",
            "description": "提交作业后列表状态未自动刷新，需手动刷新页面"
        },
        {
            "id": 3,
            "title": "成绩图表数据错位",
            "severity": "high",
            "status": "open",
            "reported_by": "系统监控",
            "created_at": "2024-12-16 09:15:00",
            "description": "当学生参加多次考试时，成绩趋势图X轴标签出现错位"
        }
    ]

@router.get("/system-stats")
async def get_system_stats(current_user: dict = Depends(get_current_user)):
    require_admin(current_user)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            "SELECT role, COUNT(*) as count FROM users GROUP BY role"
        )
        role_counts = {r["role"]: r["count"] for r in await cursor.fetchall()}

        cursor = await db.execute("SELECT COUNT(*) as count FROM courses")
        course_count = (await cursor.fetchone())["count"]

        cursor = await db.execute("SELECT COUNT(*) as count FROM assignments")
        assignment_count = (await cursor.fetchone())["count"]

        cursor = await db.execute("SELECT COUNT(*) as count FROM chat_messages")
        message_count = (await cursor.fetchone())["count"]

        today = datetime.now().strftime("%Y-%m-%d")
        cursor = await db.execute(
            "SELECT COUNT(DISTINCT sender_id) as count FROM chat_messages WHERE created_at LIKE ?",
            (f"{today}%",)
        )
        active_today = (await cursor.fetchone())["count"]

        return {
            "users": role_counts,
            "total_users": sum(role_counts.values()),
            "courses": course_count,
            "assignments": assignment_count,
            "messages": message_count,
            "active_today": active_today
        }

@router.get("/all-users")
async def get_all_users(
    role: str = None,
    current_user: dict = Depends(get_current_user)
):
    require_admin(current_user)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if role:
            cursor = await db.execute(
                "SELECT id, username, name, role, class_name, major, created_at FROM users WHERE role = ? ORDER BY id",
                (role,)
            )
        else:
            cursor = await db.execute(
                "SELECT id, username, name, role, class_name, major, created_at FROM users ORDER BY id"
            )
        users = await cursor.fetchall()
        return [dict(u) for u in users]

@router.post("/manage-user")
async def manage_user(
    action: dict,
    current_user: dict = Depends(get_current_user)
):
    require_admin(current_user)

    action_type = action.get("action")  
    user_data = action.get("user", {})

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        if action_type == "create":
            from utils.auth_utils import hash_password
            cursor = await db.execute(
                (
                    user_data["username"],
                    user_data["name"],
                    hash_password(user_data.get("password", "123456")),
                    user_data.get("role", "student"),
                    user_data.get("class_name"),
                    user_data.get("major"),
                    datetime.now().isoformat()
                )
            )
            await db.commit()
            return {"message": "用户创建成功", "user_id": cursor.lastrowid}

        elif action_type == "update":
            user_id = user_data.get("id")
            if not user_id:
                raise HTTPException(status_code=400, detail="缺少用户ID")

            fields = []
            values = []
            for field in ("name", "role", "class_name", "major"):
                if field in user_data:
                    fields.append(f"{field} = ?")
                    values.append(user_data[field])

            if not fields:
                raise HTTPException(status_code=400, detail="没有要更新的字段")

            values.append(user_id)
            await db.execute(
                f"UPDATE users SET {', '.join(fields)} WHERE id = ?",
                values
            )
            await db.commit()
            return {"message": "用户信息更新成功"}

        elif action_type == "disable":
            user_id = user_data.get("id")
            if not user_id:
                raise HTTPException(status_code=400, detail="缺少用户ID")
            
            await db.execute(
                "UPDATE users SET password_hash = 'DISABLED' WHERE id = ?",
                (user_id,)
            )
            await db.commit()
            return {"message": "用户已禁用"}

        else:
            raise HTTPException(status_code=400, detail="无效的操作类型")