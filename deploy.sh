#!/bin/bash
docker login --username=北京_趣块远扬 registry-vpc.cn-beijing.aliyuncs.com -pckadmin123123
docker pull registry-vpc.cn-beijing.aliyuncs.com/ck_chain/faucet
docker run -itd --name faucet registry-vpc.cn-beijing.aliyuncs.com/ck_chain/faucet
if [ ! -d /mnt/new_faucet  ];then
mkdir -p /mnt/faucet/logs
fi
cd /mnt/faucet;
docker cp faucet:/app/config.py ./
docker rm -f faucet
docker run -itd --name faucet -v $PWD/config.py:/app/config.py -v $PWD/logs:/app/logs -p 8041:8041  registry-vpc.cn-beijing.aliyuncs.com/ck_chain/faucet
