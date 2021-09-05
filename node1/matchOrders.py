import re
import operator
from datetime import datetime, timezone
from operator import itemgetter

def matchOrders(orderPool, pools, symbol='zsh/usdt'):

    tradebleAsset = re.split(r'/', symbol)[0]

    buyOrders = []
    for i in range(len(orderPool)):
        if orderPool[i]['get'] == tradebleAsset:
            buyOrders.append(orderPool[i])

    if len(buyOrders) == 0:
        return [], []

    sellOrders = []
    for j in range(len(orderPool)):
        if orderPool[j]['send'] == tradebleAsset:
            sellOrders.append(orderPool[j])

    if len(sellOrders) == 0:
        return [], []

    buyOrders.sort(key=operator.itemgetter('price'), reverse=True)
    sellOrders.sort(key=operator.itemgetter('price'))

    commonTxs = []
    toRemove = []

    c = 0
    i = 0
    volFullfillment = None

    for n in range(max(len(buyOrders), len(sellOrders))):

        if buyOrders[i]['price'] >= sellOrders[c]['price']:

            if buyOrders[i]['getVol'] == sellOrders[c]['sendVol']:

                # Create common tx
                sellSendAmount = sellOrders[c]['sendVol']
                buySendAmount = sellSendAmount*sellOrders[c]['price']

                tradeSellTx = {
                    'timestamp': datetime.now(timezone.utc).timestamp(),
                    'symbol': sellOrders[c]['symbol'],
                    'contract': sellOrders[c]['send'],
                    'sender': sellOrders[c]['sender'],
                    'recipient': buyOrders[i]['sender'],
                    'sendAmount': sellSendAmount,
                    'recieveAmount': buySendAmount,
                    'price': sellOrders[c]['price'],
                    'comissionAmount': (sellOrders[c]['comissionAmount']/100)*(sellSendAmount/sellOrders[c]['sendVol']),
                    'tradeTxId': sellOrders[c]['tradeTxId']
                }

                tradeBuyTx = {
                    'timestamp': datetime.now(timezone.utc).timestamp(),
                    'symbol': sellOrders[c]['symbol'],
                    'contract': re.split(r'/', sellOrders[c]['symbol'])[1],
                    'sender': buyOrders[i]['sender'],
                    'recipient': sellOrders[c]['sender'],
                    'sendAmount': buySendAmount,
                    'recieveAmount': sellSendAmount,
                    'price': sellOrders[c]['price'],
                    'comissionAmount': (buyOrders[i]['comissionAmount']/100)*(buySendAmount/buyOrders[i]['sendVol']),
                    'tradeTxId': buyOrders[i]['tradeTxId']
                }

                sellOrders[c]['sendVol'] -= sellSendAmount
                sellOrders[c]['getVol'] -= buySendAmount
                buyOrders[i]['sendVol'] -= buySendAmount
                buyOrders[i]['getVol'] -= sellSendAmount

                commonTxs.append(tradeSellTx)
                commonTxs.append(tradeBuyTx)

                # Return remain buyers sendVol
                # ==== Turn it to the cancel transaction ====
                if buyOrders[i]['sendVol'] > 0:
                    pool = [pool for pool in pools if pool.symbol == re.split(r'/', sellOrders[c]['symbol'])[1].upper()][0]
                    pool.poolBalance -= buyOrders[i]['sendVol']
                    pool.accountsBalance[buyOrders[i]['sender']] += buyOrders[i]['sendVol']


                # Form Delete List
                toRemove.append(sellOrders[c]['tradeTxId'])
                toRemove.append(buyOrders[i]['tradeTxId'])

                if (c+1 >= len(sellOrders)) or (i+1 >= len(buyOrders)):
                    print(f'====\nI broke on c: {c} and i: {i}')
                    break
                else:
                    c+=1
                    i+=1



            elif buyOrders[i]['getVol'] > sellOrders[c]['sendVol']:
                # Fight Division by zero Bug
                if sellOrders[c]['sendVol'] <= 0.000001:
                    # Form Delete List
                    toRemove.append(sellOrders[c]['tradeTxId'])

                    if (c+1 >= len(sellOrders)) or (i+1 >= len(buyOrders)):
                        print(f'====\nI broke on c: {c} and i: {i}')
                        break
                    else:
                        c+=1

                else:
                    # Create common tx
                    sellSendAmount = sellOrders[c]['sendVol'] #min(sellOrders[c]['sendVol'], buyOrders[i]['getVol'])
                    buySendAmount = sellSendAmount*sellOrders[c]['price']

                    tradeSellTx = {
                        'timestamp': datetime.now(timezone.utc).timestamp(),
                        'symbol': sellOrders[c]['symbol'],
                        'contract': sellOrders[c]['send'],
                        'sender': sellOrders[c]['sender'],
                        'recipient': buyOrders[i]['sender'],
                        'sendAmount': sellSendAmount,
                        'recieveAmount': buySendAmount,
                        'price': sellOrders[c]['price'],
                        'comissionAmount': (sellOrders[c]['comissionAmount']/100)*(sellSendAmount/sellOrders[c]['sendVol']),
                        'tradeTxId': sellOrders[c]['tradeTxId']
                    }

                    tradeBuyTx = {
                        'timestamp': datetime.now(timezone.utc).timestamp(),
                        'symbol': sellOrders[c]['symbol'],
                        'contract': re.split(r'/', sellOrders[c]['symbol'])[1],
                        'sender': buyOrders[i]['sender'],
                        'recipient': sellOrders[c]['sender'],
                        'sendAmount': buySendAmount,
                        'recieveAmount': sellSendAmount,
                        'price': sellOrders[c]['price'],
                        'comissionAmount': (buyOrders[i]['comissionAmount']/100)*(buySendAmount/buyOrders[i]['sendVol']),
                        'tradeTxId': buyOrders[i]['tradeTxId']
                    }

                    sellOrders[c]['sendVol'] -= sellSendAmount
                    sellOrders[c]['getVol'] -= buySendAmount
                    buyOrders[i]['sendVol'] -= buySendAmount
                    buyOrders[i]['getVol'] -= sellSendAmount

                    commonTxs.append(tradeSellTx)
                    commonTxs.append(tradeBuyTx)


                    # Form Delete List
                    toRemove.append(sellOrders[c]['tradeTxId'])

                    if (c+1 >= len(sellOrders)) or (i+1 >= len(buyOrders)):
                        print(f'====\nI broke on c: {c} and i: {i}')
                        break
                    else:
                        c+=1


            elif buyOrders[i]['getVol'] < sellOrders[c]['sendVol']:

                # Fight Division by zero Bug
                if buyOrders[i]['getVol'] <= 0.000001:
                    # Form Delete List
                    toRemove.append(buyOrders[i]['tradeTxId'])

                    if (c+1 >= len(sellOrders)) or (i+1 >= len(buyOrders)):
                        print(f'====\nI broke on c: {c} and i: {i}')
                        break
                    else:
                        i+=1

                else:
                    # Create common tx
                    sellSendAmount = buyOrders[i]['getVol'] #min(sellOrders[c]['sendVol'], buyOrders[i]['getVol'])
                    buySendAmount = sellSendAmount*sellOrders[c]['price']

                    tradeSellTx = {
                        'timestamp': datetime.now(timezone.utc).timestamp(),
                        'symbol': sellOrders[c]['symbol'],
                        'contract': sellOrders[c]['send'],
                        'sender': sellOrders[c]['sender'],
                        'recipient': buyOrders[i]['sender'],
                        'sendAmount': sellSendAmount,
                        'recieveAmount': buySendAmount,
                        'price': sellOrders[c]['price'],
                        'comissionAmount': (sellOrders[c]['comissionAmount']/100)*(sellSendAmount/sellOrders[c]['sendVol']),
                        'tradeTxId': sellOrders[c]['tradeTxId']
                    }

                    tradeBuyTx = {
                        'timestamp': datetime.now(timezone.utc).timestamp(),
                        'symbol': sellOrders[c]['symbol'],
                        'contract': re.split(r'/', sellOrders[c]['symbol'])[1],
                        'sender': buyOrders[i]['sender'],
                        'recipient': sellOrders[c]['sender'],
                        'sendAmount': buySendAmount,
                        'recieveAmount': sellSendAmount,
                        'price': sellOrders[c]['price'],
                        'comissionAmount': (buyOrders[i]['comissionAmount']/100)*(buySendAmount/buyOrders[i]['sendVol']),
                        'tradeTxId': buyOrders[i]['tradeTxId']
                    }

                    sellOrders[c]['sendVol'] -= sellSendAmount
                    sellOrders[c]['getVol'] -= buySendAmount
                    buyOrders[i]['sendVol'] -= buySendAmount
                    buyOrders[i]['getVol'] -= sellSendAmount

                    commonTxs.append(tradeSellTx)
                    commonTxs.append(tradeBuyTx)


                    # Form Delete List
                    toRemove.append(buyOrders[i]['tradeTxId'])

                    if (c+1 >= len(sellOrders)) or (i+1 >= len(buyOrders)):
                        print(f'====\nI broke on c: {c} and i: {i}')
                        break
                    else:
                        i+=1

    return commonTxs, toRemove
