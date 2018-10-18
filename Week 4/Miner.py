# -*- coding: utf-8 -*-
import ecdsa
from Blockchain import Blockchain
from Block import Block
from Transaction import Transaction
from Blockchain import verify_proof
from SPVClient import SPVClient
import random
import hashlib
import schedule
import threading, time
from os import urandom
from random import getrandbits, randint

#So suppose this is the target. Any hash value should be lower than this
TARGET = '00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
#reduced the target to have two zeroes infront instead of 5 so finding the hash wouldn't take as long

COINS_PER_BLOCK = 100 #reward is at 100 SUTD coins for each Mined Block
MINIMUM_HASH_DIFFICULTY =  2  #Number of zeroes infront of the target
MAX_TRANS_PER_BLOCK = 3  #number of transactions per block
class Miner(SPVClient):

    def __init__(self, blockchain):
        self.reward = 0 #instantiate his reward to 0 first
        self.trans_pool = []
        self.blockchain = blockchain
        #Every miner can be a sender and a receiver
        
    def get_reward(self):
        self.reward += COINS_PER_BLOCK #Add on the coins based on the number of blocks the miner successfully mined
    
        
    #note that this guy only validates other's transactions, not his own. 
    def peer_validation(self, blck):
        #sanity check if previous block mentioned in previous_hash exists
        prev_header = blck.previous_hash
        supposed_previous_block = self.blockchain.chain[prev_header] #In blockchain, chain attribute stores dictionary key pairs of hash, block
            #Indexes help to keep track of which is added
        bool_prev_header = self.blockchain.validate(blck, supposed_previous_block) 
        bool_verify_transact = self.verify_transaction(blck)
        if not bool_prev_header and bool_verify_transact:
            return False
        else:
            return True

    def add_to_chain(self, blck, targetHash=None):
        #assumes end to chain
        prev_block = self.blockchain.resolve()
        blck.previous_hash = prev_block.compute_hash()
        blck.index = self.blockchain.current_block_number
        print('Block imposed')

    def verify_transaction(self, blck):
        for i in blck.past_transactions:
            print(i)
            verify_new_tree = verify_proof(i, blck.get_proof(i), blck.get_root())
            if verify_new_tree == False:
                return False
        return True
    #Create a new block
    def create_blck(self):
        blck = Block(self.trans_pool)
        blck.build()
        self.proof_of_work(blck)
        blck.compute_hash()
        return blck

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
            self.trans_pool = list_transactions
            #create a block
            blck = self.create_blck()
            return blck
                       
    def proof_of_work(self,blck):
        """
        Function that tries different value of nonce to get a 
        hash that satisfies our difficulty criteria/ or set Target criteria
        """
        i = 0
        while i < 200: ## Placed a limit of 20 tries Need to fix the count so that it arrives fast
            i += 1
            # nonce = random.getrandbits(32)
            # main_data =  str(nonce)
            trial = urandom(randint(1,8))
            hash_result = hashlib.sha256(trial).hexdigest()
            if int(hash_result,16) <= int(TARGET, 16):
                print('Found Nonce: {}'.format(nonce))
                print('Corresponding hash value is {}'.format(hash_result))
                return hash_result, nonce
        print("Failed after 200 (MAX_NONCE) tries")
        return blck.compute_hash()
      
def block_maker():
    coin = Blockchain()
    b = Miner(coin)
    c = Miner(coin)
    d = Miner(coin)
    e = Miner(coin)
    f = Miner(coin)
    #So five miners
    miners = [b,c,d,e,f]
    for i in miners:
        i.create_keys()
    tx1 = Transaction(str(b.public_key.to_string().hex()),str(c.public_key.to_string().hex()),80,"no")
    tx2 = Transaction(str(c.public_key.to_string().hex()),str(b.public_key.to_string().hex()),80,"no")
    tx3 = Transaction(str(b.public_key.to_string().hex()),str(c.public_key.to_string().hex()),80,"no")
    transactions = [tx1,tx2,tx3]
    transactions2 = [tx2,tx1,tx3]
    transactions3 = [tx3,tx2,tx1]
    transactions4 = [tx1,tx2,tx1,tx3]
    
    #test block for the said transactions
    #Create a block by b
    blck = b.update_miners(transactions)
    #After creating a block, (transaction and header) DoNE
    #header contains nonce DONE
    #check proof of work for this block. DONE
    #compute hash over the header, and less than target, that means a lot of people spend time
    #b makes a suggestion
    b.add_to_chain(blck)

    print('Verified Transaction by c', c.peer_validation(blck))
    print('Verified Transaction by d', d.peer_validation(blck))
    print('Verified Transaction by e', e.peer_validation(blck))
    print('Verified Transaction by f', f.peer_validation(blck))
#check the merkle root
#check the previous hash (it just links to some block)
    for i in blck.past_transactions:
        if hashlib.sha256(i).hexdigest() in coin.past_transactions:
            print('False')
    print('True')
        #Store all the transactions that had been appended previously or go back and check
        # balance, sender has more than spending


    #traverse through all transactions, 
    #check that transaction is not reused, that signature is authentic, and that there is no double spending

    self.blockchain.add(blck) #self.blockchain.add(blck, targetHash) once there is more than one block
#after that is done, you can start adding it. 

    #What does SPV Client do?
    #They ask for all transactions, associated with my public key
    #Go with proof that the transaction is in the blockchain
    #Validates proof of work, and the previous header
    #give me transactions if I'm sender or receiver. 
    #Miner will give them prsent proof
    #SpV client, not stroing all transactions, will validate that it's all in. 
block_maker()







        
    
        
    
     