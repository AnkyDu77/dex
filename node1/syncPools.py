import requests
from flask import request

def syncPools(commonTxs,tradeTxs,nodes):
    c = 0
    for node in nodes:
        try:
            requests.post("http://"+node+"/transactions/sync", json={'commonTxs':commonTxs, 'tradeTxs': tradeTxs, 'node': 'http://'+request.host})
            c+=1
        except:
            print(f'Access to node {node} denied.')

    return f'Tx pool synced among {c} nodes'
