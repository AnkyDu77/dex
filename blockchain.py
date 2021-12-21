import os
import re
import sys
import uuid
import hashlib
import requests
import json
import pickle
from datetime import datetime, timezone
from urllib.parse import urlparse
from flask import request
from config import Config

from matchOrders import matchOrders
from transactTrades import transactTrades
from verifyTxSignature import verifyTxSignature
from syncPools import syncPools
from syncChains import syncChains
from sendAccountState import sendAccountState
from syncTokenPools import syncTokenPools


class Pool(object):
    def __init__(self):
        self.name = None
        self.symbol = None
        self.poolAddress = Config().IDSTR+hashlib.sha3_224(uuid.uuid4().hex.encode()).hexdigest()
        self.poolBalance = None
        self.accountsBalance = {}
        self.blockHash = None
        self.validHash = None


class Account(object):
    def __init__(self):
        self.address = None
        self.balance = None
        self.blockHash = None
        self.validHash = None
        self.slt = None


    def proofExpenditure(self, sendAmount, blockHash):
        if self.balance - sendAmount >= 0:
            self.balance -= sendAmount
            self.blockHash = blockHash
            self.validHash = hashlib.sha3_224((self.address+\
                                                    str(self.balance)+\
                                                    self.blockHash).encode()).hexdigest()

            return True
        else:
            return False


    def makeTransaction(self, sendAmount, blockHash):
        self.balance += sendAmount
        self.blockHash = blockHash
        self.validHash = hashlib.sha3_224((self.address+\
                                                str(self.balance)+\
                                                self.blockHash).encode()).hexdigest()



        return True



