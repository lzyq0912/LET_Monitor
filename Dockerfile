FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY src/ ./src/
COPY run.py .
COPY config/config.yaml.example ./config/config.yaml

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建必要的目录
RUN mkdir -p /app/logs /app/data

# 设置环境变量默认值
ENV FORUM_USERNAME=""
ENV FORUM_PASSWORD=""
ENV TELEGRAM_BOT_TOKEN=""
ENV TELEGRAM_CHANNEL_ID=""
ENV CHECK_INTERVAL=5
ENV LOG_LEVEL="DEBUG"

# 创建启动脚本
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]