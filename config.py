# -*- coding:utf-8 -*-

#权限验证参数
auth_list = {
    'origon': 'YnVmZW5nQDIwMThidWZlbmc='
}

#命令行钱包地址
cli_wallet_url = "http://0.0.0.0:8048"

#请求头
headers = {"content-type": "application/json"}

#注册帐户的注册人
registrar = "nicotest"

#mysql数据库相关参数
db = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'charset': 'utf8',
    'db': 'cocosbcx'

}

#数据库操作相关语句
sql = {
    'createTable': 'create table cocosUsers(id char(10), name varchar(32), pubkey char(128), create_time char(32))default charset=utf8',
    'insertData': "insert into cocosUsers(id,name,pubkey,create_time) values('{}','{}','{}','{}')"
}

#发送奖励数量
reward = 100000

#核心资产
asset_core = 'COCOS'

#注册完成欢迎信息
memo = 'Welcome To COCOS Community!'
