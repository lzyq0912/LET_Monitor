import time
import schedule
from src.utils import load_config, setup_logging
from src.monitor import ForumMonitor


def main():
    # 加载配置
    config = load_config()
    # 设置日志
    logger = setup_logging(config)

    try:
        # 创建监控器
        monitor = ForumMonitor(config)

        # 设置定时任务
        schedule.every(config['monitoring']['check_interval']).seconds.do(
            monitor.check_new_comments
        )

        logger.info("监控程序已启动")

        # 主循环
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"运行时错误: {e}")
                time.sleep(60)  # 出错后等待一分钟再继续

    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        raise


if __name__ == "__main__":
    main()