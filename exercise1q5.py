class MerkleTree(Object):
    def __init__(self):
        self.past_transactions = []
        self.past_transaction_hashes = []
        self.tiered_node_list = []
        self.root = None


    def add(self, new_transaction):
        new_hash_hex_digest = hashlib.sha512(new_transaction).hexdigest()
        self.past_transactions.append(new_transaction)
        self.past_transactions_hashes.append(new_hash_hex_digest)
        print('add new transaction with hex digest: ', new_hash_hex_digest)
        # Add entries to tree
        

    def build(self):
        # Build tree computing new root
        num_leaves = len(self.past_transactions)#grab the number of leaves
        remaining_nodes = num_leaves
        active_level = self.past_transaction_hashes
        while remaining_nodes != 1:
            if remaining_nodes % 2:
                odd = False
            else:
                odd = True

            new_tier = []
            for i in range(1, remaining_nodes,2):
                #create the new tier on top of active_level -1 and active leve current hash
                combined_str = str(active_level[i-1]) + str(active_level[i])
                new_hash = hashlib.sha512(combined_str.encode()).hexdigest()
                new_tier.append(new_hash)
            if odd:
                #
                new_tier.append(active_level[num_leaves-1].encode())
            self.tiered_node_list.append(new_tier)
            remaining_nodes = len(new_tier)
            active_level = new_tier

        self.tiered_node_list.insert(0,self.past_transaction_hashes) #insert in front of previous hashes
        self.root = self.tiered_node_list[-1] #seize root from back of tiered node list
        print('Tree build complete\n'  + 'No. of levels: ', len(self.tiered_node_list))
        # hash_type = hash_type.lower()
        # if hash_type in ['sha256', 'md5', 'sha224', 'sha384', 'sha512',
        #                  'sha3_256', 'sha3_224', 'sha3_384', 'sha3_512']:
        #     self.hash_function = getattr(hashlib, hash_type)
        # else:
        #     raise Exception('`hash_type` {} nor supported'.format(hash_type))
        # self.leaves = list()
        # self.levels = None
        # self.is_ready = False

    def get_proof(self, index):
        # Get membership proof for entry
        if self.levels is None:
            return None
        elif not self.is_ready or index > len(self.leaves)-1 or index < 0:
            return None
        else:
            proof = []
            for x in range(len(self.levels) - 1, 0, -1):
                level_len = len(self.levels[x])
                if (index == level_len - 1) and (level_len % 2 == 1):  # skip if this is an odd end node
                    index = int(index / 2.)
                    continue
                is_right_node = index % 2
                sibling_index = index - 1 if is_right_node else index + 1
                sibling_pos = "left" if is_right_node else "right"
                sibling_value = hex(self.levels[x][sibling_index])
                proof.append({sibling_pos: sibling_value})
                index = int(index / 2.)
        return proof
    def get_leaf(self, index):
        return hex(self.leaves[index])
    def get_root(self):
        # Return the current root
        if not self.root:
            print('No root found')
            return None
        return self.tiered_node_list[-1]
    
def verify_proof():
    pass