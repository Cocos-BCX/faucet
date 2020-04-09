# -*- coding:utf-8 -*-

import os
import json
import random
import pymysql
import requests
import datetime
import time
import socket
import tornado.ioloop, tornado.web, tornado.httpserver
import logging

from config import *
from utils import *
from threading import Thread
from tornado.options import define, options, parse_command_line

from PythonMiddleware.graphene import Graphene
from PythonMiddleware.instance import set_shared_graphene_instance
from pprint import pprint
from PythonMiddleware.account import Account
from PythonMiddleware.asset import Asset
from PythonMiddleware.storage import configStorage as config

define('port', default=server_port, type=int)

logger = Logging(console=False, level=logging.DEBUG).getLogger()

gph = Graphene(node=node_address, blocking=True)
set_shared_graphene_instance(gph)

def get_account(name):
    try:
        account = Account(name)
        return account
    except Exception as e:
        logger.error('name {}, error: {}'.format(name, repr(e)))
        return None

def create_account(name, owner_key, active_key, memo_key, registrar):
    try:
        response = gph.create_account(account_name=name, registrar=registrar,
                           owner_key=owner_key, active_key=active_key, memo_key=memo_key)
        logger.debug(response)
    except Exception as e:
        logger.error('name {}, error: {}'.format(name, repr(e)))
        return False
    return True

def transfer(from_account, to, amount, asset="1.3.0", memo=""):
    try:
        response = gph.transfer(to=to, amount=amount, asset=asset, memo=[memo,0], account=from_account)
        logger.debug(response)
    except Exception as e:
        logger.error('to {}, amount: {}, error: {}'.format(to, amount, repr(e)))
        return False
    return True

def update_collateral_for_gas(from_account, beneficiary, collateral):
    try:
        response = gph.update_collateral_for_gas(beneficiary=beneficiary, collateral=collateral,
                account=from_account)
        logger.debug(response)
    except Exception as e:
        logger.error('beneficiary {}, collateral: {}, error: {}'.format(beneficiary, collateral, repr(e)))
        return False
    return True

def get_account_balance(name, symbol):
    try:
        account = get_account(name)
        if account is None:
            return None
        else:
            balance = account.balance(symbol)
            return balance
    except Exception as e:
        logger.error('name {}, symbol {}, error: {}'.format(name, symbol, repr(e)))
        return None

def get_asset(symbol):
    try:
        asset = Asset(symbol)
        return asset
    except Exception as e:
        logger.error('symbol {}, error: {}'.format(symbol, repr(e)))
        return None

def init_wallet():
    try:
        if not gph.wallet.created():
            gph.newWallet(wallet_password)
        logger.info("wallet create status: {}".format(gph.wallet.created()))

        if gph.wallet.locked():
            gph.wallet.unlock(wallet_password)
        logger.info("wallet lock status: {}".format(gph.wallet.locked()))

        if gph.wallet.getPrivateKeyForPublicKey(register_public_key) is None:
            logger.info("import private key into wallet. public key: {}".format(register_public_key))
            gph.wallet.addPrivateKey(register_private_key)

        logger.info("account id: {}, public key: {}".format(
            gph.wallet.getAccountFromPublicKey(register_public_key), register_public_key))

        config["default_prefix"] = gph.rpc.chain_params["prefix"]
        config["default_account"] = register
    except Exception as e:
        print(repr(e))

