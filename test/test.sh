# docker cp faucet_server.py faucet:/app/faucet_server.py && docker cp utils.py  faucet:/app/utils.py 
# docker restart faucet

base_url="127.0.0.1:8041"  # local test
#base_url="faucet.cocosbcx.net" # prod
#base_url="faucet.cocosbcx.net" # testnet
echo $base_url
curl http://${base_url}/api/v1/accounts -H "Content-Type:application/json" -H "authorization:YnVmZW5nQDIwMThidWZlbmc="  -X POST --data '{"account":{"name":"test-faucet36","owner_key":"COCOS8J2bZ2r96WKJcePL22975Qh94qrfZ8LsK7mkc44nsoJrDQmCao","active_key":"COCOS51EP3KzxW42gzsmmwMEqvejkHRohKkgZEfpktbWkN4uFDXMs2B"}}'

echo " "

