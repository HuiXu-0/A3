# 部署指南

## 1. 环境要求

- Python 3.9+
- pip
- (可选) Docker & Docker Compose
- (可选) Nginx（生产环境反向代理）

## 2. 快速部署

### 2.1 直接运行

```bash
# 克隆项目
git clone <repo-url>
cd ai-education-platform

# 安装依赖
pip install -r backend/requirements.txt

# 启动服务
python backend/main.py
```

服务将在 http://0.0.0.0:8000 启动。

### 2.2 使用启动脚本

```bash
chmod +x start.sh
./start.sh
```

脚本会自动检查环境、安装依赖、初始化数据库并启动服务。

## 3. Docker 部署

### 3.1 单容器部署

```bash
# 构建镜像
docker build -t ai-edu-platform .

# 运行容器
docker run -d -p 8000:8000 --name edu-platform ai-edu-platform
```

### 3.2 Docker Compose 部署

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

## 4. 生产环境部署

### 4.1 Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/ai-education-platform/frontend/;
        expires 1d;
    }
}
```

### 4.2 Systemd 服务配置

```ini
[Unit]
Description=AI Education Platform
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/ai-education-platform
ExecStart=/usr/bin/python3 backend/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 5. 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| HOST | 0.0.0.0 | 监听地址 |
| PORT | 8000 | 监听端口 |
| DB_PATH | database.db | 数据库文件路径 |
| JWT_SECRET | (随机生成) | JWT签名密钥 |
| LLM_MODE | mock | LLM模式(mock/api/local) |
| LLM_API_KEY | - | LLM API密钥 |
| LLM_API_URL | - | LLM API地址 |

## 6. 数据库备份

```bash
# 备份
cp database.db database_backup_$(date +%Y%m%d).db

# 恢复
cp database_backup_20240101.db database.db
```

## 7. 故障排查

### 问题：端口被占用
```bash
# 查找占用端口的进程
lsof -i :8000
# 或
netstat -tlnp | grep 8000

# 终止进程
kill -9 <PID>
```

### 问题：数据库锁定
```bash
# 检查是否有多个进程访问数据库
fuser database.db
# 终止多余进程
```

### 问题：依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 8. 性能调优

- 使用 Uvicorn 多 worker：`uvicorn main:app --workers 4`
- 启用 Gzip 压缩
- 配置 CDN 加速静态资源
- 数据库迁移到 PostgreSQL（大规模部署）
