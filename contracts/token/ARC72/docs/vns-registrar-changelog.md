# VNSRegistrar Changelog

All notable changes to the VNSRegistrar contract will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses a **dual versioning system** with separate contract and deployment versions.

## Dual Versioning System

The VNSRegistrar contract uses two independent version numbers:

- **`contract_version`**: Tracks the contract code version (major functionality changes)
- **`deployment_version`**: Tracks the deployment instance version (deployment-specific updates)

### Version Format: `contract_version.deployment_version`

Examples:
- `1.0` = contract_version=1, deployment_version=0 (initial contract, first deployment)
- `1.1` = contract_version=1, deployment_version=1 (same contract, new deployment)
- `2.0` = contract_version=2, deployment_version=0 (new contract version, first deployment)

## Version History Summary

| Version | Contract Version | Deployment Version | Release Date | Key Features |
|---------|----------------|-------------------|--------------|--------------|
| 1.2 | 1 | 2 | 2025-09-18 | Subname registration, enhanced NFT minting, multi-token support |
| 1.1 | 1 | 1 | 2025-09-17 | Enhanced domain management, improved NFT integration, CLI enhancements |
| 1.0 | 0 | 0 | 2024-09-23 | Initial release with core domain registration features |

## Migration Guide

### Upgrading from 1.1 to 1.2

#### Version Changes
- **Contract Version**: 1 → 1 (same contract code)
- **Deployment Version**: 1 → 2 (new deployment with enhanced features)

#### Breaking Changes
- Enhanced `register()` method with subname support
- Dynamic payment token selection
- Improved validation requirements
- Enhanced controller permissions

#### Migration Steps
1. Update client library to support version 1.2
2. Review registration method calls for new parameters
3. Update payment token handling for dynamic selection
4. Verify controller permissions for administrative functions

### Upgrading from 1.0 to 1.1

#### Version Changes
- **Contract Version**: 0 → 1 (new contract code)
- **Deployment Version**: 0 → 1 (new deployment)

#### Changes
- Enhanced method implementations
- Improved error handling
- Better state management
- Enhanced security features

#### Migration Steps
1. Update client library to support version 1.1
2. Review method calls for enhanced functionality
3. Update error handling in applications
4. Verify security configurations

---

## [1.2] - 2025-09-18
**Contract Version: 1, Deployment Version: 2**

### 🚀 Subname Registration & Enhanced Management Release

This release introduces comprehensive subname registration capabilities, NFT minting functionality, and enhanced name management features, significantly expanding the VNS system's capabilities.

**Version Details:**
- `contract_version`: 1 (same contract code as 1.1)
- `deployment_version`: 2 (new deployment with enhanced features)

### Added

#### Subname Registration System
- **Dynamic Subname Registration**
  - Support for hierarchical subname creation (e.g., `subdomain.domain.voi`)
  - Dynamic parent domain resolution from URL parameters
  - Automatic payment token detection based on parent domain
  - Support for non-.voi domains and custom TLDs

#### Enhanced Name Management
- **NFT Minting Functionality**
  - Controller-based NFT minting for name owners
  - Enhanced minting process with improved validation
  - Integration with ARC72 NFT standard for domain tokens
  - Support for bulk domain operations

- **Default Name Management**
  - "Set as Default" feature for primary identity management
  - Enhanced domain prioritization and management
  - Improved domain transfer mechanisms
  - Better domain expiration handling

#### Improved Contract Methods
- **Enhanced Registration Methods**
  - `register()` method with improved validation
  - Enhanced `mint()` method with controller support
  - Improved `renew()` method with better error handling
  - New utility methods for domain management

- **Controller Management**
  - Enhanced `approve_controller()` method
  - Improved `is_controller()` validation with owner check
  - Better controller permission management
  - Enhanced security for administrative functions

#### Technical Enhancements
- **Client Library Improvements**
  - Refactored VNSRegistrarClient with enhanced functionality
  - Updated client methods with better error handling
  - Enhanced parameter validation and error handling
  - Improved transaction processing

- **Multi-Token Support**
  - Support for multiple payment tokens based on parent domain
  - Dynamic token selection during registration
  - Enhanced payment processing for different domain types
  - Improved treasury management

### Changed

#### Contract Method Updates
- **Breaking Changes**
  - Enhanced `register()` method with subname support
  - Payment token selection is now dynamic based on parent domain
  - Improved registration flow for hierarchical domains
  - Enhanced validation for domain names

#### State Management Improvements
- Enhanced contract state management
- Improved expiration tracking
- Better controller management
- Enhanced treasury integration

### Fixed

#### Bug Fixes
- Improved error handling in registration methods
- Enhanced parameter validation in registration flow
- Better domain expiration handling
- Fixed edge cases in subname registration process
- Improved payment processing reliability

