# python 3.6

from sys import argv, exit
import json
import websocket
import time
import settings
from nano25519 import ed25519_oop as ed25519
from jcnanolib import nano


def get_socket(server):
    try:
        ws = websocket.create_connection(server)
#        ws.settimeout(2.0)
        print(f"Connected to {server}")
        return ws
    except Exception as e:
        print(f"Unable to connect to {server}: {e}")
        return None


def setup(ws, account, api_key):
    try:
        ws.send(json.dumps({"action": "subscribe","topic": "confirmation","options": {"accounts": [account]}}))
        return True
    except Exception as e:
        print("Unable to send account")
        return False


def get_details(block):
    try:
        amount_raw = block["message"]["amount"]
        # block contents need another json format
#        contents = json.loads(block["message"]["block"])
        contents = block["message"]["block"]
        destination = contents["link_as_account"]
        type = contents["subtype"]

        return amount_raw, destination, type
    except Exception as e:
        print(f"Failed to get block info: {e}")
        return None, None


def convert_amount(raw):
    return str(float(raw)/1e30)

def process_pending(account, index_pos, api_key, wallet_seed):
    pending = nano.get_pending(str(account))
#    print("Process Pending: {}".format(pending))
    previous = nano.get_previous(str(account))
#    print(previous)
    if len(pending) > 0:
        pending = nano.get_pending(str(account))
       # try:
        if len(previous) == 0:
            print("Opening Account")
            hash, balance = nano.open_xrb(int(index_pos), account, wallet_seed, settings.api_key)
            previous = nano.get_previous(str(account))
        else:
            hash, balance = nano.receive_xrb(int(index_pos), account, wallet_seed, settings.api_key)
        print("Reply {} {}".format(hash, balance))
       # except:
       #     print("Error")
    else:
        return 0


def send_nano(xrb_address, raw_amount, index, api_key, dest_account):
    print("Sending Nano...")
    process_pending(xrb_address, index, api_key, settings.wallet_seed)

    current_balance = nano.get_account_balance(xrb_address)
    print(current_balance, raw_amount)

    if int(current_balance) > 0:
#TODO
#        try:
        return_block = nano.send_xrb(dest_account, int(raw_amount), xrb_address, int(index), settings.wallet_seed, settings.api_key)
        print(return_block)
        return(return_block)
#        except:
#            return('Error')


def main():
# examples for arguments:
# SERVER = 'ws://yapraiwallet.space/callsocket/'
# API_KEY = '123456'
# ACCOUNT = 'xrb_1dgt79j1bwjbhf9raywnwq51nut988c99dj7suf56yfpgxayaj9efw1hjdkb'

#    server = 'wss://yapraiwallet.space/call'
    server = 'wss://rainstorm.city/websocket'
    key = '12345'
    account = 'nano_3jwrszth46rk1mu7rmb4rhm54us8yg1gw3ipodftqtikf5yqdyr7471nsg1k'

    process_pending(settings.source_address, settings.index, settings.api_key, settings.wallet_seed)

    print(account)

    ws = get_socket(server)
    if not ws: exit(1)
    if not setup(ws, account, key): exit(1)
    time_last_msg = time.time()

    while 1:
        rec = ws.recv()
        time_last_msg = time.time()
        block = json.loads(rec)
        print(f"Block received! Printing contents after JSON format...\n\n{block}\n\n")
        if 'ack' in block:
            continue

        amount_raw, destination, type = get_details(block)


        if amount_raw is None or destination is None or type != 'send':
            continue

        amount_NANO = convert_amount(amount_raw)

        print(f"{amount_NANO} NANO going to {destination}")

        if destination not in settings.redlist:
            print('Sending fee refund')
            raw_amount = 10000000000000000000000000000
            send_nano(settings.source_address, raw_amount, settings.index, settings.api_key, destination)
        else:
            print('Redlist')

        print('Done')
if __name__ == "__main__":
    main()
