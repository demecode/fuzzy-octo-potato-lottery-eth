from os import access
import pytest
import time
from scripts.deploy import deploy_lotto
from scripts.helpers import LOCAL_BLOCKCHAIN_ENVIRONMENTS, fund_with_link, get_account
from brownie import network


def test_ensure_program_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    lotto = deploy_lotto()
    account = get_account()
    lotto.startLottery({"from": account})
    lotto.enter({"from": account, "value": lotto.getEntranceFee()})
    lotto.enter({"from": account, "value": lotto.getEntranceFee()})
    
    fund_with_link(lotto)
    lotto.endLottery({"from":account})
    time.sleep(360) # wait for the chainklink node to respond
    
    assert lotto.recentWinner() == account
    assert lotto.balance() == 0
    
        