def init_reward():
    global asset_core_precision, core_exchange_rate, reward_gas
    global gas_core_exchange_rate, register_id, asset_gas_precision

    try:
        properties = gph.rpc.get_object("2.0.0")
        transfer_fee = properties['parameters']['current_fees']['parameters'][0]
        if transfer_fee[0] == 0:
            logger.info("asset {}".format(asset_core))
            asset = get_asset(asset_core)
            asset_core_precision = asset['precision']
            logger.info("asset {} precision: {}".format(asset_core, asset_core_precision))

            logger.info("asset {}".format(asset_gas))
            asset = get_asset(asset_gas)
            asset_gas_precision = asset['precision']
            core_exchange_rate = asset['options']['core_exchange_rate']
            gas_core_exchange_rate = round(core_exchange_rate['quote']['amount']/core_exchange_rate['base']['amount'])
            logger.info("asset {} precision: {}, gas_exchange_rate: {}".format(asset_gas,
                asset_gas_precision, gas_core_exchange_rate))
            reward_gas = transfer_fee[1]['fee'] * gas_core_exchange_rate * transfer_operation_N

            logger.info("init register({}) account id".format(register))
            register_account = get_account(register)
            if register_account:
                register_id = register_account["id"]
            else:
                logger.error("get_account {} failed".format(register))
            logger.info('register:{}, id:{}, gas rate:{}, reward_gas:{}, reward_core:{}, transfer fee:{}'.format(
                register, register_id, gas_core_exchange_rate, reward_gas, reward_core, transfer_fee))
    except Exception as e:
        logger.error('init failed. error: {}'.format(repr(e)))
        push_message("init reward error")

def init_database():
    my_db = pymysql.connect(**db)
    cursor = my_db.cursor()
    try:
        cursor.execute(sql["create_table"])
        my_db.commit()
    except Exception as e:
        my_db.rollback()
        logger.warn('init failed. error: {}'.format(repr(e)))
    my_db.close()

def init_host_info():
    global g_hostname, g_ip
    try:
        g_hostname = socket.getfqdn(socket.gethostname())
        g_ip = socket.gethostbyname(g_hostname)
    except Exception as e:
        logger.warn('init host info. error: {}'.format(repr(e)))
    if 'HOST_NAME' in os.environ:
        g_hostname = os.environ['HOST_NAME']
    logger.info('hostname: {}, ip: {}'.format(g_hostname, g_ip))

def initialize():
    logger.info("init wallet")
    init_wallet()
    logger.info("init host info")
    init_host_info()
    logger.info("init database")
    init_database()
    logger.info("init reward")
    init_reward()
    logger.info('ip_limit_list: {}'.format(ip_limit_list))
    logger.info('init done.')

def push_message(message, labels=['faucet']):
    content = "[{}]{} {}, {}".format(env, str(labels), g_hostname, message)
    logger.debug('push content: {}'.format(content))
    return    # no need

    try:
        body_relay = {
            "jsonrpc": "2.0",
            "msgtype": "text",
            "text": { "content": content },
            "id":1
        }
        json.loads(requests.post(faucet_alert_address, data = json.dumps(body_relay), headers = headers).text)
    except Exception as e:
        logger.error('push error. {}'.format(repr(e)))

def params_valid(account):
    logger.info('account: {}'.format(account))
    name = account.get('name', '')
    active_key = account.get('active_key', '')
    owner_key = account.get('owner_key', '')
    if not name:
        return False, response_dict['bad_request'], {}
    if not is_cheap_name(name):
        return False, response_dict['not_cheap_account'], {}
    account_object = get_account(name)
    if account_object:
        return False, response_dict['account_registered'], {}

    if not active_key:
        return False, response_dict['bad_request'], {}
    if not owner_key:
        owner_key = active_key
    if not is_valid_name(name):
        msg = response_module(response_dict['bad_request']['code'], msg="account {} illegal".format(name))
        return False, msg, {}
    return True, '', {'name': name, 'active_key': active_key, 'owner_key': owner_key}

def send_reward_transfer(account_name, memo=memo):
    try:
        balance = get_account_balance(register, asset_core)
        if balance is None:
            return False
        core_amount = balance["amount"]
        logger.debug("{} balance: {} {}".format(register, core_amount, asset_core))
        if reward_core < core_amount:
            status = transfer(register, account_name, reward_core, asset_core, memo)
            if status:
                return True
            else:
                message = '{} {} failed.'.format(body_relay['method'], body_relay['params'])
                logger.warn(message)
        else:
            message = 'register {} no enough {}({}), reward need {}'.format(
                register, asset_core, core_amount/(10**asset_core_precision), reward_core)
            logger.warn(message)
    except Exception as e:
        message = 'register {} no {}, reward need {}'.format(register, asset_core, reward_core)
        logger.error('{}, error: {}'.format(message, repr(e)))
    return False

