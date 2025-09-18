# OpenSubmarine ARC72 VNS (Voi Name Service)

A comprehensive decentralized naming service built on the Algorand blockchain using ARC72 (NFT) and ARC200 (Token) standards. This system provides domain name registration, resolution, and management capabilities similar to Ethereum's ENS but optimized for the Algorand ecosystem.

## 🚀 Quick Start

### Prerequisites
- Node.js and npm/pnpm
- Algorand development environment
- TypeScript support

### Installation
```bash
npm install
npm run build
npm test
```

### Deployment
```bash
npm run deploy
```

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Core Features](#core-features)
- [Smart Contracts](#smart-contracts)
- [CLI Usage](#cli-usage)
- [API Reference](#api-reference)
- [Security](#security)
- [Testing](#testing)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## 🏗️ Architecture

The VNS system consists of several interconnected smart contracts:

### Core Contracts
1. **VNS Registry** - Central registry managing domain ownership and subdomain delegation
2. **VNS Resolver** - Handles domain resolution to addresses and other records
3. **VNS Registrar** - Manages domain registration, renewal, and pricing
4. **Reverse Registrar** - Enables reverse resolution (address to domain)
5. **Collection Registrar** - Manages domain collections and bulk operations
6. **Staking Registrar** - Handles staking mechanisms for domain management
7. **RSVP Contract** - Manages domain reservations and pre-registration

### Token Contracts
- **ARC200 Token** - Payment token for domain registration and management
- **ARC200 Token Factory** - Factory contract for creating new payment tokens

## ✨ Core Features

### Domain Registration
- **Hierarchical Structure**: Supports multi-level domains (e.g., `subdomain.domain.tld`)
- **Dynamic Pricing**: Cost varies based on domain length and registration duration
- **Payment System**: Uses ARC200 tokens for registration fees
- **Duration Management**: Configurable registration periods with renewal capabilities
- **Grace Periods**: 90-day grace period for expired domains

### Domain Resolution
- **Address Resolution**: Map domain names to Algorand addresses
- **Reverse Resolution**: Map addresses back to domain names
- **Text Records**: Support for arbitrary text data storage
- **Multi-address Support**: Handle multiple address types

### NFT Integration
- **ARC72 Compliance**: Domains are represented as NFTs
- **Transfer Management**: Controlled transfer mechanisms
- **Metadata Support**: Rich metadata for domain information
- **Enumeration**: Support for listing owned domains

### Staking & Governance
- **Staking Mechanisms**: Stake tokens for governance participation
- **Upgrade Management**: Controlled contract upgrades
- **Treasury Management**: Fee collection and distribution

## 🔧 Smart Contracts

### VNS Registry
Central registry managing domain ownership and subdomain delegation.

```python
class VNSRegistry(ARC4Contract):
    def setSubnodeOwner(self, node: Bytes32, label: Bytes32, owner: arc4.Address) -> Bytes32
    def setResolver(self, node: Bytes32, resolver: arc4.Address) -> None
    def setOwner(self, node: Bytes32, owner: arc4.Address) -> None
```

### VNS Resolver
Handles domain resolution to addresses and other records.

```python
class VNSPublicResolver(ARC4Contract):
    def setAddr(self, node: Bytes32, addr: arc4.Address) -> None
    def resolveAddr(self, node: Bytes32) -> arc4.Address
    def setRecord(self, node: Bytes32, key: arc4.String, value: arc4.String) -> None
```

### VNS Registrar
Manages domain registration, renewal, and pricing.

```python
class VNSRegistrar(ARC72Token, Upgradeable, Stakeable):
    def register(self, name: Bytes32, owner: arc4.Address, duration: arc4.UInt256) -> Bytes32
    def renew(self, name: Bytes32, duration: arc4.UInt256) -> None
    def reclaim(self, name: Bytes32) -> None
```

## 💻 CLI Usage

The system provides a comprehensive CLI for interacting with all contracts:

### Domain Registration
```bash
# Register a domain
node command.js registrar register \
  --apid <REGISTRAR_ID> \
  --name <SUBDOMAIN_NAME> \
  --owner <OWNER_ADDRESS> \
  --duration <YEARS>

# Check name availability
node command.js registrar checkName \
  --apid <REGISTRAR_ID> \
  --name <SUBDOMAIN_NAME>

# Get registration price
node command.js registrar getPrice \
  --apid <REGISTRAR_ID> \
  --name <SUBDOMAIN_NAME> \
  --duration <YEARS>
```

### Domain Resolution
```bash
# Set address resolution
node command.js resolver setAddr \
  --apid <RESOLVER_ID> \
  --node <DOMAIN> \
  --addr <ADDRESS>

# Resolve domain to address
node command.js resolver resolveAddr \
  --apid <RESOLVER_ID> \
  --node <DOMAIN>
```

### Token Operations
```bash
# Approve spending for registration
node command.js arc200 approve \
  --apid <TOKEN_ID> \
  --spender <REGISTRAR_ADDRESS> \
  --amount <AMOUNT>

# Check balance
node command.js arc200 balanceOf \
  --apid <TOKEN_ID> \
  --owner <OWNER_ADDRESS>
```

## 📖 API Reference

### Contract Interfaces

#### OwnableInterface
```python
class OwnableInterface(ARC4Contract):
    def transfer(self, new_owner: arc4.Address) -> None
```

#### StakeableInterface
```python
class StakeableInterface(ARC4Contract):
    def stake(self, amount: arc4.UInt64) -> None
    def unstake(self, amount: arc4.UInt64) -> None
    def delegate(self, delegate: arc4.Address) -> None
```

#### ARC200TokenInterface
```python
class ARC200TokenInterface(ARC4Contract):
    def transfer(self, to: arc4.Address, amount: arc4.UInt256) -> bool
    def approve(self, spender: arc4.Address, amount: arc4.UInt256) -> bool
    def balanceOf(self, owner: arc4.Address) -> arc4.UInt256
```

#### ARC72TokenCoreInterface
```python
class ARC72TokenCoreInterface(ARC4Contract):
    def arc72_transferFrom(self, from_: arc4.Address, to: arc4.Address, tokenId: arc4.UInt256) -> None
    def arc72_ownerOf(self, tokenId: arc4.UInt256) -> arc4.Address
    def arc72_approve(self, to: arc4.Address, tokenId: arc4.UInt256) -> None
```

## 🔒 Security Features

- **Access Control**: Role-based permissions for different operations
- **Upgrade Safety**: Controlled upgrade mechanisms with approval processes
- **Payment Validation**: Secure payment handling with token approvals
- **Domain Validation**: Name validation to prevent invalid registrations
- **Expiration Management**: Graceful handling of expired domains

## 🧪 Testing

The system includes comprehensive test suites covering:

### Core Functionality Tests
- **Registry Tests**: Domain ownership, subdomain creation, resolver management
- **Resolver Tests**: Address resolution, record management, reverse resolution
- **Registrar Tests**: Domain registration, renewal, pricing, expiration
- **ARC200 Tests**: Token operations, approvals, transfers
- **RSVP Tests**: Reservation management, pricing, admin operations

### Running Tests
```bash
npm test
```

## 📚 Documentation

- [Main Documentation](docs/index.md) - Complete system overview
- [Registrar Guide](docs/REGISTRAR.md) - Detailed registrar documentation
- [CLI Subname Guide](docs/CLI_SUBNAME_GUIDE.md) - Step-by-step CLI usage

## 💰 Pricing Model

Dynamic pricing based on domain length:
- 1 character: 32x base cost
- 2 characters: 16x base cost
- 3 characters: 8x base cost
- 4 characters: 4x base cost
- 5 characters: 2x base cost
- 6+ characters: 1x base cost

**Example Pricing** (assuming 1 USDC base cost, 5x multiplier):
- `a.voi` (1 char): 160 USDC/year
- `al.voi` (2 chars): 80 USDC/year
- `alice.voi` (5 chars): 10 USDC/year
- `alice123.voi` (8 chars): 5 USDC/year

## 🚀 Deployment

### Environment Setup
```bash
# Required environment variables
export MN="your_mnemonic_phrase"
export MN2="second_account_mnemonic"
export MN3="third_account_mnemonic"
```

### Contract Deployment
```bash
# Deploy all contracts
npm run deploy

# Deploy specific contract
node command.js deploy -t vns-registry -n vns-registry
node command.js deploy -t vns-resolver -n vns-resolver
node command.js deploy -t vns-registrar -n vns-registrar
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for information on how to contribute to this project.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🆘 Support

For technical support and questions:
- Check the documentation in the `docs/` directory
- Review contract source code
- Test with simulation mode first
- Use debug mode for detailed error information

## 🏷️ Version History

- **v1.0.0**: Initial stable release with complete VNS functionality
  - Full ARC72 NFT integration
  - Complete CLI tooling
  - Comprehensive test coverage
  - Production-ready smart contracts

---

**Built with ❤️ for the Algorand ecosystem**