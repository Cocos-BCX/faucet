
base_url="127.0.0.1:8041"
echo $base_url
curl http://${base_url}/api/v1/accounts -H "Content-Type:application/json" -H "authorization:YnVmZW5nQDIwMThidWZlbmc="  -X POST --data '{"account":{"name":"test-faucet33","owner_key":"COCOS8J2bZ2r96WKJcePL22975Qh94qrfZ8LsK7mkc44nsoJrDQmCao","active_key":"COCOS51EP3KzxW42gzsmmwMEqvejkHRohKkgZEfpktbWkN4uFDXMs2B"}}'

echo " "

