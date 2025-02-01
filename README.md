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

```angular2html
LET_Monitor/
│
├── config/
│   ├── config.yaml         # 实际使用的配置文件
│   └── config.yaml.example # 配置文件模板
│
├── logs/
│   ├── .gitkeep           # 保持日志目录存在
│   └── forum_monitor.log  # 运行时生成的日志文件
│
├── src/
│   ├── __init__.py        # Python 包标识文件
│   ├── monitor.py         # 核心监控逻辑
│   ├── notification.py    # 通知服务实现
│   └── utils.py          # 工具函数
│
├── .gitignore            # Git 忽略文件配置
├── README.md            # 项目说明文档
├── requirements.txt     # 项目依赖列表
└── run.py              # 程序入口文件
```


## 安装

1. 克隆仓库：
```bash
git clone https://github.com/lzyq0912/LET_Monitor.git
cd LET_Monitor
```

2. 创建虚拟环境：
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

1. 复制配置文件模板：
```bash
cp config/config.yaml.example config/config.yaml
```

2. 修改 `config/config.yaml`：
```yaml
forum:
  base_url: "https://lowendtalk.com"

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
  check_interval: 5  # 检查间隔（秒）

notification:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    channel_id: "YOUR_CHANNEL_ID"

logging:
  level: "INFO"
  file: "logs/forum_monitor.log"
```

## 设置 Telegram Bot

1. 在 Telegram 中搜索 @BotFather 创建新机器人
2. 获取 bot token
3. 创建频道并将机器人添加为管理员
4. 获取频道 ID
5. 更新配置文件中的 bot_token 和 channel_id

## 代理设置

程序默认使用本地代理：
- HTTP: 127.0.0.1:7890
- HTTPS: 127.0.0.1:7890

如需修改，请更新 `src/monitor.py` 中的代理设置。

## 运行

```bash
python run.py
```

## 注意事项

1. 需要确保本地代理正常运行
2. cookie 可能会定期失效，需要更新
3. 确保 Telegram Bot 具有向频道发送消息的权限

## 日志

- 日志文件位于 `logs/forum_monitor.log`
- 支持日志轮转，默认单文件最大 5MB
- 保留最近 5 个日志文件

## 开发计划

- [ ] cookie 自动更新
- [ ] 数据持久化
- [ ] Web 管理界面
- [ ] 更多通知方式支持

## 许可证

MIT License

---
虽然我有点笨，但还是希望这个项目对你有帮助！🤗