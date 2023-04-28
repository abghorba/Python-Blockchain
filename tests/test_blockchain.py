import os
import time

import pytest

from src.blockchain import Block, Blockchain, Transaction, get_current_blockchain
from src.utilities import DEFAULT_DIFFICULTY, MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK


class TestTransaction:
    def test_initialize_transaction_invalid_parameters(self):
        """Tests that initializing a Transaction object with invalid parameters fails as expected."""

        with pytest.raises(TypeError) as err:
            Transaction(1000, "Andrew2.0", time.time(), 999.99)
            assert "ERROR: param sender_id must be of type str" == str(err.value)

        with pytest.raises(TypeError) as err:
            Transaction("Andrew", 2000, time.time(), 999.99)
            assert "ERROR: param receiver_id must be of type str" == str(err.value)

        with pytest.raises(TypeError) as err:
            Transaction("Andrew", "Andrew2.0", "10:00PM", 999.99)
            assert "ERROR: param timestamp must be of type float" == str(err.value)

        with pytest.raises(TypeError) as err:
            Transaction("Andrew", "Andrew2.0", time.time(), "999.99")
            assert "ERROR: param amount must be of type int or float" == str(err.value)

    def test_initialize_transaction_valid_parameters(self):
        """Tests initializing a Transaction object with valid parameters is as expected."""

        transaction = Transaction("Andrew", "Andrew2.0", time.time(), 999.99)

        assert isinstance(transaction, Transaction)
        assert isinstance(transaction.sender_id, str)
        assert isinstance(transaction.receiver_id, str)
        assert isinstance(transaction.timestamp, float)
        assert isinstance(transaction.amount, (int, float))
        assert isinstance(transaction.data, dict)
        assert "sender_id" in transaction.data
        assert "receiver_id" in transaction.data
        assert "timestamp" in transaction.data
        assert "amount" in transaction.data


class TestBlock:
    def test_initialize_block_invalid_parameters(self):
        """Tests that initializing a Block object with invalid parameters fails as expected."""

        with pytest.raises(TypeError) as err:
            Block("0", [], "0xFFFFFFFF", time.time(), 0)
            assert "ERROR: param index must be of type int" == str(err.value)

        with pytest.raises(TypeError) as err:
            Block(0, {}, "0xFFFFFFFF", time.time(), 0)
            assert "ERROR: param transactions must be of type list" == str(err.value)

        with pytest.raises(TypeError) as err:
            Block(0, [], 0xFFFFFFFF, time.time(), 0)
            assert "ERROR: param previous_hash must be of type str" == str(err.value)

        with pytest.raises(TypeError) as err:
            Block(0, [], "0xFFFFFFFF", "10:00PM", 0)
            assert "ERROR: param timestamp must be of type int or float" == str(err.value)

        with pytest.raises(TypeError) as err:
            Block(0, [], "0xFFFFFFFF", time.time(), "0")
            assert "ERROR: param nonce must be of type int" == str(err.value)

    def test_initialize_block_valid_parameters(self):
        """Tests initializing a Transaction object with valid parameters is as expected."""

        block = Block(0, [], "0xFFFFFFFF", time.time(), 0)

        assert isinstance(block, Block)
        assert isinstance(block.index, int)
        assert isinstance(block.transactions, list)
        assert isinstance(block.timestamp, float)
        assert isinstance(block.previous_hash, str)
        assert isinstance(block.nonce, int)

    def test_compute_hash(self):
        """Tests Transaction.compute_hash() is as expected."""

        block = Block(0, [], "0xFFFFFFFF", time.time(), 0)

        block_hash = block.compute_hash()
        assert isinstance(block_hash, str)
        assert len(block_hash) > 0


