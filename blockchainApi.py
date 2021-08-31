import os
import re
import sys
import json

from textwrap import dedent
from time import time
from datetime import datetime, timezone
from uuid import uuid4
from sys import argv
from urllib.parse import urlparse
from flask import render_template, Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from config import Config
from blockchain import Blockchain

from createWallet import createWallet
from authoriseUser import authoriseUser
from signTransaction import signTransaction
from getCoinbase import getCoinbase
from syncPools import syncPools


app = Flask(__name__)
CORS(app)
nodeIdentifier = str(uuid4()).replace('-','')
blockchain = Blockchain()

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def index():
    # return jsonify({'MSG': 'Working'}), 200
    return render_template('index.html')

@app.route('/login.html', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/sign_up.html', methods=['GET'])
def sign_up():
    return render_template('sign_up.html')


@app.route('/mine', methods=['GET'])
def mine():
    lastBlock = blockchain.lastBlock
    lastProof = lastBlock['proof']
    proof = blockchain.pow(lastProof)

    blockchain.newTransaction(
        sender=Config().MINEADDR,
        timestamp = datetime.now(timezone.utc).timestamp(),
        recipient=blockchain.coinbase,
        sendAmount=1
    )

    # Match trade txs and route trades
    blockchain.transactTradeOrders()

    # Make Transactions
    blockHash = blockchain.hash(blockchain.chain[-1])
    for transaction in blockchain.current_transactions:
        if transaction['symbol'] == 'zsh' or transaction['contract'] == 'zsh':
            try:
                account = [account for account in blockchain.accounts if account.address == transaction['recipient']][0]
                account.makeTransaction(transaction['sendAmount'], blockHash)
            except:
                return jsonify({'MSG': f'Something went terribly wrong with transaction to recipient {transaction["recipient"]}'}), 400
        else:
            try:
                blockchain.makePoolTransaction(transaction['contract'], transaction['recipient'], transaction['sendAmount'])
            except:
                return jsonify({'MSG': f'Something went terribly wrong with pool transaction to recipient {transaction["recipient"]}'}), 400

    previousHash = blockchain.hash(lastBlock)
    block = blockchain.newBlock(proof, previousHash)


    syncStatus = syncPools(blockchain.current_transactions, blockchain.trade_transactions, blockchain.nodes)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previousHash'],
        'pool_syncing': syncStatus
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def newTx():

    # values = request.get_json()
    values = json.loads(request.data)
    required = Config().REQUIRED_TX_FIELDS
    if not all(k in values for k in required):
        return jsonify({'MSG':'Missing values'}), 400

    # Define orders type
    type = values['type']

    if type not in Config().REQUIRED_TX_TYPE:
        return jsonify({'MSG': 'Transaction type error! Provide "common" or "trade" transaction'}), 400

    if type == 'common':

        timestamp = datetime.now(timezone.utc).timestamp()
        symbol = values['symbol']
        contract = values['contract']
        sender = values['sender']
        recipient = values['recipient']
        sendAmount = values['sendAmount']
        comissionAmount = values['comissionAmount']
        get=None
        price=0.0
        tradeTxHash=None


        # Sign transaction
        transactionDict = {
            'timestamp': timestamp,
            'symbol': symbol,
            'contract': contract,
            'sender': sender,
            'recipient': recipient,
            'sendAmount': sendAmount,
            'recieveAmount': get,
            'price': price,
            'comissionAmount': float(comissionAmount),
            'tradeTxId':tradeTxHash
        }

        try:
            # Sign message
            signiture = signTransaction(str(transactionDict), blockchain.prkey)
        except:
            return jsonify({'MSG': 'Simple tx not accepted. Try to sign in first'}), 400

        try:
            # Proof expenditure amount
            account = [account for account in blockchain.accounts if account.address == sender][0]

            print('\n=====\nAccount address:\n',account.address,'\n')

            blockHash = blockchain.hash(blockchain.chain[-1])
            proofExpenditure = account.proofExpenditure(sendAmount, blockHash)

            if proofExpenditure == False:
                return jsonify({'MSG': 'Spend amount exceeds account balance'}), 400
        except:
            return jsonify({'MSG': 'Smth went terribly wrong while expenditure approve process'}), 400

        index, syncStatus = blockchain.newTransaction(type=type, timestamp=timestamp,txsig=signiture, symbol=symbol, contract=contract,\
                                        sender=sender, recipient=recipient,\
                                        sendAmount=sendAmount,\
                                        comissionAmount=comissionAmount)

    elif type == 'trade':

        timestamp = datetime.now(timezone.utc).timestamp()
        sender = values['sender']
        symbol = values['symbol']
        price = values['price']
        send = values['send']
        sendVol = values['sendVol']
        get = values['get']
        getVol = values['getVol']
        comissionAmount = values['comissionAmount']


        transactionDict = {
            'timestamp': timestamp,
            'sender': sender,
            'symbol': symbol,
            'price': price,
            'send': send,
            'sendVol': sendVol,
            'get': get,
            'getVol': getVol,
            'comissionAmount':float(comissionAmount)
        }

        try:
            # Sign message
            signiture = signTransaction(str(transactionDict), blockchain.prkey)
        except:
            return jsonify({'MSG': 'Trade tx not accepted. Try to sign in first'}), 400

        if send == 'zsh':
            try:
                # Proof expenditure amount
                account = [account for account in blockchain.accounts if account.address == sender][0]

                blockHash = blockchain.hash(blockchain.chain[-1])
                proofExpenditure = account.proofExpenditure(sendVol, blockHash)

                if proofExpenditure == False:
                    return jsonify({'MSG': 'Spend amount exceeds account balance'}), 400
            except:
                return jsonify({'MSG': 'Smth went terribly wrong while expenditure approve process'}), 400

        # Proof pool tokens expenditure
        else:
            try:
                proofPoolExpenditure = blockchain.proofPoolExpenditure(send, sender, sendVol)
                if proofPoolExpenditure == False:
                    return jsonify({'MSG': 'Spend amount exceeds account balance'}), 400
            except:
                return jsonify({'MSG': 'Smth went terribly wrong while pool expenditure approve process'}), 400


        index, syncStatus = blockchain.newTransaction(type=type, timestamp=timestamp,txsig=signiture, sender=sender, symbol=symbol,\
                        price=price, send=send, sendVol=sendVol, get=get,\
                        getVol=getVol, comissionAmount=comissionAmount)


    return jsonify({'MSG': syncStatus}), 201


@app.route('/transactions/sync', methods=['POST'])
def syncTxs():
    node = request.json['node']
    commonTxs = request.json['commonTxs']
    tradeTxs = request.json['tradeTxs']
    parsedUrl = urlparse(node)
    if parsedUrl.netloc in blockchain.nodes:
        blockchain.current_transactions = commonTxs
        blockchain.trade_transactions = tradeTxs
        print('Tx pool synced')
        return jsonify({'MSG': 'Tx pool synced'}), 200

    else:
        print('Node is not registered')
        return jsonify({'MSG': 'Node is not registered'}), 400


@app.route('/getTxPool', methods=['GET'])
def txPool():
    response = {
        'txPool': blockchain.current_transactions
    }

    return jsonify(response), 200


@app.route('/getTradeOrders', methods=['GET'])
def tradeOrders():
    response = {
        'tradeOrders': blockchain.trade_transactions
    }

    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def fullChain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200


@app.route('/chain/sync', methods=['POST'])
def syncCh():
    node = request.json['node']
    chain = request.json['chain']
    parsedUrl = urlparse(node)
    if parsedUrl.netloc in blockchain.nodes:
        blockchain.chain = chain
        if sys.getsizeof(blockchain.chain) >= Config().MAX_CHAIN_SIZE:
            with open(f'./chain/{int(datetime.now(timezone.utc).timestamp())}.json', 'w') as file:
                json.dump(blockchain.chain, file)
            blockchain.chain = [blockchain.chain[-1]]
        print('Chain synced')
        return jsonify({'MSG': 'Chain synced'}), 200

    else:
        print('Node is not registered')
        return jsonify({'MSG': 'Node is not registered'}), 400


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    print(values)

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        print(node)
        blockchain.registerNode(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolveConflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

@app.route('/nodes/getNodes', methods=['GET'])
def gNodes():
    nodes = blockchain.nodes
    nodesList = [node for node in nodes]
    return json.dumps({"nodes": nodesList})


@app.route('/nodes/getChainFilesAmount', methods=['GET'])
def getChFAm():
    chainFiles = os.listdir(os.path.join(Config().BASEDIR, 'chain'))
    chainFiles = [file for file in chainFiles if re.split(r'\.', file)[1] == 'json']
    return jsonify({'MSG': len(chainFiles)}), 200


@app.route('/nodes/sendChainData', methods=['POST'])
def sendChData():
    # Get files names list
    chainFiles = os.listdir(os.path.join(Config().BASEDIR, 'chain'))
    chainFiles = [file for file in chainFiles if re.split(r'\.', file)[1] == 'json']

    # Get files index
    fileNum = request.json['iter']

    # Send file
    return send_from_directory(
        Config().UPLOAD_FOLDER, chainFiles[fileNum], as_attachment=True
    )


@app.route('/wallet/new', methods=['POST'])
def newWallet():
    if request.method == 'POST':
        psw = json.loads(request.data)['password']
        blockHash = blockchain.hash(blockchain.chain[-1])
        if len(blockchain.accounts) == 0:
            address = createWallet(psw, blockHash, blockchain)
            blockchain.coinbase = address
        else:
            address = createWallet(psw, blockHash, blockchain)

        return jsonify({"ADDRESS": address}), 200


# ========!!!!!!! CHANGE COINBASE TO PARTICULAR ACCOUNT !!!!!!!========
@app.route('/wallet/login', methods=['POST'])
def loginUser():
    if request.method == 'POST':
        psw = json.loads(request.data)['password']
        pubKey, prKey, address = authoriseUser(psw, blockchain.accounts)
        if prKey == False:
            return jsonify({'MSG': 'Wrong password or there is no wallet'}), 400

        blockchain.prkey = prKey
        blockchain.pubKey = pubKey
        return jsonify({'MSG': True, 'ADDRESS': address}), 200


@app.route('/wallet/logout', methods=['GET'])
def logoutUser():
    blockchain.prkey = None
    blockchain.pubKey = None
    return jsonify({'MSG': True}), 200


@app.route('/wallet/getBalance', methods=['POST'])
def gBalance():
    address = json.loads(request.data)['address']
    balance = blockchain.getBalance(address)
    return jsonify({'BALACNES': [{'token': 'ZSH', 'balance':balance}]}), 200


@app.route('/pools/createPool', methods=['POST'])
def crPool():
    values = json.loads(request.data)
    creationResult = blockchain.createPool(values['name'], values['symbol'].upper())
    return jsonify({"MSG": creationResult}), 200


@app.route('/pools/getPools', methods=['GET'])
def gPools():
    pools = blockchain.getPools()
    return json.dumps({"MSG": pools}), 200



if __name__ == '__main__':
    # _, host, port = argv
    app.run(host= '0.0.0.0', port=5000)
