from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

from api.auth import router as auth_router
from api.student import router as student_router
from api.teacher import router as teacher_router
from api.counselor import router as counselor_router
from api.admin import router as admin_router
from api.chat import router as chat_router
from api.agents import router as agents_router
from database.init_db import init_database

app = FastAPI(title="AI个性化教育平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(student_router, prefix="/api/student", tags=["学生"])
app.include_router(teacher_router, prefix="/api/teacher", tags=["教师"])
app.include_router(counselor_router, prefix="/api/counselor", tags=["辅导员"])
app.include_router(admin_router, prefix="/api/admin", tags=["管理员"])
app.include_router(chat_router, prefix="/api/chat", tags=["聊天"])
app.include_router(agents_router, prefix="/api/agents", tags=["智能体"])

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.on_event("startup")
async def startup():
    init_database()

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_dir, "simple-login.html"))

@app.get("/test-login.html")
async def test_login():
    return FileResponse(os.path.join(frontend_dir, "test-login.html"))

@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI教育平台"}

@app.get("/{path:path}")
async def catch_all(path: str):
    
    if path.startswith("api/"):
        return {"detail": "Not Found"}, 404
    
    return FileResponse(os.path.join(frontend_dir, "index.html"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)