class TestBlockchain:
    def test_initialize_blockchain_invalid_parameters(self):
        """Tests that initializing a Blockchain object with invalid parameters fails as expected."""

        with pytest.raises(TypeError) as err:
            Blockchain("1")
            assert "ERROR: param difficulty must be of type int" in str(err.value)

        with pytest.raises(ValueError) as err:
            Blockchain(-1)
            assert "ERROR: param difficulty must be greater than 0" in str(err.value)

    def test_initialize_blockchain_valid_parameters(self):
        """Tests initializing a Blockchain object with valid parameters is as expected."""

        blockchain = Blockchain()

        assert isinstance(blockchain, Blockchain)
        assert isinstance(blockchain.difficulty, int)
        assert blockchain.difficulty == DEFAULT_DIFFICULTY
        assert isinstance(blockchain.unconfirmed_transactions, list)
        assert len(blockchain.unconfirmed_transactions) == 0
        assert isinstance(blockchain.chain, list)
        assert len(blockchain.chain) == 1
        assert isinstance(blockchain.last_block, Block)
        assert blockchain.last_block.index == 0

    def test_blockchain_to_dict(self):
        """Tests Blockchain.__dict__() works as intended."""

        blockchain = Blockchain()

        blockchain_dict = blockchain.__dict__()

        chain_data = []

        for block in blockchain.chain:
            chain_data.append(block.__dict__)

        assert blockchain_dict["difficulty"] == blockchain.difficulty
        assert blockchain_dict["unconfirmed_transactions"] == blockchain.unconfirmed_transactions
        assert blockchain_dict["length"] == len(blockchain.chain)
        assert blockchain_dict["chain"] == chain_data

    def test_proof_of_work_invalid_parameters(self):
        """Tests Blockchain.proof_of_work() with invalid parameters fails as expected."""

        blockchain = Blockchain()

        with pytest.raises(TypeError) as err:
            blockchain.proof_of_work("block")
            assert "ERROR: param block must be of type Block" in str(err.value)

    def test_proof_of_work(self):
        """Tests Blockchain.proof_of_work() is as expected."""

        test_difficulty = 3
        blockchain = Blockchain(test_difficulty)
        block = Block(1, [], "0xFFFFFFFF", time.time(), 0)
        computed_hash = blockchain.proof_of_work(block)

        assert isinstance(computed_hash, str)
        assert len(computed_hash) > 0
        assert computed_hash.startswith("0" * blockchain.difficulty)
        assert block.nonce > 0

    def test_is_valid_proof_invalid_parameters(self):
        """Tests Blockchain.is_valid_proof() with invalid parameters fails as expected."""

        blockchain = Blockchain()
        block = Block(1, [], "0xFFFFFFFF", time.time(), 0)

        with pytest.raises(TypeError) as err:
            blockchain.is_valid_proof("block", "0xFFFFFFFF")
            assert "ERROR: param block must be of type Block" == str(err.value)

        with pytest.raises(TypeError) as err:
            blockchain.is_valid_proof(block, 0xFFFFFFFF)
            assert "ERROR: param proof must be of type str" == str(err.value)

    def test_is_valid_proof_correct_proof(self):
        """Tests Blockchain.is_valid_proof() returns True with a correct proof."""

        blockchain = Blockchain()
        block = Block(1, [], "0xFFFFFFFF", time.time(), 0)
        proof = blockchain.proof_of_work(block)

        assert blockchain.is_valid_proof(block, proof)

    def test_is_valid_proof_incorrect_proof(self):
        """Tests Blockchain.is_valid_proof() returns False with an incorrect proof."""

        blockchain = Blockchain()
        block = Block(1, [], "0xFFFFFFFF", time.time(), 0)
        proof = blockchain.proof_of_work(block).replace("0", "1")

        assert not blockchain.is_valid_proof(block, proof)

    def test_add_block_invalid_parameters(self):
        """Tests Blockchain.add_block() with invalid parameters fails as expected."""

        blockchain = Blockchain()
        block = Block(1, [], "0xFFFFFFFF", time.time(), 0)

        with pytest.raises(TypeError) as err:
            blockchain.is_valid_proof("block", "0xFFFFFFFF")
            assert "ERROR: param block must be of type Block" == str(err.value)

        with pytest.raises(TypeError) as err:
            blockchain.is_valid_proof(block, 0xFFFFFFFF)
            assert "ERROR: param proof must be of type str" == str(err.value)

    def test_add_block_incorrect_previous_hash(self):
        """
        Tests Blockchain.add_block() returns False when the block's previous_hash is not equal to
        Blockchain.last_block.compute_hash()
        """
        blockchain = Blockchain()
        block = Block(1, [], "0xFFFFFFFF", time.time(), 0)
        proof = blockchain.proof_of_work(block)

        assert not blockchain.add_block(block, proof)
        assert blockchain.last_block is not block
        assert len(blockchain.chain) == 1

    def test_add_block_incorrect_proof(self):
        """Tests Blockchain.add_block() returns False when the block's proof is not valid."""

        blockchain = Blockchain()
        block = Block(1, [], blockchain.last_block.compute_hash(), time.time(), 0)
        proof = blockchain.proof_of_work(block).replace("0", "1")

        assert not blockchain.add_block(block, proof)
        assert blockchain.last_block is not block
        assert len(blockchain.chain) == 1

    def test_add_block(self):
        """Tests Blockchain.add_block() is as expected."""

        blockchain = Blockchain()
        block = Block(1, [], blockchain.last_block.compute_hash(), time.time(), 0)
        proof = blockchain.proof_of_work(block)

        assert blockchain.add_block(block, proof)
        assert blockchain.last_block is block
        assert len(blockchain.chain) == 2

    def test_add_block_stress_test(self):
        """Tests Blockchain.add_block() by adding 1000 blocks into the blockchain."""

        blockchain = Blockchain()
        iterations = 1000

        for index in range(1, iterations + 1):
            block = Block(index, [], blockchain.last_block.compute_hash(), time.time(), 0)
            proof = blockchain.proof_of_work(block)

            assert blockchain.add_block(block, proof)
            assert blockchain.last_block is block
            assert len(blockchain.chain) == index + 1

    def test_add_new_transaction_invalid_parameters(self):
        """Tests Blockchain.add_new_transaction() with invalid parameters fails as expected."""

        blockchain = Blockchain()

        with pytest.raises(TypeError) as err:
            blockchain.add_new_transaction(0xFFFFFFFF, "0x1FFFFFFF", time.time(), 999.99)
            assert "ERROR: param sender_id must be a str" == str(err.value)

        with pytest.raises(TypeError) as err:
            blockchain.add_new_transaction("0xFFFFFFFF", 0x1FFFFFFF, time.time(), 999.99)
            assert "ERROR: param receiver_id must be a str" == str(err.value)

        with pytest.raises(TypeError) as err:
            blockchain.add_new_transaction("0xFFFFFFFF", "0x1FFFFFFF", "10:00PM", 999.99)
            assert "ERROR: param timestamp must be a float" == str(err.value)

        with pytest.raises(TypeError) as err:
            blockchain.add_new_transaction("0xFFFFFFFF", "0x1FFFFFFF", time.time(), "999.99")
            assert "ERROR: param amount must be an int or float" == str(err.value)

    def test_add_new_transaction(self):
        """Tests Blockchain.add_new_transaction() is as expected."""

        blockchain = Blockchain()
        transaction = blockchain.add_new_transaction("0xFFFFFFFF", "0x1FFFFFFF", time.time(), 999.99)

        assert isinstance(transaction, Transaction)
        assert isinstance(transaction.sender_id, str)
        assert isinstance(transaction.receiver_id, str)
        assert isinstance(transaction.timestamp, float)
        assert isinstance(transaction.amount, (int, float))
        assert len(blockchain.unconfirmed_transactions) == 1
        assert isinstance(blockchain.unconfirmed_transactions[0], dict)
        assert transaction.data == blockchain.unconfirmed_transactions[0]

    def test_add_new_transaction_stress_test(self):
        """Tests Blockchain.add_new_transaction() by adding 1000 transactions into the list."""

        blockchain = Blockchain()
        iterations = 1000

        for iteration in range(1, iterations + 1):
            transaction = blockchain.add_new_transaction("0xFFFFFFFF", "0x1FFFFFFF", time.time(), 9.99 * iteration)

            assert isinstance(transaction, Transaction)
            assert isinstance(transaction.sender_id, str)
            assert isinstance(transaction.receiver_id, str)
            assert isinstance(transaction.timestamp, float)
            assert isinstance(transaction.amount, (int, float))
            assert len(blockchain.unconfirmed_transactions) == iteration
            assert isinstance(blockchain.unconfirmed_transactions[iteration - 1], dict)
            assert transaction.data == blockchain.unconfirmed_transactions[iteration - 1]

    def test_mine_with_insufficient_number_of_unconfirmed_transactions(self):
        """Tests Blockchain.mine() with an insufficient number of unconfirmed transactions returns False."""

        blockchain = Blockchain()
        blockchain.add_new_transaction("0xFFFFFFFF", "0x1FFFFFFF", time.time(), 9.99)

        previous_block_timestamp = blockchain.last_block.timestamp

        assert len(blockchain.unconfirmed_transactions) < MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK
        assert not blockchain.mine()

        assert len(blockchain.chain) == 1
        assert len(blockchain.unconfirmed_transactions) == 1

        # Should be the Genesis Block
        assert blockchain.last_block.index == 0
        assert blockchain.last_block.previous_hash == "0000"
        assert blockchain.last_block.timestamp == previous_block_timestamp
        assert len(blockchain.last_block.transactions) == 0

    def test_mine_with_sufficient_number_of_unconfirmed_transactions(self):
        """Tests Blockchain.mine() is as expected."""

        blockchain = Blockchain()

        for transaction_number in range(MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK):
            blockchain.add_new_transaction("0xFFFFFFFF", "0x1FFFFFFF", time.time(), 9.99 * transaction_number)

        previous_block_hash = blockchain.last_block.compute_hash()
        previous_block_timestamp = blockchain.last_block.timestamp
        current_transactions = blockchain.unconfirmed_transactions

        assert len(blockchain.unconfirmed_transactions) == MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK
        assert blockchain.mine()

        assert len(blockchain.chain) == 2
        assert len(blockchain.unconfirmed_transactions) == 0

        assert blockchain.last_block.index == 1
        assert blockchain.last_block.previous_hash == previous_block_hash
        assert blockchain.last_block.timestamp >= previous_block_timestamp
        assert blockchain.last_block.transactions == current_transactions

    def test_mine_stress_test(self):
        """Tests Blockchain.mine() is as expected after mining 1000 times successfully."""

        blockchain = Blockchain()
        iterations = 1000

        for iteration in range(1, iterations + 1):
            for transaction_number in range(MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK):
                blockchain.add_new_transaction("0xFFFFFFFF", "0x1FFFFFFF", time.time(), 9.99 * transaction_number)

            previous_block_index = blockchain.last_block.index
            previous_block_hash = blockchain.last_block.compute_hash()
            previous_block_timestamp = blockchain.last_block.timestamp
            current_transactions = blockchain.unconfirmed_transactions

            assert len(blockchain.unconfirmed_transactions) == MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK
            assert blockchain.mine()

            assert len(blockchain.chain) == iteration + 1
            assert len(blockchain.unconfirmed_transactions) == 0

            assert blockchain.last_block.index == previous_block_index + 1
            assert blockchain.last_block.previous_hash == previous_block_hash
            assert blockchain.last_block.timestamp >= previous_block_timestamp
            assert blockchain.last_block.transactions == current_transactions


