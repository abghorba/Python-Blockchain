import time

import pytest

from src.utilities import check_data_is_valid_transaction


@pytest.mark.parametrize(
    "data",
    [
        {"sender_id": "", "receiver_id": "", "timestamp": 0.0, "amount": 0.0},
        {"sender_id": "Andrew", "receiver_id": "Andrew2.0", "timestamp": time.time(), "amount": 999.99},
        {"sender_id": "Andrew2.0", "receiver_id": "", "timestamp": time.time(), "amount": 0.0}
    ],
)
def test_check_data_is_valid_transaction_with_valid_data(data):
    """Tests check_data_is_valid_transaction() returns True with valid data."""

    assert check_data_is_valid_transaction(data)


@pytest.mark.parametrize(
    "data",
    [
        None,
        [],
        {"sender_id": "Andrew", "receiver_id": "Andrew2.0", "timestamp": time.time()},
        {"sender_id": "Andrew", "receiver_id": "Andrew2.0", "timestamp": time.time(), "amount": 999.99, "extra": ""},
        {"sender": "Andrew", "receiver_id": "Andrew2.0", "timestamp": time.time(), "amount": 999.99},
        {"sender_id": "Andrew", "receiver": "Andrew2.0", "timestamp": time.time(), "amount": 999.99},
        {"sender_id": "Andrew", "receiver_id": "Andrew2.0", "time": time.time(), "amount": 999.99},
        {"sender_id": "Andrew", "receiver": "Andrew2.0", "timestamp": time.time(), "quantity": 999.99},
        {"sender_id": 100, "receiver_id": "Andrew2.0", "timestamp": time.time(), "amount": 999.99},
        {"sender_id": "Andrew", "receiver_id": 100, "timestamp": time.time(), "amount": 999.99},
        {"sender_id": "Andrew", "receiver_id": "Andrew2.0", "timestamp": "10:00PM", "amount": 999.99},
        {"sender_id": "Andrew", "receiver_id": "Andrew2.0", "timestamp": time.time(), "amount": "999.99"},
    ],
)
def test_check_data_is_valid_transaction_with_invalid_data(data):
    """Tests check_data_is_valid_transaction() returns False with invalid data."""

    assert not check_data_is_valid_transaction(data)
