from .common import fund_account, get_account, get_vault_admin_account
from .precompiles.allow_list import set_enabled
from .precompiles.fee_manager import set_fee_config
from .vault.vault import init_subnet, print_subnet_setup

CONST_ADDRESS_DEPLOYER_ACCOUNT = "0x6F2D0eB998F77595621DB2805872A894F0F1DEfB"
GATEWAY_DEPLOYER_ACCOUNT = "0xBa86A5719722B02a5D5e388999C25f3333c7A9fb"
CONST_ADDRESS_DEPLOYER = "0x0000000000000000000000000000000000000000"


def init_dev_subnet():
    account = get_account()
    vault_admin_account = get_vault_admin_account()
    # Fund accounts
    fund_account(vault_admin_account.address, 1, account)
    fund_account(CONST_ADDRESS_DEPLOYER_ACCOUNT, 1, account)
    fund_account(GATEWAY_DEPLOYER_ACCOUNT, 1, account)
    # Update gas limit for bridge
    set_fee_config("DEV", account)
    # Allow deployments for bridge
    set_enabled("deployer_list", CONST_ADDRESS_DEPLOYER_ACCOUNT, account)
    set_enabled("deployer_list", GATEWAY_DEPLOYER_ACCOUNT, account)
    set_enabled("deployer_list", CONST_ADDRESS_DEPLOYER, account)
    # Init vault
    init_subnet()
    print_subnet_setup(1)
