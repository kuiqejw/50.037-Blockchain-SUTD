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
def demo_spv():
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
    coin.add(block2) #fail because reused
    time.sleep(0.2)
    coin.add(block3, block1.hash) #fail because reused transaction. 
    time.sleep(0.2)
    print(a.receive_bloc_header(coin))
    #This is assuming that the SPV Client knows where the block is
    a.check_if_in(block1,tx1)
    b.check_transaction_in_chain(tx1, coin)
#     #Go with proof that the transaction is in the blockchain (Done in Miner man)
    print(b.check_balance_of_pub(d.public_key, coin))
#     #They ask for all transactions, associated with my public key
#     #give me transactions if I'm sender or receiver. Returns 0 because as you can see, it's all bloody balanced out. No net loss
    print(b.check_previous_header(), 'Previous headers are all valid')
#     #Validates proof of work, and the previous header
#     #Miner will give them prsent proof
#     #SpV client, not storing all transactions, will validate that it's all in.
    print(b.grab_all_transactions(coin))
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
def demo_miner2():
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
    tx = []
    for i in range(21):
        amount = random.randint(1,101)
        person = random.randint(0,4)
        person2 = random.randint(0,4)
        comment = str(time.time())
        tx1 = Transaction(miners[person].public_key,miners[person2].public_key,amount,comment)
        tx1.sign(miners[person].private_key)
        tx.append(tx1)
    for i in miners:
        random.shuffle(tx)
        i.broadcast(tx)
        blck = i.check_len()#check_len creates a new block if length >= MAX_TRANS
        prev_block = my_add(i, coin, blck)
        i.add_to_chain(blck, prev_block)
        
    print(b.verify_transaction_with_block(blck))
    
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
    if blck == None:
        return
    else:
        prev_block = my_add(miner, coin, blck)
        miner.add_to_chain(blck,prev_block)
def my_add2(miner,coin,transaction,neighbors):
    print("%s started" %miner.node_id)
    blck = miner.broadcast(transaction)
    blck = miner.check_len()
    if blck == None:
        return
    else:
        prev_block = my_add(miner, coin, blck)
        miner.add_to_chain(blck,prev_block)
        for i in neighbors:
        i.remove_broadcast(blck.past_transactions)
        print('Who get the reward? ', miner.node_id,"what's his balance: ", miner.balance)
def worker(miner,coin,transaction):
    print("%s started" %miner.node_id)
    miner.broadcast(transaction)
    blck = miner.check_len()
    if blck == None:
        return
    else: 
        print('blck have')
        return blck
def worker2(miner, coin, blck,neighbors):
    prev_block = my_add(miner, coin, blck)
    miner.add_to_chain(blck,prev_block)
    for i in neighbors:
        i.remove_broadcast(blck.past_transactions)
    print("miner's balance: ",miner.node_id, miner.balance)
    return
