from typing import Literal

from ..common import deployer_list, fee_manager, get_account, native_minter

Precompile = Literal["native_minter", "deployer_list", "fee_config_manager"]


def fetch_interface(precompile: Precompile):
    if precompile == "native_minter":
        return native_minter()
    elif precompile == "fee_config_manager":
        return fee_manager()
    elif precompile == "deployer_list":
        return deployer_list()


def set_admin(precompile: Precompile, new_admin_address: str):
    account = get_account()
    interface = fetch_interface(precompile)
    interface.setAdmin(new_admin_address, {"from": account}).wait(1)


def set_enabled(precompile: Precompile, address: str):
    account = get_account()
    interface = fetch_interface(precompile)
    interface.setEnabled(address, {"from": account}).wait(1)


def unset_address(precompile: Precompile, address: str):
    account = get_account()
    interface = fetch_interface(precompile)
    interface.setNone(address, {"from": account}).wait(1)


def read_allow_list(precompile: Precompile, address: str):
    interface = fetch_interface(precompile)
    status = interface.readAllowList(address)
    print(status)
