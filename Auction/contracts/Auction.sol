pragma solidity ^0.4.19;//which compiler can be used
//this smart contract represents an auction house
contract Auction {
  address public manager;
  address public seller;
  uint public latestBid;
  address public latestBidder;
 
  constructor() public {//This constructor is a special function that is run initially when the contract is deployed.
    manager = msg.sender;
  }
 
  function auction(uint bid) public {//write the function to set the initial amount of bid.
    latestBid = bid * 1 ether; //1000000000000000000;
    seller = msg.sender;
  }
 
  function bid() public payable {
    require(msg.value > latestBid);
 
    if (latestBidder != 0x0) { //proviso if there is no bid
      latestBidder.transfer(latestBid);
    }
    latestBidder = msg.sender;
    latestBid = msg.value;
  }
 
  function finishAuction() restricted public {
    seller.transfer(address(this).balance);
  }
 
  modifier restricted() {
    require(msg.sender == manager);
    _;
  }
}