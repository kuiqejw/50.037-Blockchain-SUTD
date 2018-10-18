CHAINDATA_DIR = 'chaindata/'
BROADCASTED_BLOCK_DIR = CHAINDATA_DIR + 'bblocs/'
NUM_ZEROS = 2

PEERS = [
    'http://localhost:5000/',
    'http://localhost:5001/',
    'http://localhost:5002/',
    'http://localhost:5003/',
    ]

BLOCK_VAR_CONVERSIONS = {'longest_link':int,'index': int, 'prev_hash': str,'nonce': int, 'hash': str,'timestamp': int}