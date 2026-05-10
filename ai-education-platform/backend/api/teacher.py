from fastapi import APIRouter, HTTPException, Depends
import aiosqlite
import json
from models.schemas import (
    CoursewareUpload, AssignmentCreate, ExamCreate,
    GradeSubmission, AttendanceRecord
)
from utils.auth_utils import get_current_user

router = APIRouter()
DB_PATH = "education.db"

@router.get("/courses")
async def get_teacher_courses(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT c.*, 
                   (SELECT COUNT(*) FROM users WHERE class_name = c.class_name AND role = 'student') as student_count
            FROM courses c
            WHERE c.teacher_id = ?
        """, (current_user["id"],))
        courses = await cursor.fetchall()
        
        result = []
        for course in courses:
            course_dict = dict(course)
            course_dict["schedule"] = json.loads(course_dict["schedule"])
            result.append(course_dict)
        
        return result

@router.get("/submissions/{assignment_id}")
async def get_submissions(assignment_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT s.*, u.name as student_name, u.class_name
            FROM submissions s
            JOIN users u ON s.student_id = u.id
            WHERE s.assignment_id = ?
            ORDER BY s.submitted_at DESC
        """, (assignment_id,))
        submissions = await cursor.fetchall()
        
        return [dict(s) for s in submissions]

@router.get("/attendance/{course_id}/{date}")
async def get_attendance_by_date(course_id: int, date: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT a.*, u.name as student_name
            FROM attendance a
            JOIN users u ON a.student_id = u.id
            WHERE a.course_id = ? AND a.date = ?
            ORDER BY u.name
        """, (course_id, date))
        records = await cursor.fetchall()
        
        return [dict(r) for r in records]

@router.get("/attendance/{course_id}")
async def get_attendance(course_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT a.*, u.name as student_name
            FROM attendance a
            JOIN users u ON a.student_id = u.id
            WHERE a.course_id = ?
            ORDER BY a.date DESC, u.name
        """, (course_id,))
        records = await cursor.fetchall()
        
        return [dict(r) for r in records]

@router.post("/attendance")
async def record_attendance(record: AttendanceRecord, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO attendance (course_id, student_id, date, status, check_in_time)
            VALUES (?, ?, ?, ?, ?)
        """, (record.course_id, record.student_id, record.date, record.status, record.check_in_time))
        await db.commit()
        
        return {"message": "考勤记录成功", "id": cursor.lastrowid}

@router.get("/students/{class_name}")
async def get_students(class_name: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT id, name FROM users WHERE class_name = ? AND role = 'student'
        """, (class_name,))
        students = await cursor.fetchall()
        
        return [dict(s) for s in students]

@router.get("/student_scores/{course_id}")
async def get_student_scores(course_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT s.student_id, u.name, AVG(s.score) as avg_score
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.id
            JOIN users u ON s.student_id = u.id
            WHERE a.course_id = ?
            GROUP BY s.student_id
        """, (course_id,))
        submission_scores = await cursor.fetchall()
        
        cursor2 = await db.execute("""
            SELECT er.student_id, u.name, AVG(er.score) as avg_score
            FROM exam_results er
            JOIN exams e ON er.exam_id = e.id
            JOIN users u ON er.student_id = u.id
            WHERE e.course_id = ?
            GROUP BY er.student_id
        """, (course_id,))
        exam_scores = await cursor2.fetchall()
        
        cursor3 = await db.execute("""
            SELECT student_id,
                   COUNT(*) as total,
                   SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present
            FROM attendance
            WHERE course_id = ?
            GROUP BY student_id
        """, (course_id,))
        attendance = await cursor3.fetchall()
        
        return {
            "submission_scores": [dict(s) for s in submission_scores],
            "exam_scores": [dict(e) for e in exam_scores],
            "attendance": [dict(a) for a in attendance]
        }

@router.get("/exam/{exam_id}")
async def get_exam(exam_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("""
            SELECT e.*, c.name as course_name
            FROM exams e
            JOIN courses c ON e.course_id = c.id
            WHERE e.id = ?
        """, (exam_id,))
        exam = await cursor.fetchone()
        
        cursor2 = await db.execute("""
            SELECT er.*, u.name as student_name
            FROM exam_results er
            JOIN users u ON er.student_id = u.id
            WHERE er.exam_id = ?
        """, (exam_id,))
        results = await cursor2.fetchall()
        
        if exam:
            exam_dict = dict(exam)
            exam_dict["results"] = [dict(r) for r in results]
            return exam_dict
        return None

@router.post("/course")
async def create_course(course: dict, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO courses (name, description, teacher_id, class_name, schedule, credits)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (course["name"], course["description"], current_user["id"], 
              course["class_name"], json.dumps(course["schedule"]), course["credits"]))
        await db.commit()
        
        return {"message": "课程创建成功", "id": cursor.lastrowid}

@router.post("/assignment")
async def create_assignment(assignment: AssignmentCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO assignments (course_id, title, description, due_date, max_score)
            VALUES (?, ?, ?, ?, ?)
        """, (assignment.course_id, assignment.title, assignment.description, 
              assignment.due_date, assignment.max_score))
        await db.commit()
        
        return {"message": "作业创建成功", "id": cursor.lastrowid}

@router.post("/exam")
async def create_exam(exam: ExamCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO exams (course_id, title, description, exam_time, max_score)
            VALUES (?, ?, ?, ?, ?)
        """, (exam.course_id, exam.title, exam.description, exam.exam_time, exam.max_score))
        await db.commit()
        
        return {"message": "考试创建成功", "id": cursor.lastrowid}

@router.post("/grade")
async def grade_submission(grade: GradeSubmission, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            UPDATE submissions SET score = ?, graded = 1, feedback = ?
            WHERE id = ?
        """, (grade.score, grade.feedback, grade.submission_id))
        await db.commit()
        
        if cursor.rowcount > 0:
            return {"message": "评分成功"}
        raise HTTPException(status_code=404, detail="提交记录不存在")

@router.post("/upload_courseware")
async def upload_courseware(courseware: CoursewareUpload, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO resources (course_id, title, type, url, description)
            VALUES (?, ?, ?, ?, ?)
        """, (courseware.course_id, courseware.title, courseware.type, 
              courseware.url, courseware.description))
        await db.commit()
        
        return {"message": "课件上传成功", "id": cursor.lastrowid}

@router.get("/courseware/{course_id}")
async def get_courseware(course_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM resources WHERE course_id = ?
        """, (course_id,))
        resources = await cursor.fetchall()
        
        return [dict(r) for r in resources]

@router.get("/leave_requests")
async def get_leave_requests(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT lr.*, u.name as student_name, u.class_name
            FROM leave_requests lr
            JOIN users u ON lr.student_id = u.id
            WHERE lr.status = 'pending'
            ORDER BY lr.created_at DESC
        """)
        requests = await cursor.fetchall()
        
        return [dict(r) for r in requests]

@router.post("/leave_request/{request_id}/approve")
async def approve_leave(request_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            UPDATE leave_requests SET status = 'approved' WHERE id = ?
        """, (request_id,))
        await db.commit()
        
        if cursor.rowcount > 0:
            return {"message": "请假已批准"}
        raise HTTPException(status_code=404, detail="请假申请不存在")

@router.post("/leave_request/{request_id}/reject")
async def reject_leave(request_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="无权限")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            UPDATE leave_requests SET status = 'rejected' WHERE id = ?
        """, (request_id,))
        await db.commit()
        
        if cursor.rowcount > 0:
            return {"message": "请假已拒绝"}
        raise HTTPException(status_code=404, detail="请假申请不存在")
