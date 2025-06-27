FROM python:3.12-slim

WORKDIR /app

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
