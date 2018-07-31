import hashlib
import json
import requests
from time import time
from uuid import uuid4
from urllib.parse import urlparse
from flask import Flask
from flask import jsonify
from flask import request

class Block:
    def __init__(self, index, timestamp, transactions, nonce, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.hash =self.hash_block()

    def hash_block(self):
        sha = hashlib.sha256()
        sha.update((str(self.index) +str(self.timestamp) +
                   str(self.transactions) +str(self.nonce) +
                   str(self.previous_hash)).encode())
        return sha.hexdigest()

    def mine(self, difficulty):
        while [v for v in self.hash[0:difficulty]] != ['0' for v in range(0, difficulty)]:
            self.nonce += 1
            self.hash = self.hash_block()
        print("mining success")

    def get_block(self):
        return {"index": self.index,
                "timestamp": self.timestamp,
                "transactions": self.transactions,
                "nonce": self.nonce,
                "previous hash": self.previous_hash,
                "hash":self.hash
                }

class Blockchain(object):
    def __init__(self):
        self.difficulty = 3
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        # create genesis block
        self.genesis_block = Block(0, time(), "Genesis Block", 0, "0")
        self.genesis_block.mine(self.difficulty)
        self.chain.append(self.genesis_block)

    def register_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self,chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            #check the hash of the block is correct
            if block.previous_hash != self.hash(last_block):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            '''
            todo: chain is list of dictionary
            '''
            if response.status_code == 200:
                chain_contents = response.json()['chain']
                if max_length < len(chain_contents):
                    new_chain = chain_contents
                    max_length = len(chain_contents)

            if new_chain:
                self.chain = new_chain
                return True

        return False

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
        self.current_transactions.append({'Sender':sender, 'Recipient':recipient, 'Amount':amount})

    def hash(block):
        block_string = json.dumps(block, sort_keys = True).encoded()
        return hashlib.sha256(block_string).hexdigest()

    def get_chain(self):
        chain_content = []
        for block in self.chain:
            chain_content.append(block.get_block())
        return chain_content


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-','')
blockchain = Blockchain()

@app.route('/transactions/new', methods=['POST'])
def new_transactions():
    transaction_data = request.get_json()
    blockchain.new_transaction(transaction_data['sender'],
                               transaction_data['recipient'],
                               transaction_data['amount'])
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
                'transactions':  new_block.transactions,
                'nonce': new_block.nonce,
                'previous_hash' : new_block.previous_hash
                }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.get_chain()
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_node():
    values = request.get_json()
    nodes = values.get("nodes")
    if nodes is None:
        return "Error:invalid nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'node_count': len(blockchain.nodes),
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response),201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response),200

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-H', '--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=5000, type=int)
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=True)

