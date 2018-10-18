import json
import time
from datetime import datetime
import hashlib
import ecdsa
import time
import random
from Transaction import Transaction
from Block import Block
class Blockchain:
	difficulty = 1
	def __init__(self):
		self.current_block_number = 0
		self.chain = {}
		self.previous_hash = None
		self.genesis_block = False
		self.past_transactions_hashes = []
		self.past_transactions = []
		self.create_genesis_block()#create the initial block

	def create_genesis_block(self):
		"""
		function to generate gensis block and append it to chain
		The block has index 0, previous hash as 0 
		and valid hash
		"""
		if self.genesis_block:
			return 'Genesis already'
		#Temporary block for the creator of the genesis block
		progenitor_privatekey = ecdsa.SigningKey.generate()
		progenitor_publickey = progenitor_privatekey.get_verifying_key()
		genesis_transaction = Transaction(progenitor_publickey, progenitor_privatekey, 50, 'Genesis transaction')
		self.previous_hash = 'genesis'
		block = Block([genesis_transaction])
		self.add(block)
		self.genesis_block = True
		return block
	def next_block_number(self):
		self.current_block_number += 1
		return self.current_block_number - 1
	def add(self, block,target_hash=None):
		"""
		A function that adds the block to the chain after verification
		"""
		block.timestamp = time.time()
		block.index = self.next_block_number()
		block.compute_hash()
		self.chain[block.hash] = block
		if target_hash:
			#add to chain at target block
			target_block = self.chain[target_hash]
			block.longest_link = target_block.longest_link + 1
			block.previous_hash = target_hash
			print(block.longest_link)
		else:
			#add to current running train
			block.longest_link += 1
			block.previous_hash = self.previous_hash
		self.previous_hash = block.hash
		self.past_transactions_hashes.extend(block.past_transaction_hashes)
		self.past_transactions.extend(block.past_transactions)
		print('Block {} created in chain at {}'.format(block.index, datetime.utcfromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')))
		print('Hash:', block.hash, '\n')
		print('Index', block.index, '\n')
	@staticmethod
	def validate(block, previous_block):
		"""
		check if block_hash is valid hash of block
		and satisfies the difficulty criteria
		"""
		if previous_block.index+1 > block.index:
			return False
		elif block.timestamp <= previous_block.timestamp:
			return False
		return True
	
	def resolve(self):
		counter = 0
		primeval_hash = None
		for i in self.chain:
			if self.chain[i].longest_link > counter:
				counter = self.chain[i].longest_link
				primeval_hash = self.chain[i]
		return primeval_hash
def verify_proof(entry, proof, root):
    # Verifies proof for entry and given root. Returns boolean.
    currhash = hashlib.sha256(entry).hexdigest()
    # print(currhash)
    print(proof)
    for i in proof:
        if(i[1] == "r"):
            newhash = currhash + i[0]
            currhash = hashlib.sha256(newhash.encode()).hexdigest()
            print(currhash, 'r')
        else:
            newhash =  i[0]+currhash
            currhash = hashlib.sha256(newhash.encode()).hexdigest()
            print(currhash, 'l')
    return root == currhash
