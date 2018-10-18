import hashlib
import ecdsa
from Transaction import Transaction
from ecdsa import SigningKey
from Blockchain import Blockchain
from Block import Block, verify_proof
import time

#     #What does SPV Client do?
#     #They ask for all transactions, associated with my public key
#     #Validates proof of work, and the previous header
#     #give me transactions if I'm sender or receiver. 
#     #Miner will give them prsent proof
#     #SpV client, not stroing all transactions, will validate that it's all in.
class SPVClient:
	def __init__(self, node_id=''):
		self.private_key = None
		self.private_key = None
		self.node_id = node_id
		self.block_header = []
		self.balance = 50
	def get_balance(self):
		return self.balance
	def get_private_key(self):
		return self.private_key
	def get_public_key(self):
		print(self.public_key)
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
				print(E)
				return False
	def generate_keys(self):
		sender = ecdsa.SigningKey.generate()
		sendervk = sender.get_verifying_key()
		return sender, sendervk
	def send_transaction(self, recipient, amount,comment):
		# print(type((self.private_key.to_string())))
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
		for key, value in blockchain.chain.items():#traverse attribute chain, the dict in which blocks are stored
			self.block_header.append(value.to_json())
		return self.block_header
	def check_if_in(self, block, transaction):
		#for the person to check that their transaction is in with an id
	    print(verify_proof(transaction, block.get_proof(transaction), block.get_root()))
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
	def check_transaction_in_chain(self, transaction, chain):
		i = transaction
		if not hashlib.sha256(i.to_json().encode()).hexdigest() in chain.past_transactions_hashes:
		    print('False')
		else:
		    print('True',)
	def check_previous_header(self):
		#basically, check if it exists
		previous_hash_list = ['genesis']
		current_hash_list = []
		for z in self.block_header:
			previous_hash_list.append(z['previous'])
			current_hash_list.append(z['hash'])
		for i in current_hash_list:
			if i not in previous_hash_list:
				return False
		return True
def demo():
	a = SPVClient('a')
	b = SPVClient('b')
	c = SPVClient('c')
	d = SPVClient('d')
	lst = [a,b,c,d]
	for i in lst:
		i.create_keys()
	#a sends a transaction across
	UTXO = a.send_transaction(b.public_key,80, 'no')
	a.verify_transaction(UTXO)
	#Should return true
	tx1 = Transaction(b.public_key,c.public_key,80,"no")
	tx2 = Transaction(c.public_key, d.public_key,80,"no")
	tx3 = Transaction(d.public_key,a.public_key,80,"no")
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
	# a.check_if_in(block1,tx1)
	b.check_transaction_in_chain(tx1, coin)
#     #Go with proof that the transaction is in the blockchain (Done in Miner man)
	print(b.check_balance_of_pub(d.public_key, coin))
#     #They ask for all transactions, associated with my public key
#     #give me transactions if I'm sender or receiver. Returns 0 because as you can see, it's all bloody balanced out. No net loss
	print(b.check_previous_header(), 'Previous headers are all valid')
#     #Validates proof of work, and the previous header
#     #Miner will give them prsent proof
#     #SpV client, not storing all transactions, will validate that it's all in.
demo()