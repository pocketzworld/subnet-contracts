from brownie import web3

from ..common import get_account, native_minter


def mint(address: str, amount: int):
    wei_amount = web3.toWei(amount, "ether")
    print(f"Minting {wei_amount} wei to {address}")
    account = get_account()
    native_minter_contract = native_minter()
    native_minter_contract.mintNativeCoin(address, wei_amount, {"from": account}).wait(
        1
    )
