# 水龙头服务
提供http服务，免费创建链上账户功能，并初始化一些核心资产到新创建的账户。    

## 依赖  
* python版本：≥ python3.5 
* python依赖：
``` shell
    pip3 install tornado requests pymysql -i https://pypi.tuna.tsinghua.edu.cn/simple
```
* MySQL

## 文件说明：
* config.py：服务配置  
* faucet_server.py：服务主逻辑  

## 手动启动  
``` shell
    nohup python3 -u faucet_server.py >> faucet_server.log 2>&1 &   
```

## 服务对外默认端口
port: 8041  
