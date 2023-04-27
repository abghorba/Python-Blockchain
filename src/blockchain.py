import json
import os
import time
from hashlib import sha256

from src.utilities import BLOCKCHAIN_CACHE_TXT_FILE, DEFAULT_DIFFICULTY, MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK


class Transaction:
    def __init__(self, sender_id, receiver_id, timestamp, amount):
        """
        Constructs the Transaction instance.

        :param sender_id: Sender ID
        :param receiver_id: Receiver ID
        :param timestamp: Timestamp of the transaction
        :param amount: Amount transacted
        """

        if not isinstance(sender_id, str):
            raise TypeError("ERROR: param sender_id must be of type str")

        if not isinstance(receiver_id, str):
            raise TypeError("ERROR: param receiver_id must be of type str")

        if not isinstance(timestamp, float):
            raise TypeError("ERROR: param timestamp must be of type float")

        if not isinstance(amount, (int, float)):
            raise TypeError("ERROR: param amount must be of type int or float")

        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.timestamp = timestamp
        self.amount = amount

    @property
    def data(self):
        """Returns transaction data as a dictionary."""

        return {
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "timestamp": self.timestamp,
            "amount": self.amount,
        }


class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=time.time(), nonce=0):
        """
        Constructs the Block instance.

        :param index: The index of the block
        :param transactions: List of transactions in the block
        :param previous_hash: The hash of the previous block
        :param timestamp: Timestamp of the block's creation
        :param nonce: Number used to change the block's hash
        """

        if not isinstance(index, int):
            raise TypeError("ERROR: param index must be of type int")

        if not isinstance(transactions, list):
            raise TypeError("ERROR: param transactions must be of type list")

        if not isinstance(previous_hash, str):
            raise TypeError("ERROR: param previous_hash must be of type str")

        if not isinstance(timestamp, (int, float)):
            raise TypeError("ERROR: param timestamp must be of type int or float")

        if not isinstance(nonce, int):
            raise TypeError("ERROR: param nonce must be of type int")

        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """
        Computes the hash of the block.

        :return: Returns the hash of the block as a string
        """

        block_string = json.dumps(self.__dict__, sort_keys=True)

        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self, difficulty=DEFAULT_DIFFICULTY):
        """
        Constructs the Blockchain instance with a genesis block.

        :param difficulty: The difficulty level of the proof-of-work algorithm
        """

        if not isinstance(difficulty, int):
            raise TypeError("ERROR: param difficulty must be of type int")

        if difficulty <= 0:
            raise ValueError("ERROR: param difficulty must be greater than 0")

        self.difficulty = difficulty
        self.unconfirmed_transactions = []
        self.chain = []
        self._create_genesis_block()

    def __dict__(self):
        """Returns blockchain attributes as a dictionary."""

        chain_data = []

        for block in self.chain:
            chain_data.append(block.__dict__)

        return {
            "difficulty": self.difficulty,
            "unconfirmed_transactions": self.unconfirmed_transactions,
            "length": len(chain_data),
            "chain": chain_data,
        }

    def _create_genesis_block(self):
        """Creates the first block, or "genesis" block in the blockchain."""

        genesis_block = Block(index=0, transactions=[], previous_hash="0000")
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """Gets the last block in the blockchain."""

        return self.chain[-1]

    def proof_of_work(self, block):
        """
        Solves for the block's nonce that will generate a valid hash.

        :param block: Block object
        :return: Valid hash of the block as a string
        """

        if not isinstance(block, Block):
            raise TypeError("ERROR: param block must be of type Block")

        computed_hash = block.compute_hash()

        # Increment nonce until the hash is valid
        while not computed_hash.startswith("0" * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def is_valid_proof(self, block, proof):
        """
        Determines if the proof provided has the correct leading number of zero bits and if the proof equals the
        provided block's hash.

        :param block: Block object
        :param proof: String representation of the block's hash
        :return: True if proof is valid; False otherwise
        """

        if not isinstance(block, Block):
            raise TypeError("ERROR: param block must be of type Block")

        if not isinstance(proof, str):
            raise TypeError("ERROR: param proof must be of type str")

        return proof.startswith("0" * self.difficulty) and proof == block.compute_hash()

    def add_block(self, block, proof):
        """
        Adds a block to the blockchain if and only if the hash of last block in the blockchain is equal to the
        previous_hash attribute of the provided block and if the proof provided is valid.

        :param block: Block object
        :param proof: String representation of the block's hash
        :return: True if block is added; False otherwise
        """

        if not isinstance(block, Block):
            raise TypeError("ERROR: param block must be of type Block")

        if not isinstance(proof, str):
            raise TypeError("ERROR: param proof must be of type str")

        previous_hash = self.last_block.compute_hash()

        if previous_hash == block.previous_hash and self.is_valid_proof(block, proof):
            self.chain.append(block)
            return True

        return False

    def add_new_transaction(self, sender_id, receiver_id, timestamp, amount):
        """
        Adds a new transaction into the unconfirmed transactions list.

        :param sender_id: String representing the Sender's identification address
        :param receiver_id: String representing the Receiver's identification address
        :param timestamp: Time of the transaction
        :param amount: Transacted amount
        :return: Transaction object
        """

        if not isinstance(sender_id, str):
            raise TypeError("ERROR: param sender_id must be a str")

        if not isinstance(receiver_id, str):
            raise TypeError("ERROR: param receiver_id must be a str")

        if not isinstance(timestamp, float):
            raise TypeError("ERROR: param timestamp must be a float")

        if not isinstance(amount, (int, float)):
            raise TypeError("ERROR: param amount must be an int or float")

        transaction_details = Transaction(sender_id, receiver_id, timestamp, amount)
        self.unconfirmed_transactions.append(transaction_details.data)

        return transaction_details

    def mine(self):
        """
        Creates a new block with the unconfirmed transactions and calculates a proof in order to add the block onto the
        blockchain.

        :return: True if the block is added successfully onto the blockchain; False otherwise
        """

        if len(self.unconfirmed_transactions) < MINIMUM_NUMBER_OF_TRANSACTIONS_PER_BLOCK:
            return False

        last_block = self.last_block

        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            previous_hash=last_block.compute_hash(),
        )

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []

        return True


