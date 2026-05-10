import json
import aiosqlite
from services.llm_service import llm_service

DB_PATH = "education.db"

class ExamAnalysisAgent:

    async def analyze_exam(self, exam_id: int) -> dict:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row

            cursor = await db.execute("""
                SELECT e.*, c.name as course_name
                FROM exams e
                JOIN courses c ON e.course_id = c.id
                WHERE e.id = ?
            """, (exam_id,))
            exam = await cursor.fetchone()
            exam = dict(exam) if exam else {}

            cursor = await db.execute("""
                SELECT er.*, u.name as student_name, u.class_name
                FROM exam_results er
                JOIN users u ON er.student_id = u.id
                WHERE er.exam_id = ?
            """, (exam_id,))
            results = await cursor.fetchall()

            data = {
                "exam": exam,
                "results": [dict(r) for r in results]
            }

            analysis = await llm_service.analyze_exam_results(data)

            cursor = await db.execute("""
                INSERT INTO ai_analysis (student_id, course_id, analysis_type, content)
                VALUES (?, ?, ?, ?)
            """, (0, exam.get("course_id", 0), "exam_analysis", json.dumps(analysis)))
            await db.commit()

            return analysis

    async def get_exam_analysis(self, exam_id: int) -> list:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT content FROM ai_analysis
                WHERE course_id = ? AND analysis_type = 'exam_analysis'
                ORDER BY created_at DESC LIMIT 1
            """, (exam_id,))
            result = await cursor.fetchone()
            
            if result:
                return json.loads(result["content"])
            return []
