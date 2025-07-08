import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

# 定义日志文件路径
LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

class MyLogger:
    def __init__(self, name="my_app", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 避免重复添加handler
        if not self.logger.handlers:
            # 控制台输出
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(console_handler)

            # 文件输出 (RotatingFileHandler)
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,  # 保留5个备份文件
                encoding='utf-8'
            )
            file_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(file_handler)

    def _get_formatter(self):
        # 统一的日志格式
        return logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def critical(self, message):
        self.logger.critical(message)


# 示例用法 (仅供测试)
if __name__ == "__main__":
    # import os
    # os.makedirs("logs", exist_ok=True) # 确保 logs 目录存在

    logger_test = MyLogger("test_logger", level=logging.DEBUG)
    logger_test.debug("这是一条调试信息")
    logger_test.info("这是一条普通信息")
    logger_test.warning("这是一条警告信息")
    logger_test.error("这是一条错误信息")
    logger_test.critical("这是一条严重错误信息")

    # 测试不同的日志器名称
    another_logger = MyLogger("another_module")
    another_logger.info("这是来自另一个模块的信息") 