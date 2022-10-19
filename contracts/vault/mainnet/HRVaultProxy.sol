// SPDX-License-Identifier: MIT
pragma solidity =0.8.12;

import "@openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol";

contract HRVaultProxy is TransparentUpgradeableProxy {
    address public constant INITIAL_ADMIN_ADDRESS =
        0x0300000000000000000000000000000000000000;
    address public constant INITIAL_LOGIC_ADDRESS =
        0x0300000000000000000000000000000000000001;
    address public constant INITIAL_OWNER = 0x9b10b6A50bf93E0eec102D7251107880F6192022;

    constructor(
        address _logic,
        address admin_,
        bytes memory _data
    ) payable TransparentUpgradeableProxy(_logic, admin_, _data) {}

    modifier notInitialized() {
        require(
            StorageSlot.getAddressSlot(_IMPLEMENTATION_SLOT).value ==
                address(0),
            "Implementation already initialized"
        );
        require(
            StorageSlot.getAddressSlot(_ADMIN_SLOT).value == address(0),
            "Proxy admin already initialized"
        );
        _;
    }

    modifier onlyAdmin() {
        require(
            msg.sender == INITIAL_OWNER,
            "Only owner can initialize proxy admin"
        );
        _;
    }

    function init() public onlyAdmin notInitialized {
        _changeAdmin(INITIAL_ADMIN_ADDRESS);
        _upgradeTo(INITIAL_LOGIC_ADDRESS);
    }
}
