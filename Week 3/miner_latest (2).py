# -*- coding: utf-8 -*-
import ecdsa
from qn1 import Blockchain
from qn1 import Block
from qn1 import Transaction
from qn1 import verify_proof
import random
import hashlib

#So suppose this is the target. Any hash value should be lower than this
TARGET = '00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
#reduced the target to have two zeroes infront instead of 5 so finding the hash wouldn't take as long

COINS_PER_BLOCK = 100 #reward is at 100 SUTD coins for each Mined Block
MINIMUM_HASH_DIFFICULTY =  2  #Number of zeroes infront of the target
MAX_TRANS_PER_BLOCK = 3  #number of transactions per block
class Miner:

    def __init__(self, blockchain):
        self.reward = 0 #instantiate his reward to 0 first
        self.trans_pool = []
        self.blockchain = blockchain
        #Every miner can be a sender and a receiver
        self.sender_pk= ecdsa.SigningKey.generate()
        self.sender_id = self.sender_pk.get_verifying_key()
        self.receiver_pk = ecdsa.SigningKey.generate()
        self.receiver_id = self.receiver_pk.get_verifying_key()
        
    def get_reward(self):
        self.reward += COINS_PER_BLOCK #Add on the coins based on the number of blocks the miner successfully mined
    
        
    #note that this guy only validates other's transactions, not his own. 
    def peer_validation(self, blck):
        #sanity check if previous block mentioned in previous_hash exists
        prev_header = blck.previous_hash
        try:
            supposed_previous_block = self.blockchain.chain[prev_header] #In blockchain, chain attribute stores dictionary key pairs of hash, block
            #Indexes help to keep track of which is added
        except:
            print('Not a valid block exist! cry FOUL')
            return False
        bool_prev_header = self.blockchain.validate(blck, supposed_previous_block) 
        bool_verify_transact = self.verify_transaction(blck)
        print(bool_verify_transact)
        if not bool_prev_header and bool_verify_transact:
            self.blockchain.chain

    def add_to_chain(self, blck, targetHash=None):
        prev_block = self.blockchain.resolve()
        blck.previous_hash = prev_block.compute_hash()
        blck.index = self.blockchain.current_block_number
        self.blockchain.add(blck, targetHash)
        self.get_reward()
        print('Transaction added')

    def verify_transaction(self, blck):
        for i in blck.past_transactions:
            print(i)
            verify_new_tree = verify_proof(i, blck.get_proof(i), blck.get_root())
            if verify_new_tree == False:
                return False
        return True
    #Create a new block
    def add_trans_to_new_block(self):
        blck = Block(self.trans_pool)
        blck.build()
        blck.compute_hash()
        return blck
        # hash_result, nonce = self.blockchain.proof_of_work(blck) #managed to hash properly
        # if self.reconstruct_merkle(self.trans_pool) and timestamp_check(blck) and (hash_result != None):



    def update_miners(self, list_transactions):
        len_of_trans_pool = len(self.trans_pool)
        len_of_added_transactions = len(list_transactions)
        if (len_of_trans_pool + len_of_added_transactions) < MAX_TRANS_PER_BLOCK:
            self.trans_pool.extend(list_transactions)
        else: #That means length of transaction pool and length of added transactions >= max_trans block and add individually
            #Create a new block and send remaining to the trans_pool
            length_added = MAX_TRANS_PER_BLOCK - len_of_trans_pool
            print(length_added, 'length added')
            for i in range(length_added):
                a = list_transactions.pop(0)
                self.trans_pool.append(a)
            #create a block
            blck = self.add_trans_to_new_block()
            self.trans_pool = list_transactions
        return blck
                       
    def proof_of_work(self,blck):
        """
        Function that tries different value of nonce to get a 
        hash that satisfies our difficulty criteria/ or set Target criteria
        """
        while True:
            nonce = random.getrandbits(32)
            main_data = str(blck.previous) + str(nonce)
            hash_result = hashlib.sha256(main_data.encode()).hexdigest()
            if int(hash_result,16) <= int(TARGET, 16):
                print('Found Nonce: {}'.format(nonce))
                print('Corresponding hash value is {}'.format(hash_result))
                return hash_result, nonce
        print("Failed after %d (MAX_NONCE) tries" % nonce)
        return hash_result
    
    
def block_maker():

    coin = Blockchain()
    b = Miner(coin)
    c = Miner(coin)
    tx1 = Transaction(b.sender_id,c.receiver_id,80,"no")
    tx2 = Transaction(c.sender_id,b.receiver_id,80,"no")
    tx3 = Transaction(b.sender_id,c.receiver_id,80,"no")
    transactions = [tx1,tx2,tx3]
    transactions2 = [tx2,tx1,tx3]
    transactions3 = [tx3,tx2,tx1]
    transactions4 = [tx1,tx2,tx1,tx3]
    
    #test block for the said transactions
    blck = b.update_miners(transactions)
    b.add_to_chain(blck)
    c.peer_validation(blck)

    #Peer is the one who verifies

    # #
    # Miner().reconstruct_merkle(transactions.extend(transactions3))
    # Miner().reconstruct_merkle(transactions2.extend(transactions4))

block_maker()







        
    
        
    
     