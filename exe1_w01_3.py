import hashlib
from hashlib import sha1
from binascii import hexlify
from itertools import product
from sys import argv
from random import getrandbits, randint
from os import urandom


# #Q3
import ecdsa
# SECP256k1 is the Bitcoin elliptic curve
sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST192p) 
vk = sk.get_verifying_key()
sig = sk.sign(b"Blockchain Technology")
vk.verify(sig, b"Blockchain Technology") # True