def test_get_cached_blockchain_nonexistent_txt_file():
    """Tests that get_current_blockchain() works as intended when blockchain_txt_file doesn't exist."""

    test_cache_file = os.getcwd() + "/cache/nonexistent.txt"
    assert not os.path.exists(test_cache_file)

    cached_blockchain = get_current_blockchain(test_cache_file)
    blockchain = Blockchain()

    assert cached_blockchain.difficulty == blockchain.difficulty
    assert cached_blockchain.unconfirmed_transactions == blockchain.unconfirmed_transactions
    assert len(cached_blockchain.chain) == len(blockchain.chain)
    assert cached_blockchain.last_block.index == blockchain.last_block.index
    assert cached_blockchain.last_block.transactions == blockchain.last_block.transactions
    assert cached_blockchain.last_block.timestamp <= blockchain.last_block.timestamp
    assert cached_blockchain.last_block.previous_hash == blockchain.last_block.previous_hash
    assert cached_blockchain.last_block.nonce == blockchain.last_block.nonce


def test_get_cached_blockchain_empty_cached_file():
    """Tests that get_current_blockchain() works as intended when blockchain_txt_file is empty."""

    test_cache_file = os.getcwd() + "/cache/empty_blockchain.txt"
    cached_blockchain = get_current_blockchain(test_cache_file)
    blockchain = Blockchain()

    assert cached_blockchain.difficulty == blockchain.difficulty
    assert cached_blockchain.unconfirmed_transactions == blockchain.unconfirmed_transactions
    assert len(cached_blockchain.chain) == len(blockchain.chain)
    assert cached_blockchain.last_block.index == blockchain.last_block.index
    assert cached_blockchain.last_block.transactions == blockchain.last_block.transactions
    assert cached_blockchain.last_block.timestamp <= blockchain.last_block.timestamp
    assert cached_blockchain.last_block.previous_hash == blockchain.last_block.previous_hash
    assert cached_blockchain.last_block.nonce == blockchain.last_block.nonce


