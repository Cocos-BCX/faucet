# 水龙头服务  
提供http服务，免费创建链上账户功能，并初始化一些核心资产和GAS到新创建的账户。    

## 依赖  
* python版本：≥ python3.5 
* python依赖：  
``` shell
    pip3 install tornado requests pymysql -i https://pypi.tuna.tsinghua.edu.cn/simple
```

* MySQL

## 文件说明：
* config.py：服务配置  
* utils.pu: 常用工具，主要是log
* faucet_server.py：水龙头服务主逻辑  

## 手动启动  
``` shell
    nohup python3 faucet_server.py >> faucet_server.log 2>&1 &   
```

## 服务接口信息  
* port: 8041  
* http request: POST    
* route: /api/v1/accounts  
* params:  
    name: string   # 注册帐户名  (必须，水龙头不提供高级账户注册，name包含至少一个横杠、数字或者不含元音字母)  
    active_key: string # active公钥  (必须)  
    owner_key: string    #owner公钥 (非必须，如果没有, owner_key = active_key)  
  
