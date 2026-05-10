from passlib.context import CryptContext
import sqlite3

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

conn = sqlite3.connect("education.db")
cursor = conn.cursor()
cursor.execute("SELECT username, password_hash FROM users WHERE username = ?", ("student1",))
user = cursor.fetchone()
conn.close()

print("用户名:", user[0])
print("密码哈希:", user[1])
print("验证密码 123456:", pwd_context.verify("123456", user[1]))
