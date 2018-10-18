import ecdsa
from Block import Block, verify_proof
from Blockchain import Blockchain
from Transaction import Transaction
from SPVClient import SPVClient
from Miner import Miner
import random
import hashlib
import threading, time
from os import urandom
from random import getrandbits, randint
from ecdsa import SigningKey
from time import sleep
import multiprocessing as mp
import sched
import concurrent.futures
#So suppose this is the target. Any hash value should be lower than this
TARGET = '00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
#reduced the target to have two zeroes infront instead of 5 so finding the hash wouldn't take as long
random.seed(42)
COINS_PER_BLOCK = 100 #reward is at 100 SUTD coins for each Mined Block
MINIMUM_HASH_DIFFICULTY =  2  #Number of zeroes infront of the target
MAX_TRANS_PER_BLOCK = 3  #number of transactions per block
def demo():
    a = SPVClient('a')
    b = SPVClient('b')
    c = SPVClient('c')
    d = SPVClient('d')
    lst = [a,b,c,d]
    for i in lst:
        i.create_keys()
    #a sends a transaction across
    UTXO = a.send_transaction(b.public_key,80, 'oneSPV')
    a.verify_transaction(UTXO)
    #Should return true
    tx1 = Transaction(b.public_key,c.public_key,80,"twoSPV")
    tx2 = Transaction(c.public_key, d.public_key,80,"threeSPV")
    tx3 = Transaction(d.public_key,a.public_key,80,"fourSPV")
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
    # b.check_transaction_in_chain(tx1, coin)
#     #Go with proof that the transaction is in the blockchain (Done in Miner man)
    # print(b.check_balance_of_pub(d.public_key, coin))
#     #They ask for all transactions, associated with my public key
#     #give me transactions if I'm sender or receiver. Returns 0 because as you can see, it's all bloody balanced out. No net loss
    # print(b.check_previous_header(), 'Previous headers are all valid')
#     #Validates proof of work, and the previous header
#     #Miner will give them prsent proof
#     #SpV client, not storing all transactions, will validate that it's all in.
# demo()      
def demo_miner():
    coin = Blockchain()
    b = Miner(coin, 'b')
    c = Miner(coin,'c')
    d = Miner(coin,'d')
    e = Miner(coin, 'e')
    f = Miner(coin, 'f')
    #So five miners
    miners = [b,c,d,e,f]
    for i in miners:
        i.create_keys()
    print(b.balance, 'b.balance')
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
    for i in miners:
        i.broadcast(transactions)
    blck = b.check_len()#check_len creates a new block if length >= MAX_TRANS
    prev_block = my_add(b, coin, blck)
    print('Verified Transaction by c', c.peer_validation(blck))
    print('Verified Transaction by d', d.peer_validation(blck))
    print('Verified Transaction by e', e.peer_validation(blck))
    print('Verified Transaction by f', f.peer_validation(blck))
    #confirmation should only come before block is added
    b.add_to_chain(blck, prev_block)
    #all miners verify block

    #After creating a block, (transaction and header) DoNE
    #header contains nonce DONE
    #check proof of work for this block. DONE
    #compute hash over the header, and less than target, that means a lot of people spend time
    #b makes a suggestion of adding this to chain

    
    #Transaction resending protection
    #check the merkle root
    #check the previous hash (it just links to some block)
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
# and that there is no double spending: Derive from past_transactions / transaction validation
#after that is done, you can start adding it. 
# def blck_check(blck, coin):
#     for i in blck.past_transactions:
#         if hashlib.sha256(i.to_json().encode()).hexdigest() in coin.past_transactions_hashes:
#             print('False', i.comment)
#         else:
#             print('True', i.comment)
def my_add(miner, coin, blck):
    prev_block = coin.resolve()
    blck.previous_hash = prev_block.hash
    blck.index = prev_block.index+1
    return prev_block
def my_add1(miner,coin,transaction):
    print("%s started" %miner.node_id)
    blck = miner.broadcast(transaction)
    blck = miner.check_len()
    print(blck)
    if blck == None:
        return
    else:
        lock = threading.Lock()
        lock.acquire()
        prev_block = my_add(miner, coin, blck)
        miner.add_to_chain(blck,prev_block)
        lock.release()
        
def worker(miner,coin,transaction):
    print("%s started" %miner.node_id)
    miner.broadcast(transaction)
    blck = miner.check_len()
    if blck == None:
        return
    else: 
        print('blck have')
        return blck
def worker2(miner, coin, blck):
    prev_block = my_add(miner, coin, blck)
    miner.add_to_chain(blck,prev_block)
    print('Get Reward', miner.balance)
