import os

from brownie import accounts, interface, network
from brownie.network.contract import InterfaceContainer
from eth_account import Account

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
LOCAL_SUBNET_ENVIRONMENTS = ["avalanche-local-subnet"]


def get_account() -> Account:
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    else:
        return accounts.load(os.getenv("DEV_ACCOUNT_NAME"))


def native_minter() -> InterfaceContainer:
    if curr_network := network.show_active() not in LOCAL_SUBNET_ENVIRONMENTS:
        raise Exception(f"Native minter not accessible on network {curr_network}")
    nm_address = os.getenv("NATIVE_MINTER_ADDRESS")
    if not nm_address:
        raise Exception("Native minter address not set")
    return interface.INativeMinter(nm_address)


def fee_manager() -> InterfaceContainer:
    if curr_network := network.show_active() not in LOCAL_SUBNET_ENVIRONMENTS:
        raise Exception(f"Fee manager not accessible on network {curr_network}")
    fm_address = os.getenv("FEE_MANAGER_ADDRESS")
    if not fm_address:
        raise Exception("Fee manager address not set")
    return interface.IFeeManager(fm_address)
