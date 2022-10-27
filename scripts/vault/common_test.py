import os

from brownie import Contract
from brownie.network.account import Account

from scripts.precompiles.allow_list import Precompile, fetch_interface

from . import VAULT_IMPL_ADDR, VAULT_PROXY_ADMIN_ADDR


def test_vault_proxy_admin(
    account: Account, vault_proxy: Contract, vault_proxy_admin: Contract
):
    print("-------------------- TEST VAULT PROXY ADMIN -------------------")
    if vault_proxy_admin.owner() == account.address:
        print(f"SUCCESS - Vault proxy admin owner is {account.address}")
    else:
        msg = f"FAILURE - Vault proxy admin owner is {vault_proxy_admin.owner()}"
        raise Exception(msg)

    if vault_proxy_admin.getProxyAdmin(vault_proxy.address) == VAULT_PROXY_ADMIN_ADDR:
        print(f"SUCCESS - Vault proxy admin at {VAULT_PROXY_ADMIN_ADDR}")
    else:
        msg = f"FAILURE - Vault proxy admin at {vault_proxy_admin.getProxyAdmin(vault_proxy.address)}"
        raise Exception(msg)

    if vault_proxy_admin.getProxyImplementation(vault_proxy.address) == VAULT_IMPL_ADDR:
        print(f"SUCCESS - Vault proxy implementation at {VAULT_IMPL_ADDR}")
    else:
        msg = f"FAILURE - Vault proxy implementation at {vault_proxy_admin.getProxyImplementation(vault_proxy.address)}"
        raise Exception(msg)
    print("---------------------------------------------------------------")


def test_vault_initialized(account: Account, vault: Contract):
    print("-------------------- TEST VAULT INITIALIZED -------------------")
    try:
        vault.initialize({"from": account}).wait(1)
    except Exception as e:
        if "Initializable: contract is already initialized" in str(e):
            print("SUCCESS - Vault already initialized")
        else:
            print("FAILURE - Vault intialization passed")
            raise e
    else:
        raise Exception("FAILURE - Vault intialization passed")

    if vault.owner() == account.address:
        print(f"SUCCESS - Vault owner is {account.address}")
    else:
        msg = f"FAILURE - Vault owner is {account.address}"
        raise Exception(msg)
    print("---------------------------------------------------------------")


def test_vault_proxy_initialized(account: Account, vault: Contract):
    print("-------------------- TEST VAULT PROXY INITIALIZED -------------------")
    try:
        vault.initialize({"from": account}).wait(1)
    except Exception as e:
        if "Initializable: contract is already initialized" in str(e):
            print("SUCCESS - Vault proxy already initialized")
        else:
            print("FAILURE - Vault proxy intialization passed")
            raise e
    else:
        raise Exception("FAILURE - Vault proxy intialization passed")

    if vault.owner() == account.address:
        print(f"SUCCESS - Vault owner is {account.address}")
    else:
        msg = f"FAILURE - Vault owner is {account.address}"
        raise Exception(msg)

    if vault.balance() > 0:
        print(f"SUCCESS - Vault has balance > 0")
    else:
        raise Exception(f"FAILURE - Vault balnce is {vault.balnce()}")
    print("---------------------------------------------------------------")


def test_vault_cannot_receive(account: Account, vault: Contract):
    print("-------------------- TEST VAULT CANNOT RECEIVE -------------------")
    try:
        account.transfer(vault.address, 1).wait(1)
    except Exception as e:
        if "execution reverted'. This transaction will likely revert" in str(e):
            print(f"SUCCESS - {vault.address} cannot receive native transfers")
        else:
            raise e
    else:
        msg = f"FAILURE - {vault.address} can receive native transfers"
        raise Exception(msg)
    print("---------------------------------------------------------------")


