import hashlib
import time
from typing import List, Dict
from fastapi import FastAPI

app = FastAPI()
"""
To represent each block in the chain which has data and hash.
It includes the position of the block(index) then, hash of the previous block,
the timestamp of the blocks creation, 
the transactions in the block and 
the block's hash
"""
class Block:
    def __init__(self, index: int, previous_hash: str, timestamp: str, transactions: List[Dict], block_hash: str):
        self.index = index 
        self.previous_hash = previous_hash  
        self.timestamp = timestamp  
        self.transactions = transactions  
        self.block_hash = block_hash  
"""
A class that manages the blockchain and operations such as adding blocks and transactions.
It includes lists to store the blocks in the chain and for keeping trace of the transactions waiting to be mined.
the timestamp of the blocks creation, 
the transactions in the bloakc and 
the block's hash
"""

class Blockchain:
    def __init__(self):
        self.chain = []  
        self.pending_transactions = []  
        # Create genesis block.
        self.create_new_block(previous_hash="1", block_hash="genesis_hash")

    def create_new_block(self, previous_hash: str, block_hash: str) -> Block:
        """
        Create a new block and add it to the blockchain.
        This method initializes a new block using the current pending transactions.
        This function increments index for every block and includes all the data needed for the chain
        (i.e hash of the block before and this block, timestamp, and the pending transactions.)
        It also adds the block to the chain.
        """
        block = Block(
            index=len(self.chain) + 1,  
            previous_hash=previous_hash,  
            timestamp=str(time.time()), 
            transactions=self.pending_transactions,  
            block_hash=block_hash, 
        )
        self.chain.append(block) 
        self.pending_transactions = []  #
        return block

    def get_last_block(self) -> Block:
        """
        Fetch the last(recent) block in the chain if it is not empty.
        """
        return self.chain[-1] if self.chain else None 

    def calculate_block_hash(self, block: Block) -> str:
        """
        Calculate a SHA-256 hash hash for a given block using its content(the data the blocks have).
        """
        block_contents = f"{block.index}{block.previous_hash}{block.timestamp}{block.transactions}"

        return hashlib.sha256(block_contents.encode('utf-8')).hexdigest()

    def validate_block(self, block: Block, previous_block: Block) -> bool:
        """
        This function checks block validity by comparing its properties with the previous block.
      
        """
   
        if block.previous_hash != previous_block.block_hash:
            return False
        calculated_block_hash = self.calculate_block_hash(block)
        if block.block_hash != calculated_block_hash:
            return False
        return True  

# blockchain instance
blockchain = Blockchain()

@app.get("/")
def read_root():
    """Display a welcome message for the Blockchain API."""
    return {"message": "Welcome "}

@app.get("/chain")
def get_chain():
    """
    Retrieve the entire blockchain.
    i.e. each block is converted to dictionary.
    """
    return {"chain": [block.__dict__ for block in blockchain.chain]}

@app.get("/block/{index}")
def get_block_by_index(index: int):
    """
    Fetch a specific block by its index.
    This is an additional functionality I implemneted just to check how it works.
    """
    if 0 < index <= len(blockchain.chain):
        return {"block": blockchain.chain[index - 1].__dict__}
    else:
        return {"message": "Block not found"}

@app.post("/mine_block")
def mine_block():
    """
    Create a new block by mining it.
    
    """
    previous_block = blockchain.get_last_block()  
    block_hash = blockchain.calculate_block_hash(previous_block) if previous_block else "genesis_hash"

    new_block = blockchain.create_new_block(
        previous_hash=previous_block.block_hash if previous_block else "1", 
        block_hash=block_hash
    )
    return {"message": "mined!", "block": new_block.__dict__}

@app.post("/new_transaction")
def new_transaction(sender: str, receiver: str, amount: float, input_utxos: List[Dict], output_utxos: List[Dict], signature: str):
    """
    Add a new transaction to the pending transactions list.
    """
    transaction = {
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "input_utxos": input_utxos,
        "output_utxos": output_utxos,
        "signature": signature,
    }
    blockchain.pending_transactions.append(transaction)  # the one that adds to the pedning transactions.
    return {"message": "Transaction added", "transaction": transaction}

@app.post("/add_block")
def add_block(block: Dict):
    """
    Validate a bloack and add a block received from another node to the chain.
    Works by converting the dict to block object then getting the last block and appending
    """
    received_block = Block(**block)
    previous_block = blockchain.get_last_block()  
    if previous_block is None or blockchain.validate_block(received_block, previous_block):
        blockchain.chain.append(received_block)  
        return {"message": "Block added to the chain", "block": block}
    else:
        return {"message": "Invalid block", "block": block}