### Security

#### Enhanced Validation
- Improved input validation for domain registration
- Better parameter sanitization in registration methods
- Enhanced security in payment token selection
- Improved access control for administrative functions

### Performance

#### Optimization Improvements
- Streamlined domain registration process
- Improved client library performance
- Better memory usage in registration operations
- Enhanced contract execution efficiency

### Breaking Changes

#### Registration Flow Changes
- Enhanced `register()` method with subname support
- Payment token selection is now dynamic based on parent domain
- Improved validation requirements for domain names
- Enhanced controller permission requirements

## [1.1] - 2025-09-17
**Contract Version: 1, Deployment Version: 1**

### 🚀 Major System Enhancement Release

This release represents a significant enhancement to the VNS (Voi Name Service) system, introducing new functionality, improved usability, and comprehensive documentation updates.

**Version Details:**
- `contract_version`: 1 (new contract code with enhanced functionality)
- `deployment_version`: 1 (first deployment of contract version 1)

### Added

#### Enhanced VNS Registrar Contract
- **Controller Management System**
  - `approve_controller(address, bool)` - Fine-grained access control for controllers
  - `is_controller(address)` - Check controller approval status
  - Enhanced security and permission management

- **Improved Domain Management**
  - `get_root_node()` - Retrieve root node information
  - `get_root_node_name()` - Get root node name
  - `get_registry()` - Get registry address
  - `get_payment_token()` - Get payment token ID
  - Enhanced domain lifecycle visibility

- **Treasury and Configuration Management**
  - `set_grace_period(uint64)` - Configurable grace period for expired domains
  - `set_treasury(address)` - Treasury address management for fee collection
  - `set_version(uint64, uint64)` - Contract version management
  - Better administrative controls

- **Simplified Operations**
  - Streamlined `mint(address, byte[32])` - Simplified domain minting with cleaner parameters
  - Simplified `post_update()` - Streamlined update method signature
  - Enhanced `set_tokenURI(uint256, byte[256])` - Improved metadata management

#### Expanded CLI Tooling
- **New Registrar Commands**
  - `set-version` - Contract version management
  - `approve-controller` / `is-controller` - Controller access management
  - `set-grace-period` - Grace period configuration
  - `mint` - Simplified domain minting
  - `get-root-node` / `get-root-node-name` - Root node information
  - `expiration` / `reclaim` - Domain lifecycle management
  - `get-app-id` - Application ID resolution
  - `set-registry` / `owner-of` - Registry operations
  - `token-uri` - ARC72 metadata access

- **Enhanced Command Features**
  - Improved error handling and debug output
  - Better parameter validation
  - Enhanced simulation mode support
  - Comprehensive help documentation

#### Comprehensive Documentation Overhaul
- **Complete README Rewrite**
  - Professional documentation with usage examples
  - Architecture overview and quick start guide
  - Comprehensive feature descriptions
  - API reference and examples

- **New Documentation Suite**
  - `docs/index.md` - Complete system overview
  - `docs/REGISTRAR.md` - Detailed registrar documentation  
  - `docs/CLI_SUBNAME_GUIDE.md` - Step-by-step CLI usage guide

- **Enhanced Documentation Features**
  - Detailed usage examples and parameter descriptions
  - Complete subname creation workflow documentation
  - Troubleshooting guides and best practices
  - Code examples and integration guides

#### Technical Improvements
- **Updated Client Libraries**
  - All TypeScript client interfaces updated to match contract changes
  - JavaScript client libraries synchronized
  - Enhanced type safety and parameter validation
  - Improved error handling throughout

- **Code Quality Enhancements**
  - Refactored client code for better maintainability
  - Improved parameter validation and type checking
  - Enhanced debug output and error reporting
  - Better code organization and documentation

### Changed

#### Contract Method Signatures
- **Breaking Changes**
  - `mint()` method signature simplified (removed `nodeName` parameter)
  - `post_update()` method signature streamlined (removed parameters)
  - Some CLI command parameters updated for consistency

#### CLI Command Updates
- Enhanced parameter validation across all commands
- Improved error messages and debug output
- Better simulation mode support
- Updated help documentation

#### Documentation Structure
- Complete README overhaul with professional formatting
- Enhanced documentation organization
- Improved code examples and usage patterns
- Better cross-referencing between documents

### Fixed

#### Bug Fixes
- Improved error handling in CLI commands
- Enhanced parameter validation
- Better type safety in client libraries
- Fixed edge cases in domain management operations

### Security

#### Access Control Improvements
- Enhanced controller management system
- Better permission validation
- Improved security in administrative functions
- Enhanced treasury management security

### Performance

