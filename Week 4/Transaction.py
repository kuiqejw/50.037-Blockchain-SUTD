from ecdsa import SigningKey
#Just add nonce!!!!
import random
import json
from datetime import datetime
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


    def make_nonce(self):
        #Generate pseudo random no. 
        # print('random bits', random.getrandbits(32))
        return random.getrandbits(32)
        # return '1111'

    def to_json(self):
        # Serializes object to JSON string
        dicty = {}
        dicty['sender'] = self.sender #Since it's an Id in a string, no conversion
        dicty['receiver'] = self.receiver
        dicty['amount'] = str(self.amount)
        dicty['comment'] = self.comment
        dicty['nonce'] = self.nonce
        return json.dumps(dicty)

    def from_json(self, data):
        # Instantiates/Deserializes object from JSON string
        tran = json.loads(data)
        print(tran)
        #since sender, and receiver public key is known
        cls2 = Transaction(sendervk,receivervk, tran['amount'], tran['comment'], tran['nonce']) 
        cls2.signature = bytes.fromhex(tran['signature'])
        return cls2

    def sign(self, private_key):
        tuccy = self.sender+self.receiver+str(self.amount)+self.comment
        # That can be called within new()
        print('touche',tuccy)
        if self.signature == "":
            self.signature = private_key.sign(str.encode(tuccy)) #self.signature in bytes


    def validate(self, signature, sendervk):
        # Validate transaction correctness.
        tuccy = self.sender+self.receiver+str(self.amount)+self.comment
        #cleared the signature
        print(sendervk.verify(signature,str.encode(tuccy)))
        

    def __eq__(self,other):
        # Check whether transactions are the same
        return self.amount == other.amount and self.receiver == other.sender and self.sender == other.receiver and self.comment == other.comment