def selfish_main(miner, coin, transaction,neighbors,lock):
    blck = worker(miner, coin, transaction)
    print("%s started" %miner.node_id)
    lock.acquire()
    if (miner.node_id == 'd' or miner.node_id == 'e' or miner.node_id == 'f'):
        worker2(miner, coin,blck, neighbors)
        print("%s finished" %miner.node_id)
    else: #else: keep two blocks and release them later
        lst_kept = [blck]
        miner.remove_broadcast(blck.past_transactions)
        blck2 = worker(miner,coin,transaction)
        lst_kept.append(blck2)
        for i in lst_kept:
            worker2(miner, coin,i,neighbors)
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
    tx = []
    for i in range(21):
        amount = random.randint(1,101)
        person = random.randint(1,4)
        person2 = random.randint(1,4)
        comment = str(time.time())
        tx1 = Transaction(miners[person].public_key,miners[person2].public_key,amount,comment)
        tx1.sign(miners[person].private_key)
        tx.append(tx1)
    tt = [tx1,tx2,tx3,tx4,tx5,tx6,tx7,tx8,tx9,tx10,tx11,tx12]
    tx.extend(tt)
    btx = tx[:-1]
    random.shuffle(tx) #note that b does not want transaction 12 to go through!
    random.shuffle(btx) #shuffling
    miners2 = [[b,btx], [c,tx],[b,btx],[e,tx]]
    for z in range(5):
        for i in miners2:
            t= threading.Thread(name='51_1', target=my_add1, args=(i[0],coin,i[1],))
            t.start()
            t.join(timeout=0.5)
    for i in miners2:
        print(i[0].node_id, i[0].balance) #can see that b makes more profit by occupying 51% and avoids t12 from being added in
         
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
    h = SPVClient('h')
    i = SPVClient('i')
    j = SPVClient('j')
    k = SPVClient('k')
    #So five miners
    people = [a,b,c,d,e,f,g, h, i ,j,k]
    for i in people:
        i.create_keys()
    tx = []
    tx1 = Transaction(a.public_key,g.public_key,10,"one")
    tx1.sign(a.private_key)
    tx2 = Transaction(g.public_key,h.public_key,20,"two")
    tx2.sign(g.private_key)
    tx3 = Transaction(h.public_key,i.public_key,30,"three")
    tx3.sign(h.private_key)
    tx4 = Transaction(i.public_key,j.public_key,40,"four")
    tx4.sign(i.private_key)
    tx5 = Transaction(j.public_key,k.public_key,50,"five")
    tx5.sign(j.private_key)
    tx6 = Transaction(k.public_key,a.public_key,60,"six")
    tx6.sign(k.private_key)
    #6 transactions
    tx7 = Transaction(a.public_key,g.public_key,10,"seven")
    tx7.sign(a.private_key)
    tx8 = Transaction(g.public_key,h.public_key,20,"eight")
    tx8.sign(g.private_key)
    tx9 = Transaction(h.public_key,i.public_key,10,"nine")
    tx9.sign(h.private_key)
    tx10 = Transaction(i.public_key,j.public_key,20,"ten")
    tx10.sign(i.private_key)
    tx11 = Transaction(j.public_key,k.public_key,20,"eleven")
    tx11.sign(j.private_key)
    tx12 = Transaction(k.public_key,a.public_key,10,"twelve")
    tx12.sign(k.private_key)
    clients_list = [a,g,h,i,j,k]
    for i in range(20):
        amount = random.randint(1,1001)
        person = random.randint(0,5)
        person2 = random.randint(0,5)
        comment = str(time.time())
        tx1 = Transaction(clients_list[person].public_key,clients_list[person2].public_key,amount,comment)
        tx1.sign(clients_list[person].private_key)
        tx.append(tx1)
    tt = [tx1,tx2,tx3,tx4,tx5,tx6,tx7,tx8,tx9,tx10,tx11,tx12]
    tx.extend(tt)
    #b and c are selfish, d,e,f are honest so have a loop to decide
    miners2 = [[b,tx], [c,tx], [d,tx],[e,tx],[f,tx]]
    miners3 = [b,c,d,e,f]
    for i in miners2:
        random.shuffle(i[1])
        i[0].broadcast(i[1])
    x = 0
    lock = threading.Lock()
    while x < 4:
        x += 1
        for i in miners2:
            #Note that I tried a random.randint here, but did not get equal time as expected
            t= threading.Thread(name='selfish_mining', target=selfish_main, args=(i[0],coin,i[1],miners3,lock,))
            t.start()
            t.join(timeout=1)
    print(coin.past_transactions)
    for i in miners3:
        print(i.node_id,  '  ::::::: ',i.balance, '\n')
        print('list_transactions', len(i.trans_pool), '\n')

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
    my_lst = [1,2,3,4,5]
    while True:
        random.shuffle(my_lst) #pop out the index
        # i = my_lst[0]
        i = 1
        person = random.choice(lst)
        if i == 1:
            print('case 1 called \n')
            person2 = random.choice(lst)
            amount = random.randint(1,50)
            comment = 'random ' + str(amount)
            UT = send_tx(person,person2,amount,'random'+comment)
            receive_tx(person2, UT)
            person.verify_transaction(UT)
            print('verified transaction \n')
            new_transaction = []
            new_transaction.append(UT)
            miner_lst = [m1,m2,m3]
            random.shuffle(miner_lst) #to give them an equal probability of getting the time needed to create and add a block
            for i in miner_lst:
                #Note that I tried a random.randint here, but did not get equal time as expected
                t= threading.Thread(name='honest_mining', target=my_add2, args=(i,coin,new_transaction,miner_lst,))
                t.start()
                t.join(timeout=0.5)
            print(len(coin.past_transactions))
            for i in lst:
                print(i.node_id,'    :    ', i.balance, '\n')
            t = person.receive_bloc_header(coin)
            print('receive header: ', t, '\n')
            time.sleep(2)
        if i == 2:
            print('case 2 called \n')
            person2 = random.choice(lst)
            if isinstance(person,Miner):
                print(person.node_id, person2.node_id)
                print(person.check_balance_of_pub(person2.public_key))
            time.sleep(2)
        if i == 3:
            print('case 3 called \n')
            t = person.receive_bloc_header(coin)
            print('receive header: ', t, '\n')
            time.sleep(2)
        if i == 4:
            print('case 4 called \n')
            print(person.check_previous_header(), 'prev_header \n')
            time.sleep(2)
        if i == 5: #randomly generate a transaction and just add to pool. half of case 1
            print('case 5 called \n')
            person2 = random.choice(lst)
            amount = random.randint(1,50)
            comment = 'random ' + str(amount)
            UT = send_tx(person,person2,amount,'random'+comment)
            receive_tx(person2, UT)
            person.verify_transaction(UT)
            new_transaction = []
            new_transaction.append(UT)
            miner_lst = [m1,m2,m3]
            for i in miner_lst:
                i.broadcast(new_transaction)
            print('broadcasting is done \n')
            print(UT)
            time.sleep(2)
            

if __name__ == '__main__':
    # scheduled_network()
    # demo_spv()
    # demo_miner2()
    simulation_attack2()
    #final things left unimplemented:
    #SpV client: check for transactions by pulling about related transactions and building merkle tree