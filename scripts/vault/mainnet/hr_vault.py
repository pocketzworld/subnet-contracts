from typing import Optional

from brownie import Contract, HRVault, HRVaultProxy, HRVaultProxyAdmin
from eth_account import Account

from ...common import get_vault_admin_account
from .. import VAULT_IMPL_ADDR, VAULT_PROXY_ADDR, VAULT_PROXY_ADMIN_ADDR

# -------------- INIT FUNCTIONS FOR SUBNET ----------------------------------


def init_vault_proxy_admin(account: Optional[Account] = None):
    print("Initializing vault proxy admin")
    if not account:
        account = get_vault_admin_account()
    vault_proxy_admin = HRVaultProxyAdmin.at(VAULT_PROXY_ADMIN_ADDR)
    vault_proxy_admin.init({"from": account}).wait(1)


def init_vault_implementation(account: Optional[Account] = None):
    print("Initializing vault implementation")
    if not account:
        account = get_vault_admin_account()
    vault = HRVault.at(VAULT_IMPL_ADDR)
    vault.initialize({"from": account, "gas_limit": 2000000}).wait(1)


def init_vault_proxy(account: Optional[Account] = None):
    print("Initializing vault proxy")
    if not account:
        account = get_vault_admin_account()
    proxy = HRVaultProxy.at(VAULT_PROXY_ADDR)
    proxy.init({"from": account, "gas_limit": 2000000}).wait(1)

    vault_proxy = Contract.from_abi("HRVault", VAULT_PROXY_ADDR, HRVault.abi)
    vault_proxy.initialize({"from": account, "gas_limit": 2000000}).wait(1)


def init_subnet():
    account = get_vault_admin_account()
    init_vault_proxy_admin(account)
    init_vault_implementation(account)
    init_vault_proxy(account)


# ---------------------------------------------------------------------------


# ----------------- VALIDATE SUBNET CONFIG ----------------------------------


def print_subnet_setup(post_init: Optional[int] = None):
    print("Initial subnet setup")
    print("------------------------------------------------------")
    vault_proxy = HRVaultProxy.at(VAULT_PROXY_ADDR)
    vault_proxy_admin = HRVaultProxyAdmin.at(VAULT_PROXY_ADMIN_ADDR)
    vault_impl = HRVault.at(VAULT_IMPL_ADDR)
    print(f"Vault Proxy Admin owner: {vault_proxy_admin.owner()}")
    print(f"Vault owner: {vault_impl.owner()}")
    if post_init is not None:
        print(
            f"Vault proxy implementation: {vault_proxy_admin.getProxyImplementation(vault_proxy.address)}"
        )
        print(
            f"Vault proxy admin: {vault_proxy_admin.getProxyAdmin(vault_proxy.address)}"
        )
        print(f"Vault proxy balance: {vault_proxy.balance()}")
    print("------------------------------------------------------")


# ---------------------------------------------------------------------------


# ----------------- WITHDRAWAL ----------------------------------------------
def withdraw():
    account = get_vault_admin_account()
    vault = Contract.from_abi("HRVault", VAULT_PROXY_ADDR, HRVault.abi)
    print(f"Current vault balance: {vault.balance()}")
    (tx := vault.withdraw({"from": account})).wait(1)
    sender = tx.events[0]["sender"]
    amount = tx.events[0]["amount"]
    print(f"{sender} initiated withdrawal of {amount} Wei")
    print(f"Vault proxy balance: {vault.balance()} Wei")
    cost = tx.gas_used * tx.gas_price
    print(f"Transaction gas fee: {cost} Wei")


# ---------------------------------------------------------------------------

# ---------------- VAULT BALANCE --------------------------------------------


def vault_balance():
    vault = Contract.from_abi("HRVault", VAULT_PROXY_ADDR, HRVault.abi)
    print(f"Current vault balance: {vault.balance()}")
    return vault.balance()


# ---------------------------------------------------------------------------
