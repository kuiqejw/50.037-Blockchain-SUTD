from hashlib import sha256
import json
import time

import ecdsa
import json


sender = ecdsa.SigningKey.generate()
sendervk = sender.get_verifying_key()
sig = sender.sign(b"message")
sendervk.verify(sig, b"message") # True)

receiver = ecdsa.SigningKey.generate()
receivervk = receiver.get_verifying_key()
sig = receiver.sign(b"message")
receivervk.verify(sig, b"message") # True
#Determine the receiver, sender key
class Transaction:

    def __init__(self, sender, receiver, amount, comment):
        # Instantiates object from passed values
        self.sender = sender #public key
        self.receiver = receiver #public key
        self.amount = amount
        self.comment = comment
        self.signature = ""
        self.sign()



    def to_json(self):
        # Serializes object to JSON string
        dicty = {}
        self.sign()
        dicty['sender'] = self.sender.to_string().hex()
        dicty['receiver'] = self.receiver.to_string().hex()
        dicty['amount'] = str(self.amount)
        dicty['comment'] = self.comment
        dicty['signature'] = str(self.signature.hex())
        print(dicty['signature'])
        return json.dumps(dicty)
        # return json.dumps(self, default = lambda o: o.__dict__, sort_keys=True, indent=4)

    def from_json(self, data):
        # Instantiates/Deserializes object from JSON string
        tran = json.loads(data)
        print(tran)
        #since sender, and receiver public key is known
        cls2 = Transaction(sendervk,receivervk, tran['amount'], tran['comment']) 
        cls2.signature = bytes.fromhex(tran['signature'])
        return cls2

    def sign(self):
        tuccy = self.sender.to_string().hex()+self.receiver.to_string().hex()+str(self.amount)+self.comment
        # That can be called within new()
        if self.signature == "":
            self.signature = sender.sign(str.encode(tuccy)) #self.signature in bytes

    def validate(self):
        # Validate transaction correctness.
        tuccy = self.sender.to_string().hex()+self.receiver.to_string().hex()+str(self.amount)+self.comment
        #cleared the signature
        print(sendervk.verify(self.signature,str.encode(tuccy)))
        

    def __eq__(self,other):
        # Check whether transactions are the same
        return self.amount == other.amount and self.receiver == other.sender and self.sender == other.receiver and self.comment == other.comment

class Block:
	TARGET = 00000ffff

	def __init__(self):
        # Instantiates object from passed values
        self.past_transactions = []
        self.past_transaction_hashes = []
        #set of transactions that form a hash tree
        self.tiered_node_list = []
        #copying from merkle treee here
        self.root = None #root of the hash tree
        self.timestamp = time.time()#time stamp
        self.nonce = self.make_nonce()# nonce 
        self.block_number = None
        self.previous = None #hash of the previous header
	
	def add(self, new_transaction):
		new_hash_hex_digest = hashlib.sha256(new_transaction).hexdigest()
		self.past_transactions.append(new_transaction)
		self.past_transaction_hashes.append(new_hash_hex_digest)
		print('added new transaction with hex digest: ', new_hash_hex_digest)

	@staticmethod
	def make_nonce():
		#Generate pseudo random no. 
		return str(random.getrandbits(32))
	def build(self):
		#Build tree computing root
		num_leaves = len(self.past_transactions)#Count the no of leaves
		remaining_nodes = num_leaves
		active_level = self.past_transaction_hashes

		while remaining nodes != 1:
			if remaining nodes %2:
				odd = False
			else:
				odd = True
			new_tier = []
			for i in range(1, remaining_nodes, 2):
				combined_str = str(active_level[i-1]) + str(active_level[i])
				new_hash = hashlib.sha256(combined_str.encode()).hexdigest()
				new_tier.append(new_hash)
			if odd:
				new_tier.append(active_level[num_leaves-1].encode())
			self.tiered_node_list.append(new_tier)
			remaining_nodes = len(new_tier)
			active_level = new_tier
		self.tiered_node_list.insert(0, self.past_transaction_hashes)
		self.root = self.tiered_node_list[-1][0]
		print('tree build complete\n' + 'No. of levels:', len(self.tiered_node_list))
	def to_json(self):
        # Serializes object to JSON string
        self.build()
        dicty = {}
        self.sign()
        dicty['block_number'] = self.block_number
        dicty['previous'] = self.previous
        dicty['timestamp'] = self.timestamp
        dicty['transactions'] = self.past_transactions
        dicty['root'] = self.root
        dicty['nonce'] = self.nonce
        return json.dumps(dicty)
	def from_json(self, data):
        # Instantiates/Deserializes object from JSON string
        tran = json.loads(data)
        blck = Block()
        blck.block_number = tran['block_number']
        blck.previous = tran['previous']
        blck.timestamp = tran['timestamp']
        blck.transactions = tran['transactions']
        blck.root = tran['root']
        blck.nonce = tran['nonce']
        return blck

	def add_block_number(self, number):
		self.block_number= number
	def add_previous_hash(self, previous_hash):
		self.previous = previous_hash
	def get_root(self):
		if not self.root:
			print('No root found')
			return None
		return self.tiered_node_list[-1][0]
	@staticmethod
	def hash_is_valid(the_hash):
		return the_hash<TARGET
	def __eq__(self,other):
        # Check whether transactions are the same
        return self.timestamp == other.timestamp and self.nonce == other.nonce and self.previous == other.previous
	def compute_hash(self):
		block_string = self.to_json()
		return sha256(block_string.encode()).hexdigest()

	#Functions yet to be approved?
	def get_proof(self):
		#Get membership proof for entry
		pass
	def verify_proof(entry, proof, root):
		pass

