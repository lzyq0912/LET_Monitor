import cloudscraper
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import json
import os
import sqlite3
from src.notification import NotificationService

logger = logging.getLogger(__name__)


class ForumMonitor:
    def __init__(self, config):
        self.config = config
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True,
                'mobile': False
            },
            interpreter='nodejs',
            allow_brotli=False
        )

        self.scraper.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive'
        })

        self.last_check_time = datetime.now()
        self.notifier = NotificationService(config)
        self.max_comments = config['monitoring'].get('max_comments', 10)

        self.db_file = "data/processed_comments.db"
        self.init_db()

        if self.config.get('proxy', {}).get('enabled', False):
            self.scraper.proxies = {
                'http': self.config['proxy']['http'],
                'https': self.config['proxy']['https']
            }
            logger.info("已启用代理")
        try:
            logger.info("尝试访问首页...")
            response = self.scraper.get(self.config['forum']['base_url'])
            if response.status_code != 200:
                raise Exception("无法访问论坛首页")
            logger.info("成功访问首页")
        except Exception as e:
            logger.error(f"访问首页出错: {e}")
            raise

        if not self.login():
            raise Exception("登录失败")

        self.check_database()

    def init_db(self):
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS processed_comments
                    (comment_id TEXT PRIMARY KEY, processed_time TIMESTAMP)''')
        conn.commit()
        conn.close()

    def login(self):
        try:
            login_url = f"{self.config['forum']['base_url']}/entry/signin"

            payload = {
                'Email': self.config['forum']['username'],
                'Password': self.config['forum']['password'],
                'ClientHour': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'RememberMe': '1'
            }

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': self.config['forum']['base_url'],
                'Referer': f"{self.config['forum']['base_url']}/",
            }

            logger.info("尝试登录...")
            response = self.scraper.post(
                login_url,
                data=payload,
                headers=headers
            )

            verify_response = self.scraper.get(f"{self.config['forum']['base_url']}/profile")
            if 'Sign In' in verify_response.text:
                logger.error("登录失败：页面仍然显示登录选项")
                return False

            logger.info("登录成功")
            return True

        except Exception as e:
            logger.error(f"登录过程出错: {e}")
            return False

    def is_comment_processed(self, comment_id):
        """检查评论是否已经处理过"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("SELECT 1 FROM processed_comments WHERE comment_id = ?", (comment_id,))
            result = c.fetchone() is not None
            conn.close()
            if result:
                logger.debug(f"评论 {comment_id} 已经处理过")
            return result
        except Exception as e:
            logger.error(f"检查评论处理状态时出错: {e}")
            return False

    def mark_comment_processed(self, comment_id):
        """标记评论为已处理"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("INSERT INTO processed_comments VALUES (?, ?)",
                      (comment_id, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            logger.debug(f"已将评论 {comment_id} 标记为已处理")
        except Exception as e:
            logger.error(f"标记评论处理状态时出错: {e}")

    def test_connection(self):
        """测试连接和会话状态"""
        try:
            # 测试首页访问
            home_response = self.scraper.get(self.config['forum']['base_url'])
            logger.debug(f"首页访问 - Status Code: {home_response.status_code}")

            # 测试用户资料页面
            profile_response = self.scraper.get(f"{self.config['forum']['base_url']}/profile")
            logger.debug(f"个人资料页面 - Status Code: {profile_response.status_code}")

            # 测试评论页面
            test_user = self.config['monitoring']['users'][0]['username']
            comments_response = self.scraper.get(f"{self.config['forum']['base_url']}/profile/comments/{test_user}")
            logger.debug(f"评论页面 - Status Code: {comments_response.status_code}")

            # 打印页面内容片段
            logger.debug(f"评论页面内容片段: {comments_response.text[:500]}")

            return True
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False

    def check_new_comments(self):
        try:
            logger.info("开始检查新评论...")
            for user_config in self.config['monitoring']['users']:
                username = user_config['username']
                keywords = user_config['keywords']
                logger.info(f"正在检查用户 {username} 的评论...")

                url = f"{self.config['forum']['base_url']}/profile/comments/{username}"
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Encoding': 'identity',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }

                response = self.scraper.get(url, headers=headers)
                if response.status_code != 200:
                    logger.error(f"获取用户页面失败: {response.status_code}")
                    continue

                try:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    comments = soup.find_all('li', id=lambda x: x and x.startswith('Comment_'))

                    if not comments:
                        logger.info(f"用户 {username} 暂无评论")
                        continue

                    comments = comments[:self.max_comments]
                    logger.info(f"用户 {username} 找到 {len(comments)} 条评论")

                    for comment in comments[:self.max_comments]:
                        comment_id = comment.get('id', '').replace('Comment_', '')

                        # 先检查是否处理过，如果处理过直接跳过
                        if self.is_comment_processed(comment_id):
                            logger.debug(f"跳过已处理的评论 {comment_id}")
                            continue

                        message_div = comment.find('div', class_='Message')
                        meta_div = comment.find('div', class_='Meta')

                        if message_div and meta_div:
                            comment_text = message_div.text.strip()
                            meta_items = meta_div.find_all('span', class_='MItem')
                            comment_time = meta_items[-1].text.strip() if meta_items else "Unknown time"

                            # if self.contains_keywords(comment_text, keywords):
                            logger.info(f"发现匹配的评论! 用户:{username}")
                            discussion_link = None
                            for item in meta_items:
                                if 'in' in item.text and item.find('a'):
                                    discussion_link = item.find('a')
                                    break

                            discussion_title = discussion_link.text.strip() if discussion_link else "Unknown Discussion"
                            notification_message = f"""新评论提醒:
                    用户: {username}
                    时间: {comment_time}
                    主题: {discussion_title}
                    内容: {comment_text}
                    链接: {self.config['forum']['base_url']}/discussion/comment/{comment_id}#Comment_{comment_id}"""

                                if self.notifier.notify(notification_message):
                                    logger.info("通知发送成功")
                                else:
                                    logger.error("通知发送失败")

                            # 无论是否匹配关键词，都标记为已处理
                            self.mark_comment_processed(comment_id)

                    logger.info(f"用户 {username} 的评论检查完成")

                except Exception as e:
                    logger.error(f"处理用户 {username} 的评论时出错: {e}")
                    continue

            logger.info("所有用户的评论检查完成")

        except Exception as e:
            logger.error(f"检查评论时出错: {e}")

    # def contains_keywords(self, text, keywords):
    #     return any(keyword.lower() in text.lower() for keyword in keywords)

    def check_database(self):
        """调试用：检查数据库内容"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("SELECT * FROM processed_comments")
            rows = c.fetchall()
            conn.close()
            logger.info(f"数据库中有 {len(rows)} 条记录")
            for row in rows[:5]:  # 只显示前5条
                logger.info(f"记录: {row}")
        except Exception as e:
            logger.error(f"检查数据库时出错: {e}")