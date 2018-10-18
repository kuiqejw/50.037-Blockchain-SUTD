import hashlib
import ecdsa
from Transaction import Transaction
from ecdsa import SigningKey
from Blockchain import Blockchain, verify_proof
from Block import Block
import time
class SPVClient:
	def __init__(self, node_id=''):
		self.private_key = None
		self.private_key = None
		self.node_id = node_id
		self.block_header = []
		self.balance = 0
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
					f.write((self.public_key.to_string()).hex())
					f.write('\n')
					f.write((self.private_key.to_string()).hex())
				return True
			except Exception as E:
				print('Saving wallet failed')
				print(E)
				return False
	def generate_keys(self):
		sender = ecdsa.SigningKey.generate()
		sendervk = sender.get_verifying_key()
		return sender, sendervk
	def send_transaction(self, recipient, amount,comment):
		# print(type((self.private_key.to_string())))
		UTXO = Transaction(str(self.public_key.to_string().hex()), recipient, amount, comment)
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
		for key, value in blockchain.chain.items():#traverse attribute chain, the dict in which blocks are stored
			self.block_header.append(value.to_json())
		return self.block_header
	def check_if_in(self, block, transaction):
		#for the person to check that their transaction is in with an id
	    entry = (transaction.to_json()).encode()
	    print(verify_proof(entry, block.get_proof(entry), block.get_root()))
def demo():
	a = SPVClient('a')
	b = SPVClient('b')
	a.create_keys()
	b.create_keys()
	UTXO = a.send_transaction(str(b.public_key.to_string().hex()),80, 'no')
	a.verify_transaction(UTXO)
	#Should return true
	tx1 = Transaction('t','c',80,"no")
	tx2 = Transaction('c', 't',80,"no")
	tx3 = Transaction('t','c',80,"no")
	transactions = [tx1, tx2, tx3]
	transactions2 = [tx2,tx1,tx3]
	transactions3 = [tx3,tx2,tx1]
	transactions4 = [tx1,tx2,tx1,tx3]
	block1 = Block(transactions, verbose=False)
	block2 = Block(transactions2, verbose=False)
	block3 = Block(transactions3, verbose=False)
	block4 = Block(transactions4, verbose=False)
	coin = Blockchain()
	coin.add(block1)
	time.sleep(0.2)
	coin.add(block2)
	time.sleep(0.2)
	coin.add(block3, block1.hash)
	time.sleep(0.2)
	print(a.receive_bloc_header(coin))
	#This is assuming that the SPV Client knows where the block is
	a.check_if_in(block1,tx1)
demo()