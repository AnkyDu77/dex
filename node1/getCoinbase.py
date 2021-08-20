import os
import hashlib

from Crypto.PublicKey import RSA
from config import Config


def getCoinbase():

    keysNames = os.listdir(os.path.join(Config().BASEDIR, 'keys'))
    # Get public key name
    pubKeyName = [name for name in keysNames if name.split('_')[1] == 'pubKey.der'][0]
    # Get and decrypt public key
    with open(os.path.join(os.path.join(Config().BASEDIR, 'keys'), pubKeyName), 'rb') as keyFile:
        key = RSA.import_key(keyFile.read())
    pubKey = key.export_key(format='DER')
    pubHash = hashlib.sha3_224(pubKey).hexdigest()
    coinbase = Config().IDSTR+pubHash

    return coinbase
