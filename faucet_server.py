# -*- coding:utf-8 -*-

import os
import json
import random
import pymysql
import requests
import datetime
import socket

import tornado.ioloop
import tornado.web
import tornado.httpserver

from tornado.options import define, options, parse_command_line
from config import *
from utils import *

logger = Logging().getLogger()

# 定义默认端口
define('port', default=8041, type=int)

def init_reward():
    global asset_core_precision
    global core_exchange_rate
    global reward_gas
    global gas_core_exchange_rate
    global register_id

    try:
        #get_global_properties --> transfer_fee
        body_relay = {
            "jsonrpc": "2.0",
            "method": "get_global_properties",
            "params": [],
            "id":1
        }
        properties = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)['result']
        transfer = properties['parameters']['current_fees']['parameters'][0]
        if transfer[0] == 0:
            #get_asset COCOS --> asset_core_precision
            body_relay = {
                "jsonrpc": "2.0",
                "method": "get_asset",
                "params": [asset_core],
                "id":1
            }
            asset = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)['result']
            logger.info('core asset: {}'.format(asset))
            asset_core_precision = asset['precision']

            #get_asset GAS --> core_exchange_rate
            body_relay = {
                "jsonrpc": "2.0",
                "method": "get_asset",
                "params": [asset_gas],
                "id":1
            }
            asset = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)['result']
            logger.info('gas asset: {}'.format(asset))
            core_exchange_rate = asset['options']['core_exchange_rate']
            gas_core_exchange_rate = round(core_exchange_rate['quote']['amount']/core_exchange_rate['base']['amount'])
            #reward_core = int(transfer[1]['fee']/(10**asset_core_precision) * transfer_operation_N)
            reward_gas = transfer[1]['fee'] * gas_core_exchange_rate * transfer_operation_N
            logger.info('gas_core_exchange_rate: {}, reward_gas: {}, reward_core: {}, transfer fee: {}'.format(gas_core_exchange_rate, reward_gas, reward_core, transfer))

            # init register account_id
            body_relay = {
                "jsonrpc": "2.0",
                "method": "get_account",
                "params": [register],
                "id":1
            }
            account_info = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)
            register_id = account_info["result"]["id"]
    except Exception as e:
        logger.error('init failed. error: {}'.format(repr(e)))
        push_message("init reward error")

def init_db():
    my_db = pymysql.connect(**db)   #连接数据库并创建表
    cursor = my_db.cursor()
    try:
        cursor.execute(sql["createTable"])
        my_db.commit()
    except Exception as e:
        my_db.rollback()
        logger.warn('init failed. error: {}'.format(repr(e)))
        # push_message("init db error")
    my_db.close()

def init_host_info():
    global g_hostname
    global g_ip
    g_hostname = socket.getfqdn(socket.gethostname(  ))
    g_ip = socket.gethostbyname(g_hostname)
    logger.info('hostname: {}, ip: {}'.format(g_hostname, g_ip))

#服务启动初始化
def initialize():
    init_host_info()
    init_db()
    init_reward()
    logger.info('ip_limit_list: {}'.format(ip_limit_list))
    logger.info('init done.')

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

def push_message(message, labels=['faucet']):
    content = "[{}]{} {}({}), {}".format(env, str(labels), g_hostname, g_ip, message)
    logger.debug('push content: {}'.format(content))
    try:
        body_relay = {
            "jsonrpc": "2.0",
            "msgtype": "text",
            "text": {
                "content": content
            },
            "id":1
        }
        response = json.loads(requests.post(faucet_alert_address, data = json.dumps(body_relay), headers = headers).text)
    except Exception as e:
        logger.error('push error. {}'.format(repr(e)))

def get_account_asset_balance(account, asset_id='1.3.0'):
    try:
        body_relay = {
            "jsonrpc": "2.0",
            "method": "list_account_balances",
            "params": [account],
            "id":1
        }
        response = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)
        balances = response['result']
        logger.debug('>> list_account_balance {}: {}'.format(account, balances))
        for asset_balance in balances:
            if asset_balance['asset_id'] == asset_id:
                return int(asset_balance['amount'])
    except Exception as e:
        logger.error('get {} balance error. {}'.format(account, repr(e)))
    return 0

def params_valid(account):
    logger.info('account: {}'.format(account)) 
    name = account.get('name', '') #获取帐户名
    active_key = account.get('active_key', '') #获取active公钥
    owner_key = account.get('owner_key', '')   #获取owner公钥
    if not name:
        return False, {'msg': 'no name', 'code': '400'}, {}
    if not is_cheap_name(name):
        return False, {'msg': 'account name {} is not cheap'.format(name), 'code': '400'}, {}
    if not active_key:
        return False, {'msg': 'no active key', 'code': '400'}, {}
    if not owner_key:
        owner_key = active_key  
    return True, '', {'name': name, 'active_key': active_key, 'owner_key': owner_key}