def send_reward_gas(account_id):
    try:
        balance = get_account_balance(register, asset_gas)
        if balance is None:
            return False
        gas_amount = balance["amount"]
        logger.debug("{} balance: {} {}".format(register, gas_amount, asset_gas))
        if reward_gas/(10**asset_gas_precision) < gas_amount:
            status = update_collateral_for_gas(register_id, account_id, reward_gas)
            if status:
                return True
            else:
                message = '{} {} failed.'.format(body_relay['method'], body_relay['params'])
                logger.warn(message)
        else:
            message = 'register {} no enough {}({}), collateral need {}'.format(
                register, asset_gas, gas_amount, reward_gas/(10**asset_gas_precision))
            logger.warn(message)
    except Exception as e:
        message = 'register {} no {}, reward need {}'.format(register, asset_gas, reward_gas/(10**asset_gas_precision))
        logger.error('{}, error: {}'.format(message, repr(e)))
    return False

def send_reward(core_count, account_id, account_name):
    if core_count < reward_core_until_N:
        transfer_status = send_reward_transfer(account_name)
    else:
        transfer_status = False
    collateral_status = send_reward_gas(account_id)
    if transfer_status or collateral_status:
        return 0  # success
    else:
        return 1  # failed

def register_account(account):
    try:
        status = create_account(account['name'], account['owner_key'], account['active_key'],
                                account['active_key'], register)
        if not status:
            return False, "register account failed", ''
    except Exception as e:
        logger.error('register account failed. account: {}, error: {}'.format(account, repr(e)))
        return False, response_dict['server_error'], ''
    try:
        account_id = ""
        account_info = get_account(account['name'])
        if account_info:
            account_id = account_info["id"]
    except Exception as e:
        logger.error('get account failed. account: {}, error: {}'.format(account, repr(e)))
    return True, "", account_id

def account_count_check(ip, date):
    my_db = pymysql.connect(**db)
    cursor = my_db.cursor()

    try:
        query_sql = "SELECT COUNT(id) FROM {} WHERE DATE_FORMAT(create_time, '%Y-%m-%d')='{}'".format(
            tables['users'], date)
        cursor.execute(query_sql)
        count = cursor.fetchone()[0]
        logger.debug('ip: {}, date: {}, count: {}. max_limit: {}'.format(ip, date, count, registrar_account_max))
        if has_account_max_limit and count > registrar_account_max:
            my_db.close()
            return False, response_dict['forbidden_today_max'], 0

        #ip max register check
        query_sql = "SELECT count(id) FROM {} WHERE ip='{}' AND DATE_FORMAT(create_time, '%Y-%m-%d')='{}'".format(
            tables['users'], ip, date)
        cursor.execute(query_sql)
        this_ip_count = cursor.fetchone()[0]

        logger.debug('this_ip_count: {}, ip_max_limit: {}'.format(this_ip_count, ip_max_register_limit))
        if has_ip_max_limit and this_ip_count > ip_max_register_limit:
            my_db.close()
            return False, response_dict['forbidden_ip_max'], 0
    except Exception as e:
        my_db.close()
        logger.error('db failed. ip: {}, error: {}'.format(ip, repr(e)))
        return False, response_dict['server_error'], 0
    my_db.close()
    return True, '', count

def store_new_account(data):
    my_db = pymysql.connect(**db)
    cursor = my_db.cursor()

    try:
        create_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(sql['create_account'].format(data['id'], data['name'], data['active_key'], data['ip'], create_time, register))
        my_db.commit()
    except Exception as e:
        my_db.rollback()
        logger.error('execute create_account sql failed. data: {}, error: {}'.format(data, repr(e)))
    finally:
        my_db.close()

def time_str_to_stamp(str_time):
    return int(time.mktime(time.strptime(str_time, "%Y-%m-%d %H:%M:%S")))

