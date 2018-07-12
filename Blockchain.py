import hashlib
import json
from time import time

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash =self.hash_block()

    def hash_block(self):
        sha = hashlib.sha256()
        sha.update((str(self.index) +
                   str(self.timestamp) +
                   str(self.data) +
                   str(self.previous_hash)).encode())
        return sha.hexdigest()

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # create genesis block
        self.genesis_block = Block(0, time(), "Genesis Block", "0")
        self.chain.append(self.genesis_block)
    def last_block(self):
        return self.chain[-1]

    def new_block(self, last_block):
        last_block = self.chain[-1]
        new_block = Block(len(self.chain)+1, time(),
                          self.current_transactions, last_block.hash)
        self.chain.append(new_block)
        return new_block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
    def hash(block):
        block_string = json.dumps(block, sort_keys = True).encoded()
        return hashlib.sha256(block_string).hexdigest()


blockchain = Blockchain()
blockchain.new_transaction("abc", "mike", 10)
blockchain.new_transaction("abc", "alice", 10)
blockchain.new_block(blockchain.last_block())
block = blockchain.last_block()
for x in range(len(block.data)):
    print(block.data[x])

print(block.previous_hash)
print(block.hash)

