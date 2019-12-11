import json
import requests
import time

cli_wallet_url = "http://127.0.0.1:8048"
faucet_url = "http://127.0.0.1:8043/api/v1/accounts"

headers = {"content-type": "application/json"}
faucet_headers = {
        "content-type": "application/json",
        "authorization": "YnVmZW5nQDIwMThidWZlbmc="
    }

# suggest_brain_key: {
# 'wif_priv_key': '5JbzD2GAVFRTEV7HsAdXqZ41DjUZHzTrfGgz1VwQtnj2kzyxoBJ', 
# 'brain_priv_key': 'PLUTEAL REFUEL UNCLING ROUPER AFEARED SWICK ROUTHIE RUSHY DOWNWAY REWEAVE TRYPA TORCH BORISM SNAKING QUIPPY TATTLE', 
# 'address_info': 'COCOSFnH7NNbyHSuW1J1XJZNJRdQ4MVe6fPqD7', 
# 'pub_key': 'COCOS7S6dg93FM1DG7ts9TZJcLYnoRY9VT9247xieEc2kuRBN7igrh1'
# }
def batch_register_account_by_faucet(name):
    pub_key = "COCOS7S6dg93FM1DG7ts9TZJcLYnoRY9VT9247xieEc2kuRBN7igrh1"
    print('>> register_account {}'.format(name))
    req_data = {
        "account":{
            "name": name,
            "owner_key": pub_key,
            "active_key": pub_key,
            "id":1
        }
    }
    response = json.loads(requests.post(faucet_url, data = json.dumps(req_data), headers = faucet_headers).text)
    print(response)
    if response['code'] != 200:
        return False
    return True

def main():
    tokens = ["abc", "abc12", "12def", "mytest1", "mytest-1", "1-test", "mytest.1", "my12test", "my-test", "my.1test", "1.233", "a.bcd.ef", "aaaaaaaaaaaaaaaaaaaaaaaaffffffffffffffffffffffffffffffffffffffffffff.fffffjjjjjjjjjjjjjjjjjzzzzzzzzzzzz", "123455", "1239900ye.abdeeeeee", "1000", "test-faucet100", "test-hello", "test-ab", "test-account-faucet-111", "test12=abjda", "test123", "test1345"]
    valid_names = []
    for token in tokens:
        if not batch_register_account_by_faucet(token):
            valid_names.append(token)
    print('valid name: {}'.format(valid_names))

if __name__ == '__main__':
    main()
