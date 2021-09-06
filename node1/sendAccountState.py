import requests
import pickle

from config import Config

def sendAccountState(recipientAccount, nodes, senderAccount=None):

    c = 0
    pickleSenderAccount = pickle.dumps(senderAccount).hex()
    pickleRecipientAccount = pickle.dumps(recipientAccount).hex()
    for node in nodes:
        try:
            requests.post("http://"+node+"/wallet/sendAccountState", json={'senderAccount':pickleSenderAccount,'recipientAccount':pickleRecipientAccount, 'node': 'http://'+Config().DEFAULT_HOST+':'+Config().DEFAULT_PORT})
            c+=1
        except:
            print(f'Access to node {node} denied.')

    return f'Account state synced among {c} nodes'
