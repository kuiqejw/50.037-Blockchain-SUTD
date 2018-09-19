import hashlib
from hashlib import sha1
from binascii import hexlify
from itertools import product
from sys import argv
from random import getrandbits, randint
from os import urandom
#Q2
#hashmap stores hash dictionary
hashmap = {}
#hashchars represents number of characters to consider in hash function, starting from begin
#ie 6 = 6 bytes of sha
HASHCHARS = 1
def sha_hash(hash_string, n):
	return hashlib.sha512(hash_string).digest()[n]

def show(right, left):
    # Print stuff.
    print('Collision found!')
    print(str(left)
            + ' hashes to ' + str(sha_hash(left, HASHCHARS))
            + ', but ' + str(right)
            + ' also hashes to ' + str(sha_hash(right, HASHCHARS)))

def is_collision(bits):
    hash = sha_hash(bits, HASHCHARS)
    if hash not in hashmap:
        hashmap[hash] = bits
        return None
    elif not (hashmap[hash] == bits):
        collision = hashmap[hash]
        show(bits, collision)
        return collision
    return None

def collide(maxinput=64):
    x = 0
    trial = urandom(randint(1, maxinput))
    while not is_collision(trial):
        trial = urandom(randint(1, maxinput))
        x += 1
    print('Took ' + str(x) + ' trials')


if len(argv) > 1:
    n = int(argv[1])
    if len(argv) > 2:
        HASHCHARS=int(argv[2])
    collide(n)
else:
    collide()
'''
Collision found!
b'8dcd7a86a0c49828af3f03f61bae91d29f80536fa256bf68c787846c0a08cd43ef17fa48d6cdd1cff0d36ec9a18e58218d38d2857a086f' hashes to 74, but b'7a9497d0d5e126008a81a1fc03c375505671ba9b7520fb3b12f37bdf06' also hashes to 74
Took 21 trials
[Finished in 0.4s]
Collision found!
b'27fb434f1a749b0e00bf' hashes to e9d3, but b'13dc36f87ee14928fc6e2c69039eeca47b976569bb7725943a34b847fe1e3f436aeea16699a9' also hashes to e9d3
Took 638 trials
[Finished in 0.3s]
for 16 bits
Collision found!
b'6cf6fd3ab4b1e299cba2274cc4168e105d2b283b21bbc611936c6993d1fb7b88cb1f5dc29c605c554c304bd546eabb60f78976' hashes to a6e487, but b'cf92206bc9023021a87150be9db36c8d94b5c979c476b6117cc018d5cfda' also hashes to a6e487
Took 807 trials
[Finished in 0.3s]
for 24 bits
Collision found!
b'14bdeaf237334ae58a7d11cb7d4e67ea0ddc5fdb0904' hashes to 00bae275, but b'062e25d1ab0bf65a0cefa9f294b408c7dbd155220a8ec58c867df0' also hashes to 00bae275
Took 71674 trials
[Finished in 2.6s]
for 32 bits
Collision found!
b'845dc68877ce9f337ddd5b7cf6' hashes to bedb696aec, but b'0d9a03672e4863eb23e8d9aaf0a18f63f7f9637faf2a8e998dc6e8e0f0defd3b32db15c20b84210811f5d4e1d1283c88e2f52b' also hashes to bedb696aec
Took 949130 trials
[Finished in 19.3s]
for 40 bits
'''

def sha_hash(hash_string, n):
	return hashlib.sha512(hash_string).digest()
# print(type(sha_hash('block'))
def is_preimage(inp):
    hash = sha_hash(inp, 8)
    if hash.startswith(b"\x00"*4):
    	print(hash.hex())
    	return hash
    else:
    	return None

def preimage(maxinput=64):
    x=0
    trial = urandom(randint(1, maxinput))
    while not is_preimage(trial):
        trial = urandom(randint(1, maxinput))
        x += 1
    print('Took ' + str(x) + ' trials')

if len(argv) > 1:
    n = int(argv[1])
    if len(argv) > 2:
        HASHCHARS=int(argv[2])
    preimage(n)
else:
    preimage()

'''
1: Took 369 trials
[Finished in 0.2s]
2: Took 63761 trials
[Finished in 1.2s]
3:Took 56834003 trials
[Finished in 870.6s]
4:
5:

'''

# #Q3
# import ecdsa
# # SECP256k1 is the Bitcoin elliptic curve
# sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST192p) 
# vk = sk.get_verifying_key()
# sig = sk.sign(b"Blockchain Technology")
# vk.verify(sig, b"Blockchain Technology") # True
