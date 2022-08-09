from attrs import define

from ..common import fee_manager, get_account


@define
class FeeConfig:
    gasLimit: int
    targetBlockRate: int
    minBaseFee: int
    targetGas: int
    baseFeeChangeDenominator: int
    minBlockGasCost: int
    maxBlockGasCost: int
    blockGasCostStep: int


dummy_config = FeeConfig(2000000, 2, 15000000000, 10000000, 36, 0, 1000000, 200000)
c_chain_config = FeeConfig(8000000, 2, 25000000000, 15000000, 36, 0, 1000000, 200000)


def _set_fee_config(fee_config: FeeConfig):
    account = get_account()
    fm_interface = fee_manager()
    print("Updating fee config to:")
    print(fee_config)
    fm_interface.setFeeConfig(
        fee_config.gasLimit,
        fee_config.targetBlockRate,
        fee_config.minBaseFee,
        fee_config.targetGas,
        fee_config.baseFeeChangeDenominator,
        fee_config.minBlockGasCost,
        fee_config.maxBlockGasCost,
        fee_config.blockGasCostStep,
        {"from": account},
    ).wait(1)


def set_fee_config(config: str):
    if config == "C":
        print("C chain config")
        _set_fee_config(c_chain_config)
    else:
        print("Dummy config")
        _set_fee_config(dummy_config)


def get_fee_config():
    fm_interface = fee_manager()
    fee_config = fm_interface.getFeeConfig()
    print(FeeConfig(*fee_config))


def get_fee_config_last_changed_at():
    fm_inteface = fee_manager()
    block_number = fm_inteface.getFeeConfigLastChangedAt()
    print(f"Fee config last changed at block: {block_number}")