def test_vault_can_receive(account: Account, vault: Contract):
    print("-------------------- TEST VAULT CAN RECEIVE -------------------")
    try:
        account.transfer(vault.address, 1).wait(1)
    except Exception as e:
        print(f"FAILURE - {vault.address} cannot receive native transfers")
        raise e
    print(f"SUCCESS - {vault.address} can receive native transfers")
    print("---------------------------------------------------------------")


def test_ownership_transfers(
    account: Account,
    vault_proxy_admin: Contract,
    vault_impl: Contract,
    vault_proxy: Contract,
):
    print("-------------------- TEST OWNERSHIP TRANSFERS -------------------")
    try:
        vault_impl.transferOwnership(account.address, {"from": account})
    except Exception as e:
        if "execution reverted: Ownable: caller is not the owner" in str(e):
            print("SUCCESS - Vault ownership not transferrable")
        else:
            raise e
    else:
        raise Exception("FAILURE - Vault ownership transferrable")

    try:
        vault_proxy.transferOwnership(account.address, {"from": account})
    except Exception as e:
        if "execution reverted: Ownable: caller is not the owner" in str(e):
            print("SUCCESS - Vault proxy ownership not transferrable")
        else:
            raise e
    else:
        raise Exception("FAILURE - Vault proxy ownership transferrable")

    try:
        vault_proxy_admin.transferOwnership(account.address, {"from": account})
    except Exception as e:
        if "execution reverted: Ownable: caller is not the owner" in str(e):
            print("SUCCESS - Vault proxy admin ownership not transferrable")
        else:
            raise e
    else:
        raise Exception("FAILURE - Vault proxy admin ownership transferrable")
    print("---------------------------------------------------------------")


def test_vault_withdrawal(
    admin_account: Account, account: Account, vault_proxy: Contract
):
    print("-------------------- TEST VAULT WITHDRAWAL -------------------")
    try:
        vault_proxy.withdraw({"from": account})
    except Exception as e:
        if "execution reverted: Ownable: caller is not the owner" in str(e):
            print("SUCCESS - Only admin can withdraw from vault")
        else:
            raise e

    vault_balance_before = vault_proxy.balance()
    balance_before = admin_account.balance()
    (tx := vault_proxy.withdraw({"from": admin_account})).wait(1)
    cost = tx.gas_used * tx.gas_price
    vault_balance_after = vault_proxy.balance()
    balance_after = admin_account.balance()
    if (
        vault_balance_after != cost
        or balance_after != balance_before + vault_balance_before - cost
    ):
        print("FAILURE - vault withdrawal failed")
    else:
        print(f"SUCCESS - vault withdrawal. Current balance {vault_balance_after}")
    print("---------------------------------------------------------------")


def test_allow_list(account: Account, to_enable: Account, precompile: Precompile):
    print(f"-------------------- TEST {precompile} ALLOW LIST -------------------")
    native_minter = fetch_interface(precompile)

    if native_minter.readAllowList(account.address) == 2:
        print(f"SUCCESS - {account.address} is {precompile} admin")
    else:
        raise Exception(f"FAILURE - {account.address} is not {precompile} admin")

    native_minter.setEnabled(to_enable, {"from": account}).wait(1)
    if native_minter.readAllowList(to_enable.address) == 1:
        print(f"SUCCESS - {to_enable.address} is {precompile} enabled")
    else:
        raise Exception(f"FAILURE - {to_enable.address} is not {precompile} enabled")

    try:
        native_minter.setEnabled(to_enable, {"from": to_enable}).wait(1)
    except Exception as e:
        if "non-admin cannot modify allow list" in str(e):
            print("SUCCESS - non admin cannot modify allow list")
        else:
            raise e

    native_minter.setNone(to_enable.address, {"from": account}).wait(1)
    if native_minter.readAllowList(to_enable.address) == 0:
        print(f"SUCCESS - {to_enable.address} is not {precompile} enabled")
    else:
        raise Exception(f"FAILURE - {to_enable.address} is {precompile} enabled")
    print("---------------------------------------------------------------")
