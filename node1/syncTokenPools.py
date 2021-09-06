import requests
from config import Config

def syncTokenPools(poolAddress, poolBalacne, accountAddress, accountBalance, nodes):
    c = 0
    for node in nodes:
        try:
            requests.post("http://"+node+"/pools/sendTokenPoolsState", json={'poolAddress': poolAddress,\
                                                'poolBalacne':poolBalacne,\
                                                'accountAddress':accountAddress,\
                                                'accountBalance':accountBalance,\
                                                'node': 'http://'+Config().DEFAULT_HOST+':'+Config().DEFAULT_PORT})
            c+=1
        except:
            print(f'Access to node {node} denied.')

    return f'Pools state synced among {c} nodes'
