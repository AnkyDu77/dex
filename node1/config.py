import os

class Config():

    BASEDIR = basedir = os.path.abspath(os.path.dirname(__file__))

    MIN_COMISSION = 1
    REQUIRED_TX_FIELDS = ['sender', 'type']
    REQUIRED_TX_TYPE = ['common', 'trade']

    DEFAULT_VALID_NODES = ['http://0.0.0.0:5000']

    UPLOAD_FOLDER = os.path.join(BASEDIR, 'chain')
