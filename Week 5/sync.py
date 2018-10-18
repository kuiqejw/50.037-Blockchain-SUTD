from Block import Block
from Blockchain import Blockchain
from config import *
from utils import is_valid_chain

import os
import json
import requests
import glob

def sync_local():
  local_chain = Chain([])
  #We're assuming that the folder and at least initial block exists
  if os.path.exists(CHAINDATA_DIR):
    for filepath in glob.glob(os.path.join(CHAINDATA_DIR, '*.json')):
      with open(filepath, 'r') as block_file:
        try:
          block_info = json.load(block_file)
        except:
          print filepath
        local_block = Block(block_info)
        local_chain.add_block(local_block)
  return local_chain

def sync_overall(save=False):
  best_chain = sync_local()
  for peer in PEERS:
    #try to connect to peer
    peer_blockchain_url = peer + 'blockchain.json'
    try:
      r = requests.get(peer_blockchain_url)
      peer_blockchain_dict = r.json()
      peer_blocks = [Block(bdict) for bdict in peer_blockchain_dict]
      peer_chain = Chain(peer_blocks)

      if peer_chain.is_valid() and peer_chain > best_chain:
        best_chain = peer_chain

    except requests.exceptions.ConnectionError:
      print "Peer at %s not running. Continuing to next peer." % peer
    else:
      print "Peer at %s is running. Gathered their blochchain for analysis." % peer
  print "Longest blockchain is %s blocks" % len(best_chain)
  #for now, save the new blockchain over whatever was there
  if save:
    best_chain.self_save()
  return best_chain

def sync(save=False):
	node_blocks = []