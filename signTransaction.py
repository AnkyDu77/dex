from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def signTransaction(msg, prKey):

    msg = msg.encode('utf-8')

    signKey = RSA.import_key(prKey)
    hashedMsg = SHA256.new(msg)
    signature = pkcs1_15.new(signKey).sign(hashedMsg).hex()

    return signature
