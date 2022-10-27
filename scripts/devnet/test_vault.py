import os

from brownie import Contract, Vault, VaultProxy, VaultProxyAdmin, VaultV2, accounts
from brownie.network.account import Account

from ..common import get_account, get_vault_admin_account, upgrade
from ..precompiles.allow_list import Precompile, fetch_interface
from ..vault.testnet.vault import (
    VAULT_IMPL_ADDR,
    VAULT_PROXY_ADDR,
    VAULT_PROXY_ADMIN_ADDR,
)


# -------------------------------------------------------------------

# Tests for subnet created from hr_local_genesis.json

# -------------------------------------------------------------------


def test_vault_initialized(account: Account):
    vault = Contract.from_abi("Vault", VAULT_IMPL_ADDR, Vault.abi)
    try:
        vault.initialize({"from": account}).wait(1)
    except Exception as e:
        if "Initializable: contract is already initialized" in str(e):
            print("SUCCESS - Vault already initialized")
        else:
            print("FAILURE - Vault intialization passed")
            raise e

    if vault.owner() == account.address:
        print(f"SUCCESS - Vault owner is {account.address}")
    else:
        msg = f"FAILURE - Vault owner is {account.address}"
        raise Exception(msg)


def test_vault_proxy_initialized(account: Account):
    vault = Contract.from_abi("Vault", VAULT_PROXY_ADDR, Vault.abi)
    try:
        vault.initialize({"from": account}).wait(1)
    except Exception as e:
        if "Initializable: contract is already initialized" in str(e):
            print("SUCCESS - Vault proxy already initialized")
        else:
            print("FAILURE - Vault proxy intialization passed")
            raise e

    if vault.owner() == account.address:
        print(f"SUCCESS - Vault owner is {account.address}")
    else:
        msg = f"FAILURE - Vault owner is {account.address}"
        raise Exception(msg)

    if vault.balance() > 0:
        print(f"SUCCESS - Vault has balance > 0")
    else:
        raise Exception(f"FAILURE - Vault balnce is {vault.balnce()}")


def test_vault_impl_cannot_receive(account: Account):
    vault = Contract.from_abi("Vault", VAULT_IMPL_ADDR, Vault.abi)
    try:
        account.transfer(vault.address, 1)
    except Exception as e:
        if "execution reverted'. This transaction will likely revert" in str(e):
            print("SUCESS - Vault implementation cannot receive native transfers")
        else:
            print("FAILURE - Vault implementation cannot receive native transfers")
            raise e


def test_vault_proxy_cannot_receive(account: Account):
    vault = Contract.from_abi("Vault", VAULT_PROXY_ADDR, Vault.abi)
    try:
        account.transfer(vault.address, 1)
    except Exception as e:
        if "execution reverted'. This transaction will likely revert" in str(e):
            print("SUCESS - Vault proxy cannot receive native transfers")
        else:
            print("FAILURE - Vault proxy cannot receive native transfers")
            raise e


def test_vault_proxy_admin(account: Account):
    vault_proxy = VaultProxy.at(VAULT_PROXY_ADDR)
    vault_proxy_admin = VaultProxyAdmin.at(VAULT_PROXY_ADMIN_ADDR)
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


def test_ownership_transfers(account: Account):
    vault_proxy_admin = VaultProxyAdmin.at(VAULT_PROXY_ADMIN_ADDR)
    vault_impl = Vault.at(VAULT_IMPL_ADDR)
    vault_proxy = Contract.from_abi("Vault", VAULT_PROXY_ADDR, Vault.abi)

    try:
        vault_impl.transferOwnership(account.address, {"from": account})
    except Exception as e:
        if "execution reverted: Ownable: caller is not the owner" in str(e):
            print("SUCCESS - Vault ownership not transferrable")
        else:
            raise e
    try:
        vault_proxy.transferOwnership(account.address, {"from": account})
    except Exception as e:
        if "execution reverted: Ownable: caller is not the owner" in str(e):
            print("SUCCESS - Vault proxy ownership not transferrable")
        else:
            raise e

    try:
        vault_proxy_admin.transferOwnership(account.address, {"from": account})
    except Exception as e:
        if "execution reverted: Ownable: caller is not the owner" in str(e):
            print("SUCCESS - Vault proxy admin ownership not transferrable")
        else:
            raise e


