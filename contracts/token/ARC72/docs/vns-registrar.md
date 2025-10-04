# VNSRegistrar Contract Documentation

## Overview

The VNSRegistrar is a specialized smart contract that manages domain name registration in the Voi Name Service (VNS) system. Built on top of the ARC72 NFT standard, it creates domain NFTs that can be registered, renewed, transferred, and managed with built-in expiration mechanisms.

## Architecture

VNSRegistrar inherits from multiple base classes to provide comprehensive domain management:

- **ARC72Token**: Core NFT functionality for domain ownership and transfers
- **Upgradeable**: Controlled contract upgrade management
- **Stakeable**: Staking and delegation capabilities for governance

This architecture creates a robust domain management system where each registered domain becomes a transferable NFT with sophisticated lifecycle management.

## Key Features

### Domain Registration
- **Hierarchical Structure**: Creates subdomains under a configurable root node (e.g., `alice.voi`)
- **NFT Integration**: Each domain becomes an ARC72 NFT with unique token ID
- **Dynamic Pricing**: Cost varies based on domain length and registration duration
- **Expiration Management**: Built-in expiration tracking with configurable grace periods
- **Transferable Ownership**: Domains can be transferred between addresses like any NFT

### Payment System
- **Dual Payment Model**: VOI for storage costs + ARC200 token for registration fees
- **Treasury Integration**: Fees collected and sent to configurable treasury address
- **Dynamic Pricing**: Shorter domains cost more (1-5 character domains have multipliers)
- **Flexible Duration**: Registration periods must be multiples of 1 year

### Advanced Management
- **Controller System**: Authorized controllers can perform administrative functions
- **Grace Period**: Buffer time before expired domains can be reclaimed
- **Automatic Expiration**: Domains automatically expire and revert to registrar
- **Reclaim Mechanism**: Expired domains can be reclaimed by anyone after grace period

## Contract State

### Core Configuration
```python
# Registrar Configuration
self.treasury = Global.creator_address          # Fee collection address
self.registry = UInt64(0)                      # VNS Registry contract ID
self.payment_token = UInt64(0)                 # ARC200 payment token ID
self.root_node = Bytes32.from_bytes(...)       # Root domain node hash
self.grace_period = UInt64(90)                 # Grace period in days

# Pricing Configuration
self.base_cost = BigUInt(1_000_000)            # Base cost (1 USDC equivalent)
self.cost_multiplier = BigUInt(5)              # Cost multiplier (5x)
self.base_period = UInt64(365 * 24 * 60 * 60)  # Base period (1 year)

# Domain Management
self.expires = BoxMap(BigUInt, BigUInt)        # Token ID -> Expiration timestamp
self.controllers = BoxMap(Account, bool)       # Authorized controllers
```

### State Variables Explained

- **treasury**: Address where registration fees are collected
- **registry**: Contract ID of the VNS Registry for DNS management
- **payment_token**: Contract ID of the ARC200 token used for payments
- **root_node**: The root domain node (e.g., `.voi`) under which subdomains are created
- **grace_period**: Days after expiration before domain can be reclaimed
- **base_cost**: Base registration cost in payment token units
- **cost_multiplier**: Multiplier applied to base cost for premium domains
- **base_period**: Minimum registration period (1 year)
- **expires**: Maps token IDs to their expiration timestamps
- **controllers**: Maps addresses to their controller status

## Contract Methods

### Domain Registration

#### `register(name: Bytes32, owner: Address, duration: UInt256) -> Bytes32`
Registers a new domain name under the root node.

**Parameters:**
- `name`: The domain name to register (e.g., "alice" for "alice.voi")
- `owner`: Address that will own the domain NFT
- `duration`: Registration duration in seconds (must be multiple of 1 year)

**Returns:**
- `Bytes32`: The namehash of the registered domain

**Process:**
1. Validates domain name format (alphanumeric and hyphens only)
2. Calculates registration cost based on name length and duration
3. Collects payment in ARC200 tokens from sender to treasury
4. Mints domain as NFT with unique token ID
5. Sets up DNS records in VNS Registry
6. Sets expiration timestamp
7. Emits `NameRegistered` event

**Example:**
```typescript
const result = await vnsRegistrar.register({
  name: "alice",
  owner: "ALICE_ADDRESS",
  duration: 365 * 24 * 60 * 60 // 1 year
});
```

#### `mint(to: Address, name: Bytes32) -> UInt256`
Mints a domain NFT (controller-only function).

**Parameters:**
- `to`: Address to receive the NFT
- `name`: Domain name to mint

