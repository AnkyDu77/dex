import json

from textwrap import dedent
from time import time
from uuid import uuid4
from sys import argv
from flask import Flask, jsonify, request

from config import Config
from blockchain import Blockchain

app = Flask(__name__)
nodeIdentifier = str(uuid4()).replace('-','')
blockchain = Blockchain()

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
        return 'Missing values', 400

    # Define orders type
    type = values['type']
    print(type)

    if type not in Config().REQUIRED_TX_TYPE:
        return 'Transaction type error! Provide "common" or "trade" transaction', 400

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

if __name__ == '__main__':
    # _, host, port = argv
    app.run(host= '0.0.0.0', port=5000)#,
    print(blockchain.nodes)
