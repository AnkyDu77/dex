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
        blockInfo = miner(host)
        print('\n=====\n',blockInfo, '\n\n')
        sleep(1)
