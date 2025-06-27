FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1 libglib2.0-0 \
      # 以下为可选但常见的 OpenCV 依赖
      libsm6 libxrender1 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目
COPY . .

# 暴露 Render PORT
ENV PORT 10000
EXPOSE 10000

# 启动命令
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--workers", "1"]
