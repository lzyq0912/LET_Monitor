# LET Monitor

一个用于监控 LowEndTalk 论坛特定用户评论的工具。支持关键词匹配和 Telegram 通知功能。

## 功能特点
- 监控指定用户的评论
- 支持多个关键词匹配
- 通过 Telegram 机器人发送通知
- 支持代理设置
- 防止重复通知
- 定时检查更新（默认每5秒）

## 目录结构
```
LET_Monitor/
│
├── config/
│   ├── config.yaml         # 实际使用的配置文件
│   └── config.yaml.example # 配置文件模板
│
├── data/
│   └── processed_comments.db  # SQLite数据库文件，运行时生成
│
├── logs/
│   ├── .gitkeep           # 保持日志目录存在
│   └── forum_monitor.log  # 运行时生成的日志文件
│
├── src/
│   ├── monitor.py         # 核心监控逻辑
│   ├── notification.py    # 通知服务实现
│   └── utils.py          # 工具函数
│
├── Dockerfile            # Docker 构建文件
├── docker-compose.yml    # Docker Compose 配置
├── docker-entrypoint.sh  # Docker 启动脚本
├── .dockerignore        # Docker 忽略文件
├── .gitignore           # Git 忽略文件配置
├── README.md            # 项目说明文档
├── requirements.txt     # 项目依赖列表
└── run.py              # 程序入口文件
```

## 使用 Docker 部署

### 前置条件
- 安装 Docker
- 安装 Docker Compose

### 部署步骤

1. 克隆仓库：
```bash
git clone https://github.com/lzyq0912/LET_Monitor.git
cd LET_Monitor
```

2. 复制并修改配置文件：
```bash
cp config/config.yaml.example config/config.yaml
```

3. 创建必要的目录：
```bash
mkdir -p logs data
```

4. 创建并编辑 docker-compose.yml：
```yaml
version: '3'

services:
  forum-monitor:
    build: .
    environment:
      - FORUM_USERNAME=你的论坛用户名
      - FORUM_PASSWORD=你的论坛密码
      - TELEGRAM_BOT_TOKEN=你的Telegram机器人token
      - TELEGRAM_CHANNEL_ID=你的Telegram频道ID
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
```

5. 启动服务：
```bash
docker-compose up -d
```

### Docker 常用命令

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose stop

# 启动服务
docker-compose start

# 重启服务
docker-compose restart

# 停止并移除容器
docker-compose down

# 更新代码后重新构建
docker-compose up -d --build
```

## 配置说明

### 必要配置项
在 docker-compose.yml 中设置以下环境变量：
- FORUM_USERNAME: 论坛用户名
- FORUM_PASSWORD: 论坛密码
- TELEGRAM_BOT_TOKEN: Telegram 机器人 token
- TELEGRAM_CHANNEL_ID: Telegram 频道 ID

### config.yaml 配置说明
```yaml
forum:
  username: "username"  # 会被环境变量覆盖
  password: "password"  # 会被环境变量覆盖
  base_url: "https://lowendtalk.com"
  timeout: 30
  retry_attempts: 3

monitoring:
  users:
    - username: "NDTN"
      keywords:
        - "sale"
        - "Coupon"
    - username: "CycloneJoker"
      keywords:
        - "nice"
        - "god"
  check_interval: 5
  max_comments: 10

notification:
  telegram:
    enabled: true
    bot_token: "your_bot_token"  # 会被环境变量覆盖
    channel_id: "your_channel_id"  # 会被环境变量覆盖
```

## 数据持久化
- 日志文件保存在 ./logs 目录
- 数据库文件保存在 ./data 目录
- 这些目录通过 Docker volumes 挂载，确保数据持久化

## 注意事项
1. 确保配置文件中的监控用户和关键词正确设置
2. 检查 Telegram Bot 是否有权限发送消息到指定频道
3. 正确设置环境变量，特别是敏感信息
4. 定期检查日志文件确保程序正常运行

## 开发计划
- [ ] cookie 自动更新
- [ ] Web 管理界面
- [ ] 更多通知方式支持
- [x] Docker 容器化部署
- [x] 数据持久化

## 许可证
MIT License

---
希望这个项目对你有帮助！🤗