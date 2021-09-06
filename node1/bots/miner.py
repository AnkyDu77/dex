import sys
import requests
import json
from time import sleep

def miner(host):
    mineReq = json.loads(requests.get(host+'/mine').content)
    return mineReq

if __name__ == "__main__":
    lst=sys.argv[1:]
    host = lst[0]

    while True:
        try:
            blockInfo = miner(host)
            print('\n=====\n',blockInfo, '\n\n')
        except:
            print('\n=====\nJson slipperage appeared\n\n')
        sleep(0.001)
