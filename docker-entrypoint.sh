#!/bin/bash

# 使用环境变量更新配置文件
sed -i "s/username: .*/username: \"$FORUM_USERNAME\"/" ./config/config.yaml
sed -i "s/password: .*/password: \"$FORUM_PASSWORD\"/" ./config/config.yaml
sed -i "s/bot_token: .*/bot_token: \"$TELEGRAM_BOT_TOKEN\"/" ./config/config.yaml
sed -i "s/channel_id: .*/channel_id: \"$TELEGRAM_CHANNEL_ID\"/" ./config/config.yaml
sed -i "s/check_interval: .*/check_interval: $CHECK_INTERVAL/" ./config/config.yaml
sed -i "s/level: .*/level: \"$LOG_LEVEL\"/" ./config/config.yaml

# 启动应用
python run.py