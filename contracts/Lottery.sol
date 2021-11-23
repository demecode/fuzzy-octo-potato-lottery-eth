// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";


// add thr VRF constructor to be able to use it to generate randomness
contract Lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    address payable public recentWinner;
    uint256 public randomness;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;

    // state of the lottery, open,  closed & processing winner
    // 0, 1, 2 - respectively
     enum LOTTERY_STATE {
         OPEN,
         CLOSED,
         CALCULATING_WINNER
     }

    LOTTERY_STATE public lottery_state;
    uint256 public fee; //this is needed for the link gas fee 
    bytes32 public keyhash; // required by VRF   code base to generate random number

    // Constructor inherits VRFConsumerBase
    constructor(
        address _priceFeedAddress, 
        address _vrfCoordinator, 
        address _link, 
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntryFee = 50 * (10 ** 18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash; // the unique way of identify the chainlink vrf node

    }

    function enter() public payable {
        // mininum $50
        require(lottery_state == LOTTERY_STATE.OPEN);
        // entrance fee needs to be equal to or greater than entranceFee function
        require(msg.value >= getEntranceFee(), "NOT ENOUGH ETHEREUM ");
        players.push(msg.sender);
    }
    
    function getEntranceFee() public view returns (uint256) {

        // what is the entrance fee?

        (,int256 price, , , ) = ethUsdPriceFeed.latestRoundData();

        uint256 adjustPrice = uint256(price) * 10 ** 10;// 18 decimals 


        // $50, $2000 / ETH
        // Solidity doesnt work with decimals so we can do 50 / 2000
        // So we can do instead: 50 * 100000 / 2000
        // should use safe math

        uint256 costToEnter = (usdEntryFee * 10 ** 18) / adjustPrice;
        return costToEnter;
        
    }
    function startLottery() public onlyOwner {
        // lottery must be closed before one can start
        require(lottery_state == LOTTERY_STATE.CLOSED, "UNABLE TO START NEW LOTTERY YET!");

        // we can now start the lottery
        lottery_state = LOTTERY_STATE.OPEN;



    }
    function endLottery() public onlyOwner {
        // when this fucntion is called - it will first request a random number
        // and then once the node has created a provable random number, it will then call second transaction. FulfilRandomness function

        // how do we choose a winner?
        // currently the admin chooses but we will update


        // bad practice for randomness below: all are predictable
        // uint256(keccak256(abi.encodePacked(nonce, msg.sender, block.difficulty, block.timestamp)) % players.length;

        // More secure and good practice for randomness:
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyhash, fee); // this should return a bytes32 request id as per the (requestRandomness chainlink) function states/rerturns



    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override {

        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER, "Not ready to calculate winner");
        require(_randomness > 0, "RANDOM NOT FOUND!");
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        
        // send the recent winner total balance ... hmm from the contract address?
        recentWinner.transfer(address(this).balance);

        // reset 
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;

        // 10 players
        // 22 
        // 22 % 7  = 2
        // 10 * 2 = 20
    }

} 