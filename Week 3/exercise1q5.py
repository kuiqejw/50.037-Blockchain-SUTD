import hashlib
from typing import List
class Node():
    # Each node has a parent, a left and a right child.
    # Some nodes (firsthash) only have one child (data)
    def __init__(self, hashvalue: bytes):
        self.data = hashvalue
        self.parent, self.left, self.right = None, None, None
        
    def addparent(self, parent: 'Node'):
        self.parent = parent
    
    def addchildren(self, left: 'Node' = None, right: 'Node' = None):
        self.left = left
        self.right = right

class MerkleTree():

    def __init__(self, transactions=None):
        self.nodes = []
        self.past_transactions = []
        self.past_transactions_hashes = []
        if transactions != None:
            for i in transactions:
                self.add(i)


    def add(self, new_transaction):
        # self.past_transactions.append(new_transaction)
        new_hash_hex_digest = hashlib.sha256(new_transaction).hexdigest()
        self.past_transactions.append(new_transaction)
        self.past_transactions_hashes.append(new_hash_hex_digest)
        print('add new transaction with hex digest: ', new_hash_hex_digest)
        # Add entries to tree
        
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
        for i in self.past_transactions_hashes:
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
        print(currnode.parent.parent.data)
        # When we find the entry, we can get hashes required for proof
        while(currnode.parent != None):
            prevnode = currnode
            currnode = currnode.parent
            if(currnode.left == prevnode):
                hashlist.append([currnode.right.data, "r", self.check(currnode.right.data)])
            else:
                hashlist.append([currnode.left.data, "l", self.check(currnode.left.data)])
        print(hashlist)
        return hashlist

    def check(self, entryhash):
        for i,j in enumerate(self.tiered_node_list):
                if(j.data == entryhash):
                    itemindex = i 
        return itemindex   
    def get_root(self):
        # Return the current root
        self.build()
        return self.tiered_node_list[-1].data
    
def verify_proof(entry, proof, root):
    # Verifies proof for entry and given root. Returns boolean.
    currhash = hashlib.sha256(entry).hexdigest()
    # print(currhash)
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

if __name__ == "__main__":
    x = MerkleTree()
    x.add(b'1')
    x.add(b'second')
    x.add(b'tres')
    x.build()
    assert(len(x.past_transactions) == 3)
    assert(len(x.tiered_node_list) == 5)
    
    x.add(b'umpat')
    x.add(b'quin')
    x.build()
    assert(len(x.past_transactions) == 5)
    # print(len(x.tiered_node_list))
    assert(len(x.tiered_node_list) == 9)
    for i in x.tiered_node_list:
        print(i.data)
        print('/n')
    print(x.get_root().data)

    totalhash = x.tiered_node_list[0].data + x.tiered_node_list[1].data
    firsthash = Node(hashlib.sha256(totalhash.encode()).hexdigest())
    totalhash = x.tiered_node_list[2].data + x.tiered_node_list[3].data
    secondhash = Node(hashlib.sha256(totalhash.encode()).hexdigest())
    # print(firsthash.data)
    # print(secondhash.data)
    totalhash = firsthash.data + secondhash.data
    thirdhash = Node(hashlib.sha256(totalhash.encode()).hexdigest())
    # print(thirdhash.data)
    print(verify_proof(b'tres', x.get_proof(b'tres'), x.get_root()))