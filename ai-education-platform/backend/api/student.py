from fastapi import APIRouter, HTTPException, Depends
import aiosqlite
import json
from models.schemas import (
    SubmissionCreate, LeaveRequestCreate, CourseResponse,
    AssignmentResponse, SubmissionResponse, ExamResponse,
    ExamResultResponse, ResourceResponse, LeaveRequestResponse,
    StudyRecordResponse, DormBillResponse, ScheduleItem, AttendanceResponse
)
from utils.auth_utils import get_current_user

router = APIRouter()
DB_PATH = "education.db"

@router.get("/courses")
async def get_student_courses(current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT c.*, u.name as teacher_name
            FROM courses c
            JOIN users u ON c.teacher_id = u.id
            WHERE c.class_name = ?
        """, (current_user["class_name"],))
        courses = await cursor.fetchall()
        
        result = []
        for course in courses:
            course_dict = dict(course)
            course_dict["schedule"] = json.loads(course_dict["schedule"])
            
            # Get assignments for this course
            cursor2 = await db.execute("""
                SELECT a.*, 
                       (SELECT score FROM submissions 
                        WHERE assignment_id = a.id AND student_id = ?) as my_score,
                       (SELECT graded FROM submissions 
                        WHERE assignment_id = a.id AND student_id = ?) as my_graded
                FROM assignments a
                WHERE a.course_id = ?
                ORDER BY a.created_at DESC
            """, (current_user["id"], current_user["id"], course["id"]))
            assignments = await cursor2.fetchall()
            course_dict["assignments"] = [dict(a) for a in assignments]
            
            # Get exams for this course
            cursor3 = await db.execute("""
                SELECT e.*,
                       (SELECT score FROM exam_results WHERE exam_id = e.id AND student_id = ?) as my_score
                FROM exams e
                WHERE e.course_id = ?
                ORDER BY e.exam_time DESC
            """, (current_user["id"], course["id"]))
            exams = await cursor3.fetchall()
            course_dict["exams"] = [dict(e) for e in exams]
            
            result.append(course_dict)
        
        return result

@router.get("/exam_results")
async def get_exam_results(current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT er.*, e.title as exam_name, c.name as course_name
            FROM exam_results er
            JOIN exams e ON er.exam_id = e.id
            JOIN courses c ON e.course_id = c.id
            WHERE er.student_id = ?
            ORDER BY er.id DESC
        """, (current_user["id"],))
        results = await cursor.fetchall()
        
        return [dict(r) for r in results]

@router.get("/weak_points/{course_id}")
async def get_weak_points(course_id: int, current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT weak_points FROM learning_profiles
            WHERE student_id = ? AND course_id = ?
        """, (current_user["id"], course_id))
        result = await cursor.fetchone()
        
        if result:
            return {"weak_points": json.loads(result["weak_points"])}
        return {"weak_points": []}

@router.get("/resources/{course_id}")
async def get_course_resources(course_id: int, current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT * FROM resources WHERE course_id = ?
        """, (course_id,))
        resources = await cursor.fetchall()
        
        return [dict(r) for r in resources]

@router.get("/schedule")
async def get_student_schedule(current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT c.id as course_id, c.name as course_name, c.schedule,
                   u.name as teacher_name, c.class_name
            FROM courses c
            JOIN users u ON c.teacher_id = u.id
            WHERE c.class_name = ?
        """, (current_user["class_name"],))
        courses = await cursor.fetchall()
        
        schedule = {}
        for course in courses:
            course_schedule = json.loads(course["schedule"])
            for day, slots in course_schedule.items():
                if day not in schedule:
                    schedule[day] = []
                for slot in slots:
                    schedule[day].append({
                        "course_id": course["id"],
                        "course_name": course["name"],
                        "teacher_name": course["teacher_name"],
                        "time": slot
                    })
        
        return schedule

@router.get("/learning_profile/{course_id}")
async def get_learning_profile(course_id: int, current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT * FROM learning_profiles
            WHERE student_id = ? AND course_id = ?
        """, (current_user["id"], course_id))
        result = await cursor.fetchone()
        
        if result:
            profile = dict(result)
            profile["weak_points"] = json.loads(profile["weak_points"])
            profile["learning_style"] = json.loads(profile["learning_style"])
            return profile
        return None

@router.get("/study_records")
async def get_study_records(current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT sr.*, r.title as resource_title, r.type as resource_type
            FROM study_records sr
            JOIN resources r ON sr.resource_id = r.id
            WHERE sr.student_id = ?
            ORDER BY sr.id DESC
        """, (current_user["id"],))
        records = await cursor.fetchall()
        
        return [dict(r) for r in records]

@router.post("/submit_assignment")
async def submit_assignment(submission: SubmissionCreate, current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO submissions (assignment_id, student_id, content, submitted_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (submission.assignment_id, current_user["id"], submission.content))
        await db.commit()
        
        return {"message": "提交成功", "id": cursor.lastrowid}

@router.get("/submissions")
async def get_submissions(current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT s.*, a.title as assignment_title, c.name as course_name
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.id
            JOIN courses c ON a.course_id = c.id
            WHERE s.student_id = ?
            ORDER BY s.submitted_at DESC
        """, (current_user["id"],))
        submissions = await cursor.fetchall()
        
        return [dict(s) for s in submissions]

@router.post("/leave_request")
async def create_leave_request(request: LeaveRequestCreate, current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO leave_requests (student_id, start_date, end_date, reason, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (current_user["id"], request.start_date, request.end_date, request.reason))
        await db.commit()
        
        return {"message": "请假申请已提交", "id": cursor.lastrowid}

@router.get("/leave_requests")
async def get_leave_requests(current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT * FROM leave_requests
            WHERE student_id = ?
            ORDER BY created_at DESC
        """, (current_user["id"],))
        requests = await cursor.fetchall()
        
        return [dict(r) for r in requests]

@router.get("/attendance")
async def get_attendance(current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT * FROM attendance
            WHERE student_id = ?
            ORDER BY date DESC
        """, (current_user["id"],))
        records = await cursor.fetchall()
        
        return [dict(r) for r in records]

@router.get("/dorm_bill")
async def get_dorm_bill(current_user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT * FROM dorm_bills
            WHERE student_id = ?
            ORDER BY month DESC
        """, (current_user["id"],))
        bills = await cursor.fetchall()
        
        return [dict(b) for b in bills]