def test_get_cached_blockchain_valid_cache_file():
    """Tests that get_current_blockchain() works as intended when blockchain_txt_file is valid."""

    test_cache_file = os.getcwd() + "/cache/sample_blockchain.txt"
    cached_blockchain = get_current_blockchain(test_cache_file)

    # Values are taken from cache/sample_blockchain.txt
    assert cached_blockchain.difficulty == 3
    assert cached_blockchain.unconfirmed_transactions == [
        {"sender_id": "", "receiver_id": "", "timestamp": 0.0, "amount": 0.0},
        {"sender_id": "", "receiver_id": "", "timestamp": 0.0, "amount": 0.0},
    ]
    assert len(cached_blockchain.chain) == 11
    assert cached_blockchain.last_block.index == 10
    assert cached_blockchain.last_block.transactions == [
        {"sender_id": "A", "receiver_id": "B", "timestamp": 0.0, "amount": 0.0},
        {"sender_id": "A", "receiver_id": "B", "timestamp": 0.0, "amount": 0.0},
        {"sender_id": "A", "receiver_id": "B", "timestamp": 0.0, "amount": 0.0},
    ]
    assert cached_blockchain.last_block.timestamp <= 1670746118.523479
    assert (
        cached_blockchain.last_block.previous_hash == "00003638464f452c5e9df0de5fb20fbad4b02b1b6698d8789246139efeb65965"
    )
    assert cached_blockchain.last_block.nonce == 1689
