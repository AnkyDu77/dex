import json

from textwrap import dedent
from time import time
from uuid import uuid4
from sys import argv
from flask import Flask, jsonify, request

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
        amount=1
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

    type="common"
    contractSend=None
    contractGet=None
    amountToSend=0.0
    amountToGet=0.0
    tradeTxHash=None

    values = request.get_json()
    required = ['sender', 'recipient', 'amount']

    if not all(k in values for k in required):
        return 'Missing values', 400


    # txRequired = ['type','contractSend','contractGet','amountToSend','amountToGet','tradeTxHash']
    if 'contractSend' in values:
        type = values['type']
        contractSend = values['contractSend']
        contractGet = values['contractGet']
        amountToSend = values['amountToSend']
        amountToGet = values['amountToGet']
        tradeTxHash = values['tradeTxHash']

    index = blockchain.newTransaction(values['sender'], values['recipient'],\
                                     values['amount'], type, contractSend, contractGet,\
                                     amountToSend, amountToGet, tradeTxHash)


    response = {'msg': f'Transaction will be added to Block {index}'}

    return jsonify(response), 201

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
