// SPDX-License-Identifier: MIT
pragma solidity =0.8.12;

import "@openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol";

contract HRVaultProxy is TransparentUpgradeableProxy {
    address public constant INITIAL_ADMIN_ADDRESS =
        0x0300000000000000000000000000000000000000;
    address public constant INITIAL_LOGIC_ADDRESS =
        0x0300000000000000000000000000000000000001;

    constructor()
        TransparentUpgradeableProxy(
            INITIAL_LOGIC_ADDRESS,
            INITIAL_ADMIN_ADDRESS,
            ""
        )
    {}

    modifier notInitialized() {
        require(
            _getImplementation() == address(0),
            "Implementation already initialized"
        );
        _;
    }

    function init() public notInitialized {
        _changeAdmin(INITIAL_ADMIN_ADDRESS);
        _upgradeTo(INITIAL_LOGIC_ADDRESS);
    }
}
