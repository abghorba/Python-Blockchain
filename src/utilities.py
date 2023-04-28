import os

BLOCKCHAIN_CACHE_TXT_FILE = os.getcwd() + "/cache/blockchain.txt"
TEST_BLOCKCHAIN_CACHE_TXT_FILE = os.getcwd() + "/cache/test_blockchain.txt"
DEFAULT_DIFFICULTY = 3
MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK = 3


def check_data_is_valid_transaction(data):
    """
    Checks if data obtained from a POST request is a valid blockchain transaction.

    :param data: Data dictionary obtained from POST request
    :return: True if data is a valid transaction; False otherwise
    """

    if not isinstance(data, dict):
        print("data is not of type dict")
        return False

    if len(data) != 4:
        print("len(data) is not equal to 4")
        return False

    if "sender_id" not in data:
        print("sender_id not in data")
        return False

    if "receiver_id" not in data:
        print("receiver_id not in data")
        return False

    if "timestamp" not in data:
        print("timestamp not in data")
        return False

    if "amount" not in data:
        print("amount not in data")
        return False

    if not isinstance(data["sender_id"], str):
        print("sender_id is not of type str")
        return False

    if not isinstance(data["receiver_id"], str):
        print("receiver_id is not of type str")
        return False

    if not isinstance(data["timestamp"], float):
        print("timestamp is not of type float")
        return False

    if not isinstance(data["amount"], (int, float)):
        print("amount is not of type int or float")
        return False

    return True
