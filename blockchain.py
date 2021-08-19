import os
import re
import sys
import hashlib
import requests
import json
from datetime import datetime, timezone
from urllib.parse import urlparse
from config import Config

from matchOrders import matchOrders
from transactTrades import transactTrades
from signTransaction import signTransaction


class Blockchain(object):
    def __init__(self):
        self.cnfg = Config()

        self.chain=[]
        self.current_transactions=[]
        self.trade_transactions=[]
        self.nodes = {node for node in self.cnfg.DEFAULT_VALID_NODES if len(self.cnfg.DEFAULT_VALID_NODES)>0}
        self.prkey = None

        # # Get chain data from default nodes
        # for node in self.nodes:
        #     if requests.get(node).status_code == 200:
        #         # Get num of files
        #         filesNum = json.loads(requests.get(node+'/nodes/getChainFilesAmount').content)['MSG']
        #         # Download files
        #         for i in range(filesNum):
        #             chainFile = requests.post(node+'/nodes/sendChainData', json={'iter':i})
        #             fileName = re.split(r'; filename=', chainFile.headers['Content-Disposition'])[1]
        #             with open(os.path.join(os.path.join(self.cnfg.BASEDIR, 'chain'), f'{fileName}'), 'wb') as file:
        #                 file.write(chainFile.content)

        # Get latest block or initiate genesis
        chainFiles = os.listdir(os.path.join(self.cnfg.BASEDIR, 'chain'))
        chainFiles = [file for file in chainFiles if re.split(r'\.', file)[1] == 'json']
        if len(chainFiles) > 0:
            with open(os.path.join(os.path.join(self.cnfg.BASEDIR, 'chain'), f'{chainFiles[-1]}'), 'r') as file:
                self.chain = [json.load(file)[-1]]
        else:
            # Genesis block creation
            self.newBlock(previousHash=1, proof=100)


    def newBlock(self, proof, previousHash=None):
        """
        New block creation

        :param proof: <int> Доказательства проведенной работы
        :param previous_hash: (Опционально) хеш предыдущего блока
        :return: <dict> Новый блок
        """

        # Match trade txs and route trades
        self.transactTradeOrders()

        # Make new block
        block = {
            'index': len(self.chain)+1,
            'timestamp': datetime.now(timezone.utc).timestamp(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previousHash': previousHash or self.hash(self.chain[-1])
        }

        # Current txs list reload
        self.current_transactions = []
        self.chain.append(block)

        # Get chain size and write it to file if necessary
        if sys.getsizeof(self.chain) >= 2831155:
            with open(f'./chain/{int(datetime.now(timezone.utc).timestamp())}.json', 'w') as file:
                json.dump(self.chain, file)

            self.chain = [self.chain[-1]]

        return block

    def newTransaction(self,sender,sendAmount=0.0, price=0.0, recipient=None,\
    symbol='zsh', type="common", contract=None,\
    send=None, get=None, sendVol=0.0,\
    getVol=0.0, tradeTxHash=None, comissionAmount=Config().MIN_COMISSION):

        """
        Направляет новую транзакцию в следующий блок

        :param sender: <str> Адрес отправителя
        :param recipient: <str> Адрес получателя
        :param amount: <int> Сумма
        :return: <int> Индекс блока, который будет хранить эту транзакцию
        """

        if comissionAmount < self.cnfg.MIN_COMISSION:
            comissionAmount = self.cnfg.MIN_COMISSION

        if type == 'common':
            self.current_transactions.append({
                'timestamp': datetime.now(timezone.utc).timestamp(),
                'symbol': symbol,
                'contract': contract,
                'sender': sender,
                'recipient': recipient,
                'sendAmount': sendAmount,
                'recieveAmount': get,
                'price': price,
                'comissionAmount': float(comissionAmount),
                'tradeTxId':tradeTxHash
            })

        elif type == 'trade':

            tradeTx = {
                'timestamp': datetime.now(timezone.utc).timestamp(),
                'sender': sender,
                'symbol': symbol,
                'price': price,
                'send': send,
                'sendVol': sendVol,
                'get': get,
                'getVol': getVol,
                'comissionAmount':float(comissionAmount)
            }

            tradeTxJson = json.dumps(tradeTx, sort_keys=True).encode()
            tradeTxHash = hashlib.sha256(tradeTxJson).hexdigest()
            tradeTx['tradeTxId'] = tradeTxHash

            self.trade_transactions.append(tradeTx)

        else:
            print('smth went terribly wrong')

        return self.lastBlock['index']+1


    def transactTradeOrders(self):
        """
        1. Get trade txs
        2. Find txs where contractSend == contractGet
        3. Find txs among txs above where prices are equal
        4. Form common transactions and append it to common txs pool
        5. Reduce volumes of amount to send of trade txs
        6. If amount to send of trade tx equals to zero -- append this tx to common txs pool and append it to block
        """
        mathchedOrders = matchOrders(self.trade_transactions)

        txDir, commonTxs = transactTrades(mathchedOrders, self.trade_transactions)

        # Include tarde txs to common transaction pool
        for tx in commonTxs:
            self.current_transactions.append(tx)

        # Remove zero getVol transactions from tradeTxs pool
        txDirKeys = list(txDir.keys())
        toRemove = []

        for key in txDirKeys:
            toRemoveTemp = [order for i,order in enumerate(txDir[key]) if order['getVol']==0]
            if len(toRemoveTemp) > 0:
                toRemove.append(toRemoveTemp[0])

        for removeOrder in toRemove:
            self.trade_transactions.remove(removeOrder)



    @staticmethod
    def hash(block):
        """
        Hashing new block

        :param block: <dict> Блок
        :return: <str>
        """
        blockString = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockString).hexdigest()

    @property
    def lastBlock(self):
        return self.chain[-1]

    def pow(self, lastProof):
        """
        Простая проверка алгоритма:
         - Поиска числа p`, так как hash(pp`) содержит 4 заглавных нуля, где p - предыдущий
         - p является предыдущим доказательством, а p` - новым

        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.validProof(lastProof, proof) is False:
            proof += 1

        return proof


    @staticmethod
    def validProof(lastProof, proof):
        """
        Подтверждение доказательства: Содержит ли hash(last_proof, proof) 4 заглавных нуля?

        :param last_proof: <int> Предыдущее доказательство
        :param proof: <int> Текущее доказательство
        :return: <bool> True, если правильно, False, если нет.
        """

        guess = f'{lastProof}{proof}'.encode()
        guessHash = hashlib.sha256(guess).hexdigest()

        return guessHash[:4]=="0000"


    def registerNode(self, address):
        """
        Вносим новый узел в список узлов

        :param address: <str> адрес узла , другими словами: 'http://192.168.0.5:5000'
        :return: None
        """

        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)


    def validChain(self, chain):
        """
        Проверяем, является ли внесенный в блок хеш корректным

        :param chain: <list> blockchain
        :return: <bool> True если она действительна, False, если нет
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Проверьте правильность хеша блока
            if block['previousHash'] != self.hash(last_block):
                return False

            # Проверяем, является ли подтверждение работы корректным
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolveConflicts(self):
        """
        Это наш алгоритм Консенсуса, он разрешает конфликты,
        заменяя нашу цепь на самую длинную в цепи

        :return: <bool> True, если бы наша цепь была заменена, False, если нет.
        """

        neighbours = self.nodes
        new_chain = None

        # Ищем только цепи, длиннее нашей
        max_length = len(self.chain)

        # Захватываем и проверяем все цепи из всех узлов сети
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Проверяем, является ли длина самой длинной, а цепь - валидной
                if length > max_length and self.validChain(chain):
                    max_length = length
                    new_chain = chain

        # Заменяем нашу цепь, если найдем другую валидную и более длинную
        if new_chain:
            self.chain = new_chain
            return True

        return False
