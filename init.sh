#!/bin/bash
if [ ! -d logs ];then
mkdir logs
fi
nohup python3 -u faucet_server.py >> logs/faucet_server.log 2>&1 & 
tail -f logs/faucet_server.log