#### Optimization Improvements
- Streamlined contract method signatures
- Improved client library performance
- Enhanced CLI command execution speed
- Better memory usage in client operations

### Breaking Changes

#### Contract Changes
- `mint(address, byte[32], string)` → `mint(address, byte[32])` - Removed `nodeName` parameter
- `post_update(uint64, byte[32], uint64)` → `post_update()` - Simplified signature

#### CLI Changes
- Some command parameters may have changed - see updated documentation
- Enhanced parameter validation may require updated command usage

### Migration Guide

#### For Contract Users
- Update client code to use new method signatures
- Review controller management implementation
- Update administrative function calls

#### For CLI Users
- Review updated command documentation
- Update scripts using modified commands
- Test commands in simulation mode first

### Dependencies

#### Updated Dependencies
- Enhanced TypeScript client libraries
- Updated JavaScript client libraries
- Improved CLI tooling dependencies

### Known Issues

#### Resolved Issues
- Fixed parameter validation edge cases
- Improved error handling in CLI commands
- Enhanced type safety in client libraries

### Deprecations

#### Deprecated Features
- Old `mint()` method signature (use new simplified version)
- Old `post_update()` method signature (use new simplified version)

## [1.0] - 2024-09-23
**Contract Version: 0, Deployment Version: 0**

### 🎉 Initial Release

This is the initial release of the VNSRegistrar contract, providing comprehensive domain name registration and management capabilities for the Voi Name Service (VNS) system.

**Version Details:**
- `contract_version`: 0 (initial contract code)
- `deployment_version`: 0 (initial deployment)

### Added

#### Core Domain Registration
- **Domain Registration System**
  - `register()` method for domain registration
  - Support for hierarchical domain structure
  - Dynamic pricing based on domain length
  - Configurable registration duration

#### Domain Management
- **Domain Lifecycle Management**
  - `renew()` method for domain renewal
  - `expiration()` method for expiration tracking
  - `is_expired()` method for expiration checking
  - `reclaim()` and `reclaimExpiredName()` for domain recovery

#### NFT Integration
- **ARC72 NFT Support**
  - Full ARC72 standard implementation
  - Domain NFTs with unique token IDs
  - Transferable domain ownership
  - NFT metadata and URI support

#### Payment System
- **Dual Payment Model**
  - VOI payment for storage costs
  - ARC200 token payment for registration fees
  - Configurable treasury address
  - Dynamic pricing system

#### Controller Management
- **Administrative Controls**
  - `approve_controller()` for controller management
  - `is_controller()` for permission checking
  - Controller-based domain minting
  - Enhanced administrative security

#### Utility Methods
- **Domain Validation**
  - `check_name()` for domain name validation
  - `get_length()` for name length calculation
  - `get_price()` for cost calculation
  - Enhanced validation rules

#### Configuration Methods
- **Contract Configuration**
  - `setResolver()` for resolver configuration
  - `setRootNode()` for root node management
  - `setPaymentToken()` for payment token setup
  - `setGracePeriod()` for grace period configuration

#### Integration Features
- **VNS System Integration**
  - VNS Registry integration
  - VNS Resolver integration
  - ARC200 token integration
  - Reverse Registrar support

#### Events
- **Event System**
  - `NameRegistered` event
  - `NameRenewed` event
  - `NameReclaimed` event
  - `ControllerApproved` event

#### Security Features
- **Security Controls**
  - Access control for administrative functions
  - Payment validation
  - Input sanitization
  - Contract upgrade safety

#### Testing
- **Comprehensive Testing**
  - Unit tests for all methods
  - Integration tests for workflows
  - Edge case testing
  - Performance testing

### Technical Specifications

#### Contract Architecture
- Inherits from ARC72Token, Upgradeable, and Stakeable
- Uses Algorand Box storage for efficient data management
- Implements ARC72 NFT standard for domain tokens
- Supports controlled contract upgrades

#### Pricing Model
- Base cost: 1 USDC equivalent
- Cost multiplier: 5x for premium domains
- Length-based pricing for shorter domains
- Duration-based pricing scaling

#### State Management
- Treasury address for fee collection
- Registry contract ID for DNS management
- Payment token ID for fee processing
- Root node configuration
- Grace period management
- Controller permissions
- Domain expiration tracking

---

## Support

For migration assistance and technical support:

- **Documentation**: Check the [VNSRegistrar Documentation](vns-registrar.md)
- **Issues**: Submit issues to the project repository
- **Community**: Join community discussions
- **Examples**: Review provided usage examples

## License

This changelog is part of the OpenSub ARC72 VNS project. Please refer to the project license for usage terms and conditions.

---

*This changelog is maintained as part of the OpenSub ARC72 VNS project. For the most up-to-date information, please refer to the project repository.*
