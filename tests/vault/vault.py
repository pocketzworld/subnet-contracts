import pytest
from brownie import Contract, Vault, exceptions, web3
from brownie.network.account import Account, LocalAccount
from brownie.network.contract import ProjectContract

from . import VAULT_OWNER


def test_vault_already_initialzied(admin: Account, vault: ProjectContract):
    with pytest.raises(exceptions.VirtualMachineError) as excinfo:
        vault.initialize({"from": admin})
    assert "revert: Initializable: contract is already initialized" in str(
        excinfo.value
    )


def test_vault_ownership(
    admin: Account, vault_owner: LocalAccount, vault_proxy: ProjectContract
):
    vault = Contract.from_abi("Vault", vault_proxy.address, Vault.abi)
    assert vault.owner() == VAULT_OWNER
    assert vault.owner() == vault_owner.address

    with pytest.raises(exceptions.VirtualMachineError) as excinfo:
        vault.transferOwnership(admin, {"from": admin})
    assert "revert: Ownable: caller is not the owner" in str(excinfo.value)

    vault.transferOwnership(admin.address, {"from": vault_owner})
    assert vault.owner() == admin


def test_vault_balance(alice: LocalAccount, vault: ProjectContract):
    wei_amount = web3.toWei(1, "ether")
    alice.transfer(vault.address, wei_amount)
    assert vault.balance() == wei_amount


def test_vault_withdrawal(
    alice: LocalAccount, vault_owner: LocalAccount, vault_proxy: ProjectContract
):
    wei_amount = web3.toWei(1, "ether")
    alice.transfer(vault_proxy.address, wei_amount)

    vault = Contract.from_abi("Vault", vault_proxy.address, Vault.abi)

    with pytest.raises(exceptions.VirtualMachineError) as excinfo:
        vault.withdraw({"from": alice})
    assert "revert: Ownable: caller is not the owner" in str(excinfo.value)

    tx = vault.withdraw({"from": vault_owner})
    assert vault_owner.balance() == wei_amount
    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == vault_owner
    assert tx.events[0]["amount"] == wei_amount
