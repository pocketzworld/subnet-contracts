from scripts.common import fee_manager, get_account


fee_config = {
    "gasLimit": 2,
    "targetBlockRate": 2,
    "minBaseFee": 2,
    "targetGas": 2,
    "baseFeeChangeDenominator": 2,
    "minBlockGasCost": 2,
    "maxBlockGasCost": 2,
    "blockGasCostStep": 2,
}


def set_fee_config():
    account = get_account()
    fm_interface = fee_manager()
    print("Updating fee config to:")
    print(fee_config)
    fm_interface.setFeeConfig(
        fee_config["gasLimit"],
        fee_config["targetBlockRate"],
        fee_config["minBaseFee"],
        fee_config["targetGas"],
        fee_config["baseFeeChangeDenominator"],
        fee_config["minBlockGasCost"],
        fee_config["maxBlockGasCost"],
        fee_config["blockGasCostStep"],
        {"from": account},
    ).wait(1)


def get_fee_config():
    fm_interface = fee_manager()
    fee_data = fm_interface.getFeeConfig()
    print(fee_data)


def get_fee_config_last_changed_at():
    fm_inteface = fee_manager()
    block_number = fm_inteface.getFeeConfigLastChangedAt()
    print(block_number)
