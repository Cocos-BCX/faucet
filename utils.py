# -*- coding:utf-8 -*-

import os
import re
import logging
import datetime as dt
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler

class SubFormatter(logging.Formatter):
    converter=dt.datetime.fromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s

class Logging(object):
    def __init__(self, log_dir='./logs', log_name='server', console=True):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)
        #formatter = logging.Formatter("%(asctime)s [%(name)s] [%(funcName)s:%(lineno)s] [%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
        formatter = SubFormatter(fmt='%(asctime)s [%(name)s] [%(funcName)s:%(lineno)s] [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S.%f')

        # file handler
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = log_dir + '/' + log_name
        #fh = logging.FileHandler(log_file)
        #fh = TimedRotatingFileHandler(filename=log_file, when="D", interval=1, backupCount=7)
        fh = TimedRotatingFileHandler(filename=log_file, when="H", interval=1, backupCount=3*24)
        fh.suffix = "%Y-%m-%d_%H-%M.log"
        fh.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # console handler
        # define a Handler which writes INFO messages or higher to the sys.stderr
        if console:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def getLogger(self):
        return self.logger


def code_text(code, text):
    return {"code": code, "text": text}

status_text = {
    "ok":                   code_text(200, ""),
    "bad_request":          code_text(400001, "illegal request parameter"),
    "not_cheap_account":    code_text(400002, "not cheap account"),
    "account_registered":   code_text(400003, "the account name already exists"),
    "forbidden_no_auth":    code_text(401001, "no auth"),
    "forbidden_ip_max":     code_text(401002, "You already register too many free account"),
    "forbidden_today_max":  code_text(401003, "Account creation limit reached"),
    "server_error":         code_text(500, "internal server error") 
}

status_text_cn = {
    "ok":                   code_text(200, ""),
    "bad_request":          code_text(400001, "请求参数非法"),
    "not_cheap_account":    code_text(400002, "账户名不是便宜账户"),
    "account_registered":   code_text(400003, "账户名已存在"),
    "forbidden_no_auth":    code_text(401001, "没有权限"),
    "forbidden_ip_max":     code_text(401002, "今日你创建的账户已达最大限制"),
    "forbidden_today_max":  code_text(401003, "今日账户创建已达最大限制"),
    "server_error":         code_text(500, "内部服务错误") 
}


