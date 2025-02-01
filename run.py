import schedule
import time
from src.utils import load_config, setup_logging
from src.monitor import ForumMonitor


def main():
    # 加载配置
    config = load_config()

    # 设置日志
    logger = setup_logging(config)

    # 创建监控器
    monitor = ForumMonitor(config)

    # 设置定时任务
    schedule.every(config['monitoring']['check_interval']).seconds.do(monitor.check_new_comments)

    logger.info("监控程序已启动")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()