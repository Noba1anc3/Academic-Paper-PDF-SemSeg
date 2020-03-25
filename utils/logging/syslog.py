
import logging

class Logger:
    def __init__(self, loggername):

        #创建一个logger
        self.logger = logging.getLogger(loggername)
        self.logger.setLevel(logging.INFO)

        #创建一个handler，用于写入日志文件
        logname = './utils/logging/out.log'
        fh = logging.FileHandler(logname, encoding = 'utf-8')
        fh.setLevel(logging.INFO)

        #创建一个handler，用于将日志输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)


    def get_log(self):
        return self.logger
