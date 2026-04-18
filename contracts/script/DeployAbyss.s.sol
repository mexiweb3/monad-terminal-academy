// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script, console} from "forge-std/Script.sol";
import {MonadAbyss} from "../src/MonadAbyss.sol";

contract DeployAbyss is Script {
    function run() external {
        uint256 pk = vm.envUint("PRIVATE_KEY");
        uint256 initialSupply = 1_000_000_000 ether;
        vm.startBroadcast(pk);
        MonadAbyss token = new MonadAbyss(initialSupply);
        vm.stopBroadcast();
        console.log("ABYSS deployed at:", address(token));
    }
}
