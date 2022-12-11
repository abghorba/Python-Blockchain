import json
from flask import Flask, request

from src.blockchain import Blockchain
from src.utilities import check_data_is_valid_transaction

app = Flask(__name__)
blockchain = Blockchain()


@app.route('/chain', methods=['GET'])
def get_chain():
    """
    Get JSON formatted string of the current blockchain.

    Get the current blockchain:

        curl http://127.0.0.1:5000/chain

    :return: JSON formatted string of the current blockchain
    """

    chain_data = []

    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    return json.dumps({"length": len(chain_data), "chain": chain_data}, indent=4) + '\n'


@app.route('/send', methods=['POST'])
def add_transaction_to_blockchain():
    """
    Adds transaction into unconfirmed transactions list. If the unconfirmed transactions list exceeds the minimum
    number of transactions needed for a block, attempt to mine the block.

    Send a transaction by using command line:

        curl http://127.0.0.1:5000/send -H 'Content-Type: application/json' -d '{"sender_id": "", "receiver_id": "", "timestamp": 0.0, "amount": 0.0}'

    :return: JSON formatted string of transaction details or error message
    """

    try:

        data = request.get_json()

        if not check_data_is_valid_transaction(data):

            return "Invalid Transaction! Transaction must be of form:\n " \
                   "{\"sender_id\": str, \"receiver_id\": str, \"timestamp\": float, \"amount\": float}\n"

        transaction_details = \
            blockchain.add_new_transaction(data["sender_id"], data["receiver_id"], data["timestamp"], data["amount"])

        blockchain.mine()

        return json.dumps(transaction_details.data, indent=4) + '\n'

    except:

        return "Failure!"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
