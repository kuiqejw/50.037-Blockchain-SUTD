from ecdsa import SigningKey
#Just add nonce!!!!
#Transaction with blockchain
import random
import json
from datetime import datetime
import binascii
from collections import OrderedDict
class Transaction:

    def __init__(self, sender, receiver, amount,comment=None, nonce=None,private_key=None):
        # Instantiates object from passed values
        self.sender = sender #public key
        self.receiver = receiver #public key
        self.amount = amount
        self.private_key = private_key
        self.comment=comment
        if nonce == None:
            self.nonce = self.make_nonce()# nonce 
        self.signature = ""
        # self.sign(private_key)


    def make_nonce(self):
        #Generate pseudo random no. 
        return random.getrandbits(32)

    def to_json(self):
        # Serializes object to JSON string
        dicty = {}
        dicty['sender'] = self.sender.to_string().hex() #Since it's an Id in a string, no conversion
        dicty['receiver'] = self.receiver.to_string().hex()
        dicty['amount'] = str(self.amount)
        dicty['nonce'] = self.nonce
        dicty['comment'] = self.comment
        return json.dumps(dicty)
    def to_dict(self):
        return OrderedDict({'sender_address': binascii.hexlify(self.sender.to_string()).decode('ascii'),
                            'recipient_address': binascii.hexlify(self.receiver.to_string()).decode('ascii'),
                            'value': self.amount,
                            'nonce':self.nonce,
                            'comment':self.comment})

    def from_json(self, data):
        # Instantiates/Deserializes object from JSON string
        tran = json.loads(data)
        #since sender, and receiver public key is known
        cls2 = Transaction(sendervk,receivervk, tran['amount'],nonce=tran['nonce'], comment=tran['comment']) 
        cls2.signature = bytes.fromhex(tran['signature'])
        return cls2

    def sign(self, private_key):
        tuccy = self.sender.to_string().hex()+self.receiver.to_string().hex()+str(self.amount)
        # That can be called within new()
        if self.signature == "":
            self.signature = private_key.sign(str.encode(tuccy)) #self.signature in bytes
        return binascii.hexlify(self.signature).decode('ascii')


    def validate(self, signature, sendervk):
        # Validate transaction correctness.
        tuccy = self.sender.to_string().hex()+self.receiver.to_string().hex()+str(self.amount)
        #cleared the signature
        print('tuccy', tuccy)
        signature =  binascii.unhexlify(signature.encode('ascii'))
        try:
            print(sendervk.verify(signature,str.encode(tuccy)))
            return sendervk.verify(signature,str.encode(tuccy))
        except:
            print('False Signature')

# class Transaction:

#     def __init__(self, sender, receiver, amount, private_key=None, comment=None):
#         # Instantiates object from passed values
#         self.sender = sender #public key
#         self.receiver = receiver #public key
#         self.amount = amount
#         # self.timestamp = datetime.now()
#         self.nonce = self.make_nonce()# nonce 
#         self.comment = comment
#         self.private_key= private_key
#         self.signature = ""


#     def make_nonce(self):
#         #Generate pseudo random no. 
#         return random.getrandbits(32)

#     def to_json(self):
#         # Serializes object to JSON string
#         dicty = {}
#         dicty['sender'] = self.sender.to_string().hex() #Since it's an Id in a string, no conversion
#         dicty['receiver'] = self.receiver.to_string().hex()
#         dicty['amount'] = str(self.amount)
#         dicty['nonce'] = self.nonce
#         return json.dumps(dicty)
#     def to_dict(self):
#         return OrderedDict({'sender_address': binascii.hexlify(self.sender.to_string()).decode('ascii'),
#                             'recipient_address': binascii.hexlify(self.receiver.to_string()).decode('ascii'),'value': self.amount})

#     def from_json(self, data):
#         # Instantiates/Deserializes object from JSON string
#         tran = json.loads(data)
#         print(tran)
#         #since sender, and receiver public key is known
#         cls2 = Transaction(sendervk,receivervk, tran['amount']) 
#         cls2.signature = bytes.fromhex(tran['signature'])
#         return cls2

#     def sign(self, private_key):
#         tuccy = self.sender.to_string().hex()+self.receiver.to_string().hex()+str(self.amount)+self.nonce
#         # That can be called within new()
#         if self.signature == "":
#             self.signature = private_key.sign(str.encode(tuccy)) #self.signature in bytes
#         return binascii.hexlify(self.signature).decode('ascii')


#     def validate(self, signature, sendervk):
#         # Validate transaction correctness.
#         tuccy = self.sender.to_string().hex()+self.receiver.to_string().hex()+str(self.amount)+self.nonce
#         #cleared the signature
#         print(type(self.sender))
#         print(type(self.receiver))
#         signature =  binascii.unhexlify(signature.encode('ascii'))
#         print(sendervk.verify(signature,str.encode(tuccy)))
#         return sendervk.verify(signature,str.encode(tuccy))
