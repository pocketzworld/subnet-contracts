import os
from typing import Any, NewType, Optional

import eth_utils
from brownie import accounts, config, interface, network, project, web3
from brownie.network.contract import ContractTx, InterfaceContainer
from eth_account import Account

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
SUBNET_ENVIRONMENTS = [
    "highrise-local",
    "highrise-devnet",
]
DEV_SUBNETS = ["local-dev1", "local-dev2", "dev-c-chain", "dev-highrise"]
HIGHRISE_TESTNET = "highrise-testnet"

Project = NewType("Project", Any)


def get_account() -> Account:
    active_network = network.show_active()
    if active_network in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    elif active_network == HIGHRISE_TESTNET:
        return accounts.load(os.getenv("TESTNET_ACCOUNT_NAME"))
    else:
        return accounts.load(os.getenv("DEV_ACCOUNT_NAME"))


def get_vault_admin_account() -> Account:
    return accounts.load(os.getenv("TESTNET_ACCOUNT_NAME"))


def native_minter() -> InterfaceContainer:
    if (
        curr_network := network.show_active()
        not in SUBNET_ENVIRONMENTS + DEV_SUBNETS + [HIGHRISE_TESTNET]
    ):
        raise Exception(f"Native minter not accessible on network {curr_network}")
    nm_address = os.getenv("NATIVE_MINTER_ADDRESS")
    if not nm_address:
        raise Exception("Native minter address not set")
    return interface.INativeMinter(nm_address)


def fee_manager() -> InterfaceContainer:
    if (
        curr_network := network.show_active()
        not in SUBNET_ENVIRONMENTS + DEV_SUBNETS + [HIGHRISE_TESTNET]
    ):
        raise Exception(f"Fee manager not accessible on network {curr_network}")
    fm_address = os.getenv("FEE_MANAGER_ADDRESS")
    if not fm_address:
        raise Exception("Fee manager address not set")
    return interface.IFeeManager(fm_address)


def deployer_list() -> InterfaceContainer:
    if (
        curr_network := network.show_active()
        not in SUBNET_ENVIRONMENTS + DEV_SUBNETS + [HIGHRISE_TESTNET]
    ):
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


def fund_account(account: str, amount: int, funded_account: Optional[Account] = None):
    print(f"Funding {account} with {amount}")
    if not funded_account:
        funded_account = get_account()
    funded_account.transfer(account, web3.toWei(amount, "ether")).wait(1)
