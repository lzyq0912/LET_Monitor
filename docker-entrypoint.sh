#!/bin/bash

# 替换 forum 下的用户名和密码
sed -i "/forum:/,/base_url:/ s/username: .*/username: \"$FORUM_USERNAME\"/" ./config/config.yaml
sed -i "/forum:/,/base_url:/ s/password: .*/password: \"$FORUM_PASSWORD\"/" ./config/config.yaml

# 替换 telegram 下的 bot_token 和 channel_id
sed -i "/telegram:/,/logging:/ s/bot_token: .*/bot_token: \"$TELEGRAM_BOT_TOKEN\"/" ./config/config.yaml
sed -i "/telegram:/,/logging:/ s/channel_id: .*/channel_id: \"$TELEGRAM_CHANNEL_ID\"/" ./config/config.yaml

# 启动应用
python run.py