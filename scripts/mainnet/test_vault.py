import os

from brownie import Contract, HRVault, HRVaultProxy, HRVaultProxyAdmin, accounts

from ..common import get_vault_admin_account
from ..vault import VAULT_IMPL_ADDR, VAULT_PROXY_ADDR, VAULT_PROXY_ADMIN_ADDR
from ..vault.common_test import (
    test_allow_list,
    test_ownership_transfers,
    test_vault_cannot_receive,
    test_vault_initialized,
    test_vault_proxy_admin,
    test_vault_proxy_initialized,
    test_vault_withdrawal,
)

# -------------------------------------------------------------------

# Tests for subnet created from mainnet_genesis.json

# -------------------------------------------------------------------


def test():
    vault_admin_account = get_vault_admin_account()
    non_admin_account = accounts.load(os.getenv("TESTNET_ACCOUNT_NAME"))
    dev_account = accounts.load(os.getenv("DEV_ACCOUNT_NAME"))
    vault = HRVault.at(VAULT_IMPL_ADDR)
    vault_proxy = HRVaultProxy.at(VAULT_PROXY_ADDR)
    vault_proxy_admin = HRVaultProxyAdmin.at(VAULT_PROXY_ADMIN_ADDR)
    vault_proxy_as_vault = Contract.from_abi("HRVault", VAULT_PROXY_ADDR, HRVault.abi)
    test_vault_proxy_admin(vault_admin_account, vault_proxy, vault_proxy_admin)
    test_vault_initialized(vault_admin_account, vault)
    test_vault_proxy_initialized(vault_admin_account, vault_proxy_as_vault)
    test_vault_cannot_receive(vault_admin_account, vault)
    test_vault_cannot_receive(vault_admin_account, vault_proxy_as_vault)
    test_ownership_transfers(
        non_admin_account, vault_proxy_admin, vault, vault_proxy_as_vault
    )
    test_vault_withdrawal(vault_admin_account, non_admin_account, vault_proxy_as_vault)
    test_allow_list(vault_admin_account, dev_account, "native_minter")
    test_allow_list(vault_admin_account, dev_account, "deployer_list")
    test_allow_list(vault_admin_account, dev_account, "fee_config_manager")
    print("------------------------------------------------------------")
    print("SUBNET SETUP IS VALID")
