import pytest
from brownie import Contract, Vault, VaultV2, exceptions, web3
from brownie.network.account import Account, LocalAccount
from brownie.network.contract import ProjectContract

from scripts.common import encode_function_data, upgrade

from . import VAULT_OWNER


def test_init_success(vault_proxy: ProjectContract):
    vault = Contract.from_abi("Vault", vault_proxy.address, Vault.abi)
    assert vault.owner() == VAULT_OWNER


def test_init_proxy_only_once(admin: Account, vault_proxy: ProjectContract):
    vault = Contract.from_abi("HighriseLand", vault_proxy.address, Vault.abi)
    with pytest.raises(exceptions.VirtualMachineError) as excinfo:
        vault.initialize({"from": admin})
    assert "revert: Initializable: contract is already initialized" in str(
        excinfo.value
    )


def test_init_implementation_only_once(
    admin: Account, vault_proxy: ProjectContract, vault_proxy_admin: Account
):
    implementation_address = vault_proxy_admin.getProxyImplementation(vault_proxy)
    vault = Contract.from_abi("Vault", implementation_address, Vault.abi)
    with pytest.raises(exceptions.VirtualMachineError) as excinfo:
        vault.initialize({"from": admin})
    assert "revert: Initializable: contract is already initialized" in str(
        excinfo.value
    )


def test_upgrade(
    admin: LocalAccount,
    alice: LocalAccount,
    vault_proxy: ProjectContract,
    vault_proxy_admin: ProjectContract,
):
    vault = Contract.from_abi("Vault", vault_proxy.address, Vault.abi)
    vault_v2 = VaultV2.deploy({"from": admin})

    upgrade_transaction = upgrade(
        admin,
        vault_proxy,
        vault_v2.address,
        proxy_admin_contract=vault_proxy_admin,
        initializer=vault_v2.initializeV2,
    )
    upgrade_transaction.wait(1)
    vault_proxy_v2 = Contract.from_abi("VaultV2", vault_proxy.address, VaultV2.abi)

    # Verify implementation address changed
    implementation_address = vault_proxy_admin.getProxyImplementation(vault_proxy)
    assert implementation_address == vault_v2.address

    # Verify owner has been initalzied
    assert vault_proxy_v2.owner() == vault_proxy_admin.address

    # Verify new functionality
    wei_amount = web3.toWei(1, "ether")
    alice.transfer(vault_proxy_v2.address, wei_amount)
    assert vault_proxy_v2.balance() == wei_amount

    balance_before = admin.balance()
    vault_proxy_v2.withdrawAmount(wei_amount, {"from": admin, "gas_limit": 2000000})
    assert vault_proxy_v2.balance() == 0
    assert admin.balance() == balance_before + wei_amount
