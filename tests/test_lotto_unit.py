
from _pytest.config import exceptions
from brownie import Lottery, accounts, config, network, exceptions
from toolz.itertoolz import get
from web3 import Web3
from scripts.deploy import deploy_lotto
from web3 import Web3
import pytest
from scripts.helpers import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link, get_contract


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lotto = deploy_lotto() # Arrange
    # Act
    entrance_fee_expected = Web3.toWei(0.025, "ether")
    entrance_fee = lotto.getEntranceFee()
    
    # Assert
    assert entrance_fee_expected == entrance_fee

def test_user_cant_enter_unless_lotto_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

        # Arrange
        lotto = deploy_lotto()
        
        # Act & Assert 
        with pytest.raises(exceptions.VirtualMachineError):
            lotto.enter({"from": get_account(), "value": lotto.getEntranceFee()})
        

def test_user_can_enter_lotto():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
        
    #  Arrange 
    lotto = deploy_lotto()
    account = get_account()
    lotto.startLottery({"from": account})
    
     # Act
    lotto.enter({"from": account, "value": lotto.getEntranceFee()})
        
    # Assert
    assert lotto.players(0) == account
    
            
def test_lotto_can_end():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
        
    # Arrange
    lotto = deploy_lotto()
    account = get_account()
    lotto.startLottery({"from": account})
    lotto.enter({"from": account, "value": lotto.getEntranceFee()})
    
    
    # Act
    fund_with_link(lotto)
    lotto.endLottery({"from": account})
    
    # Assert
    assert lotto.lottery_state() == 2 
    
    
def test_winner_is_selected_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    # Arrange
    lotto = deploy_lotto()
    account = get_account()
    lotto.startLottery({"from": account})
    # player 1, 2 & 3
    lotto.enter({"from": account, "value": lotto.getEntranceFee()})
    lotto.enter({"from": get_account(index=1), "value": lotto.getEntranceFee()})
    lotto.enter({"from": get_account(index=2), "value": lotto.getEntranceFee()})
    
    # Act
    fund_with_link(lotto)
    transaction = lotto.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"] # get the RequestRadomness event from the list of events
    
    # now we have the request Id, we will simulate a chainlink node and utilise the callBackRandomness to dummy a rgenerating a random number 
    get_contract("vrf_coordinator").callBackWithRandomness(request_id, 666, lotto.address, {"from":account})
    
    
    # Assert
    starting_balance_account = account.balance()
    balance_of_lotto = lotto.balance()
    
    assert lotto.recentWinner() == account # index of recent winner will be always be 0
    assert lotto.balance() == 0 # balance of lotto is 0
    print(starting_balance_account)
    print(balance_of_lotto)
    assert account.balance() == starting_balance_account + balance_of_lotto