def selfish_main(miner, coin, transaction, lst_kept=[]):
    blck = worker(miner, coin, transaction)
    lock = threading.Lock()
    lock.acquire()
    lst_kept.append(blck)
    print("%s started" %miner.node_id)
    if (miner.node_id == 'd' or miner.node_id == 'e' or miner.node_id == 'f'):
        for i in lst_kept:
            worker2(miner, coin,i)
            print("%s finished" %miner.node_id)
    else:#b and c are selfish, but have a probability of 0.4 to keep their blocks rather than firing into the system. 
        decider = random.random()
        if decider > 0.4:
            for i in lst_kept:
                worker2(miner, coin,i)
                print("%s finished" %miner.node_id)
    lock.release()
def simulation_attack():
    #51% attack:
    #51% attack can be done via making one server run faster than the other, such that the transaction taking place is not added. 
    coin = Blockchain()
    b = Miner(coin, 'b')
    c = Miner(coin, 'c')
    d = Miner(coin, 'd')
    e = Miner(coin, 'e')
    f = Miner(coin, 'f')
    #So five miners
    miners = [b,c,d,e,f]
    for i in miners:
        i.create_keys()
    tx1 = Transaction(b.public_key,c.public_key,10,"one")
    tx1.sign(b.private_key)
    tx2 = Transaction(c.public_key,b.public_key,20,"two")
    tx2.sign(c.private_key)
    tx3 = Transaction(b.public_key,c.public_key,30,"three")
    tx3.sign(b.private_key)
    tx4 = Transaction(b.public_key,c.public_key,40,"four")
    tx4.sign(b.private_key)
    tx5 = Transaction(c.public_key,b.public_key,50,"five")
    tx5.sign(c.private_key)
    tx6 = Transaction(b.public_key,c.public_key,60,"six")
    tx6.sign(b.private_key)
    #6 transactions
    tx7 = Transaction(b.public_key,c.public_key,10,"seven")
    tx7.sign(b.private_key)
    tx8 = Transaction(c.public_key,b.public_key,20,"eight")
    tx8.sign(c.private_key)
    tx9 = Transaction(b.public_key,c.public_key,10,"nine")
    tx9.sign(b.private_key)
    tx10 = Transaction(b.public_key,c.public_key,20,"ten")
    tx10.sign(b.private_key)
    tx11 = Transaction(c.public_key,b.public_key,20,"eleven")
    tx11.sign(c.private_key)
    tx12 = Transaction(b.public_key,d.public_key,10,"twelve")
    tx12.sign(b.private_key)
    
    #b does not want to show d's transaction, tx12
    #Create a block by b
    transactions = [tx1,tx2,tx3]
    transactions2 = [tx4,tx5,tx6]
    transactions3 = [tx10,tx11,tx8]
    transactions4 = [tx10,tx11,tx12]
    transactions5 = [tx3,tx6,tx9]
    transactions6 = [tx8,tx2,tx4]
    miners2 = [[b,transactions],[b,transactions2],[b,transactions3],[d,transactions4], [e, transactions5], [f, transactions6]]
    random.shuffle(miners2)
    for i in miners2:
        t= threading.Thread(name='51_1', target=my_add1, args=(i[0],coin,i[1],))
        t.start()
        t.join(timeout=1)
    for i in coin.past_transactions:
        print(i.comment)
         
