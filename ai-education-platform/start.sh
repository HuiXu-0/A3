#!/bin/bash

set -e

echo "=========================================="
echo "  AI个性化教育平台 - 启动脚本"
echo "  第15届中国软件杯 A3命题"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python 版本: $PYTHON_VERSION"

# Install dependencies
echo "📦 安装依赖..."
pip install -r backend/requirements.txt -q 2>/dev/null || \
pip3 install -r backend/requirements.txt -q 2>/dev/null || {
    echo "⚠️ 使用国内镜像安装..."
    pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q
}
echo "✅ 依赖安装完成"

# Start server
echo ""
echo "🚀 启动服务器..."
echo "📍 访问地址: http://localhost:8000"
echo "🔑 演示账号: student1/123456, teacher1/123456"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=========================================="
echo ""

cd "$(dirname "$0")"
python3 backend/main.py