**Returns:**
- `UInt256`: Token ID of the minted NFT

**Access Control:** Only authorized controllers can call this method.

### Domain Renewal

#### `renew(name: Bytes32, duration: UInt256)`
Renews an existing domain registration.

**Parameters:**
- `name`: Domain name to renew
- `duration`: Additional duration to add (must be multiple of 1 year)

**Process:**
1. Verifies domain exists and is not expired beyond grace period
2. Calculates renewal fee based on name length and duration
3. Collects payment in ARC200 tokens
4. Extends expiration timestamp
5. Emits `NameRenewed` event

**Example:**
```typescript
await vnsRegistrar.renew({
  name: "alice",
  duration: 365 * 24 * 60 * 60 // 1 year
});
```

### Domain Management

#### `expiration(tokenId: UInt256) -> UInt256`
Returns the expiration timestamp for a domain.

**Parameters:**
- `tokenId`: Token ID of the domain

**Returns:**
- `UInt256`: Expiration timestamp (0 if no expiration set)

#### `is_expired(tokenId: UInt256) -> Bool`
Checks if a domain has expired beyond the grace period.

**Parameters:**
- `tokenId`: Token ID of the domain

**Returns:**
- `Bool`: True if expired beyond grace period

#### `reclaim(name: Bytes32)`
Reclaims an expired domain (owner or controller only).

**Parameters:**
- `name`: Domain name to reclaim

**Access Control:** Only domain owner or authorized controllers.

#### `reclaimExpiredName(name: Bytes32)`
Reclaims a domain that has expired beyond the grace period.

**Parameters:**
- `name`: Domain name to reclaim

**Access Control:** Anyone can reclaim domains expired beyond grace period.

### Controller Management

#### `approve_controller(controller: Address, approved: Bool)`
Approves or revokes controller permissions (owner only).

**Parameters:**
- `controller`: Address to approve/disapprove
- `approved`: True to approve, false to revoke

**Access Control:** Only contract owner.

#### `is_controller(controller: Address) -> Bool`
Checks if an address is an authorized controller.

**Parameters:**
- `controller`: Address to check

**Returns:**
- `Bool`: True if controller or owner

### Utility Methods

#### `check_name(name: Bytes32) -> Bool`
Validates domain name format.

**Parameters:**
- `name`: Domain name to validate

**Returns:**
- `Bool`: True if valid format (alphanumeric and hyphens only)

**Validation Rules:**
- Only characters: `0-9`, `a-z`, `-` (hyphen)
- No uppercase letters
- No special characters

#### `get_length(name: Bytes32) -> UInt64`
Returns the length of a domain name.

**Parameters:**
- `name`: Domain name

**Returns:**
- `UInt64`: Length of the name

#### `get_price(name: Bytes32, duration: UInt256) -> UInt256`
Calculates registration/renewal price.

**Parameters:**
- `name`: Domain name
- `duration`: Registration duration

**Returns:**
- `UInt256`: Price in payment token units

**Pricing Formula:**
- Base cost × Cost multiplier × Duration factor
- Shorter domains have higher multipliers

### Configuration Methods

#### `setResolver(resolver: UInt64)`
Sets the resolver contract for the root node (owner only).

**Parameters:**
- `resolver`: Resolver contract ID

#### `setRootNode(root_node: Bytes32)`
Sets the root node for the registrar (owner only).

**Parameters:**
- `root_node`: Root node hash

#### `setPaymentToken(token: UInt64)`
Sets the payment token contract (owner only).

**Parameters:**
- `token`: ARC200 token contract ID

#### `setGracePeriod(grace_period: UInt64)`
Sets the grace period for expired domains (owner only).

**Parameters:**
- `grace_period`: Grace period in seconds

## Domain Registration Process

### Step-by-Step Process

1. **Name Validation**
   - Domain name must contain only alphanumeric characters and hyphens
   - No uppercase letters or special characters allowed
   - Name must not be empty

2. **Availability Check**
   - Domain must not already be registered
   - Check performed during NFT minting (will fail if already exists)

3. **Duration Validation**
   - Registration duration must be at least 1 year
   - Duration must be a multiple of 1 year
   - Maximum duration typically limited by contract configuration

4. **Cost Calculation**
   - Price based on name length and duration
   - Shorter domains cost more (premium pricing)
   - Formula: `base_cost × cost_multiplier × duration_factor`

5. **Payment Collection**
   - VOI payment for storage costs (minimum required)
   - ARC200 token payment for registration fee
   - Payment sent to treasury address

