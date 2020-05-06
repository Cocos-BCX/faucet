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
* utils.py: 常用工具，主要是log
* faucet_server.py：水龙头服务主逻辑  

## 服务启动  
``` shell
    nohup python3 faucet_server.py >> faucet_server.log 2>&1 &   
```

## 服务停止
``` shell  
 ps -ef | grep "faucet_server" | grep -v "grep" | awk '{print $2}' | xargs kill -9
```  

## 服务接口信息  
* port: 8041  
* http request: POST    
* route: /api/v1/accounts  
* 参数:  
    name: string   # 注册帐户名  (必须，水龙头不提供高级账户注册，name包含至少一个横杠、数字或者不含元音字母)  
    active_key: string # active公钥  (必须)  
    owner_key: string    #owner公钥 (非必须，如果没有, owner_key = active_key)  
* 请求返回格式：  

``` json  
    {"code": int, "data": object, "msg": string} 
```
* code说明：  

``` text  
    200     -- 请求成功  
    400001  --  请求参数非法  
    400002  --  账户名不是便宜账户  
    400003  --  账户名已存在   
    401001  --  没有权限  
    401002  --  今日你创建的账户已达最大限制  
    401003  --  今日账户创建已达最大限制  
    500     --  内部服务错误  
```