class Blockchain:
	difficulty = 2
	def __init__(self):
		self.chain = []
		self.current_data = [] #stores info about the transaction
		self.nodes = set()
		self.create_genesis_block()#create the initial block
		# self.unconfirmed_transactions = [] #data yet to get into blockchain
		# self.chain = []
		# self.create_genesis_block()

	def create_genesis_block(self):
		"""
		function to generate gensis block and append it to chain
		The block has index 0, previous hash as 0 
		and valid hash
		"""
		self.build_block(proof_number = 0, previous_hash = 0)
	def build_block(self, proof_number, previous_hash):
		block = Block()
		block.block_number = len(self.chain)
		block.nonce = proof_number
		block.previous_hash = previous_hash
		block.past_transactions = self.current_data

		self.current_data = []
		self.chain.append(block)
		return block

	@property
	def last_block(self):
		return self.chain[-1]

	def proof_of_work(self,block):
		"""
		Function that tries different value of nonce to get a 
		hash that satisfies our difficulty criteria
		"""
		while True:
			nonce = random.getrandbits(32)
			main_data = str(block.previous) + str(nonce)
			hash_result = hashlib.sha256(main_data.encode()).hexdigest()

			if hash_result[:difficulty] == "0"*difficulty:
				print('Found Nonce: {}'.format(nonce))
				print('Corresponding hash value is {}'.format(hash_result))
				return hash_result, nonce
		print("Failed after %d (MAX_NONCE) tries" % nonce)
        return nonce
		
	def add(self, block,previous_hash=None):
		"""
		A function that adds the block to the chain after verification
		"""
		#TODO: add ability to select location

		if not previous_hash:
			#add to main
			previous_hash = self.chain[-1].to_json()
		block.add_previous_hash(previous_hash)
		block.add_block_number(self.last_block.block_number+1)
		self.chain.append(block)
		# previous_hash = self.last_block.hash
		# if previous_hash = block.previous_hash:
		# 	return False
		# if not self.is_valid_proof(block, proof):
		# 	return False
		# block.hash = proof
		# self.chain.append(block)
		# return True
	@staticmethod
	def validate(block, previous_block):
		"""
		check if block_hash is valid hash of block
		and satisfies the difficulty criteria
		"""
		if previous_block.block_number+1 != block.block_number:
			return False
		elif block.timestamp <= previous_block.timestamp:
			return False
		return True
	def get_data(self, sender,receiver, amount ):
		self.current_data.append({'sender': sender, 'receiver':receiver, 'amount':amount})
		return True

		## methods yet to be implemented
	def resolve(self):
		pass
