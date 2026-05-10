import json
import aiosqlite
from services.llm_service import llm_service

DB_PATH = "education.db"

class StudentAnalysisAgent:

    async def analyze_student(self, student_id: int, course_id: int) -> dict:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row

            cursor = await db.execute("SELECT * FROM users WHERE id = ?", (student_id,))
            student = await cursor.fetchone()
            if not student:
                return {"error": "学生不存在"}

            student = dict(student)

            cursor = await db.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
            course = await cursor.fetchone()
            course = dict(course) if course else {}

            cursor = await db.execute("""
                SELECT er.*, e.title as exam_title
                FROM exam_results er
                JOIN exams e ON er.exam_id = e.id
                WHERE er.student_id = ? AND e.course_id = ?
                ORDER BY er.id DESC
            """, (student_id, course_id))
            exam_results = await cursor.fetchall()

            cursor = await db.execute("""
                SELECT s.*, a.title as assignment_title
                FROM submissions s
                JOIN assignments a ON s.assignment_id = a.id
                WHERE s.student_id = ? AND a.course_id = ?
                ORDER BY s.id DESC
            """, (student_id, course_id))
            submissions = await cursor.fetchall()

            cursor = await db.execute("""
                SELECT * FROM attendance
                WHERE student_id = ? AND course_id = ?
                ORDER BY date DESC LIMIT 20
            """, (student_id, course_id))
            attendance = await cursor.fetchall()

            cursor = await db.execute("""
                SELECT * FROM learning_profiles
                WHERE student_id = ? AND course_id = ?
            """, (student_id, course_id))
            profile = await cursor.fetchone()
            profile = dict(profile) if profile else {}

            cursor = await db.execute("""
                SELECT sr.*, r.title as resource_title
                FROM study_records sr
                JOIN resources r ON sr.resource_id = r.id
                WHERE sr.student_id = ? AND r.course_id = ?
            """, (student_id, course_id))
            study_records = await cursor.fetchall()

            data = {
                "student": student,
                "course": course,
                "exam_results": [dict(r) for r in exam_results],
                "submissions": [dict(s) for s in submissions],
                "attendance": [dict(a) for a in attendance],
                "learning_profile": profile,
                "study_records": [dict(sr) for sr in study_records]
            }

            analysis = await llm_service.analyze_student_data(data)

            cursor = await db.execute("""
                INSERT INTO ai_analysis (student_id, course_id, analysis_type, content)
                VALUES (?, ?, ?, ?)
            """, (student_id, course_id, "comprehensive", json.dumps(analysis)))
            await db.commit()

            return analysis

    async def get_analysis_history(self, student_id: int, course_id: int) -> list:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM ai_analysis
                WHERE student_id = ? AND course_id = ?
                ORDER BY created_at DESC
            """, (student_id, course_id))
            results = await cursor.fetchall()
            
            return [dict(r) for r in results]
