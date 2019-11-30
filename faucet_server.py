# -*- coding:utf-8 -*-

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
            print('[initalize] core asset: {}'.format(asset))
            asset_core_precision = asset['precision']

            #get_asset GAS --> core_exchange_rate
            body_relay = {
                "jsonrpc": "2.0",
                "method": "get_asset",
                "params": [asset_gas],
                "id":1
            }
            asset = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)['result']
            print('[initalize] gas asset: {}'.format(asset))
            core_exchange_rate = asset['options']['core_exchange_rate']
            gas_core_exchange_rate = round(core_exchange_rate['quote']['amount']/core_exchange_rate['base']['amount'])
            #reward_core = int(transfer[1]['fee']/(10**asset_core_precision) * transfer_operation_N)
            reward_gas = transfer[1]['fee'] * gas_core_exchange_rate * transfer_operation_N
            print('[initalize] gas_core_exchange_rate: {}, reward_gas: {}, reward_core: {}, transfer fee: {}'.format(gas_core_exchange_rate, reward_gas, reward_core, transfer))
    except Exception as e:
        print('[ERROR][init reward] {}'.format(repr(e)))
        push_message("faucet_server init reward error")

def init_db():
    my_db = pymysql.connect(**db)   #连接数据库并创建表
    cursor = my_db.cursor()
    try:
        cursor.execute(sql["createTable"])
        my_db.commit()
    except:
        push_message("faucet_server init db error")
        my_db.rollback()
    my_db.close()

#服务启动初始化
def initalize():
    init_db()
    init_reward()
    print('[initalize] ip_limit_list: {}'.format(ip_limit_list))
    print('[initalize] init done.')

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

def push_message(message, keys='[faucet]'):
    try:
        body_relay = {
            "jsonrpc": "2.0",
            "msgtype": "text",
            "text": {
                "content": keys + message
            },
            "id":1
        }
        response = json.loads(requests.post(faucet_alert_address, data = json.dumps(body_relay), headers = headers).text)
        print('[push_message] response: {}'.format(response))
    except Exception as e:
        print(repr(e))

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
        #print('>> list_account_balance:\n {}\n'.format(balances))
        for asset_balance in balances:
            #print('asset_balance: {}, type: {}, amount: {}'.format(asset_balance, type(asset_balance['amount']), asset_balance['amount']))
            if asset_balance['asset_id'] == asset_id:
                return int(asset_balance['amount'])
    except Exception as e:
        print(repr(e))
    return 0

def params_valid(account):
    name = account.get('name', '') #获取帐户名
    active_key = account.get('active_key', '') #获取active公钥
    owner_key = account.get('owner_key', '')   #获取owner公钥
    print('[params_valid] name: {}, active: {}, owner: {}'.format(name, active_key, owner_key)) 
    if not name:
        return False, {'msg': 'no name!', 'code': '400'}, {}
    if not is_cheap_name(name):
        return False, {'msg': 'account name {} is not cheap'.format(name), 'code': '400'}, {}
    if not active_key:
        return False, {'msg': 'no active key!', 'code': '400'}, {}
    if not owner_key:
        owner_key = active_key  #如果没有owner_key默认值为active_key
    return True, '', {'name': name, 'active_key': active_key, 'owner_key': owner_key}

def send_reward(core_count, account_to):
    is_return = False
    core_amount = get_account_asset_balance(register)

    #发送奖励core_asset
    if core_count <= reward_core_until_N:
        try: 
            if reward_core*(10**asset_core_precision) < core_amount:
                body_relay = {
                    "jsonrpc": "2.0",
                    "method": "transfer",
                    "params": [register, account_to, reward_core, asset_core, [memo, "false"], "true"],
                    "id":1
                }
                requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers)
            else:
                is_return = True
                push_message('register {} no {}'.format(register, asset_core))
        except Exception as e:
            print(repr(e))
            return False, {'msg': 'transfer failed!', 'data': repr(e), 'code': '400'}

    #发送奖励gas
    if not is_return:
        if reward_gas < core_amount * gas_core_exchange_rate:
            try:
                body_relay = {
                    "jsonrpc": "2.0",
                    "method": "update_collateral_for_gas",
                    "params": [register, account_to, reward_gas, "true"],
                    "id":1
                }
                requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers)
            except Exception as e:
                print(repr(e))
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
            return False, {'msg': 'register account {} failed. {}'.format(account['name'], error), 'code': '400'}, ''
    except Exception as e:
        print(repr(e))
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
        userid = account_info["result"]["id"]
    except Exception as e:
        print(repr(e))
        return False, {"msg": "obtain user id error!", "code": 400}, ''
    return True, '', userid

def account_count_check(ip, date):
    # 数据库连接
    my_db = pymysql.connect(**db)
    cursor = my_db.cursor()

    #today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    try:
        count = cursor.execute(sql['count'].format(date, date))
        if count % 20 == 0:
            print('{} already create {} account'.format(date, count))
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
        print(repr(e))
        my_db.rollback()
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
        auth = self.request.headers.get('authorization', '') #验证权限
        if auth not in auth_list.values():
            return self.write({'msg': 'no access authority!', 'code': '400'})
        
        #ip black check
        remote_ip = self.request.remote_ip
        print("ip:>>>>%s" % remote_ip)
        if remote_ip in ip_limit_list:
            return self.write({"msg": "no access authority", "code": 400})
        
        # request params check
        data = json.loads(self.request.body.decode("utf8"))
        account = data.get("account")
        status, msg, account_data = params_valid(account)
        if not status:
            print('[ERROR] {}'.format(msg))
            return self.write(msg)

        # check register count
        today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        status, msg, account_count = account_count_check(today, remote_ip)
        if not status:
            print('[ERROR] {}'.format(msg))
            return self.write(msg)
        
        #register account
        status, msg, userid = register_account(account_data)
        if not status:
            #print('[ERROR] {}'.format(msg))
            return self.write(msg)

        # send reward
        status, msg = send_reward(account_count, account_data['name'])
        if not status:
            print('[ERROR] {}'.format(msg))
            return self.write(msg)
        
        #store new account data
        account_data['id'] = userid
        account_data['ip'] = remote_ip
        store_new_account(account_data)

        #return
        del account_data['ip']
        return self.write({'msg': 'Regist successful! {}, {}'.format(account_data['name'], memo), 'data': {"account": account_data }, 'code': '200'})

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