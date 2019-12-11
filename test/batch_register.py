import json
import requests
import time

cli_wallet_url = "http://127.0.0.1:8048"
faucet_url = "http://127.0.0.1:8041/api/v1/accounts"

headers = {"content-type": "application/json"}
faucet_headers = {
        "content-type": "application/json",
        "authorization": "YnVmZW5nQDIwMThidWZlbmc="
    }

def batch_register_account_by_faucet(prefix='test-', size=10):
    req_data = {
        "jsonrpc": "2.0",
        "method": "suggest_brain_key",
        "params": [],
        "id":1
    }
    response = json.loads(requests.post(cli_wallet_url, data = json.dumps(req_data), headers = headers).text)
    assert 'error' not in response
    suggest_brain_key = response['result']
    print('suggest_brain_key: {}'.format(suggest_brain_key))
    brain_priv_key = suggest_brain_key['brain_priv_key']
    tokens = brain_priv_key.split()
    pub_key = suggest_brain_key['pub_key']
    success = 0
    failed = 0
    for token in tokens:
        for index in range(0, len(token)+size):
            account_name = '{}{}{}'.format(prefix, token.lower(), index)
            print('>> register_account {}'.format(account_name))
            req_data = {
                "account":{
                    "name": account_name,
                    "owner_key": pub_key,
                    "active_key": pub_key,
                    "id":1
                }
            }
            response = json.loads(requests.post(faucet_url, data = json.dumps(req_data), headers = faucet_headers).text)
            if response['code'] != 200:
                failed = failed + 1
                print(response)
            else:
                success = success + 1
    print('register account success {}, failed: {}'.format(success, failed))

# suggest_brain_key: {
# 'wif_priv_key': '5JbzD2GAVFRTEV7HsAdXqZ41DjUZHzTrfGgz1VwQtnj2kzyxoBJ', 
# 'brain_priv_key': 'PLUTEAL REFUEL UNCLING ROUPER AFEARED SWICK ROUTHIE RUSHY DOWNWAY REWEAVE TRYPA TORCH BORISM SNAKING QUIPPY TATTLE', 
# 'address_info': 'COCOSFnH7NNbyHSuW1J1XJZNJRdQ4MVe6fPqD7', 
# 'pub_key': 'COCOS7S6dg93FM1DG7ts9TZJcLYnoRY9VT9247xieEc2kuRBN7igrh1'
# }
def batch_register_account_by_faucet2(prefix='test-faucet', size=5):
    pub_key = "COCOS7S6dg93FM1DG7ts9TZJcLYnoRY9VT9247xieEc2kuRBN7igrh1"
    success = 0
    failed = 0
    for index in range(0, len(prefix)+size):
        account_name = '{}{}'.format(prefix.lower(), index)
        print('>> register_account {}'.format(account_name))
        req_data = {
            "account":{
                "name": account_name,
                "owner_key": pub_key,
                "active_key": pub_key,
                "id":1
            }
        }
        response = json.loads(requests.post(faucet_url, data = json.dumps(req_data), headers = faucet_headers).text)
        print(response)
        if response['code'] != 200:
            failed = failed + 1
        else:
            success = success + 1
        time.sleep(0.3)
    print('register account success {}, failed: {}'.format(success, failed))

def main(is_use_cli_wallet=False, prefix='test-faucet', size=3):
    if is_use_cli_wallet:
        batch_register_account_by_faucet(size=size)
    else:
        batch_register_account_by_faucet2(prefix=prefix, size=size)

if __name__ == '__main__':
    main()
