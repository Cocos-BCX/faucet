import json
import requests

cli_wallet_url = "http://127.0.0.1:8048"
faucet_url = "http://127.0.0.1:8041/api/v1/accounts"

headers = {"content-type": "application/json"}
faucet_headers = {
        "content-type": "application/json",
        "authorization": "YnVmZW5nQDIwMThidWZlbmc="
    }

def batch_register_account_by_faucet(size=10):
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
            account_name = 'test-{}{}'.format(token.lower(), index)
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

batch_register_account_by_faucet()
