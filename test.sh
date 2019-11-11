
#base_url="123.56.98.47:8061"
#echo $base_url
#curl http://${base_url}/api/v1/accounts -H "Content-Type:application/json" -H "authorization:YnVmZW5nQDIwMThidWZlbmc="  -X POST --data '{"account":{"name":"test1","owner_key":"COCOS8J2bZ2r96WKJcePL22975Qh94qrfZ8LsK7mkc44nsoJrDQmCao","referror":"","memo_key":"COCOS51EP3KzxW42gzsmmwMEqvejkHRohKkgZEfpktbWkN4uFDXMs2B","active_key":"COCOS51EP3KzxW42gzsmmwMEqvejkHRohKkgZEfpktbWkN4uFDXMs2B"}}'

base_url="test-faucet.cocosbcx.io"
echo $base_url
curl http://${base_url}/api/v1/accounts -H "Content-Type:application/json" -H "authorization:YnVmZW5nQDIwMThidWZlbmc="  -X POST --data '{"account":{"name":"test1","owner_key":"COCOS8J2bZ2r96WKJcePL22975Qh94qrfZ8LsK7mkc44nsoJrDQmCao","referror":"","memo_key":"COCOS51EP3KzxW42gzsmmwMEqvejkHRohKkgZEfpktbWkN4uFDXMs2B","active_key":"COCOS51EP3KzxW42gzsmmwMEqvejkHRohKkgZEfpktbWkN4uFDXMs2B"}}'

echo " "

