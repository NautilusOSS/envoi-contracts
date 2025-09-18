# VNS Registrar Documentation

## Overview

The VNS Registrar is a smart contract that manages domain name registration on the Algorand blockchain. It serves as the primary interface for users to register subdomains under the VNS root domain (e.g., `alice.voi`). The registrar combines ARC72 NFT functionality with domain management capabilities, making each registered domain a transferable NFT.

## Architecture

The VNS Registrar inherits from multiple base classes:
- **ARC72Token**: Provides NFT functionality for domains
- **Upgradeable**: Allows controlled contract upgrades
- **Stakeable**: Supports staking mechanisms for governance

## Key Features

### Domain Registration
- **Hierarchical Structure**: Creates subdomains under a configurable root node
- **NFT Integration**: Each domain becomes an ARC72 NFT with unique token ID
- **Dynamic Pricing**: Cost varies based on domain length and registration duration
- **Expiration Management**: Built-in expiration tracking with grace periods
- **Transferable**: Domains can be transferred between addresses

### Payment System
- **Dual Payment**: VOI for storage costs + ARC200 token for registration fees
- **Treasury Integration**: Fees collected and sent to configurable treasury
- **Dynamic Pricing**: Shorter domains cost more (1-5 chars have multipliers)

## Contract State

### Core State Variables
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

## Registration Process

### 1. Name Validation
```python
def check_name(self, name: Bytes32) -> arc4.Bool:
    # Validates: alphanumeric + hyphens only
    # Length: 1-32 characters
    # Format: [0-9a-z-]
```

### 2. Registration Method
```python
def register(
    self, 
    name: Bytes32,           # Subdomain name (without .voi)
    owner: arc4.Address,    # Owner address
    duration: arc4.UInt256  # Duration in seconds
) -> Bytes32:               # Returns node hash
```

### 3. Internal Registration Flow
The `_register` subroutine performs:

1. **Validation**: Duration ≥ 1 year, valid name format
2. **Node Creation**: Generates unique node hash using namehash
3. **Payment Processing**: 
   - VOI payment for storage (336,700 microVOI)
   - ARC200 token payment for registration fee
4. **NFT Minting**: Creates ARC72 NFT representing the domain
5. **Registry Integration**: Registers subdomain in VNS registry
6. **Expiration Setting**: Sets expiration timestamp

## Pricing Model

### Base Cost Calculation
```python
def _base_cost(self, unit: BigUInt, name_length: UInt64) -> BigUInt:
    if name_length == 1:    return unit * 32  # 32x for 1 char
    elif name_length == 2:  return unit * 16  # 16x for 2 chars  
    elif name_length == 3:  return unit * 8   # 8x for 3 chars
    elif name_length == 4:  return unit * 4   # 4x for 4 chars
    elif name_length == 5:  return unit * 2   # 2x for 5 chars
    else:                   return unit * 1   # 1x for 5+ chars
```

### Total Price Formula
```python
total_price = base_cost * cost_multiplier * years
```

**Example Pricing** (assuming 1 USDC base cost, 5x multiplier):
- `a.voi` (1 char): 1 USDC × 5 × 32 = 160 USDC/year
- `al.voi` (2 chars): 1 USDC × 5 × 16 = 80 USDC/year  
- `alice.voi` (5 chars): 1 USDC × 5 × 2 = 10 USDC/year
- `alice123.voi` (8 chars): 1 USDC × 5 × 1 = 5 USDC/year

## CLI Commands

### Registration Commands

#### Register a Domain
```bash
node command.js registrar register \
  --apid <REGISTRAR_ID> \
  --name <SUBDOMAIN_NAME> \
  --owner <OWNER_ADDRESS> \
  --duration <YEARS>
```

**Example:**
```bash
node command.js registrar register \
  --apid 123456 \
  --name "alice" \
  --owner "ALICE_ADDRESS_HERE" \
  --duration 1
```

#### Check Name Availability
```bash
node command.js registrar checkName \
  --apid <REGISTRAR_ID> \
  --name <SUBDOMAIN_NAME>
```

#### Get Registration Price
```bash
node command.js registrar getPrice \
  --apid <REGISTRAR_ID> \
  --name <SUBDOMAIN_NAME> \
  --duration <YEARS>
```

### Domain Management Commands

#### Check Domain Owner
```bash
node command.js registrar ownerOf \
  --apid <REGISTRAR_ID> \
  --tokenId <TOKEN_ID>
```

#### Check Expiration
```bash
node command.js registrar expiration \
  --apid <REGISTRAR_ID> \
  --tokenId <TOKEN_ID>
```

#### Renew Domain
```bash
node command.js registrar renew \
  --apid <REGISTRAR_ID> \
  --name <SUBDOMAIN_NAME> \
  --duration <YEARS>
```

#### Reclaim Expired Domain
```bash
node command.js registrar reclaim \
  --apid <REGISTRAR_ID> \
  --name <SUBDOMAIN_NAME>
```

### Admin Commands

#### Set Treasury Address
```bash
node command.js registrar setTreasury \
  --apid <REGISTRAR_ID> \
  --treasury <TREASURY_ADDRESS>
```

#### Set Payment Token
```bash
node command.js registrar setPaymentToken \
  --apid <REGISTRAR_ID> \
  --token <TOKEN_ID>
```

#### Set Registry
```bash
node command.js registrar setRegistry \
  --apid <REGISTRAR_ID> \
  --registry <REGISTRY_ID>
```

