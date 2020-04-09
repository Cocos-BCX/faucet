# -*- coding:utf-8 -*-

import os
import json
import random
import pymysql
import requests
import datetime
import time
import socket
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

logger = Logging(console=True, level=logging.DEBUG).getLogger()

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
        print('\033[1;32;40m')
        print("{}\n".format(response))
        print('\033[0m')
        # logger.debug(response)
    except Exception as e:
        logger.error('name {}, error: {}'.format(name, repr(e)))
        return False
    return True

def transfer(from_account, to, amount, asset="1.3.0", memo=""):
    try:
        response = gph.transfer(to=to, amount=amount, asset=asset, memo=[memo,0], account=from_account)
        # logger.info(response)
        print('\033[1;32;40m')
        print("{}\n".format(response))
        print('\033[0m')
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


def transfer_test():
    init_wallet()
    to_accounts = ["1.2.8", "nicotest", "1.2.5"]
    # to_accounts = ["1.2.8", "1.2.5"]
    for to_account in to_accounts:
        transfer("nicotest", to_account, 10000)
        time.sleep(2)

if __name__ == '__main__':
    # main()
    transfer_test()
