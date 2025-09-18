# OpenSub ARC72 VNS Documentation

## Overview

OpenSub ARC72 VNS (Voi Name Service) is a comprehensive decentralized naming system built on the Algorand blockchain using ARC72 (NFT) and ARC200 (Token) standards. The system provides domain name registration, resolution, and management capabilities similar to Ethereum's ENS but optimized for the Algorand ecosystem.

## Architecture

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

## Key Features

### Domain Registration
- **Hierarchical Structure**: Supports multi-level domains (e.g., `subdomain.domain.tld`)
- **Pricing Model**: Dynamic pricing based on domain length and registration duration
- **Payment**: Uses ARC200 tokens for registration fees
- **Duration**: Configurable registration periods with renewal capabilities

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

## Contract Interfaces

### OwnableInterface
```python
class OwnableInterface(ARC4Contract):
    def transfer(self, new_owner: arc4.Address) -> None
```
Manages contract ownership and transfer operations.

### StakeableInterface
```python
class StakeableInterface(ARC4Contract):
    def stake(self, amount: arc4.UInt64) -> None
    def unstake(self, amount: arc4.UInt64) -> None
    def delegate(self, delegate: arc4.Address) -> None
```
Handles staking operations and delegation.

### ARC200TokenInterface
```python
class ARC200TokenInterface(ARC4Contract):
    def transfer(self, to: arc4.Address, amount: arc4.UInt256) -> bool
    def approve(self, spender: arc4.Address, amount: arc4.UInt256) -> bool
    def balanceOf(self, owner: arc4.Address) -> arc4.UInt256
```
Standard token operations for payment handling.

### ARC72TokenCoreInterface
```python
class ARC72TokenCoreInterface(ARC4Contract):
    def arc72_transferFrom(self, from_: arc4.Address, to: arc4.Address, tokenId: arc4.UInt256) -> None
    def arc72_ownerOf(self, tokenId: arc4.UInt256) -> arc4.Address
    def arc72_approve(self, to: arc4.Address, tokenId: arc4.UInt256) -> None
```
NFT operations for domain management.

### VNSCoreInterface
```python
class VNSCoreInterface(ARC4Contract):
    def setSubnodeOwner(self, node: Bytes32, label: Bytes32, owner: arc4.Address) -> Bytes32
    def setResolver(self, node: Bytes32, resolver: arc4.Address) -> None
    def setOwner(self, node: Bytes32, owner: arc4.Address) -> None
```
Core VNS operations for domain management.

## CLI Commands

The system provides a comprehensive CLI for interacting with all contracts:

### Deployment Commands
- `deploy` - Deploy new contract instances
- `postUpdate` - Update contract configurations
- `killApplication` - Remove contract instances

### Registry Operations
- `setSubnodeOwner` - Create subdomains
- `setOwner` - Transfer domain ownership
- `setResolver` - Set domain resolver
- `setTTL` - Set domain TTL
- `ownerOf` - Query domain ownership
- `resolver` - Query domain resolver
- `ttl` - Query domain TTL

### Resolver Operations
- `setAddr` - Set address resolution
- `resolveAddr` - Resolve domain to address
- `setRecord` - Set arbitrary records
- `resolveName` - Reverse resolve address to domain

### Registrar Operations
- `register` - Register new domains
- `renew` - Renew domain registration
- `reclaim` - Reclaim domain ownership
- `getPrice` - Query registration pricing
- `checkName` - Validate domain names
- `isExpired` - Check domain expiration

### ARC200 Token Operations
- `arc200Mint` - Mint new tokens
- `arc200Transfer` - Transfer tokens
- `arc200Approve` - Approve token spending
- `arc200BalanceOf` - Query token balance
- `arc200Allowance` - Query spending allowance

### RSVP Operations
- `reserve` - Reserve domain names
- `release` - Release domain reservations
- `adminReserve` - Admin reservation management
- `adminRelease` - Admin release management
- `price` - Query reservation pricing

## CLI Usage Guide

For detailed instructions on creating subnames using the command-line interface, see the [CLI Subname Creation Guide](CLI_SUBNAME_GUIDE.md). This comprehensive guide covers:

- Deploying registrar contracts
- Configuring registrar settings
- Minting and verifying subnames
- Reclaiming subname ownership
- Troubleshooting common issues

## Testing

The system includes comprehensive test suites covering:

### Core Functionality Tests
- **Registry Tests**: Domain ownership, subdomain creation, resolver management
- **Resolver Tests**: Address resolution, record management, reverse resolution
- **Registrar Tests**: Domain registration, renewal, pricing, expiration
- **ARC200 Tests**: Token operations, approvals, transfers
- **RSVP Tests**: Reservation management, pricing, admin operations

### Test Structure
```javascript
describe("VNSRegistry:core:registrar Test Suite", function () {
  // Registry and registrar integration tests
});

describe("VNSRegistry:core:resolver Test Suite", function () {
  // Resolver functionality tests
});

describe("VNS:core:arc200 Test Suite", function () {
  // Token operation tests
});

describe("VNS:rsvp Test Suite", function () {
  // Reservation system tests
});
```

## Usage Examples

### Domain Registration
```typescript
// Deploy contracts
const vnsRegistry = await deploy({ type: "vns-registry", name: "vns-registry" });
const vnsResolver = await deploy({ type: "vns-resolver", name: "vns-resolver" });
const vnsRegistrar = await deploy({ type: "vns-registrar", name: "vns-registrar" });

// Set up root domain
await setSubnodeOwner({
  apid: vnsRegistry,
  node: "",
  label: "voi",
  owner: vnsRegistrar
});

// Register subdomain
await register({
  apid: vnsRegistrar,
  name: "example",
  owner: userAddress,
  duration: 365 * 24 * 60 * 60
});
```

### Domain Resolution
```typescript
// Set address resolution
await setAddr({
  apid: vnsResolver,
  node: "example.voi",
  addr: targetAddress
});

// Resolve domain to address
const resolvedAddress = await resolveAddr({
  apid: vnsResolver,
  node: "example.voi"
});
```

### Token Operations
```typescript
// Approve spending for registration
await arc200Approve({
  apid: paymentToken,
  spender: vnsRegistrar,
  amount: registrationPrice
});

// Check balance
const balance = await arc200BalanceOf({
  apid: paymentToken,
  owner: userAddress
});
```

## Security Features

- **Access Control**: Role-based permissions for different operations
- **Upgrade Safety**: Controlled upgrade mechanisms with approval processes
- **Payment Validation**: Secure payment handling with token approvals
- **Domain Validation**: Name validation to prevent invalid registrations
- **Expiration Management**: Graceful handling of expired domains

## Configuration

### Environment Variables
- `MN`, `MN2`, `MN3` - Mnemonics for test accounts
- Contract addresses and configuration parameters

### Pricing Model
- Dynamic pricing based on domain length
- Duration-based pricing multipliers
- Treasury fee collection

## Development

### Prerequisites
- Node.js and npm/pnpm
- Algorand development environment
- TypeScript support

### Setup
```bash
npm install
npm run build
npm test
```

### Contract Deployment
```bash
npm run deploy
```

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

Please refer to the project's contribution guidelines for information on how to contribute to this project.
