// SPDX-License-Identifier: MIT
pragma solidity =0.8.12;

import "@openzeppelin/contracts/proxy/transparent/ProxyAdmin.sol";

contract HRVaultProxyAdmin is ProxyAdmin {
    address public constant INITIAL_OWNER =
        0x7e978A9169e1D06066d9E5DDbf19d15Ea4b913a9;

    modifier notInitialized() {
        require(owner() == address(0), "Vault Proxy Admin already initialized");
        _;
    }

    function init() public notInitialized {
        _transferOwnership(INITIAL_OWNER);
    }
}
