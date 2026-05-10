import requests

# 测试登录接口
response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={'username': 'student1', 'password': '123456'}
)

print("状态码:", response.status_code)
print("响应内容:", response.json())
