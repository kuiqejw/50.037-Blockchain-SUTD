import hashlib
import ecdsa
from Transaction import Transaction
from ecdsa import SigningKey
from Blockchain import Blockchain
from Block import Block, verify_proof
import time
import json

#     #What does SPV Client do?
#     #They ask for all transactions, associated with my public key
#     #Validates proof of work, and the previous header
#     #give me transactions if I'm sender or receiver. 
#     #Miner will give them prsent proof
#     #SpV client, not stroing all transactions, will validate that it's all in.
class SPVClient:
	def __init__(self, node_id=''):
		self.public_key = None
		self.private_key = None
		self.block_header = []
		self.node_id = node_id
		self.balance = 50
	def get_balance(self):
		return self.balance
	def get_private_key(self):
		return self.private_key
	def get_public_key(self):
		return self.public_key
	def create_keys(self):
		#Have their key pairs associated
		private_key, public_key = self.generate_keys()
		self.private_key = private_key
		self.public_key = public_key
		return private_key, public_key
	def save_keys(self):
		"""Saves the keys to a file (wallet.txt)"""
		if self.public_key is not None and self.private_key is not None:
			try:
				with open('wallet-{}.txt'.format(self.node_id), 'w') as f:
					f.write(self.public_key.to_string().hex())
					f.write('\n')
					f.write(self.private_key.to_string().hex())
				return True
			except Exception as E:
				print('Saving wallet failed')
				return False
	def generate_keys(self):
		sender = ecdsa.SigningKey.generate()
		sendervk = sender.get_verifying_key()
		return sender, sendervk
	def send_transaction(self, recipient, amount,comment):
		UTXO = Transaction(self.public_key, recipient, amount, comment)
		UTXO.sign(self.private_key)
		self.balance -= amount
		return UTXO
	def receive_transaction(self, transaction):
		UTXO = Transaction(transaction.sender, transaction.receiver, transaction.amount, transaction.comment)
		self.balance += transaction.amount
	def verify_transaction(self, transaction): #verifying your own transaction
		UTXO = Transaction(transaction.sender, transaction.receiver, transaction.amount, transaction.comment)
		verify = UTXO.validate(transaction.signature, self.public_key)
	def receive_bloc_header(self, blockchain):
		self.block_header = []
		for key, value in blockchain.chain.items():#traverse attribute chain, the dict in which blocks are stored
			self.block_header.append(value.to_json())#to_json will only download all of the headers, not the actual block
		return self.block_header
	def check_if_in(self, block, transaction):#3) Get proof
		#for the person to check that their transaction is in with an id. Returns boolean
	    return verify_proof(transaction, block.get_proof(transaction), block.get_root())
	def check_balance_of_pub(self, public_key, chain): 
		transactions_list = []
		balance = 0
		for v in chain.past_transactions:
		    if v.sender == public_key:
		        balance -= v.amount
		        transactions_list.append(v)
		    if v.receiver == public_key:
		        balance += v.amount
		        transactions_list.append(v)
		return balance
	#2) Transactions sent or received by them
	def grab_all_transactions(self, chain):
		transactions_list = []
		balance = 0
		for v in chain.past_transactions:
			if v.sender == self.public_key:
				print('sender b')
				transactions_list.append(v)
			elif v.receiver == self.public_key:
				transactions_list.append(v)
				print('receiver b')
		return transactions_list
	def check_transaction_in_chain(self, transaction, chain):
		i = transaction
		if not hashlib.sha256(i.to_json().encode()).hexdigest() in chain.past_transactions_hashes:
		    print('False', 'check_transact')
		else:
		    print('True','check_transact')

	def check_previous_header(self):
		#basically, check if it exists in self
		previous_hash_list = ['genesis']
		current_hash_list = []
		for z in self.block_header:
			dictz = json.loads(z)
			prev = dictz.get('previous')
			previous_hash_list.append(prev)
			hasher = dictz.get('hash')
			current_hash_list.append(hasher)
		for i in current_hash_list:
			if i not in previous_hash_list:
				return False
		return True
