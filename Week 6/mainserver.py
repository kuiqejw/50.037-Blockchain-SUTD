from flask import Flask, request
import json

app = Flask(__name__)

miners_list = []

# todo: (low priority) remove /updateSPVMinerList, use this instead
# runs on http://127.0.0.1:8080/
@app.route('/')
def setupServer():
    json_miners_list = json.dumps({'miners_list': miners_list})
    return json_miners_list


@app.route('/add', methods=["POST"])
def addNewMiner():
    global miners_list

    miner = request.form.get('miner')

    if miner not in miners_list:
        miners_list.append(miner)
    return setupServer()


@app.route('/updateSPVMinerList')
def updateMinerList():
    json_miners_list = json.dumps({'miners_list' : miners_list})
    return json_miners_list


if __name__ == '__main__':
    # use this for visibility to others
    machine_IP = ""
    if machine_IP == "":
        machine_IP = "localhost"
    app.run(host=machine_IP, port=8080)
