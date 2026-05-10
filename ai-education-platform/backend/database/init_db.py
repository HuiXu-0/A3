import sqlite3
import json
from datetime import datetime, timedelta
from utils.auth_utils import hash_password
from config import DB_PATH

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student','teacher','counselor','admin')),
            class_name TEXT,
            major TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            class_name TEXT,
            schedule TEXT,
            description TEXT,
            credits INTEGER DEFAULT 3,
            FOREIGN KEY (teacher_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS courseware (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            file_path TEXT NOT NULL,
            upload_time TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );

        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            max_score INTEGER DEFAULT 100,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );

        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            content TEXT,
            score REAL,
            feedback TEXT,
            submitted_at TEXT DEFAULT (datetime('now','localtime')),
            graded INTEGER DEFAULT 0,
            FOREIGN KEY (assignment_id) REFERENCES assignments(id),
            FOREIGN KEY (student_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            max_score INTEGER DEFAULT 100,
            exam_time TEXT,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );

        CREATE TABLE IF NOT EXISTS exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            score REAL,
            weak_points TEXT,
            FOREIGN KEY (exam_id) REFERENCES exams(id),
            FOREIGN KEY (student_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('present','absent','late')),
            check_in_time TEXT,
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (student_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (student_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER,
            group_id INTEGER,
            content TEXT NOT NULL,
            msg_type TEXT DEFAULT 'text',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (sender_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS chat_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            course_id INTEGER,
            members TEXT,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );

        CREATE TABLE IF NOT EXISTS learning_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            weak_points TEXT,
            strong_points TEXT,
            learning_style TEXT,
            updated_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );

        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT,
            url TEXT,
            course_id INTEGER,
            description TEXT,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );

        CREATE TABLE IF NOT EXISTS study_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            resource_id INTEGER NOT NULL,
            duration INTEGER DEFAULT 0,
            progress REAL DEFAULT 0,
            last_position TEXT,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (resource_id) REFERENCES resources(id)
        );

        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (author_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS ai_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            analysis_type TEXT NOT NULL,
            content TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );

        CREATE TABLE IF NOT EXISTS dorm_bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'unpaid' CHECK(status IN ('paid','unpaid')),
            FOREIGN KEY (student_id) REFERENCES users(id)
        );
    """)

    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (username, name, password_hash, role)
            VALUES ('admin', '管理员', ?, 'admin')
        """, (hash_password('admin123'),))

    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'teacher1'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (username, name, password_hash, role, class_name)
            VALUES ('teacher1', '张老师', ?, 'teacher', '高三1班')
        """, (hash_password('teacher123'),))

    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'student1'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (username, name, password_hash, role, class_name, major)
            VALUES ('student1', '李明', ?, 'student', '高三1班', '理科')
        """, (hash_password('student123'),))

    conn.commit()
    conn.close()
    print("数据库初始化完成")

if __name__ == "__main__":
    init_database()
