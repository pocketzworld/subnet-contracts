// SPDX-License-Identifier: MIT
pragma solidity =0.8.12;

import "@openzeppelin/contracts/proxy/transparent/ProxyAdmin.sol";

contract HRVaultProxyAdmin is ProxyAdmin {
    address public constant INITIAL_OWNER =
        0x9b10b6A50bf93E0eec102D7251107880F6192022;

    modifier notInitialized() {
        require(owner() == address(0), "Vault Proxy Admin already initialized");
        _;
    }

    function init() public notInitialized {
        _transferOwnership(INITIAL_OWNER);
    }
}
