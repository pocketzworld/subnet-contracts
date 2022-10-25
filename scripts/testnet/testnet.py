from ..common import fund_account, get_account
from ..precompiles.allow_list import set_enabled

GATEWAY_DEPLOYER = "0xB8Cd93C83A974649D76B1c19f311f639e62272BC"
CONST_ADRESS_DEPLOYER_DEPLOYER = "0xe86375704cdb8491a5ed82d90dcece02ee0ac25f"
CONST_ADDRESS_DEPLOYER = "0x98b2920d53612483f91f12ed7754e51b4a77919e"


def allow_axelar():
    account = get_account()
    fund_account(GATEWAY_DEPLOYER, 1, account)
    fund_account(CONST_ADRESS_DEPLOYER_DEPLOYER, 1, account)
    set_enabled("deployer_list", GATEWAY_DEPLOYER, account)
    set_enabled("deployer_list", CONST_ADRESS_DEPLOYER_DEPLOYER, account)
