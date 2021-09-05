import os
import hashlib

from Crypto.PublicKey import RSA
from config import Config

def authoriseUser(password, accounts):

    # Get keys names
    keysNames = []
    fileNames = os.listdir(os.path.join(Config().BASEDIR, 'keys'))
    address = None
    for account in accounts:
        hsh = hashlib.sha3_224((password+account.slt).encode()).hexdigest()
        for name in fileNames:
            if name.split('_')[0] == hsh:
                address = account.address
                keysNames.append(name)

    # Get keys names
    # keysNames = os.listdir(os.path.join(Config().BASEDIR, 'keys'))
    try:
        # Get private key name
        prKeyName = [name for name in keysNames if name.split('_')[1] == 'prKey.der'][0]
    except:
        return False, False, False

    # Get and decrypt private key
    try:
        with open(os.path.join(os.path.join(Config().BASEDIR, 'keys'), prKeyName), 'rb') as keyFile:
            key = RSA.import_key(keyFile.read(), passphrase=password)
    except:
        return False, False, False

    prKey = key.export_key()
    pubKey = key.public_key().export_key(format='DER')

    return pubKey, prKey, address
