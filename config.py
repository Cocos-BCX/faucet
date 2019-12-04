# -*- coding:utf-8 -*-

#权限验证参数
auth_list = {
    'origon': 'YnVmZW5nQDIwMThidWZlbmc='
}

#命令行钱包地址
cli_wallet_url = "http://127.0.0.1:8048"
#cli_wallet_url = "http://172.17.25.154:8048"

#请求头
headers = {"content-type": "application/json"}

# test | prod
env = "prod"
g_hostname = "localhost"
g_ip = "127.0.0.1"

#注册帐户的注册人
# faucet1 1.2.18 faucet2 1.2.19 faucet3 1.2.20 faucet4 1.2.21
register = "nicotest"
register_id = "1.2.16" 

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
reward_core = 0.1
reward_core_until_N = 1000
transfer_operation_N = 2
reward_gas = reward_core * (10 ** asset_core_precision) * gas_core_exchange_rate * transfer_operation_N

#注册完成欢迎信息
memo = 'Welcome To COCOS Community!'

#每天创建账户最大数
has_account_max_limit = True
registrar_account_max = 10000

# ip 限制(每天)
has_ip_max_limit = True 
ip_max_register_limit = 20

#ip 黑名单
ip_limit_list = set()
#ip_limit_list.add("127.0.0.1")

# dingding
#test token: ddf5792a6a4ddc5117026dfc7f90b14e22584b7ecf72a66f4ddf45506fa076f7
access_token = "ddf5792a6a4ddc5117026dfc7f90b14e22584b7ecf72a66f4ddf45506fa076f7"
#faucet_alert_address = "https://oapi.dingtalk.com/robot/send?access_token=e9ccd60b531c8d12ea9fd984ebc2a53e770237e347c25cd1ef4d72c8ec0a5275"
faucet_alert_address = "https://oapi.dingtalk.com/robot/send?access_token=" + access_token



