import pytest
from brownie import Vault, VaultProxy, VaultProxyAdmin
from brownie.network.account import Account
from brownie.network.contract import ProjectContract

from scripts.common import encode_function_data


@pytest.fixture(scope="session")
def vault_proxy_admin(admin: Account) -> ProjectContract:
    proxy_admin = VaultProxyAdmin.deploy({"from": admin})
    return proxy_admin


@pytest.fixture
def vault_proxy(
    admin: Account,
    vault_proxy_admin: ProjectContract,
) -> ProjectContract:
    # Vault
    vault = Vault.deploy(
        {"from": admin},
    )
    # Vault Proxy
    vault_encoded_initializer_function = encode_function_data(
        vault.initialize,
    )
    vault_proxy = VaultProxy.deploy(
        vault.address,
        vault_proxy_admin.address,
        vault_encoded_initializer_function,
        {"from": admin, "gas_limit": 2000000},
    )
    return vault_proxy


@pytest.fixture
def vault(admin: Account):
    vault = Vault.deploy({"from": admin})
    return vault
