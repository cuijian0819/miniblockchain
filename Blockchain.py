import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask
from flask import jsonify
from flask import request

class Transaction:
    def __init__(self, sender_addr, recipient_addr, amount):
        self.sender_addr = sender_addr
        self.recipient_addr  =  recipient_addr
        self.amount = amount
    def transaction_contents(self):
        return "from sender "+ str(self.sender_addr)  + " to recipient " + str(self.recipient_addr)  + " - amount is " + str(self.amount) + ";  "

class Block:
    def __init__(self, index, timestamp, data, nonce, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.hash =self.hash_block()

    def hash_block(self):
        sha = hashlib.sha256()
        sha.update((str(self.index) +str(self.timestamp) +
                   str(self.data) +str(self.nonce) +
                   str(self.previous_hash)).encode())

        return sha.hexdigest()

    def mine(self, difficulty):
        while [v for v in self.hash[0:difficulty]] != ['0' for v in range(0, difficulty)]:
            self.nonce += 1
            #print(self.nonce)
            self.hash = self.hash_block()
        print("mining success")

    def get_block(self):
        return {"index": self.index,
                "timestamp": self.timestamp,
                "data": self.transaction_data(),
                "nonce": self.nonce,
                "previous hash": self.previous_hash,
                "hash":self.hash
                }
    def transaction_data(self):
        transaction_contents = ""
        for i in range(len(self.data)):
            transaction = self.data[i]
            transaction_contents = transaction_contents + transaction.transaction_contents()
        return transaction_contents

class Blockchain(object):
    def __init__(self):
        self.difficulty = 3
        self.chain = []
        self.current_transactions = []
        # create genesis block
        self.genesis_block = Block(0, time(), "Genesis Block", 0, "0")
        self.genesis_block.mine(self.difficulty)
        self.chain.append(self.genesis_block)

    def last_block(self):
        return self.chain[-1]
    def cur_index(self):
        return self.last_block().index

    def new_block(self):
        last_block = self.chain[-1]
        new_block = Block(len(self.chain), time(),
                          self.current_transactions, 0, last_block.hash)
        new_block.mine(self.difficulty)
        self.current_transactions= []
        self.chain.append(new_block)
        return new_block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append(Transaction(sender, recipient, amount))

    def hash(block):
        block_string = json.dumps(block, sort_keys = True).encoded()
        return hashlib.sha256(block_string).hexdigest()

    def get_chain(self):
        chain_content = []
        for block in self.chain:
            if isinstance(block.data, str) == False:
                chain_content.append(block.get_block())
        return chain_content


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-','')
blockchain = Blockchain()

@app.route('/transactions/new', methods=['POST'])
def new_transactions():

    transaction_data = request.get_json()
    #print(transaction_data)
    blockchain.new_transaction(transaction_data['sender'], transaction_data['recipient'], transaction_data['amount'])
    response = {'message': 'Transaction will be added to Block'}
    return jsonify(response), 201


@app.route('/mine', methods=['GET'])
def mine():

    blockchain.new_transaction(sender = "0",
                               recipient = node_identifier,
                               amount=25)
    new_block = blockchain.new_block()
    response = {'message': "new block added",
                'index': new_block.index,
                'transactions':  str(new_block.transaction_data()),
                'nonce': new_block.nonce,
                'previous_hash' : new_block.previous_hash
                }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': str(blockchain.get_chain())
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