#### Set Root Node
```bash
node command.js registrar setRootNode \
  --apid <REGISTRAR_ID> \
  --rootNode <ROOT_NODE_HASH>
```

## Domain Lifecycle

### 1. Registration
- User calls `register()` with name, owner, and duration
- Contract validates name and processes payment
- NFT is minted and domain is registered in VNS registry
- Expiration timestamp is set

### 2. Active Period
- Domain owner can transfer NFT to other addresses
- Domain resolves normally through VNS resolver
- Owner can renew before expiration

### 3. Expiration
- Domain expires after duration period
- Grace period begins (90 days by default)
- During grace period: domain still resolves but cannot be renewed
- After grace period: domain can be reclaimed by anyone

### 4. Reclamation
- Anyone can call `reclaim()` on expired domains
- Reclaimer becomes new owner
- New expiration timestamp is set

## Integration Points

### VNS Registry
- Registrar calls `setSubnodeOwner()` to create subdomains
- Registry manages domain ownership hierarchy
- Registrar must own the root node in registry

### VNS Resolver
- Registrar can set resolver for root domain
- Resolver handles domain-to-address resolution
- Supports reverse resolution (address to domain)

### ARC200 Tokens
- Payment processing for registration fees
- Requires user approval before registration
- Fees transferred to treasury address

## Security Features

### Access Control
- Only owner can modify configuration
- Only upgrader can upgrade contract
- Controllers can mint domains (currently disabled)

### Payment Security
- Requires explicit token approval
- Validates payment amounts
- Secure fee collection to treasury

### Domain Validation
- Strict name format validation
- Prevents invalid character usage
- Length limits prevent abuse

## Configuration

### Initial Setup
After deployment, the registrar must be configured:

1. **Set Registry**: Link to VNS Registry contract
2. **Set Root Node**: Configure root domain node hash
3. **Set Payment Token**: Specify ARC200 token for fees
4. **Set Treasury**: Configure fee collection address
5. **Set Resolver**: Link to VNS Resolver contract

### Environment Variables
```bash
# Required for CLI usage
MN="your_mnemonic_phrase"
MN2="second_account_mnemonic"
MN3="third_account_mnemonic"
```

## Error Handling

### Common Errors
- `"name must be valid"`: Invalid name format
- `"duration must be at least 1 year"`: Insufficient duration
- `"payment amount accurate"`: Insufficient payment
- `"sender must be owner"`: Unauthorized access
- `"VNS must be owned by registrar"`: Registry configuration issue

### Debug Mode
Use `--debug` flag for detailed transaction information:
```bash
node command.js registrar register \
  --apid 123456 \
  --name "alice" \
  --owner "ALICE_ADDRESS" \
  --duration 1 \
  --debug
```

## Best Practices

### For Users
1. **Check Availability**: Always verify name availability before registration
2. **Calculate Costs**: Use `getPrice()` to estimate registration costs
3. **Approve Tokens**: Ensure sufficient token approval before registration
4. **Monitor Expiration**: Set up monitoring for domain expiration
5. **Renew Early**: Renew domains before expiration to avoid grace period

### For Developers
1. **Validate Inputs**: Always validate name format and duration
2. **Handle Errors**: Implement proper error handling for failed registrations
3. **Monitor Events**: Listen for `NameRegistered` events
4. **Check Ownership**: Verify domain ownership before operations
5. **Test Thoroughly**: Use simulation mode for testing

## Events

### NameRegistered
```python
class NameRegistered(arc4.Struct):
    token_id: arc4.UInt256    # NFT token ID
    owner: arc4.Address      # Domain owner
    expiration: arc4.UInt64  # Expiration timestamp
```

### NameRenewed
```python
class NameRenewed(arc4.Struct):
    token_id: arc4.UInt256    # NFT token ID
    expiration: arc4.UInt64  # New expiration timestamp
```

## API Reference

### Read-Only Methods
- `arc72_ownerOf(tokenId)`: Get domain owner
- `expiration(tokenId)`: Get expiration timestamp
- `check_name(name)`: Validate name format
- `get_price(name, duration)`: Calculate registration cost
- `get_length(name)`: Get name length

### State-Changing Methods
- `register(name, owner, duration)`: Register new domain
- `renew(name, duration)`: Renew domain registration
- `reclaim(name)`: Reclaim expired domain
- `set_treasury(treasury)`: Set treasury address
- `set_payment_token(token)`: Set payment token
- `set_registry(registry)`: Set registry contract
- `set_root_node(root_node)`: Set root domain node

## Troubleshooting

### Registration Fails
1. Check name format (alphanumeric + hyphens only)
2. Verify sufficient token balance and approval
3. Ensure minimum duration (1 year)
4. Check if name is already registered

### Domain Not Resolving
1. Verify domain is not expired
2. Check VNS resolver configuration
3. Ensure proper registry setup
4. Verify domain ownership

### Payment Issues
1. Check token approval amount
2. Verify treasury address is correct
3. Ensure sufficient VOI balance for fees
4. Check payment token configuration

## Version History

- **v1.0**: Initial implementation with basic registration
- **v1.1**: Added expiration management and grace periods
- **v1.2**: Integrated ARC72 NFT functionality
- **v1.3**: Added dynamic pricing model
- **v1.4**: Simplified to single payment method (VOI + ARC200)

## Support

For technical support and questions:
- Check the main VNS documentation
- Review contract source code
- Test with simulation mode first
- Use debug mode for detailed error information
