# 1. In order to to deploty a contract you always need an account

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
    
def main():
    deploy()