def reward():
    while True:
        my_db = pymysql.connect(**db)
        cursor = my_db.cursor()
        try:
            today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            query_sql = "SELECT COUNT(id) FROM {} WHERE status={} AND DATE_FORMAT(create_time, '%Y-%m-%d')='{}'".format(
                tables['users'], g_reward_status["SUCCESS"], today)
            cursor.execute(query_sql)
            count = cursor.fetchone()[0]

            str_time = (datetime.datetime.utcnow()-datetime.timedelta(seconds=6)).strftime("%Y-%m-%d %H:%M:%S")
            before_seconds_stamp = time_str_to_stamp(str_time)
            query_sql = "SELECT account_id, name, status, create_time FROM {} WHERE status < {} AND register='{}' AND DATE_FORMAT(create_time, '%Y-%m-%d')='{}'".format(
                tables['users'], g_reward_retry_count, register, today)
            cursor.execute(query_sql)
            results = cursor.fetchall()
            for result in results:
                account_name = result[1]
                status = result[2]
                create_time_stamp = time_str_to_stamp(result[3])
                account_info = get_account(account_name)
                if account_info and create_time_stamp < before_seconds_stamp:
                    account_id = account_info["id"]
                    reward_status = send_reward(count, account_id, account_name)
                    if account_id != result[0]:
                        logger.info('name: {}, status: {}, id: {} -> {}, reward_status: {}, create_time_stamp: {}, before seconds: {}'.format(
                        account_name, status, result[0], account_id, reward_status, create_time_stamp, before_seconds_stamp))
                    if reward_status != -1:
                        if reward_status == 0:
                            status = 4 #success
                        else:
                            status = status + 1 #failed +1
                        update_sql = "UPDATE {} SET STATUS='{}', account_id='{}' WHERE register='{}' AND name='{}' ".format(
                            tables['users'], status, account_id, register, account_name)
                        cursor.execute(update_sql)
                        my_db.commit()
        except Exception as e:
            my_db.rollback()
            logger.error('reward exception. {}'.format(repr(e)))
        finally:
            my_db.close()
        time.sleep(5)

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
            return self.write(response_dict['forbidden_no_auth'])

        #ip black check
        remote_ip = self.request.remote_ip
        real_ip = self.request.headers.get('X-Real-IP')
        forwarded_ips  = self.request.headers.get('X-Forwarded-For')
        ip_data = 'remote_ip: {}, real_ip: {}, forwarded-for: {}'.format(remote_ip, real_ip, forwarded_ips)
        logger.info("request ip_data: {}, ip_limit_list: {}".format(ip_data, ip_limit_list))
        if real_ip is None:
            real_ip = remote_ip
        if real_ip in ip_limit_list:
            return self.write(response_dict['forbidden_no_auth'])

        # request params check
        data = json.loads(self.request.body.decode("utf8"))
        account = data.get("account")
        status, msg, account_data = params_valid(account)
        if not status:
            logger.error('status:{}, msg: {}, account_data: {}'.format(status, msg, account_data))
            return self.write(msg)

        # check register count
        today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        status, msg, account_count = account_count_check(real_ip, today)
        logger.info('[account_count_check] real_ip: {}, today: {}, status: {}, msg: {}, account_count: {}'.format(
            real_ip, today, status, msg, account_count))
        if not status:
            return self.write(msg)

        status, msg, new_account_id = register_account(account_data)
        logger.info('status:{}, msg: {}, new_account_id: {}, account: {}'.format(status, msg, new_account_id, account_data))
        if not status:
            return self.write(msg)

        #store new account data
        account_data['id'] = new_account_id
        account_data['ip'] = real_ip
        store_new_account(account_data)

        #return
        del account_data['ip']
        return self.write(response_module(response_dict['ok']['code'], data={"account": account_data}, msg='Register successful! {}, {}'.format(account_data['name'], memo)))

def main():
    logger.info('-------------- faucet server start ----------------')
    initialize()

    reward_thread = Thread(target=reward)
    reward_thread.start()

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
