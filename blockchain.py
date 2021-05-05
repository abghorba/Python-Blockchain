from hashlib import sha256
import json
import time

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        """
        Constructs the block instance.
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """
        Computes the hash of the block.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

class Blockchain: 
    def __init__(self):
        """
        Constructs the blockchain instance with a genesis block.
        """
        self.difficulty = 1
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Creates the first block, or "genesis" block in the blockchain.
        """
        genesis_block = Block(0, [], time.time(), "0000")
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """
        Gets the last block in the blockchain.
        """
        return self.chain[-1]

    def increase_difficulty(self):
        """
        Increases the difficulty for the proof-of-work algorithm.
        """
        self.difficulty += 1

    def proof_of_work(self, block):
        """
        Solves for the block's nonce that will generate a valid hash.
        """
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block, proof):
        """
        Adds a block to the blockchain if and only if the hash of last block in the blockchain
        is equal to the previous_hash attribute of the provided block and if the proof
        provided is valid.
        """
        previous_hash = self.last_block.compute_hash()
        if previous_hash == block.previous_hash and self.is_valid_proof(block, proof):
            self.chain.append(block)
            return True
        return False

    def is_valid_proof(self, block, proof):
        """
        Determines if the proof provided has the correct leading number of zero bits
        and if the proof equals the provided block's hash.
        """
        return (proof.startswith('0' * self.difficulty) and
                proof == block.compute_hash())

    def add_new_transaction(self, transaction):
        """
        Appends a new transaction to the unconfirmed transaction list.
        """
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        """
        Creates a new block with the unconfirmed transactions and calculates
        a proof in order to add the block onto the blockchain.
        """
        if not self.unconfirmed_transactions:
            return False
        last_block = self.last_block
        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.compute_hash())
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index