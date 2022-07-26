from brownie import web3

from .common import get_account, native_minter


def mint(address: str, amount: int):
    eth_amount = web3.toWei(amount, "ether")
    print(f"Minting {eth_amount} tokens to {address}")
    account = get_account()
    native_minter_contract = native_minter()
    native_minter_contract.mintNativeCoin(address, eth_amount, {"from": account}).wait(
        1
    )