class Blockchain(object):
    def __init__(self):

        blockchainStateFiles = [file for file in os.listdir('./blockchainState') if file.split('.')[1]=='json']

        if len(blockchainStateFiles) > 0:
            self.chain=[]
            self.accounts=[]
            self.pools = []
            self.current_transactions=[]
            self.trade_transactions=[]
            self.coinbase = None

            self.loadBlockchainState()
            self.cnfg = Config()
            self.nodes = {node for node in self.cnfg.DEFAULT_VALID_NODES if len(self.cnfg.DEFAULT_VALID_NODES)>0}
            self.prkey = None
            self.pubKey = None

            # Get chain data from default nodes
            if len(self.nodes) > 0:
                for node in self.nodes:
                    try:
                        # Get num of files
                        filesNum = json.loads(requests.get(node+'/nodes/getChainFilesAmount').content)['MSG']
                        # Download files
                        for i in range(filesNum):
                            chainFile = requests.post('http://'+node+'/nodes/sendChainData', json={'iter':i})
                            fileName = re.split(r'; filename=', chainFile.headers['Content-Disposition'])[1]
                            with open(os.path.join(os.path.join(self.cnfg.BASEDIR, 'chain'), f'{fileName}'), 'wb') as file:
                                file.write(chainFile.content)
                    except:
                        print(f'Node {node} does not respond')

        else:
            self.cnfg = Config()
            self.chain=[]
            self.accounts=[]
            self.pools = []
            self.current_transactions=[]
            self.trade_transactions=[]
            self.nodes = {node for node in self.cnfg.DEFAULT_VALID_NODES if len(self.cnfg.DEFAULT_VALID_NODES)>0}
            self.coinbase = None
            self.prkey = None
            self.pubKey = None

            # Get chain data from default nodes
            if len(self.nodes) > 0:
                for node in self.nodes:
                    try:
                        # Get num of files
                        filesNum = json.loads(requests.get(node+'/nodes/getChainFilesAmount').content)['MSG']
                        # Download files
                        for i in range(filesNum):
                            chainFile = requests.post('http://'+node+'/nodes/sendChainData', json={'iter':i})
                            fileName = re.split(r'; filename=', chainFile.headers['Content-Disposition'])[1]
                            with open(os.path.join(os.path.join(self.cnfg.BASEDIR, 'chain'), f'{fileName}'), 'wb') as file:
                                file.write(chainFile.content)
                    except:
                        print(f'Node {node} does not respond')

                    # Get pools info

                    # Get accounts info

            # Get latest block or initiate genesis
            chainFiles = os.listdir(os.path.join(self.cnfg.BASEDIR, 'chain'))
            chainFiles = [file for file in chainFiles if re.split(r'\.', file)[1] == 'json']
            if len(chainFiles) > 0:
                with open(os.path.join(os.path.join(self.cnfg.BASEDIR, 'chain'), f'{chainFiles[-1]}'), 'r') as file:
                    self.chain = [json.load(file)[-1]]
            else:
                # Genesis block creation
                self.newBlock(previousHash=1, proof=100)



    def getBalance(self, address):
        balance = [account.balance for account in self.accounts if account.address == address][0]
        return balance


    def newBlock(self, proof, previousHash=None):
        """
        New block creation

        :param proof: <int> Доказательства проведенной работы
        :param previous_hash: (Опционально) хеш предыдущего блока
        :return: <dict> Новый блок
        """

        # # Match trade txs and route trades
        # self.transactTradeOrders()

        # Make new block
        block = {
            'index': self.chain[-1]['index']+1 or len(self.chain)+1,
            'timestamp': datetime.now(timezone.utc).timestamp(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previousHash': previousHash or self.hash(self.chain[-1])
        }

        # Current txs list reload
        self.current_transactions = []
        self.chain.append(block)

        # # Sync chain among the nodes
        # if len(self.nodes) > 0:
        #     syncChains(self.chain, self.nodes)

        # Get chain size and write it to file if necessary
        #if sys.getsizeof(self.chain) >= Config().MAX_CHAIN_SIZE:
        #    with open(f'./chain/{int(datetime.now(timezone.utc).timestamp())}.json', 'w') as file:
        #        json.dump(self.chain, file)
#
        #    self.chain = [self.chain[-1]]

        if len(self.chain) >= Config().MAX_CHAIN_SIZE:
            with open(f'./chain/{int(datetime.now(timezone.utc).timestamp())}.json', 'w') as file:
                json.dump(self.chain, file)

            self.saveBlockchainState()

            self.chain = [self.chain[-1]]

        return block


    def saveBlockchainState(self):
        blockchainState = {
            'chain': self.chain,
            'accounts': [pickle.dumps(account).hex() for account in self.accounts],
            'pools': [pickle.dumps(pool).hex() for pool in self.pools],
            'current_transactions': self.current_transactions,
            'trade_transactions': self.trade_transactions,
            'coinbase': self.coinbase
        }

        with open(f'./blockchainState/{int(datetime.now(timezone.utc).timestamp())}.json', 'w') as file:
            json.dump(blockchainState, file)

        return True


    def loadBlockchainState(self):

        files = [file for file in os.listdir('./blockchainState') if file.split('.')[1]=='json']
        files.sort(key=lambda f: int(re.sub('\D', '', f)))

        with open(f'./blockchainState/{files[-1]}', 'r') as file:
            loadedState = json.load(file)

        self.chain = [loadedState['chain'][-1]]
        self.accounts = [pickle.loads(bytes.fromhex(account)) for account in loadedState['accounts']]
        self.pools = [pickle.loads(bytes.fromhex(pool)) for pool in loadedState['pools']]
        self.current_transactions = loadedState['current_transactions']
        self.trade_transactions = loadedState['trade_transactions']
        self.coinbase = loadedState['coinbase']



    # Approve non-native tokens expenditure
    def proofPoolExpenditure(self, symbol, address, sendAmount):
        pool = [pool for pool in self.pools if pool.symbol == symbol.upper()][0]
        if pool.accountsBalance[address] - sendAmount >= 0:
            pool.accountsBalance[address] -= sendAmount
            # Send aendAmount to pool balance
            pool.poolBalance += sendAmount
            pool.blockHash = self.hash(self.chain[-1])
            pool.validHash = hashlib.sha3_224((str(pool.poolBalance)+\
                                                json.dumps(pool.accountsBalance)+\
                                                pool.blockHash).encode()).hexdigest()
            return True
        else:
            return False


    # Make non-native tokens transaction
    def makePoolTransaction(self, symbol, address, getAmount):
        pool = [pool for pool in self.pools if pool.symbol == symbol.upper()][0]
        pool.poolBalance -= getAmount
        pool.accountsBalance[address] += getAmount
        pool.blockHash = self.hash(self.chain[-1])
        pool.validHash = hashlib.sha3_224((str(pool.poolBalance)+\
                                            json.dumps(pool.accountsBalance)+\
                                            pool.blockHash).encode()).hexdigest()
        return True




    async def newTransaction(self, sender, timestamp, txsig=None, sendAmount=0.0,\
    price=0.0, recipient=None, symbol='zsh', type="common", contract=None,\
    send=None, get=None, sendVol=0.0,\
    getVol=0.0, tradeTxHash=None, comissionAmount=Config().MIN_COMISSION):

        """
        Sends new transaction in the next block

        :param sender: <str> Sender Address
        :param recipient: <str> Recipient Address
        :param amount: <int> Summ
        :return: <str> Synchronisation or Account Verification Status
        """

        if comissionAmount < self.cnfg.MIN_COMISSION:
            comissionAmount = self.cnfg.MIN_COMISSION

        if type == 'common':

            simpleTx = {
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

            if sender == Config().MINEADDR:
                self.current_transactions.append(simpleTx)
                # syncStatus = syncPools(self.current_transactions, self.trade_transactions, self.nodes)
                syncStatus = 'Tx pool synced among 0 nodes'
                # Sync account state
                if len(self.nodes) > 0:
                    account = [account for account in self.accounts if account.address == recipient][0]
                    # syncAccState = sendAccountState(account, self.nodes)
                    syncAccState = 'Account state synced among 0 nodes'
                    print(f'\n====\nAccount state sync status: {syncAccState}\n====\n\n')

                return self.lastBlock['index']+1, syncStatus

            # Check sigitures
            verifStatus = verifyTxSignature(sender, self.pubKey, str(simpleTx), txsig)
            if verifStatus == True:
                self.current_transactions.append(simpleTx)
                # syncStatus = syncPools(self.current_transactions, self.trade_transactions, self.nodes)
                syncStatus = 'Tx pool synced among 0 nodes'


                # Sync sender account state
                if len(self.nodes) > 0:
                    recipientAccount = [account for account in self.accounts if account.address == recipient][0]
                    senderAccount = [account for account in self.accounts if account.address == sender][0]
                    # syncAccState = sendAccountState(recipientAccount, self.nodes, senderAccount)
                    syncAccState = 'Account state synced among 0 nodes'
                    print(f'\n====\nAccount state sync status: {syncAccState}\n====\n\n')


                return self.lastBlock['index']+1, syncStatus

            else:
                return verifStatus, verifStatus

        elif type == 'trade':

            tradeTx = {
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

            # Check sigitures
            verifStatus = verifyTxSignature(sender, self.pubKey, str(tradeTx), txsig)
            if verifStatus == True:

                tradeTxJson = json.dumps(tradeTx, sort_keys=True).encode()
                tradeTxHash = hashlib.sha256(tradeTxJson).hexdigest()
                tradeTx['tradeTxId'] = tradeTxHash

                if len(self.nodes) > 0:
                    pool  = [pool for pool in self.pools if pool.symbol == send.upper() or pool.symbol == get.upper()][0]
                    # poolSyncState = syncTokenPools(pool.poolAddress, pool.poolBalance, sender, pool.accountsBalance[sender], self.nodes)
                    poolSyncState = 'Pools state synced among 0 nodes'
                    print(f'\n====\n{pool.symbol} pool state sync status: {poolSyncState}\n====\n\n')

                self.trade_transactions.append(tradeTx)

                # if len(self.nodes) > 0:
                # syncStatus = syncPools(self.current_transactions, self.trade_transactions, self.nodes)
                syncStatus = 'Tx pool synced among 0 nodes'

                return self.lastBlock['index']+1, syncStatus

            else:
                return verifStatus, verifStatus

        else:
            print('smth went terribly wrong')



    async def newRemoteTransaction(self, remotePublicKey, sender, timestamp, txsig=None, sendAmount=0.0,\
    price=0.0, recipient=None, symbol='zsh', type="common", contract=None,\
    send=None, get=None, sendVol=0.0,\
    getVol=0.0, tradeTxHash=None, comissionAmount=Config().MIN_COMISSION):

        """
        Sends new transaction in the next block

        :param sender: <str> Sender Address
        :param recipient: <str> Recipient Address
        :param amount: <int> Summ
        :return: <str> Synchronisation or Account Verification Status
        """

        # if comissionAmount < self.cnfg.MIN_COMISSION:
        #     comissionAmount = self.cnfg.MIN_COMISSION

        if type == 'common':

            simpleTx = {
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

            # if sender == Config().MINEADDR:
            #     self.current_transactions.append(simpleTx)
            #     syncStatus = syncPools(self.current_transactions, self.trade_transactions, self.nodes)
            #
            #     # Sync account state
            #     if len(self.nodes) > 0:
            #         account = [account for account in self.accounts if account.address == recipient][0]
            #         syncAccState = sendAccountState(account, self.nodes)
            #         print(f'\n====\nAccount state sync status: {syncAccState}\n====\n\n')
            #
            #     return self.lastBlock['index']+1, syncAccState

            # Check sigitures
            verifStatus = verifyTxSignature(sender, remotePublicKey, str(simpleTx), txsig)
            print(f'\n\nVerification status is {verifStatus}')

            if verifStatus == True:
                self.current_transactions.append(simpleTx)
                syncStatus = syncPools(self.current_transactions, self.trade_transactions, self.nodes)


                # Sync sender account state
                if len(self.nodes) > 0:
                    recipientAccount = [account for account in self.accounts if account.address == recipient][0]
                    senderAccount = [account for account in self.accounts if account.address == sender][0]
                    syncAccState = sendAccountState(recipientAccount, self.nodes, senderAccount)
                    print(f'\n====\nAccount state sync status: {syncAccState}\n====\n\n')


                return self.lastBlock['index']+1, syncStatus

            else:
                return verifStatus, verifStatus

        elif type == 'trade':

            tradeTx = {
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

            # Check sigitures
            verifStatus = verifyTxSignature(sender, remotePublicKey, str(tradeTx), txsig)
            print(f'\n\nVerification status is {verifStatus}')

            if verifStatus == True:

                tradeTxJson = json.dumps(tradeTx, sort_keys=True).encode()
                tradeTxHash = hashlib.sha256(tradeTxJson).hexdigest()
                tradeTx['tradeTxId'] = tradeTxHash

                if len(self.nodes) > 0:
                    pool  = [pool for pool in self.pools if pool.symbol == send.upper() or pool.symbol == get.upper()][0]
                    poolSyncState = syncTokenPools(pool.poolAddress, pool.poolBalance, sender, pool.accountsBalance[sender], self.nodes)
                    print(f'\n====\n{pool.symbol} pool state sync status: {poolSyncState}\n====\n\n')

                self.trade_transactions.append(tradeTx)

                # if len(self.nodes) > 0:
                syncStatus = syncPools(self.current_transactions, self.trade_transactions, self.nodes)

                return self.lastBlock['index']+1, syncStatus

            else:
                return verifStatus, verifStatus

        else:
            print('smth went terribly wrong')


    async def transactTradeOrders(self):
        """
        1. Get trade txs
        2. Find txs where contractSend == contractGet
        3. Find txs among txs above where prices are equal
        4. Form common transactions and append it to common txs pool
        5. Reduce volumes of amount to send of trade txs
        6. If amount to send of trade tx equals to zero -- append this tx to common txs pool and append it to block
        """

        commonTxs, toRemove = matchOrders(self.trade_transactions, self.pools)

        # Include tarde txs to common transaction pool
        for tx in commonTxs:
            self.current_transactions.append(tx)

        # Remove zero getVol transactions from tradeTxs pool
        removeDicts = [order for order in self.trade_transactions if order['tradeTxId'] in toRemove]
        for order in removeDicts:
            self.trade_transactions.remove(order)



    # Create new pool
    def createPool(self, name, symbol):

        pool = Pool()
        pool.name = name
        pool.symbol = symbol
        pool.poolBalance = 0.0

        # Set zero accounts balances
        for account in self.accounts:
            pool.accountsBalance[account.address] = 1000000.0

        pool.blockHash = self.hash(self.chain[-1])
        pool.validHash =  hashlib.sha3_224((str(pool.poolBalance)+\
                                            json.dumps(pool.accountsBalance)+\
                                            pool.blockHash).encode()).hexdigest()

        # Add new pool to pools list
        self.pools.append(pool)

        return pool, f'New pool was created! Name: {pool.name}, Symbol: {pool.symbol}'


    async def getPools(self):

        requestedPools = []
        for pool in self.pools:
            poolDict = {
                'name': pool.name,
                'symbol': pool.symbol,
                'poolAddress': pool.poolAddress,
                'poolBalance': pool.poolBalance,
                'accounts': pool.accountsBalance,
                'blockHash': pool.blockHash,
                'validHash': pool.validHash
            }
            requestedPools.append(poolDict)

        return requestedPools


    @staticmethod
    def hash(block):
        """
        Hashing new block

        :param block: <dict> block
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
        Proof validation. Watching for comlexity equality

        :param last_proof: <int> Previous proof
        :param proof: <int> Current proof
        :return: <bool> True if proof is rigth, False if not.
        """

        guess = f'{lastProof}{proof}'.encode()
        guessHash = hashlib.sha256(guess).hexdigest()

        return guessHash[:len(Config().MINING_COMPLEXITY)]==Config().MINING_COMPLEXITY


    def registerNode(self, address):
        """
        Connect new node

        :param address: <str> new node address
        :return: None
        """

        parsedUrl = urlparse(address)
        if parsedUrl.netloc not in self.nodes:
            self.nodes.add(parsedUrl.netloc)
            requests.post("http://"+parsedUrl.netloc+ "/nodes/register", json={'nodes':['http://'+request.host]})


    def validChain(self, chain):
        """
        Proof block hash correctness

        :param chain: <list> blockchain
        :return: <bool> True if hash works, False, if not
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
        Consensus algorithm. Switches chain on a longer one

        :return: <bool> True if chain was awitched, False if not.
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
