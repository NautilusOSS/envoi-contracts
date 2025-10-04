# VNSRegistrar Version 1.2 Documentation

**Release Date**: September 18, 2025  
**Contract Version**: 1  
**Deployment Version**: 2  

## Overview

Version 1.2 represents a significant enhancement to the VNSRegistrar contract, introducing comprehensive subname registration capabilities, enhanced NFT minting functionality, and improved domain management features. This release significantly expands the VNS system's capabilities while maintaining backward compatibility with existing deployments.

## Dual Versioning System

The VNSRegistrar contract uses a dual versioning system:

- **`contract_version`**: 1 (same contract code as version 1.1)
- **`deployment_version`**: 2 (new deployment with enhanced features)

### Version Format: `contract_version.deployment_version`
- Version 1.2 = `contract_version=1, deployment_version=2`

## Key Features

### 🚀 Subname Registration System

#### Dynamic Subname Registration
- **Hierarchical Domain Support**: Create subdomains like `subdomain.domain.voi`
- **Dynamic Parent Resolution**: Automatic parent domain resolution from URL parameters
- **Payment Token Detection**: Automatic payment token selection based on parent domain
- **Multi-TLD Support**: Support for non-.voi domains and custom TLDs

#### Implementation Details
```python
# Enhanced register() method with subname support
@arc4.abimethod
def register(self, name: Bytes32, owner: arc4.Address, duration: arc4.UInt64) -> arc4.UInt256:
    # Dynamic parent domain resolution
    # Automatic payment token detection
    # Enhanced validation for hierarchical domains
```

### 🎯 Enhanced Name Management

#### NFT Minting Functionality
- **Controller-Based Minting**: NFT minting for name controllers
- **Enhanced Validation**: Improved minting process with better validation
- **ARC72 Integration**: Full integration with ARC72 NFT standard
- **Bulk Operations**: Support for bulk domain operations

#### Default Name Management
- **Primary Identity**: "Set as Default" feature for primary identity management
- **Domain Prioritization**: Enhanced domain prioritization and management
- **Transfer Mechanisms**: Improved domain transfer mechanisms
- **Expiration Handling**: Better domain expiration handling

### 🔧 Improved Contract Methods

#### Enhanced Registration Methods
- **`register()`**: Improved validation with subname support
- **`mint()`**: Enhanced method with controller support
- **`renew()`**: Improved method with better error handling
- **Utility Methods**: New utility methods for domain management

#### Controller Management
- **`approve_controller()`**: Enhanced method with better validation
- **`is_controller()`**: Improved validation with owner check
- **Permission Management**: Better controller permission management
- **Security**: Enhanced security for administrative functions

```python
@arc4.abimethod
def is_controller(self, controller: arc4.Address) -> arc4.Bool:
    return arc4.Bool(
        self.controllers.get(controller.native, default=False)
        or controller.native == self.owner
    )
```

## Technical Enhancements

### Client Library Improvements
- **Refactored VNSRegistrarClient**: Enhanced functionality and better error handling
- **Parameter Validation**: Enhanced parameter validation and error handling
- **Transaction Processing**: Improved transaction processing
- **Type Safety**: Better type safety throughout the client libraries

### Multi-Token Support
- **Dynamic Token Selection**: Support for multiple payment tokens based on parent domain
- **Payment Processing**: Enhanced payment processing for different domain types
- **Treasury Management**: Improved treasury management
- **Token Detection**: Automatic token detection during registration

## Breaking Changes

### Registration Flow Changes
- **Enhanced `register()` Method**: Now supports subname registration
- **Dynamic Payment Tokens**: Payment token selection is now dynamic based on parent domain
- **Validation Requirements**: Improved validation requirements for domain names
- **Controller Permissions**: Enhanced controller permission requirements

### Migration Impact
- **Client Updates**: Client libraries need to be updated to support new features
- **Method Signatures**: Some method calls may need parameter updates
- **Payment Logic**: Payment token handling needs to be updated for dynamic selection

## Configuration

### Contract State
```python
# Version 1.2 Configuration
self.contract_version = UInt64(1)      # Contract version
self.deployment_version = UInt64(2)    # Deployment version
self.base_cost = BigUInt(1_000_000)    # Base cost (1 USDC)
self.cost_multiplier = BigUInt(2000)   # Cost multiplier (2x)
```

