
base_url="127.0.0.1:8041"  # local test
echo $base_url
curl http://${base_url}/api/v1/accounts -H "Content-Type:application/json" -H "authorization:YnVmZW5nQDIwMThidWZlbmc="  -X POST --data '{"account":{"name":"test-faucet1","owner_key":"COCOS7S6dg93FM1DG7ts9TZJcLYnoRY9VT9247xieEc2kuRBN7igrh1","active_key":"COCOS7S6dg93FM1DG7ts9TZJcLYnoRY9VT9247xieEc2kuRBN7igrh1"}}'

echo " "

