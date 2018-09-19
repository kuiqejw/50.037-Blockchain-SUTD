import hashlib
from hashlib import sha1
from binascii import hexlify
from itertools import product
from sys import argv
from random import getrandbits, randint
from os import urandom
####Q1
def encrypt_string256(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

def encrypt_string512(hash_string):
    sha_signature = \
        hashlib.sha512(hash_string.encode()).hexdigest()
    return sha_signature    
def encrypt_string3256(hash_string):
    sha_signature = \
        hashlib.sha3_256(hash_string.encode()).hexdigest()
    return sha_signature

def encrypt_string3512(hash_string):
    sha_signature = \
        hashlib.sha3_512(hash_string.encode()).hexdigest()
    return sha_signature

# sha_signature = encrypt_string256(hash_string)
# print(sha_signature)

# sha_signature = encrypt_string512(hash_string)
# print(sha_signature)

# sha_signature = encrypt_string3256(hash_string)
# print(sha_signature)

# sha_signature = encrypt_string3512(hash_string)
# print(sha_signature)

