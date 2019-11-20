import os
import json
import random
import pymysql
import requests
import datetime

import tornado.ioloop
import tornado.web
import tornado.httpserver

from tornado.options import define, options, parse_command_line
from config import *

# 定义默认端口
define('port', default=8041, type=int)

def init_reward():
    try:
        body_relay = {
            "jsonrpc": "2.0",
            "method": "get_global_properties",
            "params": [],
            "id":1
        }
        properties = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)['result']
        transfer = properties['parameters']['current_fees']['parameters'][0]
        if transfer[0] == 0:
            reward_core = transfer[1]['fee'] * 2
            reward_gas = transfer[1]['fee']/asset_core_precision * 2
    except Exception as e:
        print(repr(e))

def init_db():
    my_db = pymysql.connect(**db)   #连接数据库并创建表
    cursor = my_db.cursor()
    try:
        cursor.execute(sql["createTable"])
        my_db.commit()
    except:
        my_db.rollback()
    my_db.close()

#服务启动初始化
def initalize():
    init_db()
    init_reward()

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

class FaucetHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-type, Accept, connection, User-Agent, Cookie, Authorization")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self):
        self.post()

    def post(self):
        auth = self.request.headers.get('authorization', '') #验证权限
        #print("auth", auth)
        if auth not in auth_list.values():
            return self.write({'msg': 'no access authority!', 'code': '400'})
        else:
            print("ip:>>>>%s" % self.request.remote_ip)
        data = json.loads(self.request.body.decode("utf8"))
        account = data.get("account")
        name = account.get('name', '') #获取帐户名
        active_key = account.get('active_key', '') #获取active公钥
        owner_key = account.get('owner_key', '')   #获取owner公钥
        #register = registrar
        if not name:
            return self.write({'msg': 'no name!', 'code': '400'})
        if not is_cheap_name(name):
            return self.write({'msg': 'account name {} is not cheap'.format(name), 'code': '400'})
        if not active_key:
            return self.write({'msg': 'no active key!', 'code': '400'})
        if not owner_key:
            owner_key = active_key  #如果没有owner_key默认值为active_key

        # 数据库连接
        my_db = pymysql.connect(**db)
        cursor = my_db.cursor()

        if has_account_max_limit:
            today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            try:
                count = cursor.execute(sql['count'].format(today, today))
                if count % 10 == 0:
                    print('{} create count {}'.format(today, count))
                if count > registrar_account_max:
                    my_db.close()
                    return self.write({"msg": "Up to the maximum number of accounts created today", "code": 400})
            except Exception as e:
                my_db.close()
                print(repr(e))
                self.write({"msg": "db error", "code": 400})
        
        try:    #注册帐户
            body_relay = {
                "jsonrpc": "2.0",
                "method": "register_account",
                "params": [name, owner_key, active_key, register, "true"],
                "id":1
            }
            info = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)
            #print('[cli_wallet] register_account, body: {}, result: {}'.format(body_relay, info))
            if "error" in info:
                error = info["error"]["message"]
                return self.write({'msg': error, 'code': '400'})
        except Exception as e:
            print(repr(e))
            return self.write({'msg': '未知错误!', 'code': '400'})
        try:
            body_relay = {
                "jsonrpc": "2.0",
                "method": "get_account",
                "params": [name],
                "id":1
            }
            account_info = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)
            userid = account_info["result"]["id"]
        except Exception as e:
            print(repr(e))
            return self.write({"msg": "obtain user id error!", "code": 400})
        data = {
            "account": {
                "id": userid,
                "name": name,
                "owner_key": owner_key,
                "active_key": active_key
            }
        }

        # try:    #发送奖励core_asset
        #     body_relay = {
        #         "jsonrpc": "2.0",
        #         "method": "transfer",
        #         "params": [register, name, reward_core, asset_core, memo, "true"],
        #         "id":1
        #     }
        #     requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers)
        # except Exception as e:
        #     print(repr(e))
        #     return self.write({'msg': 'transfer failed!', 'data': repr(e), 'code': '400'})

        try:    #发送奖励gas
            body_relay = {
                "jsonrpc": "2.0",
                "method": "update_collateral_for_gas",
                "params": [register, name, reward_gas, "true"],
                "id":1
            }
            requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers)
        except Exception as e:
            print(repr(e))
            return self.write({'msg': 'update_collateral_for_gas failed!', 'data': repr(e), 'code': '400'})
        
        #向数据库中插入新注册用户信息
        try:
            create_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(sql['insertData'].format(userid, name, active_key, create_time))
            my_db.commit()
        except Exception as e:
            print(repr(e))
            my_db.rollback()
        finally:
            my_db.close()
        return self.write({'msg': 'Regist successful! {}, {}'.format(name, memo), 'data': data, 'code': '200'})

def main():
    initalize()
    parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r'/api/v1/accounts', FaucetHandler),
        ],
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.bind(options.port, address='0.0.0.0')
    http_server.start(2)
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
