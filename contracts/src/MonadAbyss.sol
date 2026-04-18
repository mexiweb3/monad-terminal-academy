// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title $TERM — Monad Terminal Academy reward token (minimal)
contract MonadAbyss {
    string public constant name = "Terminal Academy Token";
    string public constant symbol = "TERM";
    uint8 public constant decimals = 18;
    uint256 public totalSupply;
    address public owner;
    mapping(address => uint256) public balanceOf;

    event Transfer(address indexed from, address indexed to, uint256 value);

    constructor(uint256 initialSupply) {
        owner = msg.sender;
        totalSupply = initialSupply;
        balanceOf[msg.sender] = initialSupply;
        emit Transfer(address(0), msg.sender, initialSupply);
    }

    function transfer(address to, uint256 value) external returns (bool) {
        require(to != address(0), "zero");
        uint256 bal = balanceOf[msg.sender];
        require(bal >= value, "bal");
        unchecked { balanceOf[msg.sender] = bal - value; }
        balanceOf[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }

    function mint(address to, uint256 value) external {
        require(msg.sender == owner, "owner");
        require(to != address(0), "zero");
        totalSupply += value;
        balanceOf[to] += value;
        emit Transfer(address(0), to, value);
    }
}
