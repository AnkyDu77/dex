import sys
import requests
import json

from time import sleep
from config import Config

def miner(host=f"http://{Config().DEFAULT_HOST}:{Config().DEFAULT_PORT}"):
    mineReq = json.loads(requests.get(host+'/soloMine').content)
    return mineReq

if __name__ == "__main__":
    try:
        lst=sys.argv[1:]
        host = lst[0]

        while True:
            try:
                blockInfo = miner(host)
                print('\n=====\n',blockInfo, '\n\n')
            except:
                print('\n=====\nJson slipperage appeared\n\n')
            sleep(1)
    except:
        while True:
            try:
                blockInfo = miner()
                print('\n=====\n',blockInfo, '\n\n')
            except:
                print('\n=====\nJson slipperage appeared\n\n')
            sleep(1)
