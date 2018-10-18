import json
from datetime import datetime
import hashlib
import time
import random
from MerkleTree import MerkleTree, Node


class Block:

	def __init__(self, past_transactions, verbose = False):
		#headers
		self.longest_link = 0 #the number of ancestors
		self.index = None #when inserted into chain
		self.previous_hash = None #Applied when inserted into chain
		self.merkle_root = None #root of the hash tree
		self.timestamp = time.time()#time stamp
		self.nonce = self.make_nonce()# nonce 
		#past_transactions
		self.past_transactions = past_transactions
		self.past_transaction_hashes = []
		if self.past_transactions != None:
		    for i in range(len(past_transactions)):
		        self.add(past_transactions[i].to_json().encode())
		#Generated hash of previous header
		self.hash = None #inserted into chain
	def __repr__(self): #used for debugging without print, __repr__ > __str__
		return "Block<index: %s>, <hash: %s> , <longest_link: %s>" % (self.index, self.hash, self.longest_link)
	def __ne__(self, other):
		return not self.__eq__(other)
	def __gt__(self, other):
		return self.timestamp < other.timestamp
	def __lt__(self, other):
		return self.timestamp > other.timestamp
	def add(self, new_transaction):
		new_hash_hex_digest = hashlib.sha256(new_transaction).hexdigest()
		self.past_transaction_hashes.append(new_hash_hex_digest)
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
		self.merkle_root = self.get_root()


	@staticmethod
	def make_nonce():
		#Generate pseudo random no. 
		return random.getrandbits(32)

	def to_json(self):
        # Serializes object to JSON string
		self.build()
		dicty = {}
		dicty['index'] = self.index
		dicty['previous'] = self.previous_hash
		dicty['timestamp'] = self.timestamp
		dicty['root'] = self.merkle_root
		dicty['nonce'] = self.nonce
		dicty['hash'] = self.hash
		return json.dumps(dicty)
	def from_json(self, data):
        # Instantiates/Deserializes object from JSON string
		tran = json.loads(data)
		blck = Block(tran['previous'])
		blck.index = tran['index']
		blck.timestamp = tran['timestamp']
		blck.merkle_root = tran['root']
		blck.nonce = tran['nonce']
		blck.hash = tran['hash']
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
	def compute_hash(self):
		block_string = self.to_json()
		hasher = hashlib.sha256(block_string.encode()).hexdigest()
		self.hash = hasher
		return hasher
	def check(self, entryhash):
	    for i,j in enumerate(self.tiered_node_list):
	            if(j.data == entryhash):
	                itemindex = i 
	    return itemindex  
	#Functions yet to be approved?
	def get_proof(self, transaction):
        # Get membership proof for entry
		hashlist = []
		if (transaction not in self.past_transactions):
			return 
		# We look for the entry and its node in self.tiered_node_list
		entryhash = hashlib.sha256(transaction.to_json().encode()).hexdigest()
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

	def header_string(self):
		return str(self.index) + self.previous_hash + str(self.timestamp) + str(self.nonce)

def verify_proof(entry, proof, root):
    # Verifies proof for entry and given root. Returns boolean.
    currhash = hashlib.sha256(entry.to_json().encode()).hexdigest()
    for i in proof:
        if(i[1] == "r"):
            newhash = currhash + i[0]
            currhash = hashlib.sha256(newhash.encode()).hexdigest()
        else:
            newhash =  i[0]+currhash
            currhash = hashlib.sha256(newhash.encode()).hexdigest()
    return root == currhash
