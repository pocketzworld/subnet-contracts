import os
from typing import Any, NewType, Optional

import eth_utils
from brownie import accounts, config, interface, network, project
from brownie.network.contract import ContractTx, InterfaceContainer
from eth_account import Account

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
SUBNET_ENVIRONMENTS = ["avalanche-local-subnet", "dev-subnet"]
AVAX_TEST_C_CHAIN = ["avax-test"]

Project = NewType("Project", Any)


def get_account() -> Account:
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    else:
        return accounts.load(os.getenv("DEV_ACCOUNT_NAME"))


def native_minter() -> InterfaceContainer:
    if curr_network := network.show_active() not in SUBNET_ENVIRONMENTS:
        raise Exception(f"Native minter not accessible on network {curr_network}")
    nm_address = os.getenv("NATIVE_MINTER_ADDRESS")
    if not nm_address:
        raise Exception("Native minter address not set")
    return interface.INativeMinter(nm_address)


def fee_manager() -> InterfaceContainer:
    if curr_network := network.show_active() not in SUBNET_ENVIRONMENTS:
        raise Exception(f"Fee manager not accessible on network {curr_network}")
    fm_address = os.getenv("FEE_MANAGER_ADDRESS")
    if not fm_address:
        raise Exception("Fee manager address not set")
    return interface.IFeeManager(fm_address)


def deployer_list() -> InterfaceContainer:
    if curr_network := network.show_active() not in SUBNET_ENVIRONMENTS:
        raise Exception(f"Deployer list not accessible on network {curr_network}")
    deployer_list_address = os.getenv("DEPLOYER_LIST_ADDRESS")
    if not deployer_list_address:
        raise Exception("Fee manager address not set")
    return interface.IAllowList(deployer_list_address)


def encode_function_data(initializer: Optional[ContractTx] = None, *args) -> bytes:
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer - The initializer function we want to call
        args - Arguments to pass to the initalizer function
    Returns:
        Encoded bytes
    """
    if not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)


def upgrade(
    account: Account,
    proxy,
    new_implementation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args,
):
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                new_implementation_address,
                encoded_function_call,
                {"from": account, "gas_limit": 2000000},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address,
                new_implementation_address,
                {"from": account, "gas_limit": 2000000},
            )
    else:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeToAndCall(
                new_implementation_address,
                encoded_function_call,
                {"from": account, "gas_limit": 2000000},
            )
        else:
            transaction = proxy.upgradeTo(
                new_implementation_address, {"from": account, "gas_limit": 2000000}
            )
    return transaction


def load_openzeppelin() -> Project:
    oz = project.load(config["dependencies"][0])
    return oz
