# -*- coding: utf-8 -*-
import ecdsa
from Block import Block, verify_proof
from Blockchain import Blockchain
from Transaction import Transaction
from SPVClient import SPVClient
import random
import hashlib
import schedule
import threading, time
from os import urandom
from random import getrandbits, randint
from ecdsa import SigningKey
import threading
import time
import sched
#reduced the target to have two zeroes infront instead of 5 so finding the hash wouldn't take as long

COINS_PER_BLOCK = 100 #reward is at 100 SUTD coins for each Mined Block
MAX_TRANS_PER_BLOCK = 4#number of transactions per block
class Miner(SPVClient):

    def __init__(self,blockchain, node_id):
        #check, somehow init isn't inheriting the init, only the methods
        self.balance = 50
        self.public_key = None
        self.private_key = None
        self.block_header = []
        self.trans_pool = []
        self.node_id = node_id
        self.blockchain = blockchain
        #Every miner can be a sender and a receiver
    
    def blck_check2(self,blck):
        for i in blck.past_transactions:
            if hashlib.sha256(i.to_json().encode()).hexdigest() in self.blockchain.past_transactions_hashes:
                print('failed blck che')
                return False
            if not i.validate(i.signature,i.sender):
                # that the transaction is authentic,
                print('fail here?')
                return False
            else:
                return True
    
    def get_reward(self):
        self.balance += COINS_PER_BLOCK #Add on the coins based on the number of blocks the miner successfully mined
    
        
    #note that this guy only validates other's transactions, not his own. 
    def peer_validation(self, blck):
        #sanity check if previous block mentioned in previous_hash exists
        prev_header = blck.previous_hash
        try:
            supposed_previous_block = self.blockchain.chain[str(prev_header)] #In blockchain, chain attribute stores dictionary key pairs of hash, block
            #Indexes help to keep track of which is added
        except Exception as E:
            print('hit Exception')
            return False
        bool_prev_header = self.blockchain.validate(blck, supposed_previous_block) 
        bool_verify_transact = self.verify_transaction_with_block(blck)
        # #check that transaction has not been used transaction protection
        for i in blck.past_transactions:
            if hashlib.sha256(i.to_json().encode()).hexdigest() in self.blockchain.past_transactions_hashes:
                print('transaction has been used ')
                return False
        if not bool_prev_header:
            print('fails condition 1')
            return False
        elif not bool_verify_transact:
            print('fails condition 2')
            return False
        else:
            return True

    def add_to_chain(self, blck,prev_block, targetHash=None):
        #assumes end to chain if target_hash is None
        blck.previous_hash = prev_block.hash
        blck.index = self.blockchain.current_block_number
        if self.blck_check2(blck):
            self.blockchain.add(blck, targetHash)
            print('block was added')
            self.get_reward()
        else:
            print("Block not added due to coexisting transaction")
    def verify_transaction_with_block(self, blck):
        for i in blck.past_transactions:
            verify_new_tree = verify_proof(i, blck.get_proof(i), blck.get_root())
            if verify_new_tree == False:
                return False
        return True
    #Create a new block
    def create_blck(self):
        blck = Block(self.trans_pool)
        blck.build()
        return blck
    def remove_broadcast(self, list_transactions):
        self.trans_pool = [x for x in self.trans_pool if x not in list_transactions]
    def broadcast(self, list_transactions):
        self.trans_pool.extend(list_transactions)
    def check_len(self):
        while (len(self.trans_pool))>= MAX_TRANS_PER_BLOCK:
            saved_lst = self.trans_pool[MAX_TRANS_PER_BLOCK:]
            self.trans_pool = self.trans_pool[:MAX_TRANS_PER_BLOCK]
            blck = self.create_blck()
            self.trans_pool = saved_lst
            return blck
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
    def check_balance_of_pub(self, public_key):
        chain = self.blockchain
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
    