import re
from datetime import datetime, timezone


def transactTrades(mathchedOrders, ordersList):

    commonTxs = []
    # Get matched orders
    txDir = {}
    for i in range(len(mathchedOrders)):
        tempLst = [mathchedOrders[i][0][0], mathchedOrders[i][1][0]]
        txTempLst=[order for order in ordersList if order['sender'] in tempLst]
        txDir[f'tx_{i}'] = txTempLst

    # Calculate txs amount
    txKeys = list(txDir.keys())
    for j in range(len(txKeys)):
        tradeTxs = txDir[txKeys[j]]

        symbolSplitted = re.split(r'/', tradeTxs[0]['symbol'])[0]

        if tradeTxs[0]['send'] == symbolSplitted:

            tradePrice = tradeTxs[0]['price']

            seller = tradeTxs[0]
            sellerComission = tradeTxs[0]['comissionAmount']
            sellerIdHash = tradeTxs[0]['tradeTxId']
            buyer = tradeTxs[1]
            buyerComission = tradeTxs[1]['comissionAmount']
            buyerIdHash = tradeTxs[1]['tradeTxId']

            sellSendAddress = seller['sender']
            sellRecieveAddress = buyer['sender']
            sellSendToken = seller['send']
            sellSendAmount = min(seller['sendVol'], buyer['getVol'])
            sellComissions = sellerComission*(sellSendAmount/seller['sendVol'])

            buySendAddress = buyer['sender']
            buyRecieveAddress = seller['sender']
            buySendToken = seller['get']
            buySendAmount = sellSendAmount*tradePrice
            buyComissions = buyerComission*(buySendAmount/buyer['sendVol'])

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
            txDir[txKeys[j]][0]['sendVol'] -= sellSendAmount
            txDir[txKeys[j]][0]['getVol'] -= buySendAmount

            txDir[txKeys[j]][1]['sendVol'] -= buySendAmount
            txDir[txKeys[j]][1]['getVol'] -= sellSendAmount



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
            sellComissions = sellerComission*(sellSendAmount/seller['sendVol'])

            buySendAddress = buyer['sender']
            buyRecieveAddress = seller['sender']
            buySendToken = seller['get']
            buySendAmount = sellSendAmount*tradePrice
            buyComissions = buyerComission*(buySendAmount/buyer['sendVol'])




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
