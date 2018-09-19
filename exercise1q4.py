#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ecdsa
import json


sender = ecdsa.SigningKey.generate()
sendervk = sender.get_verifying_key()
sig = sender.sign(b"message")
sendervk.verify(sig, b"message") # True)

receiver = ecdsa.SigningKey.generate()
receivervk = receiver.get_verifying_key()
sig = receiver.sign(b"message")
receivervk.verify(sig, b"message") # True
class Transaction:

    def __init__(self, sender, receiver, amount, comment, private_key):
        # Instantiates object from passed values
        self.sender = sender #public key
        self.receiver = receiver #public key
        self.amount = amount
        self.comment = comment
        self.signature = ""
        self.sk = private_key

    def to_json(self):
        # Serializes object to JSON string
        dicty = {}
        self.sign()
        dicty['sender'] = self.sender.to_string().hex()
        dicty['receiver'] = self.receiver.to_string().hex()
        dicty['amount'] = str(self.amount)
        dicty['comment'] = self.comment
        dicty['signature'] = str(self.signature)
        return json.dumps(dicty)
        # return json.dumps(self, default = lambda o: o.__dict__, sort_keys=True, indent=4)

    def from_json(self, data):
        # Instantiates/Deserializes object from JSON string
        tran = json.loads(data)
        print(tran)
        #since sender, and receiver public key is known
        cls2 = Transaction(sendervk,receivervk, tran['amount'], tran['comment'], tran['signature']) 
        cls2.signature = tran['signature']
        return cls2

    def sign(self):
        tuccy = self.sender.to_string().hex()+self.receiver.to_string().hex()+str(self.amount)+self.comment
        # That can be called within new()
        if self.signature == "":
            self.signature = sender.sign(str.encode(tuccy)) #self.signature in bytes

    def validate(self):
        # Validate transaction correctness.
        # Can be called within from_json()
        tuccy = self.sender.to_string().hex()+self.receiver.to_string().hex()+str(self.amount)+self.comment
        #cleared the signature
        self.signature = sender.sign(str.encode(tuccy))
        print(sendervk.verify(self.signature,str.encode(tuccy)))
        

    def __eq__(self,other):
        # Check whether transactions are the same
        return self.amount == other.amount and self.receiver == other.sender and self.sender == other.receiver and self.comment == other.comment

##TEST##
#Sender creates a transaction
a = Transaction(sendervk,receivervk,80,"no", sender)#sender = private key, sendervk = sender public key, receiver vk = receiver public key
tran1 = a.to_json()
p = a.from_json(tran1)
p.validate()