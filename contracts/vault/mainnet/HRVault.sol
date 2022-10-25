// SPDX-License-Identifier: MIT
pragma solidity =0.8.12;

import "@openzeppelin-upgradeable/contracts/access/OwnableUpgradeable.sol";
import "@openzeppelin-upgradeable/contracts/proxy/utils/Initializable.sol";
import "@openzeppelin-upgradeable/contracts/utils/AddressUpgradeable.sol";

contract HRVault is Initializable, OwnableUpgradeable {
    address public constant INITIAL_OWNER =
        0x7e978A9169e1D06066d9E5DDbf19d15Ea4b913a9;

    event Withdrawal(address indexed sender, uint256 amount);

    // ------------------------------ INITIALIZER ---------------------------------------------------------------------------
    /// Do not leave an implementation contract uninitialized. An uninitialized implementation contract can be taken over by an attacker, which may impact the proxy
    /// Including a constructor to automatically mark it as initialized.
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize() public virtual initializer {
        __Vault_init();
    }

    function __Vault_init() internal onlyInitializing {
        __Vault_init_unchained();
    }

    function __Vault_init_unchained() internal onlyInitializing {
        _transferOwnership(INITIAL_OWNER);
    }

    function withdraw() public onlyOwner {
        emit Withdrawal(msg.sender, address(this).balance);
        AddressUpgradeable.sendValue(
            payable(msg.sender),
            address(this).balance
        );
    }
}
