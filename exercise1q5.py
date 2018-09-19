class MerkleTree(Object):

    def add(self, values, do_hash=False):
        # Add entries to tree
        self.is_ready = False 
        if not isinstance(values, tuple) and not isinstance(values, list):
            values = [values]
        for v in values:
            if do_hash:
                v = v.encode('utf-8')
                v = self.hash_function(v).hexdigest()
            v = bytearray.fromhex(v)
            self.leaves.append(v)

    def build(self, hash_type = 'sha256'):
        # Build tree computing new root
        hash_type = hash_type.lower()
        if hash_type in ['sha256', 'md5', 'sha224', 'sha384', 'sha512',
                         'sha3_256', 'sha3_224', 'sha3_384', 'sha3_512']:
            self.hash_function = getattr(hashlib, hash_type)
        else:
            raise Exception('`hash_type` {} nor supported'.format(hash_type))
        self.leaves = list()
        self.levels = None
        self.is_ready = False

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
        if self.is_ready:
            if self.levels is not None:
                return hex(self.levels[0][0])
            else:
                return None
        else:
        return None
    def validate_proof(self, proof, target_hash, merkle_root):
        merkle_root = bytearray.fromhex(merkle_root)
        target_hash = bytearray.fromhex(target_hash)
        if len(proof) == 0:
            return target_hash == merkle_root
        else:
            proof_hash = target_hash
            for p in proof:
                try:
                    # the sibling is a left node
                    sibling = bytearray.fromhex(p['left'])
                    proof_hash = self.hash_function(sibling + proof_hash).digest()
                except:
                    # the sibling is a right node
                    sibling = bytearray.fromhex(p['right'])
                    proof_hash = self.hash_function(proof_hash + sibling).digest()
        return proof_hash == merkle_root

def verify_proof(entry, proof, root):
    # Verifies proof for entry and given root. Returns boolean.
    mt = MerkleTools(hash_type = 'md5')
    mt.validate_proof(proof, entry,root)