6. **NFT Minting**
   - Domain becomes a transferable NFT
   - Unique token ID based on domain namehash
   - NFT metadata includes domain information

7. **DNS Setup**
   - Domain registered in VNS Registry
   - Subdomain ownership set up
   - Resolution records established

8. **Expiration Management**
   - Expiration timestamp recorded
   - Grace period starts after expiration
   - Domain can be reclaimed after grace period

## Pricing Model

### Dynamic Pricing System

The VNSRegistrar uses a sophisticated pricing model:

- **Base Cost**: 1 USDC equivalent (1,000,000 units)
- **Cost Multiplier**: 5x for premium domains
- **Length-Based Pricing**: Shorter domains cost significantly more
- **Duration Requirements**: Must be multiples of 1 year

### Pricing Examples

- **Short domains (1-3 chars)**: Premium pricing with high multipliers
- **Medium domains (4-6 chars)**: Standard pricing
- **Long domains (7+ chars)**: Base pricing
- **Duration**: Linear scaling with registration period

## Usage Examples

### Register a Domain

```typescript
import { VnsRegistrarClient } from './clients/VNSRegistrarClient';

// Initialize client
const client = new VnsRegistrarClient({
  resolveBy: 'id',
  id: registrarContractId,
  sender: senderAccount
});

// Register "alice.voi" for 1 year
const domainName = "alice";
const owner = "ALICE_ADDRESS";
const duration = 365 * 24 * 60 * 60; // 1 year in seconds

const result = await client.register({
  name: domainName,
  owner: owner,
  duration: duration
});

console.log("Registered domain:", result.returnValue);
```

### Renew a Domain

```typescript
// Renew "alice.voi" for another year
const domainName = "alice";
const duration = 365 * 24 * 60 * 60; // 1 year in seconds

await client.renew({
  name: domainName,
  duration: duration
});
```

### Check Domain Status

```typescript
// Get domain token ID
const tokenId = await client.arc72_ownerOf({ tokenId: domainTokenId });

// Check expiration
const expiration = await client.expiration({ tokenId: domainTokenId });
const isExpired = await client.is_expired({ tokenId: domainTokenId });

console.log("Domain expires at:", new Date(expiration.returnValue * 1000));
console.log("Is expired:", isExpired.returnValue);
```

### Transfer Domain NFT

```typescript
// Transfer domain NFT to new owner
await client.arc72_transferFrom({
  from: currentOwner,
  to: newOwner,
  tokenId: domainTokenId
});
```

### Check Domain Price

```typescript
// Calculate registration cost
const price = await client.get_price({
  name: "alice",
  duration: 365 * 24 * 60 * 60
});

console.log("Registration cost:", price.returnValue);
```

## Integration with VNS System

VNSRegistrar integrates with several other VNS contracts to provide a complete domain service:

### 1. VNS Registry
- **Purpose**: Manages domain ownership and subdomain delegation
- **Integration**: VNSRegistrar calls `setSubnodeOwner` to register domains
- **Function**: Establishes DNS hierarchy and ownership records

### 2. VNS Resolver
- **Purpose**: Handles domain resolution to addresses and other records
- **Integration**: VNSRegistrar can set resolver for root node
- **Function**: Enables domain-to-address resolution

### 3. ARC200 Token
- **Purpose**: Payment token for registration and renewal fees
- **Integration**: VNSRegistrar calls `arc200_transferFrom` for payments
- **Function**: Handles fee collection and treasury management

### 4. Reverse Registrar
- **Purpose**: Enables reverse resolution (address to domain)
- **Integration**: Can be configured to work with VNSRegistrar
- **Function**: Maps addresses back to domain names

## Events

VNSRegistrar emits several events for tracking important state changes:

### `NameRegistered`
Emitted when a new domain is registered.

**Parameters:**
- `token_id`: Token ID of the registered domain
- `owner`: Address of the domain owner
- `expiration`: Expiration timestamp

### `NameRenewed`
Emitted when a domain is renewed.

**Parameters:**
- `token_id`: Token ID of the renewed domain
- `expiration`: New expiration timestamp

### `NameReclaimed`
Emitted when an expired domain is reclaimed.

**Parameters:**
- `token_id`: Token ID of the reclaimed domain
- `reclaimer`: Address that reclaimed the domain

### `ControllerApproved`
Emitted when controller permissions change.

**Parameters:**
- `controller`: Controller address
- `approved`: Approval status

## Security Considerations

### Access Control
- **Owner Functions**: Only contract owner can perform administrative functions
- **Controller Functions**: Authorized controllers can mint domains and perform reclaims
- **Public Functions**: Anyone can register, renew, and reclaim expired domains