def _parse_blockchain_from_txt_file(blockchain_txt_file=BLOCKCHAIN_CACHE_TXT_FILE):
    """
    Parses blockchain stored in cache/blockchain.txt to construct a Blockchain object.

    :param blockchain_txt_file: Path to the blockchain .txt file
    :return: parsed Blockchain object
    """

    with open(blockchain_txt_file, "r") as file:
        cached_blockchain = json.load(file)

    parsed_blockchain = Blockchain()

    # Blockchain object initializes with a genesis block, so remove it
    parsed_blockchain.chain.pop(0)

    parsed_blockchain.difficulty = int(cached_blockchain["difficulty"])
    parsed_blockchain.unconfirmed_transactions = cached_blockchain["unconfirmed_transactions"]

    for block in cached_blockchain["chain"]:
        parsed_block = Block(
            index=int(block["index"]),
            transactions=block["transactions"],
            timestamp=float(block["timestamp"]),
            previous_hash=block["previous_hash"],
            nonce=int(block["nonce"]),
        )

        parsed_blockchain.chain.append(parsed_block)

    return parsed_blockchain


def get_current_blockchain(blockchain_txt_file=BLOCKCHAIN_CACHE_TXT_FILE):
    """
    If a cached Blockchain exists, return it. Otherwise, return a newly initialized Blockchain.

    :param blockchain_txt_file: Path to the blockchain .txt file
    :return: Blockchain object
    """

    # Get cached blockchain if it exists
    if os.path.exists(blockchain_txt_file) and os.path.getsize(blockchain_txt_file) > 0:
        return _parse_blockchain_from_txt_file(blockchain_txt_file)

    # There is no cached blockchain, return a new one
    return Blockchain()
