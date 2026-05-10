from fastapi import APIRouter, HTTPException, Depends
import aiosqlite
import json
from datetime import datetime
from utils.auth_utils import get_current_user
from agents.student_agent import StudentAnalysisAgent
from agents.resource_agent import ResourceGenerationAgent
from agents.teaching_agent import TeachingOptimizationAgent
from agents.exam_agent import ExamAnalysisAgent

router = APIRouter()
DB_PATH = "education.db"

student_agent = StudentAnalysisAgent()
resource_agent = ResourceGenerationAgent()
teaching_agent = TeachingOptimizationAgent()
exam_agent = ExamAnalysisAgent()

@router.post("/analyze-student")
async def analyze_student(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    student_id = request.get("student_id", current_user["id"])
    course_id = request.get("course_id", 1)

    if current_user["role"] == "student" and current_user["id"] != student_id:
        raise HTTPException(status_code=403, detail="只能分析自己的学情")

    result = await student_agent.analyze_student(student_id, course_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/generate-resources")
async def generate_resources(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    student_id = request.get("student_id", current_user["id"])
    course_id = request.get("course_id", 1)
    weak_points = request.get("weak_points", [])

    result = await resource_agent.generate_resources(student_id, course_id, weak_points)
    return result

@router.post("/exam-analysis-ai")
async def exam_analysis_ai(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    exam_id = request.get("exam_id")

    if current_user["role"] not in ("teacher", "counselor", "admin"):
        raise HTTPException(status_code=403, detail="权限不足")

    result = await exam_agent.analyze_exam(exam_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/learning-plan")
async def generate_learning_plan(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    student_id = request.get("student_id", current_user["id"])
    course_id = request.get("course_id", 1)

    result = await resource_agent.generate_resources(student_id, course_id, [])
    
    return {
        "student_id": student_id,
        "course_id": course_id,
        "weekly_plan": [
            {"day": "周一", "tasks": ["复习课堂笔记", "完成专项练习题3道", "观看推荐视频"]},
            {"day": "周二", "tasks": ["预习新课内容", "练习链表相关题目", "整理错题本"]},
            {"day": "周三", "tasks": ["课堂知识点回顾", "综合练习", "小组讨论"]},
            {"day": "周四", "tasks": ["算法练习", "代码实现", "阅读参考资料"]},
            {"day": "周五", "tasks": ["本周总结", "薄弱点强化", "完成作业"]},
            {"day": "周末", "tasks": ["复习全周内容", "完成拓展练习", "准备下周预习"]}
        ],
        "ai_suggestions": result.get("ai_analysis", {})
    }

@router.post("/teaching-suggestions")
async def get_teaching_suggestions(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    course_id = request.get("course_id")

    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="权限不足")

    result = await teaching_agent.analyze_and_suggest(course_id)
    return result