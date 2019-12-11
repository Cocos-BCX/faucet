
ps -ef | grep "faucet_server" | grep -v "grep" | awk '{print $2}' | xargs kill -9

sleep 2

nohup python3 faucet_server.py >> logs/console.log 2>&1 &

