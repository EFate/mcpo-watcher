# Step 1: 使用轻量的Python基础镜像
FROM python:3.11-slim

# Step 2: 设置工作目录
WORKDIR /app

# Step 3: 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Step 4: 复制依赖文件并安装
COPY requirements.txt .
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn && \
    # 升级pip到最新版
    pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: 复制应用代码、配置文件和启动器
COPY app ./app
COPY config.json .
COPY run.py .

# Step 6: 暴露端口
# 暴露监控API端口和默认的MCPO端口
EXPOSE 8000
EXPOSE 8080

# Step 7: 定义容器启动命令
# 使用 run.py 作为入口。具体参数将在 docker-compose.yml 中定义。
CMD ["python", "run.py"]