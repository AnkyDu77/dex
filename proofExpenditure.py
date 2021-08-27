import hashlib

def proofExpenditure(account, sendAmount, blockHash):
      if account.balance - sendAmount >= 0:
          account.balance -= sendAmount
          account.blockHash = blockHash
          account.validHash = hashlib.sha3_224((self.address+\
                                                  str(self.balance)+\
                                                  self.blockHash).encode()).hexdigest()
