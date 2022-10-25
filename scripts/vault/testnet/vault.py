from typing import Optional

from brownie import Contract, Vault, VaultProxy, VaultProxyAdmin
from eth_account import Account

from ...common import encode_function_data, get_account, get_vault_admin_account

# Subnet contract addresses defined in genesis
VAULT_PROXY_ADMIN_ADDR = "0x0300000000000000000000000000000000000000"
VAULT_IMPL_ADDR = "0x0300000000000000000000000000000000000001"
VAULT_PROXY_ADDR = "0x0100000000000000000000000000000000000000"

# ------------------ DEPLOYMENT HELPERS FOR C-CHAIN TESTING -----------------


def deploy_vault_proxy(
    vault_proxy_admin_address: str,
    vault_impl_address: str,
    account: Optional[Account] = None,
):
    if not account:
        account = get_account()
    vault = Contract.from_abi("Vault", vault_impl_address, Vault.abi)
    vault_encoded_initializer_function = encode_function_data(
        vault.initialize,
    )
    vault_proxy = VaultProxy.deploy(
        vault_impl_address,
        vault_proxy_admin_address,
        vault_encoded_initializer_function,
        {"from": account},
    )
    vault_proxy_address = vault_proxy.address
    print(f"Vault proxy deployed at: {vault_proxy_address}")


def deploy_vault_proxy_admin(account: Optional[Account] = None) -> str:
    if not account:
        account = get_account()
    # Deploy proxy admin
    proxy_admin = VaultProxyAdmin.deploy({"from": account})
    proxy_admin_address = proxy_admin.address
    print(f"Vault Proxy Admin deployed at: {proxy_admin_address}")
    return proxy_admin_address


def deploy_vault_implementation(account: Optional[Account] = None) -> str:
    if not account:
        account = get_account()
    vault_implementation = Vault.deploy({"from": account})
    impl_address = vault_implementation.address
    print(f"Vault implementation deployed at: {impl_address}")
    return impl_address


def verify_vault_proxy_admin(proxy_admin_address: str):
    contract = VaultProxyAdmin.at(proxy_admin_address)
    VaultProxyAdmin.publish_source(contract)


def verify_vault_proxy(proxy_address: str):
    contract = VaultProxy.at(proxy_address)
    VaultProxy.publish_source(contract)


def verify_vault(vault_address: str):
    contract = Vault.at(vault_address)
    Vault.publish_source(contract)


def deploy():
    account = get_account()
    impl_address = deploy_vault_implementation(account)
    proxy_admin_address = deploy_vault_proxy_admin(account)
    deploy_vault_proxy(proxy_admin_address, impl_address, account)


def verify(proxy_admin_address: str, vault_address: str, vault_proxy_address: str):
    verify_vault(vault_address)
    verify_vault_proxy(vault_proxy_address)
    verify_vault_proxy_admin(proxy_admin_address)


# ---------------------------------------------------------------------------


# -------------- INIT FUNCTIONS FOR SUBNET ----------------------------------


def init_vault_proxy_admin(account: Optional[Account] = None):
    print("Initializing vault proxy admin")
    if not account:
        account = get_vault_admin_account()
    vault_proxy_admin = VaultProxyAdmin.at(VAULT_PROXY_ADMIN_ADDR)
    vault_proxy_admin.init({"from": account}).wait(1)


def init_vault_implementation(account: Optional[Account] = None):
    print("Initializing vault implementation")
    if not account:
        account = get_vault_admin_account()
    vault = Vault.at(VAULT_IMPL_ADDR)
    vault.initialize({"from": account, "gas_limit": 2000000}).wait(1)


def init_vault_proxy(account: Optional[Account] = None):
    print("Initializing vault proxy")
    if not account:
        account = get_vault_admin_account()
    proxy = VaultProxy.at(VAULT_PROXY_ADDR)
    proxy.init({"from": account, "gas_limit": 2000000}).wait(1)

    vault_proxy = Contract.from_abi("Vault", VAULT_PROXY_ADDR, Vault.abi)
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
    vault_proxy = VaultProxy.at(VAULT_PROXY_ADDR)
    vault_proxy_admin = VaultProxyAdmin.at(VAULT_PROXY_ADMIN_ADDR)
    vault_impl = Vault.at(VAULT_IMPL_ADDR)
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
    vault = Contract.from_abi("Vault", VAULT_PROXY_ADDR, Vault.abi)
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
    vault = Contract.from_abi("Vault", VAULT_PROXY_ADDR, Vault.abi)
    print(f"Current vault balance: {vault.balance()}")


# ---------------------------------------------------------------------------