### Expiration Handling
- **Automatic Expiration**: Domains automatically expire at set timestamp
- **Grace Period**: Buffer time prevents immediate reclaiming
- **Reclaim Mechanism**: Expired domains can be reclaimed after grace period

### Payment Validation
- **Dual Payment**: Both VOI and ARC200 token payments required
- **Amount Validation**: Payment amounts validated before processing
- **Treasury Security**: Fees sent to configurable treasury address

### Name Validation
- **Format Validation**: Strict validation prevents invalid domain names
- **Character Restrictions**: Only alphanumeric and hyphens allowed
- **Length Limits**: Reasonable length limits prevent abuse

### Upgrade Safety
- **Controlled Upgrades**: Contract upgrades require multiple approvals
- **Version Management**: Contract and deployment versions tracked
- **Backward Compatibility**: Upgrades maintain existing functionality

## Error Handling

The contract includes comprehensive error handling with descriptive error messages:

### Registration Errors
- `"name must be valid"`: Invalid domain name format
- `"duration must be at least 1 year"`: Insufficient registration duration
- `"duration must be a multiple of 1 year"`: Invalid duration format

### Domain Management Errors
- `"name not registered"`: Domain doesn't exist
- `"name expired"`: Domain has expired beyond grace period
- `"sender must be owner or controller"`: Unauthorized access

### Payment Errors
- `"transfer failed"`: Payment token transfer failed
- `"insufficient payment"`: Payment amount too low

### Access Control Errors
- `"sender must be owner"`: Unauthorized access to owner functions
- `"sender must be upgrader"`: Unauthorized access to upgrade functions

## Testing

The contract includes comprehensive test coverage:

### Unit Tests
- Individual method testing
- Parameter validation testing
- Error condition testing

### Integration Tests
- End-to-end registration flow
- Payment processing tests
- Expiration and renewal tests

### Edge Case Testing
- Invalid input handling
- Boundary condition testing
- Error recovery testing

### Performance Testing
- Gas optimization testing
- Large-scale operation testing

Run tests using:
```bash
arc72-pytest
```

## Deployment

### Prerequisites
- Algorand SDK (algosdk)
- Contract compilation tools
- Proper account setup with sufficient ALGO

### Build Process
```bash
# Build Docker image
arc72-build-image

# Build artifacts
arc72-build-artifacts

# Build all
arc72-build-all
```

### Environment Configuration
Configure the following environment variables:

- `ALGOD_SERVER`: Algorand node URL
- `ALGOD_TOKEN`: Algorand node token
- `INDEXER_SERVER`: Algorand indexer URL
- `ARC72_INDEXER_SERVER`: ARC72 indexer URL

### Deployment Steps
1. Deploy the contract using provided scripts
2. Configure initial parameters (owner, treasury, etc.)
3. Set up payment token integration
4. Configure VNS Registry integration
5. Test registration and renewal flows

## Best Practices

### For Developers
- Always validate domain names before registration
- Check domain availability before attempting registration
- Handle expiration gracefully in applications
- Implement proper error handling for all operations
- Use appropriate gas limits for transactions

### For Users
- Choose meaningful domain names
- Register for appropriate durations
- Monitor domain expiration dates
- Renew domains before expiration
- Understand pricing model before registration

### For Integrators
- Implement proper event listening
- Handle contract upgrades gracefully
- Use appropriate retry mechanisms
- Implement proper error recovery
- Monitor contract state changes

## Support

For technical support and questions:

- **Documentation**: Check the main project documentation
- **Source Code**: Review the contract source code
- **Issues**: Submit issues to the project repository
- **Community**: Join community discussions
- **Examples**: Review provided usage examples

## License

This contract is part of the OpenSub ARC72 VNS project. Please refer to the project license for usage terms and conditions.

## Changelog

For detailed information about changes, new features, bug fixes, and breaking changes, please see the [VNSRegistrar Changelog](vns-registrar-changelog.md).

### Recent Versions

#### Version 2.0.0
- Subname registration support
- Enhanced NFT minting functionality
- Multi-token payment support
- Improved domain management

#### Version 1.1.1
- Enhanced domain management
- Improved NFT integration
- Better error handling
- Enhanced security features

#### Version 1.0.0
- Initial implementation of VNSRegistrar
- Basic domain registration and renewal
- ARC72 NFT integration
- Payment system integration

---

*This documentation is maintained as part of the OpenSub ARC72 VNS project. For the most up-to-date information, please refer to the project repository.*
