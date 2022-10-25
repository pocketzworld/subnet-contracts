import pytest
from brownie import accounts
from brownie.network.account import LocalAccount


@pytest.fixture(scope="session")
def oz(pm):
    oz_project = pm("OpenZeppelin/openzeppelin-contracts@4.5.0/")
    return oz_project


@pytest.fixture(scope="session")
def admin() -> LocalAccount:
    a = accounts.add()
    print(f"Admin address is: {a.address}")
    print(f"Admin balance is: {a.balance()}")
    return a


@pytest.fixture
def alice() -> LocalAccount:
    return accounts[0]


@pytest.fixture
def vault_owner() -> LocalAccount:
    return accounts[-3]


@pytest.fixture
def hr_vault_owner() -> LocalAccount:
    return accounts[-2]
