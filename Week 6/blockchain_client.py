'''
title           : blockchain_client.py
description     : A blockchain client implemenation, with the following features
                  - Wallets generation using Public/Private key encryption (based on ECDSA algorithm)
                  - Generation of transactions with ECDSA encryption      
724df00c21f50201db5d63606759b7f176a63d5bd45a7965ce71869db00248a86c1ed6051abe4451912b77ab35b9d053
f85097dffb5d49d4d3645ba5499fb0c7f2b147d46e5886ab
version         : 0.3
usage           : python blockchain_client.py
                  python blockchain_client.py -p 8080
                  python blockchain_client.py --port 8080
python_version  : 3.6.1
Comments        : Wallet generation and transaction signature is based on [1]
References      : [1] https://github.com/julienr/ipynb_playground/blob/master/bitcoin/dumbcoin/dumbcoin.ipynb
'''

from collections import OrderedDict
from ecdsa import SigningKey, NIST384p, VerifyingKey
import binascii
from KeyGenerator import generateKeyPair
import requests
import random
from flask import Flask, jsonify, request, render_template

class Transaction:

    def __init__(self, sender, receiver, amount, private_key=None,comment=None,nonce=None):
        # Instantiates object from passed values
        self.sender = sender #public key
        self.receiver = receiver #public key
        self.amount = amount
        self.private_key = private_key
        self.comment=comment
        if nonce == None:
            self.nonce = self.make_nonce()# nonce 
        self.signature = ""
        self.sign(private_key)


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
        print('tuccy', tuccy)
        if self.signature == "":
            self.signature = private_key.sign(str.encode(tuccy)) #self.signature in bytes
        return binascii.hexlify(self.signature).decode('ascii')


    def validate(self, signature, sendervk):
        # Validate transaction correctness.
        tuccy = self.sender.to_string().hex()+self.receiver.to_string().hex()+str(self.amount)
        #cleared the signature
        return sendervk.verify(signature,str.encode(tuccy))



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/make/transaction')
def make_transaction():
    return render_template('./make_transaction.html')

@app.route('/view/transactions')
def view_transaction():
    return render_template('./view_transactions.html')

@app.route('/wallet/new', methods=['GET'])
def new_wallet():
    private_key, public_key = generateKeyPair()
    response = {
        'private_key': binascii.hexlify(private_key.to_string()).decode('ascii'),
        'public_key': binascii.hexlify(public_key.to_string()).decode('ascii')
    }

    return jsonify(response), 200

@app.route('/generate/transaction', methods=['POST'])
def generate_transaction():
    sender_address = request.form['sender_address']
    sender_private_key = request.form['sender_private_key']
    recipient_address = request.form['recipient_address']
    value = request.form['amount']
    comment = request.form['comment']
    sendervk = binascii.unhexlify(sender_address.encode('ascii'))
    sendervk = VerifyingKey.from_string(sendervk)
    sender = binascii.unhexlify(sender_private_key.encode('ascii'))
    sender = SigningKey.from_string(sender)
    receivervk = binascii.unhexlify(recipient_address.encode('ascii'))
    receivervk = VerifyingKey.from_string(receivervk)

    transaction = Transaction(sendervk, receivervk, value, sender, comment)

    response = {'transaction': transaction.to_dict(),'nonce':transaction.nonce, 'signature': transaction.sign(sender)}
    try:
        return jsonify(response), 200
    except Exception as E:
        print(E)
        return "This Sucks MUCH"

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)