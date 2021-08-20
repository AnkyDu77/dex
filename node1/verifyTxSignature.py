import hashlib

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

from config import Config


def verifyTxSignature(address, pubKey, msg, signature):

    pubKeyFromAddress = address.split(Config().IDSTR)[1]
    if hashlib.sha3_224(pubKey).hexdigest() == pubKeyFromAddress:

        msg = msg.encode('utf-8')
        verifKey = RSA.import_key(pubKey)
        msgHash = SHA256.new(msg)

        try:
            pkcs1_15.new(verifKey).verify(msgHash, bytes.fromhex(signature))
            return True

        except (ValueError, TypeError):
            return False

    else:
        return 'Invalid public address'
