import json
import aiosqlite
from services.llm_service import llm_service

DB_PATH = "education.db"

class TeachingOptimizationAgent:

    async def analyze_and_suggest(self, course_id: int) -> dict:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row

            cursor = await db.execute("""
                SELECT c.*, u.name as teacher_name
                FROM courses c
                JOIN users u ON c.teacher_id = u.id
                WHERE c.id = ?
            """, (course_id,))
            course = await cursor.fetchone()
            course = dict(course) if course else {}

            cursor = await db.execute("""
                SELECT s.student_id, u.name as student_name, s.score, s.feedback
                FROM submissions s
                JOIN assignments a ON s.assignment_id = a.id
                JOIN users u ON s.student_id = u.id
                WHERE a.course_id = ?
            """, (course_id,))
            submissions = await cursor.fetchall()

            cursor = await db.execute("""
                SELECT er.*, u.name as student_name, er.weak_points
                FROM exam_results er
                JOIN exams e ON er.exam_id = e.id
                JOIN users u ON er.student_id = u.id
                WHERE e.course_id = ?
            """, (course_id,))
            exam_results = await cursor.fetchall()

            cursor = await db.execute("""
                SELECT status, COUNT(*) as count
                FROM attendance
                WHERE course_id = ?
                GROUP BY status
            """, (course_id,))
            attendance_stats = await cursor.fetchall()

            cursor = await db.execute("""
                SELECT * FROM resources WHERE course_id = ?
            """, (course_id,))
            resources = await cursor.fetchall()

            data = {
                "course": course,
                "submissions": [dict(s) for s in submissions],
                "exam_results": [dict(e) for e in exam_results],
                "attendance_stats": [dict(a) for a in attendance_stats],
                "resources": [dict(r) for r in resources]
            }

            suggestions = await llm_service.generate_teaching_suggestions(data)

            cursor = await db.execute("""
                INSERT INTO ai_analysis (student_id, course_id, analysis_type, content)
                VALUES (?, ?, ?, ?)
            """, (0, course_id, "teaching_suggestion", json.dumps(suggestions)))
            await db.commit()

            return suggestions

    async def get_suggestions(self, course_id: int) -> list:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT content FROM ai_analysis
                WHERE course_id = ? AND analysis_type = 'teaching_suggestion'
                ORDER BY created_at DESC LIMIT 1
            """, (course_id,))
            result = await cursor.fetchone()
            
            if result:
                return json.loads(result["content"])
            return []
