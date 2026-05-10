from fastapi import APIRouter, HTTPException, Depends
import aiosqlite
import json
from datetime import datetime
from models.schemas import LeaveRequestCreate
from utils.auth_utils import get_current_user

router = APIRouter()
DB_PATH = "education.db"

@router.get("/leave-requests")
async def get_leave_requests(status: str = None, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("counselor", "admin"):
        raise HTTPException(status_code=403, detail="权限不足")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if status:
            cursor = await db.execute(
                (status,)
            )
        else:
            cursor = await db.execute(
            )
        requests = await cursor.fetchall()
        return [dict(r) for r in requests]

@router.post("/approve-leave/{request_id}")
async def approve_leave(
    request_id: int,
    action: dict,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ("counselor", "admin"):
        raise HTTPException(status_code=403, detail="权限不足")

    new_status = action.get("status", "approved")  

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM leave_requests WHERE id = ?", (request_id,)
        )
        req = await cursor.fetchone()
        if not req:
            raise HTTPException(status_code=404, detail="请假申请不存在")

        await db.execute(
            "UPDATE leave_requests SET status = ?, approver_id = ? WHERE id = ?",
            (new_status, current_user["id"], request_id)
        )
        await db.commit()

        return {"message": f"请假申请已{'批准' if new_status == 'approved' else '拒绝'}"}

@router.get("/student-grades/{class_name}")
async def get_student_grades(class_name: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("counselor", "admin", "teacher"):
        raise HTTPException(status_code=403, detail="权限不足")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            (class_name,)
        )
        results = await cursor.fetchall()

        students = {}
        for r in results:
            r = dict(r)
            sid = r["id"]
            if sid not in students:
                students[sid] = {
                    "id": r["id"],
                    "name": r["name"],
                    "username": r["username"],
                    "class_name": r["class_name"],
                    "major": r["major"],
                    "exams": [],
                    "average_score": 0
                }
            if r["score"] is not None:
                students[sid]["exams"].append({
                    "exam_title": r["exam_title"],
                    "course_name": r["course_name"],
                    "score": r["score"],
                    "weak_points": json.loads(r["weak_points"]) if r["weak_points"] else []
                })

        for sid in students:
            exams = students[sid]["exams"]
            if exams:
                students[sid]["average_score"] = round(
                    sum(e["score"] for e in exams) / len(exams), 1
                )

        return list(students.values())

@router.get("/student-alerts/{class_name}")
async def get_student_alerts(class_name: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("counselor", "admin", "teacher"):
        raise HTTPException(status_code=403, detail="权限不足")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            (class_name,)
        )
        low_score = await cursor.fetchall()

        cursor = await db.execute(
            (class_name,)
        )
        high_absence = await cursor.fetchall()

        alerts = []
        for s in low_score:
            s = dict(s)
            alerts.append({
                "student_id": s["id"],
                "student_name": s["name"],
                "alert_type": "low_score",
                "message": f"平均分 {s['avg_score']:.1f}，低于60分警戒线",
                "severity": "high" if s["avg_score"] < 50 else "medium"
            })
        for s in high_absence:
            s = dict(s)
            rate = s["absences"] / max(s["total_classes"], 1) * 100
            alerts.append({
                "student_id": s["id"],
                "student_name": s["name"],
                "alert_type": "high_absence",
                "message": f"缺勤率 {rate:.0f}%（{s['absences']}/{s['total_classes']}）",
                "severity": "high" if rate > 30 else "medium"
            })

        return alerts

@router.get("/class-overview/{class_name}")
async def get_class_overview(class_name: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("counselor", "admin"):
        raise HTTPException(status_code=403, detail="权限不足")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM users WHERE class_name = ? AND role = 'student'",
            (class_name,)
        )
        student_count = (await cursor.fetchone())["count"]

        cursor = await db.execute(
            (class_name,)
        )
        pending_leaves = (await cursor.fetchone())["count"]

        cursor = await db.execute(
            (class_name,)
        )
        announcements = [dict(r) for r in await cursor.fetchall()]

        cursor = await db.execute(
            (class_name,)
        )
        grade_dist = [dict(r) for r in await cursor.fetchall()]

        return {
            "class_name": class_name,
            "student_count": student_count,
            "pending_leaves": pending_leaves,
            "announcements": announcements,
            "grade_distribution": grade_dist
        }