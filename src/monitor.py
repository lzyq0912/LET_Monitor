import cloudscraper
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from src.notification import NotificationService

logger = logging.getLogger(__name__)


class ForumMonitor:
    def __init__(self, config):
        self.config = config
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        self.last_check_time = datetime.now()
        self.notifier = NotificationService(config)
        self.max_comments = config['monitoring'].get('max_comments', 10)
        self.notified_comments = set()  # 添加这一行来记录已通知的评论

        # 设置代理
        self.scraper.proxies = {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
        }

        # 设置cookies
        cookies = {
            '_ga': 'GA1.1.1726189077.1738368714',
            'Vanilla': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NDA5Njc0NTcsImlhdCI6MTczODM3NTQ1Nywic3ViIjoyMDgzMjl9.cfVduaVOB-3nLi786QCphIOxbNDQ_qtmmjwMqZjV43g',
            'Vanilla-tk': '95DeAXW31jsQ90oV:208329:1738375457:548896914dee2b3763b644e28b4112b4',
            'Vanilla-St': '2.1738378157.8DwRNwBmJuzn65vP.uRCurNVEhq20VkhJk5DFqco.nWX25hhzkVbt4Nr9DJq0vA',
            'cf_clearance': 'uF5sbu9EUwFR77hv20ilnK2CmUZACZtyzffiH6lULBE-1738376604-1.2.1.1-Dn9yuwtEJbxa0gWPu6SebZhg1h3Wor5IEG8i_ax6D6mTfQlFCoboID4wmpJNXPXQPJCoJgB0xZIpfix.EtLmE3o.SwYLcD32L_QUgokj.2DYHA2eauhmkz61CvzFmrduXVbZasTwtqrRz75rwwBRuwe7P6dusXy.h_K4hBf6iQNCWP5yFHSSKUmJw_6EkE8S53wQh2wzS9vyiNRAvOmw._boCS6oeLtn2pb09.9djpN4mve5IvGcznow9qvfv45X.U9b3f8Zx4yd4uBWX_B7Aq5hRwmJu01DNKJ95KLkNBE',
            '_ga_TH6SK14E72': 'GS1.1.1738375383.2.1.1738376623.0.0.0',
            'Vanilla-Vv': '1738376623'
        }
        for name, value in cookies.items():
            self.scraper.cookies.set(name, value)

    def check_new_comments(self):
        try:
            logger.info("开始检查新评论...")

            for user_config in self.config['monitoring']['users']:
                username = user_config['username']
                keywords = user_config['keywords']

                logger.info(f"正在检查用户 {username} 的评论...")
                url = f"{self.config['forum']['base_url']}/profile/comments/{username}"

                response = self.scraper.get(url)

                if response.status_code != 200:
                    logger.error(f"获取用户页面失败: {response.status_code}")
                    logger.error(f"Response headers: {dict(response.headers)}")
                    if response.text:
                        logger.error(f"Response content: {response.text[:500]}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                comments = soup.find_all('li', class_='Item')[:self.max_comments]
                logger.info(f"用户 {username} 找到 {len(comments)} 条评论")

                for comment in comments:
                    comment_id = comment.get('id', '').replace('Comment_', '')

                    # 检查是否已经通知过
                    if comment_id in self.notified_comments:
                        continue

                    message_div = comment.find('div', class_='Message')
                    meta_div = comment.find('div', class_='Meta')

                    if message_div and meta_div:
                        comment_text = message_div.text.strip()
                        meta_items = meta_div.find_all('span', class_='MItem')
                        comment_time = meta_items[-1].text.strip() if meta_items else "Unknown time"

                        logger.info(f"检查评论 [ID:{comment_id}] [时间:{comment_time}]")
                        logger.info(f"评论内容: {comment_text[:100]}...")

                        if self.contains_keywords(comment_text, keywords):
                            logger.info(f"发现匹配的评论! 用户:{username}, ID:{comment_id}")
                            discussion_link = None
                            for item in meta_items:
                                if 'in' in item.text and item.find('a'):
                                    discussion_link = item.find('a')
                                    break

                            discussion_title = discussion_link.text.strip() if discussion_link else "Unknown Discussion"

                            notification_message = f"""
新评论提醒:
用户: {username}
时间: {comment_time}
主题: {discussion_title}
内容: {comment_text}
链接: {self.config['forum']['base_url']}/discussion/comment/{comment_id}#Comment_{comment_id}
"""
                            self.notifier.notify(notification_message)
                            self.notified_comments.add(comment_id)  # 添加到已通知集合

                logger.info(f"用户 {username} 的评论检查完成")

            logger.info("所有用户的评论检查完成")

        except Exception as e:
            logger.error(f"检查评论时出错: {e}")

    def contains_keywords(self, text, keywords):
        return any(keyword.lower() in text.lower() for keyword in keywords)