# -*- coding:utf-8 -*-

import os
import re
import logging
import datetime as dt
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
from config import *
import requests

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
    def __init__(self, log_dir='./logs', log_name='server', console=True, level=logging.DEBUG):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(level)
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


def response_module(code, msg="", data={}):
    return {"code": code, "msg": msg, "data": data}

response_dict = {
    "ok":                   response_module(200),
    "bad_request":          response_module(400001, "illegal request parameter"),
    "not_cheap_account":    response_module(400002, "not cheap account"),
    "account_registered":   response_module(400003, "the account name already exists"),
    "forbidden_no_auth":    response_module(401001, "no auth"),
    "forbidden_ip_max":     response_module(401002, "You already register too many free account"),
    "forbidden_today_max":  response_module(401003, "Account creation limit reached"),
    "server_error":         response_module(500, "internal server error") 
}

response_dict_cn = {
    "ok":                   response_module(200),
    "bad_request":          response_module(400001, "请求参数非法"),
    "not_cheap_account":    response_module(400002, "账户名不是便宜账户"),
    "account_registered":   response_module(400003, "账户名已存在"),
    "forbidden_no_auth":    response_module(401001, "没有权限"),
    "forbidden_ip_max":     response_module(401002, "今日你创建的账户已达最大限制"),
    "forbidden_today_max":  response_module(401003, "今日账户创建已达最大限制"),
    "server_error":         response_module(500, "内部服务错误") 
}

# 最小长度5，最大长度63，
# 可以.分隔，分隔的每一部分要求以小写字母开头，以数字或小写字母结尾; 每一部分的中间部分可以为：小写字母、数字、-; 每一部分的长度5~63
MIN_ACCOUNT_NAME_LENGTH = 5
MAX_ACCOUNT_NAME_LENGTH = 63
lower_alpha = 'abcdefghijklmnopqrstuvwxyz'
def is_lower_alpha(ch):
    if lower_alpha.find(ch) == -1:
        return False
    return True

def is_valid_name(name):
    length = len(name)
    if length < MIN_ACCOUNT_NAME_LENGTH or length > MAX_ACCOUNT_NAME_LENGTH:
        return False

    begin = 0
    while True:
        end = name.find('.', begin)
        if end == -1:
            end = length
        if end - begin < MIN_ACCOUNT_NAME_LENGTH:
            return False
        
        if not is_lower_alpha(name[begin]):
            return False
        if not (is_lower_alpha(name[end-1]) or name[end-1].isdigit()):
            return False
        for index in range(begin+1, end-1):
            ch = name[index]
            if not (is_lower_alpha(ch) or ch.isdigit() or ch == '-'):
                return False
        if end == length:
            break
        begin = end + 1
    return True

def is_cheap_name(name):
    has_spacial_char = False 
    special_char = 'aeiouy'
    special_delimiter = '.-/'
    for ch in name:
        if ch >= '0' and ch <= '9':
            return True
        #if ch == '.' or ch == '-' or ch == '/':
        if special_delimiter.find(ch) != -1:
            return True
        if special_char.find(ch) != -1:
            has_spacial_char = True
    if not has_spacial_char:
        return True
    return False


# status: 1~3 retry
g_reward_retry_count = 3
g_reward_status = {
    "NOT_REWARD": 0,
    "SUCCESS": g_reward_retry_count+1,
}
