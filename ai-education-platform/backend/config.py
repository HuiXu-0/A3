import os

# 获取项目根目录（backend 的上级目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据库路径
DB_PATH = os.path.join(BASE_DIR, "education.db")

# JWT 配置
SECRET_KEY = "ai-education-platform-secret-key-2024-very-secure"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
