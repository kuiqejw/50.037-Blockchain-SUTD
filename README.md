# Blockchain_Helper
Place to Store in case my com crashes
SUTD 50.037 Blockchain Technology

### Yes. This is an A Scoring Project. 

## Review on Bitcoin implementation - Small Mini Project

From the TA:
Base on my understanding of the submitted code, there may be an error.


For instance:

demo.demo_miner()
```
line 100 -> it call b.add_to_chain() with not prior validation. Miner.py.add_to_chain()

line 80 - before a block is added into the blockchain, it only validates by calling blck_check2() which is a function that only checks that a block's transaction has been spent before (UTXO model).However, it does not check balances, and then, adds the evaluating block to the blockchain. So a malicious miner can send transactions that spend more.


On the other hand, miner rewards (Miner.get_reward function) only add coins to miner's balance, but it does not perform a coinbase transaction. So, other miners may not be able to validate.

The network approach was defined as deploying a flask/socket based communication.

Note: I didn't deduct network points due to the implementation using threads.

I will look forward to your comments in case I misunderstood anything in your implementation.

Regards.

```
### Grading Scheme
Humbly thinks that should have made peer validation requested upon reward for mining. Add to chain needs peer validation!

1. Submission on time 	X
2. Signed transactions 	X
3. TX nonce (not re-sending) 	X
4. Block + PoW 	X
5. SPV validates Merkle tree hash in Block header 	-
6. Global UTXO/addr:balance + balance for checking TXs 	-
7. Forks 	X
8. Self-mining + 51% 	X
9. Network 	X
10. Document 	X
11. Errors/comments 	Threads instead of sockets/flask

As seen in the marking scheme above, SPV does not validate the merkle tree in their blockheader. The above comment is with regards to Global UTXO/addr:balance + balance for checking TX. This can be done via storing a balance of the public key and checking by the miner if the transaction gets issued. :__( Plus a call for Peer Validation)

Big Project is stored under https://github.com/kuiqejw/Auction-Dapp-Solidity
