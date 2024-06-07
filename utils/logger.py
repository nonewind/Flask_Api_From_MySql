# -*- encoding: utf-8 -*-
'''
@File    :   logger.py
@Time    :   2022/05/10 10:54:26
@Author  :   Zhangziheng
'''
import datetime
import inspect
import io
import logging
import os
import platform

# == 判断日志文件夹是否存在 不存在则创建 ==
if not os.path.exists('log'):
    os.mkdir('log', 0o775)


def creatLogger(name):
    """创建logger

    Args:
        name (string): 打印者的名称

    Returns:
        logger
    """
    datefmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(
        level=logging.INFO,
        datefmt=datefmt,
        format='[%(asctime)s] [%(process)d] [%(levelname)s] :: %(message)s')
    return logging.getLogger(name)


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(
        self,
        filename,
        level='info',
        fmt='%(asctime)s - %(levelname)s: %(message)s'
    ):
        self.filename = filename
        self.level = level
        self.fmt = fmt
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        self._set_handler()

    def _set_handler(self):
        self.current_date = datetime.datetime.now().strftime('%Y%m%d')  # 更新当前的日期
        filename_with_date = f"{self.filename}_{self.current_date}.log"
        sh = logging.StreamHandler()  # 往屏幕上输出
        format_str = logging.Formatter(self.fmt)  # 设置日志格式
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = logging.FileHandler(filename_with_date, encoding='utf-8')
        th.setFormatter(format_str)  # 设置文件里写入的格式
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)

    def get_stream_handler(self):
        """返回一个设置了格式和级别的日志处理器，并且这个处理器会将日志输出到一个字符串流中"""

        stream = io.StringIO()
        sh = logging.StreamHandler(stream)  # 往字符串流中输出
        format_str = logging.Formatter(self.fmt)  # 设置日志格式
        sh.setFormatter(format_str)  # 设置字符串流中显示的格式
        sh.setLevel(self.level_relations.get(self.level))  # 设置日志级别
        return sh, stream

    def debug(self, message):
        self._check_and_set_handler()
        self._log('debug', message)

    def info(self, message):
        self._check_and_set_handler()
        self._log('info', message)

    def warning(self, message):
        self._check_and_set_handler()
        self._log('warning', message)

    def error(self, message):
        self._check_and_set_handler()
        self._log('error', message)

    def crit(self, message):
        self._check_and_set_handler()
        self._log('critical', message)

    def _log(self, level, message):
        caller_frame = inspect.stack()[2]
        file_name = caller_frame.filename
        line_no = caller_frame.lineno
        func_name = caller_frame.function
        self.logger.log(
            self.level_relations[level], f'{file_name}[line:{line_no}] - {func_name}: {message}')

    def _check_and_set_handler(self):
        current_date = datetime.datetime.now().strftime('%Y%m%d')
        if current_date != self.current_date:  # 检查当前的日期是否与FileHandler的日期一致
            self._set_handler()


class bbLoger(object):
    def __init__(self, name, errorName):
        self.logger = creatLogger(name)
        # self.errorLogger = Logger(errorName)
        self._ggg_Uncaught_exception = Logger(errorName)

    def info(self, messgae):
        self.logger.info(messgae)

    def waring(self, messgae):
        self.logger.warning(messgae)

    def error(self, messgae):
        self.logger.error(messgae)
        # self.errorLogger.logger.error(messgae)
        self._ggg_Uncaught_exception .error(messgae)

    def warning(self, messgae):
        self.logger.warning(messgae)
        # self.errorLogger.logger.warning(messgae)

    def debug(self, message):
        self.logger.debug(message)

# # 加入系统判断 以防日志存储位置不正确
# if platform.system().lower() in ["linux", "darwin"]:
#     logger = creatLogger("log/zwsj.log")
#     _ggg_Uncaught_exception = creatLogger("log/Uncaught_exception.log")
#     baseLogger = Logger("log/backTask")
# else:
#     logger = creatLogger("log\\zwsj.log")
#     _ggg_Uncaught_exception = creatLogger("log\\Uncaught_exception.log")
#     baseLogger = Logger("log\\backTask")


if platform.system().lower() in ["linux", "darwin"]:
    name = "log/zwsj.log"
    errorName = "log/Uncaught_exception.log"
else:
    name = "log\\zwsj.log"
    errorName = "log\\Uncaught_exception.log"

logger = bbLoger(name, errorName)
_ggg_Uncaught_exception = bbLoger(name, errorName)
