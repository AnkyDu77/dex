import re
from datetime import datetime, timezone


def transactTrades(mathchedOrders, ordersList):

    commonTxs = []
    # Get matched orders
    txDir = {}

    # ====== PROBLEM IS HERE!!!!! =======
    # WE GOT SAME ORDERS IN txTempLst. IT HAS TO BE DIFFERENT!

    for i in range(len(mathchedOrders)):
        tempLst = [mathchedOrders[i][0][-1], mathchedOrders[i][1][-1]]
        txTempLst=[order for order in ordersList if order['tradeTxId'] in tempLst]

        print(f'\n=====\ntxTempLst {i}: {txTempLst}\n\n')

        txDir[f'tx_{i}'] = txTempLst

    # Calculate txs amount
    txKeys = list(txDir.keys())
    print(f'\n=====\ntxKeys: {txKeys}\n\n')
    for j in range(len(txKeys)):
    # for k in txKeys:
        print(f'\n=====\nj: {j}\n\n')
        print(f'\n=====\ntxKeys[j]: {txKeys[j]}\n\n')
        tradeTxs = txDir[txKeys[j]]
        # tradeTxs = txDir[k]

        print(f'\n=====\ntradeTxs: {tradeTxs}\n\n')

        symbolSplitted = re.split(r'/', tradeTxs[0]['symbol'])[0]

        if tradeTxs[0]['send'] == symbolSplitted:

            tradePrice = tradeTxs[0]['price']

            print(f'\n=====\ntradePrice: {tradePrice}\n\n')

            seller = tradeTxs[0]

            print(f'\n=====\nSeller: {seller}\n\n')


            sellerComission = tradeTxs[0]['comissionAmount']
            sellerIdHash = tradeTxs[0]['tradeTxId']
            buyer = tradeTxs[1]
            buyerComission = tradeTxs[1]['comissionAmount']
            buyerIdHash = tradeTxs[1]['tradeTxId']

            sellSendAddress = seller['sender']
            sellRecieveAddress = buyer['sender']
            sellSendToken = seller['send']
            sellSendAmount = min(seller['sendVol'], buyer['getVol'])
            sellComissions = (sellerComission/100)*(sellSendAmount/seller['sendVol'])

            buySendAddress = buyer['sender']
            buyRecieveAddress = seller['sender']
            buySendToken = seller['get']
            buySendAmount = sellSendAmount*tradePrice
            buyComissions = (buyerComission/100)*(buySendAmount/buyer['sendVol'])

            tradeSellTx = {
                'timestamp': datetime.now(timezone.utc).timestamp(),
                'symbol': seller['symbol'],
                'contract': symbolSplitted,
                'sender': sellSendAddress,
                'recipient': buySendAddress,
                'sendAmount': sellSendAmount,
                'recieveAmount': buySendAmount,
                'price': tradePrice,
                'comissionAmount': sellComissions,
                'tradeTxId': sellerIdHash
            }





            tradeBuyTx = {
                'timestamp': datetime.now(timezone.utc).timestamp(),
                'symbol': seller['symbol'],
                'contract': re.split(r'/', seller['symbol'])[1],
                'sender': buySendAddress,
                'recipient': sellSendAddress,
                'sendAmount': buySendAmount,
                'recieveAmount': sellSendAmount,
                'price': tradePrice,
                'comissionAmount': buyComissions,
                'tradeTxId': buyerIdHash
            }


            # !!!!!!!!!!!!!! ATTENTION !!!!!!!!!!!!!!
            # Decrease order vols; Fill (aka delete from trade pool) order if vols == 0
            # print(f'\n=====\ntxDir 0 sendVol name:{txDir[txKeys[j]]}\ntxDir 0 sendVol: {txDir[txKeys[j]][0]["sendVol"]}\n\n')
            txDir[txKeys[j]][0]['sendVol'] -= sellSendAmount
            # print(f'\n=====\ntxDir 0 sendVol name:{txDir[txKeys[j]]}\ntxDir 0 sendVol: {txDir[txKeys[j]][0]["sendVol"]}\n\n\n')
            txDir[txKeys[j]][0]['getVol'] -= buySendAmount
            # if txDir[txKeys[j]][0]['getVol']==0 or txDir[txKeys[j]][0]['getVol']<0.000099:
            #     ordersList.remove(txDir[txKeys[j]][0])
                # txDir[txKeys[j]].remove(txDir[txKeys[j]][0])






            # print(f'\n=====\ntxDir 1 sendVol name:{txDir[txKeys[j]]}\ntxDir 1 sendVol: {txDir[txKeys[j]][0]["sendVol"]}\n\n')
            txDir[txKeys[j]][1]['sendVol'] -= buySendAmount
            # print(f'\n=====\ntxDir 1 sendVol name:{txDir[txKeys[j]]}\ntxDir 1 sendVol: {txDir[txKeys[j]][0]["sendVol"]}\n\n\n')
            txDir[txKeys[j]][1]['getVol'] -= sellSendAmount
            # if txDir[txKeys[j]][1]['getVol']==0 or txDir[txKeys[j]][1]['getVol']<0.000099:
            #     ordersList.remove(txDir[txKeys[j]][1])
                # txDir[txKeys[j]].remove(txDir[txKeys[j]][1])


        elif tradeTxs[0]['get'] == symbolSplitted:

            tradePrice = tradeTxs[0]['price']

            seller = tradeTxs[1]
            sellerComission = tradeTxs[1]['comissionAmount']
            sellerIdHash = tradeTxs[1]['tradeTxId']
            buyer = tradeTxs[0]
            buyerComission = tradeTxs[0]['comissionAmount']
            buyerIdHash = tradeTxs[0]['tradeTxId']

            sellSendAddress = seller['sender']
            sellRecieveAddress = buyer['sender']
            sellSendToken = seller['send']
            sellSendAmount = min(seller['sendVol'], buyer['getVol'])
            sellComissions = (sellerComission/100)*(sellSendAmount/seller['sendVol'])

            buySendAddress = buyer['sender']
            buyRecieveAddress = seller['sender']
            buySendToken = seller['get']
            buySendAmount = sellSendAmount*tradePrice
            buyComissions = (buyerComission/100)*(buySendAmount/buyer['sendVol'])




            tradeSellTx = {
                'timestamp': datetime.now(timezone.utc).timestamp(),
                'symbol': seller['symbol'],
                'contract': symbolSplitted,
                'sender': sellSendAddress,
                'recipient': buySendAddress,
                'sendAmount': sellSendAmount,
                'recieveAmount': buySendAmount,
                'price': tradePrice,
                'comissionAmount': sellComissions,
                'tradeTxId': sellerIdHash
            }



            tradeBuyTx = {
                'timestamp': datetime.now(timezone.utc).timestamp(),
                'symbol': seller['symbol'],
                'contract': re.split(r'/', seller['symbol'])[1],
                'sender': buySendAddress,
                'recipient': sellSendAddress,
                'sendAmount': buySendAmount,
                'recieveAmount': sellSendAmount,
                'price': tradePrice,
                'comissionAmount': buyComissions,
                'tradeTxId': buyerIdHash
            }


            # Decrease order vols; Fill (aka delete from trade pool) order if vols == 0
            txDir[txKeys[j]][1]['sendVol'] -= sellSendAmount
            txDir[txKeys[j]][1]['getVol'] -= buySendAmount

            txDir[txKeys[j]][0]['sendVol'] -= buySendAmount
            txDir[txKeys[j]][0]['getVol'] -= sellSendAmount


        # Form tx and send it to common pool
        commonTxs.append(tradeSellTx)
        commonTxs.append(tradeBuyTx)

    return txDir, commonTxs