def send_reward(core_count, account_id):
    logger.info('account: {}, core_count:{}'.format(account_id, core_amount))
    is_return = False
    core_amount = get_account_asset_balance(register)

    #发送奖励core_asset
    if core_count <= reward_core_until_N:
        try: 
            if reward_core*(10**asset_core_precision) < core_amount:
                body_relay = {
                    "jsonrpc": "2.0",
                    "method": "transfer",
                    "params": [register_id, account_id, "%.5f"%(reward_core), asset_core, [memo, "false"], "true"],
                    "id":1
                }
                requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers)
            else:
                is_return = True
                push_message('register {} no enough {}'.format(register, asset_core))
                logger.warn('register {} no enough {}. reward_core: {}'.format(register, asset_core, reward_core))
        except Exception as e:
            logger.error('transfer failed. account: {}, error: {}'.format(account_id, repr(e)))
            return False, {'msg': 'transfer failed!', 'data': repr(e), 'code': '400'}

    #发送奖励gas
    if not is_return:
        if reward_gas < core_amount * gas_core_exchange_rate:
            try:
                body_relay = {
                    "jsonrpc": "2.0",
                    "method": "update_collateral_for_gas",
                    "params": [register_id, account_id, int(reward_gas), "true"],
                    "id":1
                }
                requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers)
            except Exception as e:
                logger.error('update_collateral_for_gas failed. account: {}, reward_gas: {}, error: {}'.format(account_id, reward_gas, repr(e)))
                return False, {'msg': 'update_collateral_for_gas failed!', 'data': repr(e), 'code': '400'}
        else:
            push_message('register {} no enough {} for collateral gas'.format(register, asset_core))
    return True, ''

#注册帐户
def register_account(account):
    try:    
        body_relay = {
            "jsonrpc": "2.0",
            "method": "register_account",
            "params": [account['name'], account['owner_key'], account['active_key'], register, "true"],
            "id":1
        }
        info = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)
        if "error" in info:
            error = info["error"]["message"]
            logger.error('register account failed. account: {}'.format(account))
            return False, {'msg': 'register account {} failed. {}'.format(account['name'], error), 'code': '400'}, ''
    except Exception as e:
        logger.error('register account failed. account: {}, error: {}'.format(account, repr(e)))
        push_message("register account {} failed".format(account['name']))
        return False, {'msg': 'register account failed', 'code': '400'}, ''
    try:
        body_relay = {
            "jsonrpc": "2.0",
            "method": "get_account",
            "params": [account['name']],
            "id":1
        }
        account_info = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)
        account_id = account_info["result"]["id"]
    except Exception as e:
        logger.error('get account failed. account: {}, error: {}'.format(account, repr(e)))
        return False, {"msg": "obtain user id error!", "code": 400}, ''
    return True, '', account_id

def account_count_check(ip, date):
    # 数据库连接
    my_db = pymysql.connect(**db)
    cursor = my_db.cursor()

    #today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    try:
        count = cursor.execute(sql['count'].format(date, date))
        logger.debug('ip: {}, date: {}, count: {}. max_limit: {}'.format(ip, date, count, registrar_account_max))
        if has_account_max_limit and count > registrar_account_max:
            my_db.close()
            return False, {"msg": "Up to the maximum number of accounts created today", "code": 400}, 0
        #ip max register check
        this_ip_count = cursor.execute(sql['ip_count'].format(ip, date))
        if has_ip_max_limit and this_ip_count > ip_max_register_limit:
            my_db.close()
            return False, {"msg": "Your address no access authority", "code": 400}, 0
    except Exception as e:
        my_db.close()
        logger.error('db failed. ip: {}, error: {}'.format(ip, repr(e)))
        return False, {"msg": "db error", "code": 400}, 0
    my_db.close()
    return True, '', count

def store_new_account(data):
    # 数据库连接
    my_db = pymysql.connect(**db)
    cursor = my_db.cursor()

    #向数据库中插入新注册用户信息
    try:
        create_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(sql['insertData'].format(data['id'], data['name'], data['active_key'], data['ip'], create_time))
        my_db.commit()
    except Exception as e:
        my_db.rollback()
        logger.error('execute failed. data: {}, error: {}'.format(data, repr(e)))
    finally:
        my_db.close()

class FaucetHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-type, Accept, connection, User-Agent, Cookie, Authorization")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self):
        self.post()

    def post(self):
        auth = self.request.headers.get('authorization', '') 
        if auth not in auth_list.values():
            return self.write({'msg': 'no access authority!', 'code': '400'})
        
        #ip black check
        remote_ip = self.request.remote_ip
        logger.info("request ip: {}, ip_limit_list: {}".format(remote_ip, ip_limit_list))
        if remote_ip in ip_limit_list:
            return self.write({"msg": "no access authority", "code": 400})
        
        # request params check
        data = json.loads(self.request.body.decode("utf8"))
        account = data.get("account")
        status, msg, account_data = params_valid(account)
        if not status:
            logger.error('status:{}, msg: {}, account_data: {}'.format(status, msg, account_data))
            return self.write(msg)

        # check register count
        today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        status, msg, account_count = account_count_check(today, remote_ip)
        if not status:
            logger.error('status:{}, msg: {}, account_count: {}'.format(status, msg, account_count))
            return self.write(msg)
        
        #register account
        status, msg, userid = register_account(account_data)
        if not status:
            logger.error('status:{}, msg: {}, userid: {}'.format(status, msg, userid))
            return self.write(msg)

        # send reward
        status, msg = send_reward(account_count, userid)
        if not status:
            logger.error('status:{}, msg: {}, account_count: {}'.format(status, msg, account_count))
            return self.write(msg)
        
        #store new account data
        account_data['id'] = userid
        account_data['ip'] = remote_ip
        store_new_account(account_data)

        #return
        del account_data['ip']
        return self.write({'msg': 'Register successful! {}, {}'.format(account_data['name'], memo), 'data': {"account": account_data }, 'code': '200'})

def main():
    initialize()
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
