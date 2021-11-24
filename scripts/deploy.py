# 1. In order to to deploty a contract you always need an account

from os import access
from scripts.helpers import get_account, get_contract
from brownie import Lottery, network, config



def deploy():
    account = get_account()
    lottery = Lottery.deploy(get_contract("eth_usd_price_feed").address,
                             get_contract("vrf_coordinator").address,
                             get_contract("link_token").address,
                             config["networks"][network.show_active()]["fee"],
                             config["networks"][network.show_active()]["keyhash"],
                             {"from": account},
                            # to pubish this we need to get a verify key, if thats not available, just return False
                             publish_source = config["networks"][network.show_active()].get("verify", False)
    )
    
    print('THE LOTTO IS DEPLOYED')   
    

def start_lotto():
    account = get_account()
    lotto = Lottery[-1] # call the most recent lotto deployment
    transactionn = lotto.startLottery({'from': account})
    transactionn.wait(1) # random error (web3 not connected -brownie gets confused I suppose, works when wait for th last tx to complete)
    print("LOTTO STARTED")
    
def enter_lotto():
    account = get_account()
    lotto = Lottery[-1]
    
    # we need an entrance fee in order to enter (added extra weth)
    value = lotto.getEntranceFee() + 10000000000
    transactionn = lotto.enter({'from': account, "value": value})
    transactionn.wait(1)
    print(f'ENTERED LOTTO with {value} Ethereum')
    

def end_lotto():
    account = get_account()
    lotto = Lottery[-1]
    transactionn = lotto.endLottery()
    
    # endLottery need a link token. We use the requestRandomness function from chainlink
    # therefore we need to fund the contract with the Link token
    # will add the funding with Link token as a helper
    
    
    
    
    
def main():
    deploy()
    start_lotto()
    enter_lotto()
    end_lotto()