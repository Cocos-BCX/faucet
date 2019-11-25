# -*- coding:utf-8 -*-

#权限验证参数
auth_list = {
    'origon': 'YnVmZW5nQDIwMThidWZlbmc='
}

#命令行钱包地址
#cli_wallet_url = "http://127.0.0.1:8047"
cli_wallet_url = "http://172.17.25.154:8048"

#请求头
headers = {"content-type": "application/json"}

#注册帐户的注册人
register = "nicotest"

#mysql数据库相关参数
db = { 
    'host': '172.17.25.150',
    'port': 3306,
    'user': 'faucet',
    'password': 'iyeQSG0j',
    'charset': 'utf8',
    'db': 'cocosbcx'
}

tables = { 
    'users': 'cocosUsers'
}

#数据库操作相关语句
sql = {
    'createTable': 'create table If Not Exists ' + tables['users'] + ' (id char(10), name varchar(32), pubkey char(128), ip char(32), create_time char(32))default charset=utf8',
    'insertData': "insert into " + tables['users'] + " (id, name, pubkey, ip, create_time) values('{}','{}','{}','{}','{}')",
    'count': "select * from " + tables['users'] + " where DATE_FORMAT(create_time, '%Y-%m-%d') between '{}' and '{}'",
    'ip_count': "select * from " + tables['users'] + " where ip='{}' and DATE_FORMAT(create_time, '%Y-%m-%d')='{}' "
}

#核心资产
asset_core = 'COCOS'
asset_core_precision = 5

#Gas
asset_gas = 'GAS'
gas_core_exchange_rate = 1

#发送奖励数量
reward_core = 10
reward_core_until_N = 100
transfer_operation_N = 2
reward_gas = reward_core * (10 ** asset_core_precision) * gas_core_exchange_rate * transfer_operation_N

#注册完成欢迎信息
memo = 'Welcome To COCOS Community!'

#每天创建账户最大数
has_account_max_limit = True
registrar_account_max = 3000

# ip 限制(每天)
has_ip_max_limit = True 
ip_max_register_limit = 500

#ip 黑名单
ip_limit_list = set()
#ip_limit_list.add("127.0.0.1")

# dingding
faucet_alert_address = "https://oapi.dingtalk.com/robot/send?access_token=e9ccd60b531c8d12ea9fd984ebc2a53e770237e347c25cd1ef4d72c8ec0a5275"