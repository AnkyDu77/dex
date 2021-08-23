import os
import hashlib

from Crypto.PublicKey import RSA

class Config():

    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    IDSTR = 'z01x00'
    MINEADDR = 'z01x0000000000000000000000000000000000000000000000000000000000'

    MIN_COMISSION = 1
    MAX_CHAIN_SIZE = 2831155
    REQUIRED_TX_FIELDS = ['sender', 'type']
    REQUIRED_TX_TYPE = ['common', 'trade']
    
    DEFAULT_VALID_NODES = ['0.0.0.0:5002']

    UPLOAD_FOLDER = os.path.join(BASEDIR, 'chain')
