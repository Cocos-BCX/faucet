# -*- coding:utf-8 -*-

auth_list = {
    'origon': 'YnVmZW5nQDIwMThidWZlbmc='
}

server_port = 8041

node_address = "wss://api.cocosbcx.net"
wallet_password = "123456"

headers = {"content-type": "application/json"}

# testnet | prod
env = "prod"

g_hostname = "localhost"
g_ip = "127.0.0.1"

register = "register-test1"
register_id = "1.2.18"
register_private_key = "5J2SChqadMor9VC2k9NT4Rskfdaslqjabfjafhokna"
register_public_key = "COCOS56dTnfGpuPoWACnYj65dahcXMpTrNQkV3hHALfsaAnpJl5mXsa"

#mysql数据库相关参数
db = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'charset': 'utf8',
    'db': 'cocosbcx'
}

tables = {
    'users': 'cocosUsers'
}

#数据库操作相关语句
sql = {
    'create_table': 'CREATE TABLE IF NOT EXISTS ' + tables['users'] + ' (\
        `id` int(11) NOT NULL AUTO_INCREMENT, \
        `account_id` varchar(32), \
        `name` varchar(32), \
        `pubkey` char(128), \
        `ip` char(32), \
        `create_time` char(32), \
        `status` TINYINT DEFAULT 0, \
        `register` varchar(32) DEFAULT NULL, \
        PRIMARY KEY (`id`))ENGINE=InnoDB auto_increment=1 DEFAULT CHARSET=utf8;',
    'create_account': "INSERT INTO " + tables['users'] + " (account_id, name, pubkey, ip, create_time, register) \
            VALUES('{}','{}','{}','{}','{}','{}')"
}

#core asset
asset_core = 'COCOS'
asset_core_precision = 5

#GAS asset
asset_gas = 'GAS'
asset_gas_precision = 5
gas_core_exchange_rate = 1

#发送奖励数量
reward_core = 0.1
reward_core_until_N = 1000
transfer_operation_N = 6
reward_gas = 20000

#注册完成欢迎信息
memo = 'Welcome To COCOS Community!'

#每天创建账户最大数
has_account_max_limit = True
registrar_account_max = 10000

# ip 限制(每天)
has_ip_max_limit = True
ip_max_register_limit = 200

#ip 黑名单
ip_limit_list = set()
#ip_limit_list.add("127.0.0.1")

# ding
access_token = "ddf5792a6a4ddc5117026dfc7f90b14e22584b7ecf72a66f4ddf45506fa076f7"
faucet_alert_address = "https://oapi.dingtalk.com/robot/send?access_token=" + access_token
