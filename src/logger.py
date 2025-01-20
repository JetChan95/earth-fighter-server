import logging
import os


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class LoggerFactory(metaclass=SingletonMeta):
    def __init__(self, log_file='app.log'):
        self.logger = self.configure_logging(log_file)

    def configure_logging(self, log_file):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # 创建一个控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 创建一个文件处理器
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # 创建一个格式化器
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # 将处理器添加到记录器中
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        return logger

    @staticmethod
    def getLogger():
        return LoggerFactory().logger