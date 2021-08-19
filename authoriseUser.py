import os

from config import Config

def authoriseUser(password):

    # Get keys names
    keysNames = os.listdir(os.path.join(Config().BASEDIR, 'keys'))
    # Get private key name
    prKeyName = [name for name in keysNames if name.split('_')[1] == 'prKey.der'][0]

    # Get and decrypt private key
    try:
        with open(os.path.join(os.path.join(Config().BASEDIR, 'keys'), prKeyName), 'rb') as keyFile:
            key = RSA.import_key(keyFile.read(), passphrase=password)
    except:
        return "Wrong password"

    prKey = key.export_key()

    return prKey
