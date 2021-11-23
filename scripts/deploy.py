# 1. In order to to deploty a contract you always need an account

from scripts.helpers import get_account, get_contract
from brownie import Lottery



def deploy():
    account = get_account()
    lottery = Lottery.deploy(get_contract("eth_usd_price_feed").address)

def main():
    deploy()