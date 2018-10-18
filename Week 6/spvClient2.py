import requests
import json
from flask import Flask, request
from KeyGenerator import generateKeyPair
from Transaction import Transaction


app = Flask(__name__)

miners_list = []
user = None
miner_server = 'http://127.0.0.1:8080'


# Single Client
# Functionalities: i) Create Transactions, ii) Verify transactions validated
class SPVClient:

    def __init__(self, privatekey, publickey):
        self.privatekey = privatekey
        self.publickey = publickey

    def save_keys(self):
        """Saves the keys to a file (wallet.txt)"""
        if self.publickey is not None and self.privatekey is not None:
            try:
                with open('wallet-{}.txt'.format(self.node_id), 'w') as f:
                    f.write(self.publickey.to_string().hex())
                    f.write('\n')
                    f.write(self.privatekey.to_string().hex())
                return True
            except Exception as E:
                print('Saving wallet failed')
                print(E)
                return False
    # Creates transaction and sign with private key
    def createTransaction(self, receivervk, amount, comment):
        new_transaction = Transaction(self.publickey, receivervk,
                                                   amount, comment)
        new_transaction.sign(self.privatekey)
        return new_transaction

    # Check acc balance of specified spvclient
    def checkBalance(self, _address):
        # get blockchain from miner
        blockchain = ""

        response = requests.get(_address + '/blockchain',
                     headers={'Content-Type': 'application/json'}, json=blockchain)

        # not sure if this is needed
        blockchain = response.json()

        balance = blockchain["current_block"]["state"]["Balance"][self.publickey]
        return balance
    def check_transaction_in_chain(self, transaction, chain):
        i = transaction
        if not hashlib.sha256(i.to_json().encode()).hexdigest() in chain.past_transactions_hashes:
            print('False')
        else:
            print('True',)
    def getMiners(self, _trusted_server):
        response = requests.get(_trusted_server)
        return response.json()["miners_list"]

@app.route('/')
def homepage():
    return "This is the homepage of SPV Clients"


# todo: create endpoint which provides frontend for creation of transaction
@app.route('/login/<pub>/<priv>')
def login(pub, priv):
    # temporary
    global user
    user = SPVClient(privatekey=priv, publickey=pub)
    return homepage()


# When Transaction created, Broadcast to all miners done here
@app.route('/createTransaction', methods=['POST'])
def createTransaction():
    if user is None:
        return "Please login"

    if request.headers['Content-Type'] == 'application/json':
        #Receive data regarding transaction
        json_received = request.json
        transaction_data = json.loads(json_received)
        print(transaction_data)

        transaction = user.createTransaction(
                        receivervk=transaction_data["recv"],
                        amount=transaction_data["Amount"],
                        comment=transaction_data["Comment"]
                        )

        miners_list = user.getMiners(miner_server + '/updateSPVMinerList')

        # broadcast to all known miners
        for miner in miners_list:
            # execute post request to broadcast transaction
            broadcast_endpoint = miner + "/newTransaction"
            requests.post(
                url=broadcast_endpoint,
                json=transaction.to_json()
            )

    else:
        return 'wrong format of transaction sent'


# Check with any miner on acc balance (Based on public key received)
@app.route('/clientCheckBalance', methods=['GET'])
def clientCheckBalance():
    return user.checkBalance(miners_list[0])


if __name__ == '__main__':
    app.run(port=8081)

