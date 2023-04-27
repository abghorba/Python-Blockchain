import json

from flask import Flask, request

from src.blockchain import get_current_blockchain
from src.utilities import BLOCKCHAIN_CACHE_TXT_FILE, check_data_is_valid_transaction

app = Flask(__name__)
blockchain = get_current_blockchain(BLOCKCHAIN_CACHE_TXT_FILE)


@app.route("/chain", methods=["GET"])
def get_chain():
    """
    Get JSON formatted string of the current blockchain.

    Get the current blockchain:

        curl http://127.0.0.1:5000/chain

    :return: JSON formatted string of the current blockchain or error message
    """

    try:
        return json.dumps(blockchain.__dict__(), indent=4) + "\n"

    except:
        return "FAILURE"


@app.route("/send", methods=["POST"])
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
            return (
                "Invalid Transaction! Transaction must be of form:\n "
                '{"sender_id": str, "receiver_id": str, "timestamp": float, "amount": float}\n'
            )

        transaction_details = blockchain.add_new_transaction(
            data["sender_id"], data["receiver_id"], data["timestamp"], data["amount"]
        )

        blockchain.mine()

        with open(BLOCKCHAIN_CACHE_TXT_FILE, "w") as file:
            file.write(json.dumps(blockchain.__dict__(), indent=4) + "\n")

        return json.dumps(transaction_details.data, indent=4) + "\n"

    except:
        return "FAILURE"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
