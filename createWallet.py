import os
import uuid
import hashlib
import pickle
import requests

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from blockchain import Account

from config import Config


def createWallet(password, blockHash, blockchain):
    # Create wallet ID
    uid = uuid.uuid4().hex
    hsh = hashlib.sha3_224((password+uid).encode()).hexdigest()

    # Generate keys pair
    key = RSA.generate(1024)
    # Export public and private keys and save them
    pubKey = key.publickey().export_key(format='DER')
    with open(os.path.join(os.path.join(Config().BASEDIR, 'keys'), f'{hsh}_pubKey.der'), 'wb') as pubFile:
        pubFile.write(pubKey)

    prKey = key.export_key(format='DER', passphrase=password, pkcs=8,
                              protection="scryptAndAES128-CBC")
    with open(os.path.join(os.path.join(Config().BASEDIR, 'keys'), f'{hsh}_prKey.der'), 'wb') as prFile:
        prFile.write(prKey)

    # Form address and return it to the user
    pubHash = hashlib.sha3_224(pubKey).hexdigest()
    address = Config().IDSTR+pubHash

    # Registrer new account
    newAccount = Account()
    newAccount.address = address
    newAccount.balance = 0.0
    newAccount.blockHash = blockHash
    newAccount.validHash = hashlib.sha3_224((newAccount.address+\
                                            str(newAccount.balance)+\
                                            newAccount.blockHash).encode()).hexdigest()

    newAccount.slt = uid

    blockchain.accounts.append(newAccount)

    # Sync accounts between nodes
    c = 0
    try:
        whiteIp = requests.get('https://api.ipify.org').content
        whiteIp = whiteIp.decode()
    except:
        print('ipify.org connection denied')

    pickleAccount = pickle.dumps(newAccount).hex()
    for node in blockchain.nodes:
        try:
            # requests.post("http://"+node+"/wallet/sync", json={'account': newAccount, 'node': 'http://'+whiteIp+':'+Config().DEFAULT_PORT})
            requests.post("http://"+node+"/wallet/sync", json={'account': pickleAccount, 'node': 'http://'+Config().DEFAULT_HOST+':'+Config().DEFAULT_PORT})
            c+=1
        except:
            print(f'Access to node {node} denied.')

    return f'New account synced among {c} nodes'


    return address
