# Blockchain_Helper
Place to Store in case my com crashes
SUTD 50.037 by 1002464

## Review on Bitcoin implementation - Week 

From the TA:
Base on my understanding of the submitted code, there may be an error.


For instance:

demo.demo_miner()

   |- line 100 -> it call b.add_to_chain() with not prior validation

           |- Miner.py.add_to_chain()

                   |- line 80 - before a block is added into the blockchain, it only validates by calling blck_check2() which is a

                                     function that only checks that a block's transaction has been spent before (UTXO model).

                                     However, it does not check balances, and then, adds the evaluating block to the blockchain.

                                     So a malicious miner can send transactions that spend more.


On the other hand, miner rewards (Miner.get_reward function) only add coins to miner's balance, but it does not perform a coinbase transaction. So, other miners may not be able to validate.


The network approach was defined as deploying a flask/socket based communication.


Note: I didn't deduct network points due to the implementation using threads.


I will look forward to your comments in case I misunderstood anything in your implementation.


Regards.

Humbly thinks that should have made peer validation requested upon reward for mining. Add to chain needs peer validation!

Submission on time 	X
Signed transactions 	X
TX nonce (not re-sending) 	X
Block + PoW 	X
SPV validates Merkle tree hash in Block header 	-
Global UTXO/addr:balance + balance for checking TXs 	-
Forks 	X
Self-mining + 51% 	X
Network 	X
Document 	X
Errors/comments 	Threads instead of sockets/flask

As seen in the marking scheme above, SPV does not validate the merkle tree in their blockheader. The above comment is with regards to Global UTXO/addr:balance + balance for checking TX. This can be done via storing a balance of the public key and checking by the miner if the transaction gets issued. :__( Plus a call for Peer Validation)

Let's work harder for Distributed Hash