def test_vault_withdrawal(admin_account: Account, account: Account):
    vault_proxy = Contract.from_abi("Vault", VAULT_PROXY_ADDR, Vault.abi)
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


def test_allow_list(account: Account, to_enable: Account, precompile: Precompile):
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
            print("SUCESS - non admin cannot modify allow list")
        else:
            raise e

    native_minter.setNone(to_enable.address, {"from": account}).wait(1)
    if native_minter.readAllowList(to_enable.address) == 0:
        print(f"SUCCESS - {to_enable.address} is not {precompile} enabled")
    else:
        raise Exception(f"FAILURE - {to_enable.address} is {precompile} enabled")


def test():
    vault_admin_account = get_vault_admin_account()
    non_admin_account = accounts.load(os.getenv("MAINNET_ACCOUNT_NAME"))
    dev_account = accounts.load(os.getenv("DEV_ACCOUNT_NAME"))
    test_vault_proxy_admin(vault_admin_account)
    test_vault_initialized(vault_admin_account)
    test_vault_proxy_initialized(vault_admin_account)
    test_vault_impl_cannot_receive(vault_admin_account)
    test_vault_proxy_cannot_receive(vault_admin_account)
    test_ownership_transfers(non_admin_account)
    test_vault_withdrawal(vault_admin_account, non_admin_account)
    test_allow_list(dev_account, vault_admin_account, "native_minter")
    test_allow_list(dev_account, vault_admin_account, "deployer_list")
    test_allow_list(dev_account, vault_admin_account, "fee_config_manager")
    print("------------------------------------------------------------")
    print("SUBNET SETUP IS VALID")


def upgrade_vault_v2():
    account = get_account()
    vault_admin_account = get_vault_admin_account()
    vault_v2 = VaultV2.deploy({"from": account})
    vault_proxy = VaultProxy.at(VAULT_PROXY_ADDR)
    vault_proxy_admin = VaultProxyAdmin.at(VAULT_PROXY_ADMIN_ADDR)

    upgrade_transaction = upgrade(
        vault_admin_account,
        vault_proxy,
        vault_v2.address,
        proxy_admin_contract=vault_proxy_admin,
        initializer=vault_v2.initializeV2,
    )
    upgrade_transaction.wait(1)
    vault_proxy_v2 = Contract.from_abi("VaultV2", vault_proxy.address, VaultV2.abi)
    # Verify implementation address changed
    implementation_address = vault_proxy_admin.getProxyImplementation(vault_proxy)
    if implementation_address == vault_v2.address:
        print("SUCCESS - Vault proxy implementation")
    else:
        print("FAILURE - Vault proxy implementation")

    if vault_proxy_v2.owner() == vault_proxy_admin.address:
        print("SUCCESS - Admin set correctly")
    else:
        print("FAILURE - Admin not set correctly")

    balance_before = account.balance()
    vault_balance_before = vault_proxy_v2.balance()
    (tx := vault_proxy_v2.withdrawAmount(vault_balance_before, {"from": account})).wait(
        1
    )
    cost = tx.gas_used * tx.gas_price

    balance_after = account.balance()
    vault_balance_after = vault_proxy_v2.balance()
    user_balance_check = balance_after == balance_before - cost + vault_balance_before
    vault_balance_check = vault_balance_after == cost
    if user_balance_check and vault_balance_check:
        print(f"SUCCESS - Balanche check: {user_balance_check} {vault_balance_check}")
    else:
        print("FAILURE - balance check")
