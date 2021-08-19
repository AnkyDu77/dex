import os
import re
import json

from textwrap import dedent
from time import time
from uuid import uuid4
from sys import argv
from flask import Flask, jsonify, request, send_from_directory

from config import Config
from blockchain import Blockchain

from createWallet import createWallet
from authoriseUser import authoriseUser

app = Flask(__name__)
nodeIdentifier = str(uuid4()).replace('-','')
blockchain = Blockchain()

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def index():
    return jsonify({'MSG': 'Working'}), 200


@app.route('/mine', methods=['GET'])
def mine():
    lastBlock = blockchain.lastBlock
    lastProof = lastBlock['proof']
    proof = blockchain.pow(lastProof)

    blockchain.newTransaction(
        sender="0",
        recipient=nodeIdentifier,
        sendAmount=1
    )

    previousHash = blockchain.hash(lastBlock)
    block = blockchain.newBlock(proof, previousHash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previousHash']
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def newTx():

    values = request.get_json()
    required = Config().REQUIRED_TX_FIELDS
    if not all(k in values for k in required):
        return jsonify({'MSG':'Missing values'}), 400

    # Define orders type
    type = values['type']
    print(type)

    if type not in Config().REQUIRED_TX_TYPE:
        return jsonify({'MSG': 'Transaction type error! Provide "common" or "trade" transaction'}), 400

    if type == 'common':
        symbol = values['symbol']
        contract = values['contract']
        sender = values['sender']
        recipient = values['recipient']
        sendAmount = values['sendAmount']
        comissionAmount = values['comissionAmount']

        index = blockchain.newTransaction(type=type,symbol=symbol, contract=contract,\
                                        sender=sender, recipient=recipient,\
                                        sendAmount=sendAmount,\
                                        comissionAmount=comissionAmount)

    elif type == 'trade':
        sender = values['sender']
        symbol = values['symbol']
        price = values['price']
        send = values['send']
        sendVol = values['sendVol']
        get = values['get']
        getVol = values['getVol']
        comissionAmount = values['comissionAmount']

        index = blockchain.newTransaction(type=type, sender=sender, symbol=symbol,\
                        price=price, send=send, sendVol=sendVol, get=get,\
                        getVol=getVol, comissionAmount=comissionAmount)

    # txRequired = ['type','contractSend','contractGet','amountToSend','amountToGet','tradeTxHash']


    response = {'msg': f'Transaction will be added to Block {index}'}

    return jsonify(response), 201


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
        psw = request.json['password']
        address = createWallet(password)

        return jsonify({"ADDRESS": address}), 200


@app.route('/wallet/login', methods=['POST'])
def loginUser():
    if request.method == 'POST':
        psw = request.json['password']
        prKey = authoriseUser(password)
        if prKey == 'Wrong password':
            return jsonify({'MSG': prKey}), 400

        blockchain.prkey = prKey
        return jsonify({'MSG': True}), 200


@app.route('wallet/logout', methods=['GET'])
def logoutUser():
    blockchain.prkey = None
    return jsonify({'MSG': True}), 200


if __name__ == '__main__':
    # _, host, port = argv
    app.run(host= '0.0.0.0', port=5000)
    print(blockchain.nodes)