def simulation_attack2():
    #selfish mining requires the blocks to be created, but not added to the chain. Until you say so. 
    coin = Blockchain()
    b = Miner(coin, 'b')
    c = Miner(coin, 'c')
    d = Miner(coin, 'd')
    e = Miner(coin, 'e')
    f = Miner(coin, 'f')
    a = SPVClient('a')
    g = SPVClient('g')
    #So five miners
    people = [a,b,c,d,e,f,g]
    for i in people:
        i.create_keys()
    tx = []
    tx1 = Transaction(b.public_key,c.public_key,10,"one")
    tx1.sign(b.private_key)
    tx2 = Transaction(c.public_key,b.public_key,20,"two")
    tx2.sign(c.private_key)
    tx3 = Transaction(b.public_key,c.public_key,30,"three")
    tx3.sign(b.private_key)
    tx4 = Transaction(b.public_key,c.public_key,40,"four")
    tx4.sign(b.private_key)
    tx5 = Transaction(c.public_key,b.public_key,50,"five")
    tx5.sign(c.private_key)
    tx6 = Transaction(b.public_key,c.public_key,60,"six")
    tx6.sign(b.private_key)
    #6 transactions
    tx7 = Transaction(b.public_key,c.public_key,10,"seven")
    tx7.sign(b.private_key)
    tx8 = Transaction(c.public_key,b.public_key,20,"eight")
    tx8.sign(c.private_key)
    tx9 = Transaction(b.public_key,c.public_key,10,"nine")
    tx9.sign(b.private_key)
    tx10 = Transaction(b.public_key,c.public_key,20,"ten")
    tx10.sign(b.private_key)
    tx11 = Transaction(c.public_key,b.public_key,20,"eleven")
    tx11.sign(c.private_key)
    tx12 = Transaction(b.public_key,d.public_key,10,"twelve")
    tx12.sign(b.private_key)
    
    for i in range(21):
        amount = random.randint(1,101)
        person = random.randint(1,6)
        person2 = random.randint(1,6)
        comment = str(time.time())
        tx1 = Transaction(people[person].public_key,people[person2].public_key,amount,comment)
        tx1.sign(people[person].private_key)
        tx.append(tx1)
    tt = [tx1,tx2,tx3,tx4,tx5,tx6,tx7,tx8,tx9,tx10,tx11,tx12]
    tx.extend(tt)
    #b does not want to show d's transaction, tx12
    #Create a block by b
    # random.shuffle(tx)
    #create two threads, one for selfish, one for honest
    #Each will take turns to run
    #First thread for honest will run my_add1
    #second thread for selfish will consist of two parts
    #create block
    #On some probability (or when greater than 2, add to chain)
    #b and c are selfish, d,e,f are honest so have a loop to decide
    miners2 = [[b,tx], [c,tx],[d,tx],[e,tx],[f,tx]]
    # executor = concurrent.futures.ProcessPoolExecutor(max_workers=5)
    # wait_for = [executor.submit(selfish_main,i[0], coin, i[1],) for i in miners2]
    # for f in concurrent.futures.as_completed(wait_for):
        # print(f.result())
        
    #b and c are dishonest, while d,e,f are honest
    # miners2 = [[b,transactions],[c,transactions2],[b,transactions3],[d,transactions4], [e, transactions5], [d, transactions6]]
    # random.shuffle(miners2)
    x = 0
    while x < 20:
        x += 1
        for i in miners2:
            #Note that I tried a random.randint here, but did not get equal time as expected
            t= threading.Thread(name='selfish_mining', target=selfish_main, args=(i[0],coin,i[1],))
            t.start()
            t.join(timeout=0.5)
        print(len(coin.past_transactions))
        for i in miners2:
            print(i[0].node_id, i[0].balance)
# lst_of_fn = [send_transaction, receive_transaction, verify_transaction, update_miners, verify_block ]
def send_tx(sender, recipient, amount, comment): #sender and recipient are SPV Client members
    return sender.send_transaction(recipient.public_key, amount,comment)
def receive_tx(receiver, transaction):
    receiver.receive_transaction(transaction)
def verify_tx(sender, transaction):
    sender.verify_transaction(transaction)
def miner_update_pool(miner,list_transactions): #update_miner
    blck = miner.update_miners(list_transactions)
def scheduled_network():
    coin = Blockchain()
    m1 = Miner(coin, 'm1')
    m2 = Miner(coin, 'm2')
    m3 = Miner(coin, 'm3')
    s1 = SPVClient('s1')
    s2 = SPVClient('s2')
    lst = [m1,m2,m3,s1,s2]
    for i in lst:
        i.create_keys()
    my_lst = [1,2,3,4]
    while True:
        i = random.choice(my_lst)
        person = random.choice(lst)
        if i == 1:
            person2 = random.choice(lst)
            amount = random.randint(1,50)
            comment = 'random ' + str(amount)
            UT = send_tx(person,person2,amount,'random'+comment)
            receive_tx(person2, UT)
            person.verify_transaction(UT)

            new_transaction = []
            new_transaction.append(UT)
            miner_lst = [m1,m2,m3]

            scheduler = sched.scheduler(time.time, time.sleep)
            for tta in miner_lst:
                tta.broadcast(new_transaction)
            def run_sched_check_len(miner):
                blck = miner.check_len()
                if blck_check2(blck, coin):
                    prev_block = coin.resolve()
                    miner.add_to_chain(blck,prev_block)
                    print('miner passed')
                    return
                else:
                    print('mining failed')
                    return
                for i in range(60):
                    scheduler.enter(100*i, 1, run_sched_check_len,(tta))
        if i == 2:
            person2 = random.choice(lst)
            if isinstance(person,Miner):
                person.check_balance_of_pub(person2.public_key)
        if i == 3:
            t = person.receive_bloc_header(coin)
            print('receive header')
        if i == 4:
            print(person.check_previous_header(), 'prev_header')


# demo_miner()
if __name__ == '__main__':
    simulation_attack()
