FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1-mesa-glx libglib2.0-0 \
      # 以下为可选但常见的 OpenCV 依赖
      libsm6 libxrender1 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目
COPY . .

# Render.com 会自动设置 $PORT 环境变量
EXPOSE 10000

# 启动命令，使用 shell form 以支持 $PORT 环境变量
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1
