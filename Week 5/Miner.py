# -*- coding: utf-8 -*-
import ecdsa
from Blockchain import Blockchain
from Block import Block, verify_proof
from Transaction import Transaction
from SPVClient import SPVClient
import random
import hashlib
import schedule
import threading, time
from os import urandom
from random import getrandbits, randint
from ecdsa import SigningKey

#So suppose this is the target. Any hash value should be lower than this
TARGET = '00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
#reduced the target to have two zeroes infront instead of 5 so finding the hash wouldn't take as long

COINS_PER_BLOCK = 100 #reward is at 100 SUTD coins for each Mined Block
MINIMUM_HASH_DIFFICULTY =  2  #Number of zeroes infront of the target
MAX_TRANS_PER_BLOCK = 3  #number of transactions per block
def is_preimage(inp):
    hash = hashlib.sha256(inp).digest()
    if hash.startswith(b"\x00"*MINIMUM_HASH_DIFFICULTY):
        print(hash.hex())
        return hash
    else:
        return None

class Miner(SPVClient):

    def __init__(self, blockchain):
        #check, somehow init isn't inheriting the init, only the methods
        self.balance = 50

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
        try:
            supposed_previous_block = self.blockchain.chain[prev_header] #In blockchain, chain attribute stores dictionary key pairs of hash, block
            #Indexes help to keep track of which is added
        except Exception as E:
            return False
        bool_prev_header = self.blockchain.validate(blck, supposed_previous_block) 
        bool_verify_transact = self.verify_transaction(blck)
        if not bool_prev_header and bool_verify_transact:
            return False
        else:
            return True

    def add_to_chain(self, blck, targetHash=None):
        #assumes end to chain if target_hash is None
        prev_block = self.blockchain.resolve()
        blck.previous_hash = prev_block.compute_hash()
        blck.index = self.blockchain.current_block_number
        self.blockchain.add(blck, targetHash)
        print('Transaction added')

    def verify_transaction(self, blck):
        for i in blck.past_transactions:
            print(i)
            verify_new_tree = verify_proof(i, blck.get_proof(i), blck.get_root())
            if verify_new_tree == False:
                return False
        return True
    #Create a new block
    def create_blck(self):
        print('len of trans_pool', self.trans_pool)
        blck = Block(self.trans_pool)
        blck.build()
        self.proof_of_work(blck)
        blck.compute_hash()
        return blck

    def update_miners(self, list_transactions): #Note that transactions is type (transactions, not bytes!)
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
                print(a)
                self.trans_pool.append(a)
            blck = self.create_blck()
            self.trans_pool = list_transactions
            #create a block
            return blck
    def is_preimage(self,inp):
        hash = hashlib.sha256(inp).digest()
        if hash.startswith(b"\x00"*MINIMUM_HASH_DIFFICULTY) and str(hash.hex()) < hex(int(TARGET, 16)):
            print(hash.hex())
            return hash
        else:
            return None               
    def proof_of_work(self,blck, maxinput = 16):
        """
        Function that tries different value of nonce to get a 
        hash that satisfies our difficulty criteria/ or set Target criteria
        """
        x=0
        trial = urandom(randint(1, maxinput))
        while not self.is_preimage(trial):
            trial = urandom(randint(1, maxinput))
            x += 1
        print('Took ' + str(x) + ' trials')
        # i = 0
        # while True: ## Placed a limit of 200 tries Need to fix the count so that it arrives fast
        #     i += 1
        #     # nonce = random.getrandbits(32)
        #     # main_data =  str(nonce)
        #     trial = urandom(randint(1,8))
        #     hash_result = hashlib.sha256(trial).hexdigest()
        #     if int(hash_result,16) <= int(TARGET, 16):
        #         print('Found Nonce: {}'.format(nonce))
        #         print('Corresponding hash value is {}'.format(hash_result))
        #         return hash_result, nonces
        # print(i)
        # return blck.compute_hash()
      
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
    tx1 = Transaction(b.public_key,c.public_key,60,"one")
    tx1.sign(b.private_key)
    tx2 = Transaction(c.public_key,b.public_key,20,"two")
    tx2.sign(c.private_key)
    tx3 = Transaction(b.public_key,c.public_key,10,"three")
    tx3.sign(b.private_key)
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
    #b makes a suggestion of adding this to chain
    b.add_to_chain(blck)
    blck = c.update_miners(transactions4)
    c.add_to_chain(blck)

    #all miners verify block
    print('Verified Transaction by c', c.peer_validation(blck))
    print('Verified Transaction by d', d.peer_validation(blck))
    print('Verified Transaction by e', e.peer_validation(blck))
    print('Verified Transaction by f', f.peer_validation(blck))
    #check the merkle root
    #check the previous hash (it just links to some block)
    for i in blck.past_transactions:
        if hashlib.sha256(i.to_json().encode()).hexdigest() in coin.past_transactions_hashes:
            print('False')
        else:
            print('True', i.comment)
    #traverse through all transactions, and check that 
    #check that transaction is not reused,
    for i in blck.past_transactions:
        if i.validate(i.signature,i.sender ):
            print('True', i)
        else:
            print('False', i)
    # that the transaction is authentic,
    print(coin.past_transactions, 'coin past transactions form')
    for i in blck.past_transactions:
        sender_check = i.sender #sender_check is the public key of the sender in this transaction
        balance = 0
        for v in coin.past_transactions:
            if v.sender == sender_check:
                balance -= v.amount
            if v.receiver == sender_check:
                balance += v.amount
        if i.amount > balance:
            print('False', i.amount, balance)
        else:
            print('True', i.amount, balance)
# and that there is no double spending: Derive from past_transactions
#after that is done, you can start adding it. 
 
block_maker()
