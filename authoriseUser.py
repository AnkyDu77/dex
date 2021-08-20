import os

from Crypto.PublicKey import RSA
from config import Config

def authoriseUser(password):

    # Get keys names
    keysNames = os.listdir(os.path.join(Config().BASEDIR, 'keys'))
    try:
        # Get private key name
        prKeyName = [name for name in keysNames if name.split('_')[1] == 'prKey.der'][0]
    except:
        return False, False

    # Get and decrypt private key
    try:
        with open(os.path.join(os.path.join(Config().BASEDIR, 'keys'), prKeyName), 'rb') as keyFile:
            key = RSA.import_key(keyFile.read(), passphrase=password)
    except:
        return False, False

    prKey = key.export_key()
    pubKey = key.public_key().export_key(format='DER')

    return pubKey, prKey
