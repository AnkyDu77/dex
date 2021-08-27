import os
import uuid
import hashlib

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


    return address
