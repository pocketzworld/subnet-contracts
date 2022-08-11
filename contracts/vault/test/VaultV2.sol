// SPDX-License-Identifier: MIT
pragma solidity =0.8.12;

import "@openzeppelin-upgradeable/contracts/access/OwnableUpgradeable.sol";
import "@openzeppelin-upgradeable/contracts/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts/utils/Address.sol";

contract VaultV2 is Initializable, OwnableUpgradeable {
    address constant INITIAL_OWNER = 0x9b10b6A50bf93E0eec102D7251107880F6192022;

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
        __Ownable_init();
        __Vault_init_unchained();
    }

    function __Vault_init_unchained() internal onlyInitializing {
        _transferOwnership(INITIAL_OWNER);
    }

    function withdraw() public onlyOwner {
        emit Withdrawal(msg.sender, address(this).balance);
        Address.sendValue(payable(owner()), address(this).balance);
    }

    // Function to handle plain ether transactions
    receive() external payable {}

    function initializeV2() public reinitializer(2) {
        _transferOwnership(msg.sender);
    }

    function withdrawAmount(uint256 amount) public {
        require(
            address(this).balance >= amount,
            "Insufficient amount to withdraw"
        );
        Address.sendValue(payable(msg.sender), address(this).balance);
    }
}
