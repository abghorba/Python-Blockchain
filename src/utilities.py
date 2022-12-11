DEFAULT_DIFFICULTY = 1
MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK = 3


def check_data_is_valid_transaction(data):
    """
    Checks if data obtained from a POST request is a valid blockchain transaction.

    :param data: Data dictionary obtained from POST request
    :return: True if data is a valid transaction; False otherwise
    """

    if not isinstance(data, dict):
        return False

    if len(data) != 4:
        return False

    if not ("sender_id" in data and "receiver_id" in data and "timestamp" in data and "amount" in data):
        return False

    if not isinstance(data["sender_id"], str):
        return False

    if not isinstance(data["receiver_id"], str):
        return False

    if not isinstance(data["timestamp"], float):
        return False

    if not isinstance(data["amount"], (int, float)):
        return False

    return True
