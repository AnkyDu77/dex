import hashlib
import requests
import json
from time import time
from urllib.parse import urlparse


class Blockchain(object):
    def __init__(self):
        self.chain=[]
        self.current_transactions=[]
        self.trade_transactions=[]
        self.nodes = set()

        # Genesis block creation
        self.newBlock(previousHash=1, proof=100)

    def newBlock(self, proof, previousHash=None):
        """
        New block creation

        :param proof: <int> Доказательства проведенной работы
        :param previous_hash: (Опционально) хеш предыдущего блока
        :return: <dict> Новый блок
        """

        # match trade txs

        block ={
            'index': len(self.chain)+1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previousHash': previousHash or self.hash(self.chain[-1])
        }

        # Current txs list reload
        self.current_transactions = []
        self.chain.append(block)

        return block

    def newTransaction(self,sender,recipient,amount,type="common",\
    contractSend=None, contractGet=None, amountToSend=0.0,\
    amountToGet=0.0, tradeTxHash=None):

        """
        Направляет новую транзакцию в следующий блок

        :param sender: <str> Адрес отправителя
        :param recipient: <str> Адрес получателя
        :param amount: <int> Сумма
        :return: <int> Индекс блока, который будет хранить эту транзакцию
        """
        if type is "common":
            self.current_transactions.append({
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'contractSend': contractSend,
                'contractGet': contractGet,
                'amountToSend': amountToSend,
                'amountToGet': amountToGet,
                'tradeTxHash':tradeTxHash
            })

        elif type is "trade":

            tradeTx = {
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'contractSend': contractSend,
                'contractGet': contractGet,
                'amountToSend': amountToSend,
                'amountToGet': amountToGet,
            }

            tradeTxJson = json.dumps(block, sort_keys=True).encode()
            tradeTxHash = hashlib.sha256(tradeTxJson).hexdigest()
            tradeTx['tradeTxHash'] = tradeTxHash

            self.trade_transactions.append(tradeTx)

        return self.lastBlock['index']+1




    def matchTradeTxs(self):
        """
         1. Get trade txs
         2. Find txs where contractSend == contractGet
         3. Find txs among txs above where prices are equal
         4. Form common transactions and append it to common txs pool
         5. Reduce volumes of amount to send of trade txs
         6. If amount to send of trade tx equals to zero -- append this tx to common txs pool and append it to block
        """
        tradeTxs = self.trade_transactions
        for i in len(tradeTxs)-1:
            if tradeTxs[i]['contractSend'] == 







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
