from brownie import Multicall2
from ..common import get_account


def deploy():
    account = get_account()
    multicall = Multicall2.deploy({"from": account})
    print(f"Multicall2 contract deployed at: {multicall.address}")
