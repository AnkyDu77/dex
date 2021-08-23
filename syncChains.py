import requests
from flask import request

def syncChains(chain, nodes):
    c = 0
    for node in nodes:
        try:
            requests.post("http://"+node+"/chain/sync", json={'chain':chain, 'node': 'http://'+request.host})
            c+=1
        except:
            print(f'Access to node {node} denied.')

    return f'Chain synced among {c} nodes'
