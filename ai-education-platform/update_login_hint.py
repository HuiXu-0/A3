with open('frontend/simple-login.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_text = '<p>演示账号: <span>student1</span> / <span>teacher1</span> / <span>counselor1</span> / <span>admin1</span></p>'
new_text = '<p>演示账号: <span>student1</span> / <span>student2</span> / <span>teacher1</span> / <span>counselor1</span> / <span>admin1</span> / <span>admin</span></p>'

content = content.replace(old_text, new_text)

with open('frontend/simple-login.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("登录界面演示账号已更新")
