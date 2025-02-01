import logging
from telegram import Bot
from telegram.constants import ParseMode
import asyncio

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
            self._send_telegram_sync(message)

    def _send_telegram_sync(self, message):
        async def send_message():
            if not self.bot:
                logger.error("Telegram bot 未初始化")
                return False

            try:
                async with self.bot:
                    await self.bot.send_message(
                        chat_id=self.config['notification']['telegram']['channel_id'],
                        text=message,
                        parse_mode=ParseMode.HTML
                    )
                logger.info("Telegram消息发送成功")
                return True
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                return False

        try:
            asyncio.run(send_message())
        except Exception as e:
            logger.error(f"发送过程出错: {e}")
            # 如果失败，尝试重新初始化并重试
            try:
                self.setup_telegram()
                asyncio.run(send_message())
            except Exception as retry_e:
                logger.error(f"重试发送失败: {retry_e}")