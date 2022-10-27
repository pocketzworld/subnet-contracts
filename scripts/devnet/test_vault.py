import os

from brownie import Contract, Vault, VaultProxy, VaultProxyAdmin, VaultV2, accounts

from ..common import get_account, get_vault_admin_account, upgrade
from ..vault import VAULT_IMPL_ADDR, VAULT_PROXY_ADDR, VAULT_PROXY_ADMIN_ADDR
from ..vault.common_test import (
    test_allow_list,
    test_ownership_transfers,
    test_vault_can_receive,
    test_vault_initialized,
    test_vault_proxy_admin,
    test_vault_proxy_initialized,
    test_vault_withdrawal,
)

# -------------------------------------------------------------------

# Tests for subnet created from hr_local_genesis.json

# -------------------------------------------------------------------


def test_pre_init():
    vault_proxy = VaultProxy.at(VAULT_PROXY_ADDR)
    vault_proxy_admin = VaultProxyAdmin.at(VAULT_PROXY_ADMIN_ADDR)
    dev_account = accounts.load(os.getenv("DEV_ACCOUNT_NAME"))

    print("---------- TEST NOT AN OWNER CANNOT INITIALIZE VAULT PROXY ------------")
    try:
        vault_proxy.init({"from": dev_account}).wait(1)
    except Exception as e:
        if "execution reverted: Only owner can initialize proxy admin" in str(e):
            print("SUCCESS - Vault proxy not initialized")
        else:
            print("FAILURE - Vault proxy intialization failed with unexpected error")
            raise e
    else:
        raise Exception("FAILURE - Vault proxy initialization succeeded")
    print("-----------------------------------------------------------------------")

    print(
        "---------- TEST NOT AN OWNER CANNOT INITIALIZE VAULT PROXY ADMIN ------------"
    )
    try:
        vault_proxy_admin.init({"from": dev_account}).wait(1)
    except Exception as e:
        if "execution reverted: Only owner can initialize proxy admin" in str(e):
            print("SUCCESS - Vault Proxy Admin not initialized")
        else:
            print(
                "FAILURE - Vault Proxy Admin intialization failed with unexpected error"
            )
            raise e
    else:
        raise Exception("FAILURE - Vault Proxy Admin initialization succeeded")
    print("-----------------------------------------------------------------------")


def test():
    vault_admin_account = get_vault_admin_account()
    non_admin_account = accounts.load(os.getenv("MAINNET_ACCOUNT_NAME"))
    dev_account = accounts.load(os.getenv("DEV_ACCOUNT_NAME"))
    vault = Vault.at(VAULT_IMPL_ADDR)
    vault_proxy = VaultProxy.at(VAULT_PROXY_ADDR)
    vault_proxy_admin = VaultProxyAdmin.at(VAULT_PROXY_ADMIN_ADDR)
    vault_proxy_as_vault = Contract.from_abi("Vault", VAULT_PROXY_ADDR, Vault.abi)
    test_vault_proxy_admin(vault_admin_account, vault_proxy, vault_proxy_admin)
    test_vault_initialized(vault_admin_account, vault)
    test_vault_proxy_initialized(vault_admin_account, vault_proxy_as_vault)
    test_vault_can_receive(vault_admin_account, vault)
    test_vault_can_receive(vault_admin_account, vault_proxy_as_vault)
    test_ownership_transfers(
        non_admin_account, vault_proxy_admin, vault, vault_proxy_as_vault
    )
    test_vault_withdrawal(vault_admin_account, non_admin_account, vault_proxy_as_vault)
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
