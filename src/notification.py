import logging
from telegram import Bot
from telegram.constants import ParseMode
import asyncio
import time

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, config):
        self.config = config
        self.bot = None
        if self.config['notification']['telegram']['enabled']:
            self.setup_telegram()

    def setup_telegram(self):
        try:
            self.bot = Bot(token=self.config['notification']['telegram']['bot_token'])
            logger.info("Telegram bot 初始化成功")
        except Exception as e:
            logger.error(f"Telegram bot setup failed: {e}")

    def notify(self, message):
        logger.info("开始发送通知...")
        if self.config['notification']['telegram']['enabled']:
            logger.info("尝试发送Telegram通知...")
            return self._send_telegram_sync(message)  # 添加 return
        return False  # 如果没有启用 telegram，返回 False

    def _send_telegram_sync(self, message):
        async def send_message():
            if not self.bot:
                self.setup_telegram()
                if not self.bot:
                    return False

            try:
                max_retries = 3
                retry_delay = 2

                for attempt in range(max_retries):
                    try:
                        async with self.bot:
                            await self.bot.send_message(
                                chat_id=self.config['notification']['telegram']['channel_id'],
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            await asyncio.sleep(1)  # 添加延迟避免频率限制
                        return True
                    except Exception as e:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay * (attempt + 1))
                            continue
                        raise e
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                return False

        try:
            return asyncio.run(send_message())
        except Exception as e:
            logger.error(f"发送过程出错: {e}")
            return False