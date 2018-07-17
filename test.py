'''
blockchain = Blockchain()
blockchain.new_transaction("a", "b", 10)
blockchain.new_transaction("c", "d", 10)
blockchain.new_transaction("c", "d", 10)
blockchain.new_block()
block = blockchain.last_block()
transaction_contents = ""
for i in range(len(block.data)):
    transaction = block.data[i]
    transaction_contents = transaction_contents + transaction.transaction_contents()
print(transaction_contents)

for x in range(len(block.data)):
    transaction = block.data[x];
    print(transaction.transaction_contents())
print(block.previous_hash)
print(block.hash)
'''
