import requests
import pickle

from config import Config

def sendNewPool(pool, nodes):
    c = 0
    picklePool = pickle.dumps(pool).hex()

    for node in nodes:
        try:
            requests.post("http://"+node+"/pools/getNewPool", json={'pool':picklePool, 'node': 'http://'+Config().DEFAULT_HOST+':'+Config().DEFAULT_PORT})
            c+=1
        except:
            print(f'Access to node {node} denied.')

    return f'Account state synced among {c} nodes'
