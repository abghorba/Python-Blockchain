import os
import random
import string
import time

import pytest

from application import app
from src.blockchain import get_current_blockchain
from src.utilities import MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK, TEST_BLOCKCHAIN_CACHE_TXT_FILE

app.config["TESTING"] = True


@pytest.fixture(autouse=True)
def clear_blockchain_cache():
    """Clears the blockchain cache before each test."""

    with open(TEST_BLOCKCHAIN_CACHE_TXT_FILE, "w") as file:
        time.sleep(1)


class TestAppRouteGetChain:
    def test_get_chain(self):
        """Tests that the /chain app route works as intended."""
        response = app.test_client().get("/chain")

        assert response.status_code == 200
        assert isinstance(response.data.decode("utf-8"), str)

    def test_get_chain_multiple_requests_per_second(self):
        """Tests that the /chain app route can handle multiple requests per second successfully."""

        number_of_iterations = 100

        for iteration in range(number_of_iterations):
            response = app.test_client().get("/chain")

            assert response.status_code == 200
            assert isinstance(response.data.decode("utf-8"), str)


class TestAppRouteAddTransactionToBlockchain:
    def test_add_valid_transaction(self):
        """Tests that the /send app route returns status code 200 with a valid transaction."""

        sender_id = "0x1234ABCD"
        receiver_id = "0xABCD1234"
        timestamp = 123456789.999
        amount = 0.99

        transaction = {"sender_id": sender_id, "receiver_id": receiver_id, "timestamp": timestamp, "amount": amount}

        response = app.test_client().post("/send", json=transaction)
        data = response.data.decode("utf-8")

        assert response.status_code == 200
        assert isinstance(data, str)
        assert sender_id in data
        assert receiver_id in data
        assert str(timestamp) in data
        assert str(amount) in data

        # Check that there are 0 blocks and 1 unconfirmed transaction added to the blockchain
        blockchain = get_current_blockchain(TEST_BLOCKCHAIN_CACHE_TXT_FILE)

        # Exclude genesis block
        assert len(blockchain.chain) - 1 == 0
        assert len(blockchain.unconfirmed_transactions) == 1

    def test_add_invalid_transaction(self):
        """Tests that the /send app route returns status code 400 with an invalid transaction."""

        # Send sender_id as an int instead of a str to create invalid transaction
        sender_id = 0x1234ABCD
        receiver_id = "0xABCD1234"
        timestamp = 123456789.999
        amount = 99999.99

        transaction = {"sender_id": sender_id, "receiver_id": receiver_id, "timestamp": timestamp, "amount": amount}

        response = app.test_client().post("/send", json=transaction)
        data = response.data.decode("utf-8")

        assert response.status_code == 400
        assert isinstance(data, str)
        assert "Invalid Transaction!" in data

        # Check that there are 0 blocks and 0 unconfirmed transaction added to the blockchain
        blockchain = get_current_blockchain(TEST_BLOCKCHAIN_CACHE_TXT_FILE)

        # Exclude genesis block
        assert len(blockchain.chain) - 1 == 0
        assert len(blockchain.unconfirmed_transactions) == 0

    def test_add_min_number_of_transactions_per_block_creates_new_block(self):
        sender_id = "0x1234ABCD"
        receiver_id = "0xABCD1234"
        amount = 99999.99

        for iteration in range(MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK):
            timestamp = time.time()

            transaction = {"sender_id": sender_id, "receiver_id": receiver_id, "timestamp": timestamp, "amount": amount}

            response = app.test_client().post("/send", json=transaction)
            assert response.status_code == 200

        blockchain = get_current_blockchain(TEST_BLOCKCHAIN_CACHE_TXT_FILE)

        # Exclude genesis block
        assert len(blockchain.chain) - 1 == 1
        assert len(blockchain.unconfirmed_transactions) == 0

    def test_add_multiple_valid_transactions_per_second(self):
        """Tests that the /send app route returns status code 200 with a multiple valid transactions per second."""

        number_of_iterations = 100
        sender_id = "0x1234ABCD"
        receiver_id = "0xABCD1234"

        for iteration in range(number_of_iterations):
            timestamp = time.time()
            amount = 99999.99 + iteration

            transaction = {"sender_id": sender_id, "receiver_id": receiver_id, "timestamp": timestamp, "amount": amount}

            response = app.test_client().post("/send", json=transaction)
            data = response.data.decode("utf-8")

            assert response.status_code == 200
            assert isinstance(data, str)
            assert sender_id in data
            assert receiver_id in data
            assert str(timestamp) in data
            assert str(amount) in data

        # Check that the correct number of blocks and unconfirmed transactions have been added to the blockchain
        blockchain = get_current_blockchain(TEST_BLOCKCHAIN_CACHE_TXT_FILE)

        blocks, unconfirmed_transactions = divmod(number_of_iterations, MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK)

        # Exclude genesis block
        assert len(blockchain.chain) - 1 == blocks
        assert len(blockchain.unconfirmed_transactions) == unconfirmed_transactions

    def test_add_multiple_invalid_transactions_per_second(self):
        """Tests that the /send app route returns status code 400 with a multiple invalid transactions per second."""

        number_of_iterations = 100

        # Send sender_id as an int instead of a str to create invalid transaction
        sender_id = 0x1234ABCD
        receiver_id = "0xABCD1234"

        for iteration in range(number_of_iterations):
            timestamp = time.time()
            amount = 99999.99 + iteration

            transaction = {"sender_id": sender_id, "receiver_id": receiver_id, "timestamp": timestamp, "amount": amount}

            response = app.test_client().post("/send", json=transaction)
            data = response.data.decode("utf-8")

            assert response.status_code == 400
            assert isinstance(data, str)
            assert "Invalid Transaction!" in data

        # Check that there are no added blocks or unconfirmed transactions in the blockchain
        blockchain = get_current_blockchain(TEST_BLOCKCHAIN_CACHE_TXT_FILE)

        # Exclude genesis block
        assert len(blockchain.chain) - 1 == 0
        assert len(blockchain.unconfirmed_transactions) == 0

    @pytest.mark.parametrize("invalid_pct,valid_pct", [(0, 100), (20, 80), (40, 60), (60, 40), (80, 20), (100, 0)])
    def test_add_multiple_valid_and_invalid_transactions_per_second(self, invalid_pct, valid_pct):
        """
        Tests that the /send app route returns appropriate status codes with a mix of multiple valid/invalid
        transactions per second.

        :param invalid_pct: Percent of operations that are invalid
        :param valid_pct: Percent of operations that are valid
        :return: None
        """

        number_of_iterations = 100
        valid_sender_id = "0xFFFFFFFF"
        invalid_sender_id = 0x00000001
        receiver_id = "0xABCD1234"

        sender_id_list = [valid_sender_id, invalid_sender_id]
        weights = [invalid_pct / 100.0, valid_pct / 100.0]

        valid_transactions = 0
        invalid_transactions = 0

        for iteration in range(number_of_iterations):
            # Choose sender_id based on a weighted probability
            sender_id = random.choices(sender_id_list, weights=weights)[0]
            print(sender_id)

            timestamp = time.time()
            amount = 99999.99 + iteration

            transaction = {"sender_id": sender_id, "receiver_id": receiver_id, "timestamp": timestamp, "amount": amount}

            response = app.test_client().post("/send", json=transaction)
            data = response.data.decode("utf-8")

            # Invalid transaction
            if sender_id == invalid_sender_id:
                assert response.status_code == 400
                assert isinstance(data, str)
                assert "Invalid Transaction!" in data
                invalid_transactions += 1

            # Valid transaction
            else:
                assert response.status_code == 200
                assert isinstance(data, str)
                assert valid_sender_id in data
                assert receiver_id in data
                assert str(timestamp) in data
                assert str(amount) in data
                valid_transactions += 1

        # Check that the correct number of blocks and unconfirmed transactions have been added to the blockchain
        blockchain = get_current_blockchain(TEST_BLOCKCHAIN_CACHE_TXT_FILE)

        blocks, unconfirmed_transactions = divmod(valid_transactions, MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK)

        # Exclude genesis block
        assert len(blockchain.chain) - 1 == blocks
        assert len(blockchain.unconfirmed_transactions) == unconfirmed_transactions

        # Log the actual percentages of each operation
        print(f"Percent of Valid Transactions = {valid_transactions/number_of_iterations * 100}%")
        print(f"Percent of Invalid Transactions = {invalid_transactions/number_of_iterations * 100}%")


class TestAppInvalidRoutes:
    def test_invalid_route(self):
        """Verifies that invalid app routes return 404 status code."""

        number_of_iterations = 10

        for iteration in range(number_of_iterations):
            # Generate random strings of length 10
            random_string = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

            response = app.test_client().get("/" + random_string)
            assert response.status_code == 404
