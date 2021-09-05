import requests

from flask import request
from config import Config


def syncChains(chain, nodes):
    c = 0
    for node in nodes:
        try:
            whiteIp = requests.get('https://api.ipify.org').content
            whiteIp = whiteIp.decode()
            # requests.post("http://"+node+"/chain/sync", json={'chain':chain, 'node': 'http://'+whiteIp+':'+Config().DEFAULT_PORT})
            requests.post("http://"+node+"/chain/sync", json={'chain':chain, 'node': 'http://'+Config().DEFAULT_HOST+':'+Config().DEFAULT_PORT})
            c+=1
        except:
            print(f'Access to node {node} denied.')

    return f'Chain synced among {c} nodes'
