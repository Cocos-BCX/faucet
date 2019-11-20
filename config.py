# -*- coding:utf-8 -*-

#权限验证参数
auth_list = {
    'origon': 'YnVmZW5nQDIwMThidWZlbmc='
}

#命令行钱包地址
cli_wallet_url = "http://127.0.0.1:8048"

#请求头
headers = {"content-type": "application/json"}

#注册帐户的注册人
register = "nicotest"

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
    'users': 'cocosUsers_test'
}

#数据库操作相关语句
sql = {
    'createTable': 'create table ' + tables['users'] + ' (id char(10), name varchar(32), pubkey char(128), create_time char(32))default charset=utf8',
    'insertData': "insert into " + tables['users'] + " (id,name,pubkey,create_time) values('{}','{}','{}','{}')",
    'count': "select * from " + tables['users'] + " where DATE_FORMAT(create_time, '%Y-%m-%d') between '{}' and '{}'"
}

#发送奖励数量
reward_core = 10
reward_gas = 1000000

#核心资产
asset_core = 'COCOS'
asset_core_precision = 100000

#注册完成欢迎信息
memo = 'Welcome To COCOS Community!'

#每天创建账户最大数
has_account_max_limit = True
registrar_account_max = 3000