### Pricing Model
- **Base Cost**: 1,000,000 units (1 USDC equivalent)
- **Cost Multiplier**: 2x (2000/1000)
- **Dynamic Pricing**: Payment token selection based on parent domain
- **Treasury Integration**: Enhanced treasury management

## Security Enhancements

### Input Validation
- **Domain Registration**: Improved input validation for domain registration
- **Parameter Sanitization**: Better parameter sanitization in registration methods
- **Payment Security**: Enhanced security in payment token selection
- **Access Control**: Improved access control for administrative functions

### Controller Security
- **Owner Check**: Controllers now include owner in validation
- **Permission Validation**: Enhanced permission validation
- **Administrative Functions**: Better security for administrative functions

## Performance Improvements

### Optimization
- **Registration Process**: Streamlined domain registration process
- **Client Performance**: Improved client library performance
- **Memory Usage**: Better memory usage in registration operations
- **Contract Execution**: Enhanced contract execution efficiency

### Scalability
- **Hierarchical Domains**: Efficient handling of multi-level domains
- **Bulk Operations**: Support for bulk domain operations
- **Dynamic Resolution**: Efficient parent domain resolution

## API Reference

### New Methods
```python
# Enhanced registration with subname support
def register(self, name: Bytes32, owner: arc4.Address, duration: arc4.UInt64) -> arc4.UInt256

# Enhanced controller validation
def is_controller(self, controller: arc4.Address) -> arc4.Bool

# Enhanced minting with controller support
def mint(self, to: arc4.Address, nodeId: Bytes32) -> arc4.UInt256
```

### Updated Methods
- **`register()`**: Enhanced with subname support and dynamic payment tokens
- **`mint()`**: Improved with controller support
- **`is_controller()`**: Enhanced with owner check
- **`renew()`**: Better error handling and validation

## Migration Guide

### From Version 1.1 to 1.2

#### Required Updates
1. **Client Library**: Update to version 1.2 compatible client
2. **Registration Logic**: Review registration method calls for new parameters
3. **Payment Handling**: Update payment token handling for dynamic selection
4. **Controller Permissions**: Verify controller permissions for administrative functions

#### Breaking Changes
- **Payment Token Selection**: Now dynamic based on parent domain
- **Registration Parameters**: Enhanced parameter requirements
- **Controller Validation**: Updated controller permission logic

### Testing Recommendations
1. **Subname Registration**: Test subname registration functionality
2. **Payment Tokens**: Verify dynamic payment token selection
3. **Controller Functions**: Test enhanced controller management
4. **Migration Path**: Validate migration from version 1.1

## Examples

### Subname Registration
```typescript
// Register a subname
const result = await registrar.register(
    namehash("subdomain.domain.voi"),
    ownerAddress,
    durationInSeconds
);
```

### Controller Management
```typescript
// Check if address is controller (includes owner check)
const isController = await registrar.isController(controllerAddress);

// Approve controller
await registrar.approveController(controllerAddress, true);
```

### Dynamic Payment Token Selection
```typescript
// Payment token automatically selected based on parent domain
const paymentToken = await registrar.getPaymentTokenForDomain(parentDomain);
```

## Troubleshooting

### Common Issues
1. **Payment Token Errors**: Ensure dynamic payment token selection is properly implemented
2. **Controller Permissions**: Verify controller permissions include owner check
3. **Subname Registration**: Check parent domain resolution and validation
4. **Migration Issues**: Ensure proper client library updates

### Debug Information
- **Contract Version**: Check `contract_version` and `deployment_version`
- **Controller Status**: Verify controller permissions and owner status
- **Payment Tokens**: Confirm dynamic token selection logic
- **Domain Validation**: Check domain name validation rules

## Support

For technical support and migration assistance:
- **Documentation**: Refer to main VNSRegistrar documentation
- **Issues**: Submit issues to the project repository
- **Community**: Join community discussions
- **Examples**: Review provided usage examples

## License

This documentation is part of the OpenSub ARC72 VNS project. Please refer to the project license for usage terms and conditions.

---

*This documentation covers VNSRegistrar Version 1.2. For other versions, please refer to the main changelog or version-specific documentation.*
