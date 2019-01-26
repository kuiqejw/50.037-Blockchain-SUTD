pragma solidity ^0.4.25;

//First contract to make, the Auction

contract AuctionContract {

    struct Auction {
        address seller;
        address topBidder;
        uint256 startPrice;
        uint256 endPrice;
        string itemDescription;
        uint8 auctionStatus;
        //uint64 auctionDuration; 
        uint256 highestBid;
        uint256 auctionEndTime;
        
    }

    //Assign an identity to an Auction
    mapping(uint256 => Auction) public iDtoAuction;

    //Allowed withdrawals of previous bids
    mapping(address => uint) pendingReturns;

    //Couple of events needed for the 
    event NewAuction(address seller, uint256 startPrice, string itemDescription, uint8 auctionStatus, uint64 auctionDuration, uint256 auctionEndTime);
    event NewBid (address seller, uint256 startPrice, uint8 auctionStatus);
    event highestBidIncreased(address topBidder, uint256 amount);
    event AuctionEnded(address topBidder, uint256 endPrice, uint8 auctionStatus);

    //Instantiating a new Auction object herer
    Auction auction;


    //When a user wants to make a full new fresh auction from scratch with these properties
    function createAuction(address _seller, uint256 _startPrice, string _itemDescription) {
        auction.seller = _seller;
        auction.startPrice = _startPrice;
        auction.itemDescription = _itemDescription;
        auction.auctionStatus = 0;    //assign the auction status to 0, meaning "Open"
        //auction.auctionDuration = 10 minutes;
        auction.auctionEndTime = now + 10 minutes;

    } 

    //When the auction is in process and is getting bids coming in 
    function processAuction(address _seller, uint256 _startPrice, string _itemDescription) { 
        bid();
        returnHighestBid();
    }

    function bid() public payable {

        require( 
            now <= auction.auctionEndTime,
            "You still have time to make a bid"
        );

        require(
            msg.value > highestBid,
            "There is already a higher bid"
        );

        if (HighestBid != 0) {
            
            HighestBid = msg.value;
            topBidder = msg.sender;
            emit highestBidIncreased (msg.value, msg.sender);
        }
    }
    
    function returnHighestBid(uint256 highestBid)returns uint256 highestBid{
        returns highestBid, "The Highest Bid for this item is " + highestBid;
    }

    //Withdraw a bid that was overbid
    function withdraw() public returns (bool){
        uint amount = pendingReturns[msg.sender];
        if(amount>0){
            pendingReturns[msg.sender]=0;

            if(!msg.sender.send(amount)){
                pendingReturns[msg.sender] = amount;
                return false;
            }
        }
        return true;

    }

    function auctionEnd() public {

        require(now >= auctionEndTime, "This Auction has not ended yet");
        require(!ended, "auctionEnd has already been called");

        ended = true;
        emit AuctionEnded(topBidder, highestBid);

        seller.transfer(highestBid);
    }

}

