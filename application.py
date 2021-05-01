from blockchain import *
from flask import Flask, request
import requests

app =  Flask(__name__)
blockchain = Blockchain()

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                      "chain": chain_data})

@app.route('/send', methods=['POST'])
def add_transaction_to_blockchain():
    start_time = time.time()
    transaction = request.get_json()
    blockchain.add_new_transaction(transaction)
    if len(blockchain.unconfirmed_transactions) == 3:
        blockchain.mine()
    return transaction

app.run(debug=True, port=5000)