import sys
import random
import requests
import json
from time import sleep


def seller(host, price, getVol, address):

    sellTx = {
        'type': 'trade',
        'sender': address,
        'symbol': 'zsh/usdt',
        'price': price,
        'send': 'zsh',
        'sendVol': getVol,
        'get': 'usdt',
        'getVol': price*getVol,
        'comissionAmount':2
    }

    requests.post(host+'/transactions/new', json=sellTx)
    balances = json.loads(requests.post(host+'/wallet/getBalance', json={'address': address}).content)['BALACNES']
    remainBalance = [balance['balance'] for balance in balances if balance['token']=='ZSH'][0]

    return remainBalance


def buyer(host, price, getVol, address):

    buyTx = {
        'type': 'trade',
        'sender': address,
        'symbol': 'zsh/usdt',
        'price': price,
        'send': 'usdt',
        'sendVol': price*getVol,
        'get': 'zsh',
        'getVol': getVol,
        'comissionAmount':2
    }

    requests.post(host+'/transactions/new', json=buyTx)
    balances = json.loads(requests.post(host+'/wallet/getBalance', json={'address': address}).content)['BALACNES']
    remainBalance = [balance['balance'] for balance in balances if balance['token']=='USDT'][0]

    return remainBalance


if __name__ == '__main__':
    lst=sys.argv[1:]
    address = lst[0]
    host = lst[1]
    price = 10
    getVol = 0.1

    while True:
        # === Set buy order ===
        c = random.randrange(-5,10,1)/10
        price += c
        if price < 0.5:
            price = 10

        n = random.randrange(-10,10,1)/10
        getVol += n
        if getVol < 0 or getVol > 1:
            getVol = 0.1

        remainBalance = buyer(host, price, getVol, address)

        if remainBalance < 1:
            break

        sleep(2)

        # === Set sell order ===
        c = random.randrange(-5,10,1)/10
        price += c
        if price < 0.5:
            price = 10

        n = random.randrange(-10,10,1)/10
        getVol += n
        if getVol < 0 or getVol > 1:
            getVol = 1

        remainBalance = seller(host, price, getVol, address)

        if remainBalance < 1:
            break

        sleep(2)
