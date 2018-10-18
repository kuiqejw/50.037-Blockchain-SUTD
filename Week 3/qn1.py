from hashlib import sha256
import json
import time
from datetime import datetime
import hashlib

import ecdsa
import json
from ecdsa import SigningKey, NIST192p
from pprint import pprint
import time
import random
from exercise1q5 import MerkleTree, Node

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
        return json.dumps(dicty)

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
	Target = 0000

	def __init__(self, past_transactions, verbose = False):
		#headers
		self.version = '0.2'
		self.longest_link = 0 #the number of ancestors
		self.index = None #when inserted into chain
		self.previous_hash = None #Applied when inserted into chain
		self.merkle_root = None #root of the hash tree
		self.timestamp = time.time()#time stamp
		self.nonce = self.make_nonce()# nonce 
		#past_transactions
		self.past_transactions = []
		self.past_transaction_hashes = []
		if past_transactions != None:
		    for i in past_transactions:
		        self.add(i.to_json().encode())
		#Generated hash of previous header
		self.hash = None #inserted into chain
	
	def add(self, new_transaction):
		new_hash_hex_digest = hashlib.sha256(new_transaction).hexdigest()
		self.past_transactions.append(new_transaction)
		self.past_transaction_hashes.append(new_hash_hex_digest)
		print('added new transaction with hex digest: ', new_hash_hex_digest)
	def build_next_level(self, lst):
        #Takes in a list of nodes
        # This method builds a single level upwards.
        # Since the list passed in has mutable objects, 
        # when we edit lst we edit the list outside too.
        # All hashes should be in bytes
		nextlevel = []
		for i in range(len(lst)//2):
		    i = i*2
		    totalhash =  lst[i].data +lst[i+1].data
		    newnode = Node(hashlib.sha256(totalhash.encode()).hexdigest())
		    newnode.addchildren(left=lst[i], right=lst[i+1])
		    lst[i].addparent(newnode)
		    lst[i+1].addparent(newnode)
		    nextlevel.append(newnode)
		return nextlevel

	def build(self):
        # Build tree computing new root
		self.tiered_node_list = []
		active_level = []
		temp = None
		for i in self.past_transaction_hashes:
		    active_level.append(Node(i))
		if (len(active_level)%2 == 1):
		    # We only feed in an even number of active levels into build_next_level(),
		    # We include the odd one out after building the next level.
		    temp = active_level[-1]
		    active_level = active_level[:-1]
		self.tiered_node_list += active_level
		nextlevel = self.build_next_level(active_level)
		# We build the next level and add the current level into tiered_node_list
		if(temp != None):
		    nextlevel.append(temp)
		    temp = None
		while (len(nextlevel)>1):
		    # We continuously run build_next_level() on each level, taking care to only use it on even-numbered lists
		    # We omit the odd-numbered node until it has found a pair.
		    # i.e. only nodes that are put into build_next_level() are added to self.tiered node list
		    active_level = nextlevel
		    nextlevel = []
		    if(len(active_level)%2 == 1):
		        # We only feed in an even number of currlevels into _build_next_level(),
		        # We include the odd one out after building the next level.
		        temp = active_level[-1]
		        active_level = active_level[:-1]
		    self.tiered_node_list += (active_level)
		    nextlevel = self.build_next_level(active_level)
		    if(temp != None):
		        nextlevel.append(temp)
		        temp = None
		self.tiered_node_list += nextlevel # This is the last/root node


	@staticmethod
	def make_nonce():
		#Generate pseudo random no. 
		print('random bits', random.getrandbits(32))
		return random.getrandbits(32)

	def to_json(self):
        # Serializes object to JSON string
		self.build()
		dicty = {}
		dicty['version'] = self.version
		dicty['index'] = self.index
		dicty['previous'] = self.previous_hash
		dicty['timestamp'] = self.timestamp
		dicty['root'] = self.merkle_root
		dicty['nonce'] = self.nonce
		return json.dumps(dicty)
	def from_json(self, data):
        # Instantiates/Deserializes object from JSON string
		tran = json.loads(data)
		blck = Block(tran['previous'])
		blck.version = tran['version']
		blck.index = tran['index']
		blck.timestamp = tran['timestamp']
		blck.merkle_root = tran['root']
		blck.nonce = tran['nonce']
		return blck

	def add_index(self, number):
		self.index= number
	def add_previous_hash(self, previous_hash):
		self.previous = previous_hash
	def get_root(self):
		return self.tiered_node_list[-1].data
	@staticmethod
	def hash_is_valid(the_hash):
		return the_hash<TARGET
	def __eq__(self,other):
        # Check whether transactions are the same
		return self.timestamp == other.timestamp and self.nonce == other.nonce and self.previous == other.previous
	def compute_hash(self):
		block_string = self.to_json()
		hasher = sha256(block_string.encode()).hexdigest()
		self.hash = hasher
		return hasher
	def check(self, entryhash):
	    for i,j in enumerate(self.tiered_node_list):
	            if(j.data == entryhash):
	                itemindex = i 
	    return itemindex  
	#Functions yet to be approved?
	def get_proof(self, index):
        # Get membership proof for entry
		hashlist = []
		if (index not in self.past_transactions):
		    return 
		# We look for the entry and its node in self.tiered_node_list
		entryhash = hashlib.sha256(index).hexdigest()
		for i,j in enumerate(self.tiered_node_list):
		    if(j.data == entryhash):
		        itemindex = i
		currnode = self.tiered_node_list[itemindex]
		# When we find the entry, we can get hashes required for proof
		while(currnode.parent != None):
		    prevnode = currnode
		    currnode = currnode.parent
		    if(currnode.left == prevnode):
		        hashlist.append([currnode.right.data, "r", self.check(currnode.right.data)])
		    else:
		        hashlist.append([currnode.left.data, "l", self.check(currnode.left.data)])
		return hashlist

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
class Blockchain:
	difficulty = 1
	def __init__(self):
		self.current_block_number = 0
		self.chain = {}
		self.previous_hash = None
		self.genesis_block = False
		self.create_genesis_block()#create the initial block

	def create_genesis_block(self):
		"""
		function to generate gensis block and append it to chain
		The block has index 0, previous hash as 0 
		and valid hash
		"""
		if self.genesis_block:
			return 'Genesis already'
		genesis_transaction = Transaction(sendervk, receivervk, 50, 'Genesis transaction')
		self.previous_hash = 'genesis'
		block = Block([genesis_transaction])
		self.add(block)
		self.genesis_block = True
		return block
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
		return None, nonce
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
				primeval_hash = self.chain[i]
		return primeval_hash

def demo():
    tx1 = Transaction(sendervk,receivervk,80,"no")
    tx2 = Transaction(sendervk,receivervk,80,"no")
    tx3 = Transaction(sendervk,receivervk,80,"no")

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
    t = coin.chain[block3.hash]
    entry = (tx1.to_json()).encode()
    print(type(tx1))
    print(verify_proof(entry, block1.get_proof(entry), block1.get_root()))



if __name__ == '__main__':
	sender = ecdsa.SigningKey.generate()
	sendervk = sender.get_verifying_key()
	sig1 = sender.sign(b"message")
	sendervk.verify(sig1, b"message") # True)

	receiver = ecdsa.SigningKey.generate()
	receivervk = receiver.get_verifying_key()
	sig = receiver.sign(b"message")
	receivervk.verify(sig, b"message") # True

	print('Running blockchain demo!')
	demo()