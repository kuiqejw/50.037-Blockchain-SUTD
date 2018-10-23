from ecdsa import SigningKey
#Just add nonce!!!!
import random
import json
from datetime import datetime
import binascii
from collections import OrderedDict
class Transaction:

    def __init__(self, sender, receiver, amount, comment):
        # Instantiates object from passed values
        self.sender = sender #public key
        self.receiver = receiver #public key
        self.amount = amount
        self.comment = comment
        # self.timestamp = datetime.now()
        self.nonce = self.make_nonce()# nonce 
        self.signature = ""
        self.sender_str = sender.to_string().hex()
        self.recevier_str = receiver.to_string().hex()
    def __repr__(self): #used for debugging without print, __repr__ > __str__
        return "Transaction<sender: %s>, <receiver: %s> , <amount: %s> \n, <nonce: %i>, <comment %s>\n" % (self.sender_str,
         self.recevier_str, self.amount, self.nonce, self.comment)
    def make_nonce(self):
        #Generate pseudo random no. 
        return random.getrandbits(32)

    def to_json(self):
        # Serializes object to JSON string
        dicty = {}
        dicty['sender'] = self.sender.to_string().hex() #Since it's an Id in a string, no conversion
        dicty['receiver'] = self.receiver.to_string().hex()
        dicty['amount'] = str(self.amount)
        dicty['comment'] = self.comment
        dicty['nonce'] = self.nonce
        return json.dumps(dicty)
    def to_dict(self):
        return OrderedDict({'sender_address': binascii.hexlify(self.sender.to_string()).decode('ascii'),
                            'recipient_address': binascii.hexlify(self.receiver.to_string()).decode('ascii'),'value': self.amount})

    def from_json(self, data):
        # Instantiates/Deserializes object from JSON string
        tran = json.loads(data)
        #since sender, and receiver public key is known
        cls2 = Transaction(sendervk,receivervk, tran['amount'], tran['comment'], tran['nonce']) 
        cls2.signature = bytes.fromhex(tran['signature'])
        return cls2

    def sign(self, private_key):
        tuccy = self.sender.to_string().hex()+self.receiver.to_string().hex()+str(self.amount)+self.comment
        # That can be called within new()
        if self.signature == "":
            self.signature = private_key.sign(str.encode(tuccy)) #self.signature in bytes
        return binascii.hexlify(self.signature).decode('ascii')


    def validate(self, signature, sendervk):
        # Validate transaction correctness.
        tuccy = self.sender.to_string().hex()+self.receiver.to_string().hex()+str(self.amount)+self.comment
        #cleared the signature
        return sendervk.verify(signature,str.encode(tuccy))
