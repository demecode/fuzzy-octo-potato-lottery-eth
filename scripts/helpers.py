from brownie import network, config, accounts, MockV3Aggregator
from brownie.network.contract import Contract
from web3 import Web3

from scripts.deploy import deploy

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local", "ganache-local-3"]


DECIMALS = 8
INITIAL_VALUE = 200000000000


def get_account(index=None, id=None):
    # accounts[0] is ganache
    # accounts.add("env") - local env variables
    # accounts.load("id")
    
    if index:
        return accounts[index]
    
    if id:
        return accounts.load(id)
    
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active in FORKED_LOCAL_ENVIRONMENTS:
        return accounts[0]
    
        
    return accounts.add(config["wallets"]["from_key"])

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator
}


def get_contract(contract_name):
    """
    This fuction will get the contract addressfrom the brownie config
    if defined. else it will deploy a mock version of that contract,
    and return that mock contract
    
    Args:
        contract name (string)
        
    return:
        brownie.networkcontract.ProjectContract: most recently deployed version of the contract        
    """
    
    contract_type = contract_to_mock[contract_name]
    # we need to check if we're on local blockchain or not
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # ABI
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)  
    return contract
 
def deploy_mocks(decimal=DECIMALS, initial_value=INITIAL_VALUE):
    account  = get_account()
    MockV3Aggregator.deploy(decimal, initial_value, {"from": account})
    print("DEPLOYED BUMBA")
    
    
    