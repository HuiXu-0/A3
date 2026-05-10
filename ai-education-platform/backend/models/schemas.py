from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    name: str
    role: str = "student"
    class_name: Optional[str] = None
    major: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    role: str
    class_name: Optional[str] = None
    major: Optional[str] = None
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class CourseResponse(BaseModel):
    id: int
    name: str
    teacher_id: int
    teacher_name: Optional[str] = None
    class_name: Optional[str] = None
    schedule: Optional[str] = None
    description: Optional[str] = None

class CoursewareResponse(BaseModel):
    id: int
    course_id: int
    title: str
    file_path: str
    upload_time: str

class AssignmentCreate(BaseModel):
    course_id: int
    title: str
    content: str
    deadline: str

class AssignmentResponse(BaseModel):
    id: int
    course_id: int
    title: str
    content: str
    deadline: str
    created_at: str

class SubmissionCreate(BaseModel):
    assignment_id: int
    content: str

class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    student_name: Optional[str] = None
    content: str
    score: Optional[float] = None
    feedback: Optional[str] = None
    submit_time: str
    graded: int = 0

class GradeSubmission(BaseModel):
    score: float
    feedback: str

class LeaveRequestCreate(BaseModel):
    type: str  
    reason: str

class LeaveRequestResponse(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    type: str
    reason: str
    status: str
    approver_id: Optional[int] = None
    created_at: str

class ExamCreate(BaseModel):
    course_id: int
    title: str
    total_score: float
    exam_time: str

class ExamResponse(BaseModel):
    id: int
    course_id: int
    title: str
    total_score: float
    exam_time: str

class ExamResultResponse(BaseModel):
    id: int
    exam_id: int
    student_id: int
    student_name: Optional[str] = None
    score: float
    weak_points: Optional[list] = None

class AttendanceRecord(BaseModel):
    student_id: int
    status: str  

class AttendanceResponse(BaseModel):
    id: int
    course_id: int
    student_id: int
    student_name: Optional[str] = None
    date: str
    status: str
    check_in_time: Optional[str] = None

class ChatMessage(BaseModel):
    receiver_id: Optional[int] = None
    group_id: Optional[int] = None
    content: str
    msg_type: str = "text"

class ChatMessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_name: Optional[str] = None
    receiver_id: Optional[int] = None
    group_id: Optional[int] = None
    content: str
    msg_type: str
    created_at: str

class ChatGroupCreate(BaseModel):
    name: str
    course_id: Optional[int] = None
    member_ids: List[int] = []

class ChatGroupResponse(BaseModel):
    id: int
    name: str
    course_id: Optional[int] = None
    members: Optional[list] = None

class AIAnalysisRequest(BaseModel):
    student_id: int
    course_id: int
    analysis_type: str  

class AIAnalysisResponse(BaseModel):
    student_id: int
    course_id: int
    analysis_type: str
    content: dict
    created_at: str

class ResourceRecommendation(BaseModel):
    student_id: int
    course_id: int
    weak_points: List[str]

class ResourceResponse(BaseModel):
    id: int
    title: str
    type: str
    url: Optional[str] = None
    course_id: int
    tags: Optional[list] = None
    difficulty: Optional[str] = None

class CoursewareUpload(BaseModel):
    course_id: int
    title: str
    file_path: str

class ManageUser(BaseModel):
    user_id: int
    action: str  
    value: Optional[str] = None

class LearningPlanRequest(BaseModel):
    student_id: int
    course_id: int

class TeachingSuggestionRequest(BaseModel):
    course_id: int

class StudyRecordResponse(BaseModel):
    id: int
    student_id: int
    resource_id: int
    resource_title: Optional[str] = None
    duration: int
    progress: float
    last_position: Optional[str] = None

class DormBillResponse(BaseModel):
    id: int
    dorm_id: str
    amount: float
    status: str
    due_date: str

class ScheduleItem(BaseModel):
    course_id: int
    course_name: str
    schedule: str
    teacher_name: str
    classroom: Optional[str] = None

class ClassAnalysisResponse(BaseModel):
    course_id: int
    course_name: str
    total_students: int
    avg_score: float
    attendance_rate: float
    submission_rate: float
    score_distribution: dict
    top_students: list
    struggling_students: list