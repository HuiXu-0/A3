import json
import aiosqlite
from services.llm_service import llm_service

DB_PATH = "education.db"

class ResourceGenerationAgent:

    async def generate_resources(self, student_id: int, course_id: int, weak_points: list) -> dict:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row

            cursor = await db.execute("SELECT * FROM users WHERE id = ?", (student_id,))
            student = await cursor.fetchone()
            student = dict(student) if student else {}

            cursor = await db.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
            course = await cursor.fetchone()
            course = dict(course) if course else {}

            cursor = await db.execute("""
                SELECT * FROM resources WHERE course_id = ?
            """, (course_id,))
            existing_resources = await cursor.fetchall()

            resources = await llm_service.generate_resources(course.get("name", ""), weak_points)

            cursor = await db.execute("""
                INSERT INTO ai_analysis (student_id, course_id, analysis_type, content)
                VALUES (?, ?, ?, ?)
            """, (student_id, course_id, "resource_recommendation", json.dumps(resources)))
            await db.commit()

            return resources

    async def get_recommended_resources(self, student_id: int, course_id: int) -> list:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT content FROM ai_analysis
                WHERE student_id = ? AND course_id = ? AND analysis_type = 'resource_recommendation'
                ORDER BY created_at DESC LIMIT 1
            """, (student_id, course_id))
            result = await cursor.fetchone()
            
            if result:
                return json.loads(result["content"])
            return []
