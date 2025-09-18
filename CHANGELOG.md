# Changelog

All notable changes to the OpenSubmarine ARC72 VNS project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-09-18

### 🎯 Subname Registration & Enhanced Management Release

This release introduces comprehensive subname registration capabilities, NFT minting functionality, and enhanced name management features, significantly expanding the VNS system's capabilities.

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
  - MintModal component for streamlined minting process
  - Integration with ARC72 NFT standard for domain tokens

- **Default Name Management**
  - "Set as Default" feature for primary identity management
  - ConfirmSetDefaultModal for setting primary domain
  - Enhanced user experience for name prioritization

#### Improved User Interface
- **Enhanced ProfilePage Components**
  - New ConfirmSetDefaultModal for setting primary identity
  - Improved MintModal for controller-based NFT minting
  - Enhanced TransferModal with better UX and validation
  - Better dark mode styling and UI consistency

- **Dynamic Registration Flow**
  - New route support for subname registration (`/register/:name/:subname`)
  - Dynamic parent name resolution from URL parameters
  - Automatic payment token selection per parent domain
  - Improved registration workflow for subnames

#### Technical Enhancements
- **Client Library Improvements**
  - Refactored VNSRegistrarClient with enhanced functionality
  - Updated ConnectWallet component with better error handling
  - Enhanced useNameRegistration hook with new features
  - Improved parameter validation and error handling

- **Multi-Token Support**
  - Support for multiple payment tokens based on parent domain
  - Dynamic token selection during registration
  - Enhanced payment processing for different domain types

### Changed

#### Registration System Updates
- **Breaking Changes**
  - RegisterName component now supports subname registration via URL params
  - Payment token selection is now dynamic based on parent domain
  - Enhanced registration flow for hierarchical domains

#### User Interface Improvements
- Enhanced dark mode styling across all components
- Improved modal components with better UX
- Better error handling and user feedback
- Streamlined registration process for subnames

### Fixed

#### Bug Fixes
- Improved error handling in ConnectWallet component
- Enhanced parameter validation in registration flow
- Better UI consistency across dark/light modes
- Fixed edge cases in subname registration process

### Security

#### Enhanced Validation
- Improved input validation for subname registration
- Better parameter sanitization in URL-based registration
- Enhanced security in payment token selection

### Performance

#### Optimization Improvements
- Streamlined subname registration process
- Improved client library performance
- Better memory usage in registration operations
- Enhanced UI responsiveness

### Breaking Changes

#### Registration Flow Changes
- RegisterName now supports subname registration via URL params
- Payment token selection is now dynamic based on parent domain
- Enhanced parameter requirements for subname registration

### Migration Guide

#### For Frontend Users
- Update registration URLs to support subname parameters
- Review payment token selection logic for dynamic domains
- Test subname registration flow in development environment

#### For Contract Users
- Review subname registration implementation
- Update client code for enhanced registration functionality
- Test multi-token payment scenarios

### Dependencies

#### Updated Dependencies
- Enhanced client libraries for subname support
- Updated UI components for better UX
- Improved error handling libraries

### Known Issues

#### Resolved Issues
- Fixed subname registration edge cases
- Improved error handling in registration flow
- Enhanced UI consistency across components

---

## [1.1.0] - 2025-01-17

### 🚀 Major System Enhancement Release

This release represents a significant enhancement to the VNS (Voi Name Service) system, introducing new functionality, improved usability, and comprehensive documentation updates.

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

---

## [1.0.0] - 2025-01-XX

### 🎉 Initial Release - Complete Decentralized Naming System

This release marks the first stable version of OpenSubmarine ARC72 VNS, a comprehensive decentralized naming service built on the Algorand blockchain using ARC72 (NFT) and ARC200 (Token) standards.

### Added

#### Core Smart Contracts
- **VNS Registry Contract** (`VNSRegistry`)
  - Domain ownership management
  - Subdomain delegation system
  - Resolver assignment functionality
  - TTL (Time To Live) management
  - Owner transfer capabilities

- **VNS Public Resolver Contract** (`VNSPublicResolver`)
  - Address resolution (domain → address)
  - Reverse resolution (address → domain)
  - Text record management
  - Multi-address support
  - Record validation and storage

- **VNS Registrar Contract** (`VNSRegistrar`)
  - Domain registration with dynamic pricing
  - ARC72 NFT integration for domains
  - Domain renewal and expiration management
  - Grace period handling (90 days default)
  - Domain reclamation for expired names
  - Hierarchical domain structure support

- **Reverse Registrar Contract** (`ReverseRegistrar`)
  - Reverse domain resolution
  - Address-to-domain mapping
  - Reverse domain management

- **Collection Registrar Contract** (`CollectionRegistrar`)
  - Bulk domain operations
  - Collection management
  - Batch registration capabilities

- **Staking Registrar Contract** (`StakingRegistrar`)
  - Token staking mechanisms
  - Governance participation
  - Staking rewards and delegation

- **RSVP Contract** (`VNSRSVP`)
  - Domain reservation system
  - Pre-registration management
  - Admin reservation controls
  - Reservation pricing

#### Token Integration
- **ARC200 Token Contract** (`ARC200Token`)
  - Standard ERC-20 equivalent for Algorand
  - Payment token for domain registration
  - Transfer, approve, and allowance functionality
  - Balance tracking and management

- **ARC200 Token Factory Contract** (`ARC200TokenFactory`)
  - Factory pattern for creating new tokens
  - Token deployment and configuration
  - Factory management capabilities

#### Base Contracts and Interfaces
- **Ownable Contract** (`Ownable`)
  - Ownership management
  - Owner transfer functionality
  - Access control mechanisms

- **Upgradeable Contract** (`Upgradeable`)
  - Controlled contract upgrades
  - Upgrade approval processes
  - Version management

- **Stakeable Contract** (`Stakeable`)
  - Staking functionality
  - Delegation mechanisms
  - Stake management

#### CLI Tools and Scripts
- **Command Line Interface** (`command.ts`)
  - Complete CLI for all contract operations
  - Domain registration commands
  - Resolution and management tools
  - Token operation commands
  - RSVP management commands
  - Debug and simulation modes

- **Client Libraries**
  - TypeScript client libraries for all contracts
  - JavaScript client libraries
  - Generated client code for easy integration

#### Testing Framework
- **Comprehensive Test Suite**
  - Registry functionality tests
  - Resolver operation tests
  - Registrar registration and renewal tests
  - ARC200 token operation tests
  - RSVP reservation system tests
  - Integration tests for all components
  - Mocha and Chai testing frameworks

#### Documentation
- **Main Documentation** (`docs/index.md`)
  - Complete system overview
  - Architecture documentation
  - API reference
  - Usage examples

- **Registrar Guide** (`docs/REGISTRAR.md`)
  - Detailed registrar documentation
  - Pricing model explanation
  - Domain lifecycle management
  - Configuration instructions

- **CLI Subname Guide** (`docs/CLI_SUBNAME_GUIDE.md`)
  - Step-by-step CLI usage
  - Subname creation examples
  - Troubleshooting guide
  - Best practices

### Features

#### Domain Registration System
- **Hierarchical Domain Structure**
  - Multi-level domain support (e.g., `subdomain.domain.tld`)
  - Root domain management
  - Subdomain delegation

- **Dynamic Pricing Model**
  - Length-based pricing (1-32x multiplier)
  - Duration-based pricing
  - Treasury fee collection
  - Configurable pricing parameters

- **Domain Lifecycle Management**
  - Registration with expiration tracking
  - Renewal capabilities
  - Grace period handling
  - Expired domain reclamation

#### NFT Integration
- **ARC72 Compliance**
  - Domains as transferable NFTs
  - Unique token IDs for each domain
  - Metadata support
  - Enumeration capabilities

- **Transfer Management**
  - Controlled domain transfers
  - Ownership validation
  - Transfer approval mechanisms

#### Resolution System
- **Address Resolution**
  - Domain-to-address mapping
  - Multi-address support
  - Address validation

- **Reverse Resolution**
  - Address-to-domain mapping
  - Reverse lookup capabilities
  - Reverse domain management

- **Text Records**
  - Arbitrary text data storage
  - Key-value record system
  - Record validation and retrieval

#### Payment System
- **Dual Payment Model**
  - VOI for storage costs (336,700 microVOI)
  - ARC200 tokens for registration fees
  - Secure payment processing

- **Treasury Management**
  - Fee collection and distribution
  - Configurable treasury addresses
  - Payment validation

#### Security Features
- **Access Control**
  - Role-based permissions
  - Owner-only operations
  - Controller management

- **Domain Validation**
  - Name format validation (alphanumeric + hyphens)
  - Length restrictions (1-32 characters)
  - Invalid character prevention

- **Payment Security**
  - Token approval requirements
  - Payment amount validation
  - Secure fee collection

#### Governance and Staking
- **Staking Mechanisms**
  - Token staking for governance
  - Delegation capabilities
  - Stake management

- **Upgrade Management**
  - Controlled contract upgrades
  - Upgrade approval processes
  - Version tracking

### Technical Specifications

#### Contract Standards
- **ARC72 Compliance**: Full NFT standard implementation
- **ARC200 Compliance**: ERC-20 equivalent token standard
- **ARC4 Compliance**: Algorand Python contract standard

#### Development Tools
- **Algorand Python**: Smart contract development
- **TypeScript/JavaScript**: Client library development
- **Node.js**: CLI tooling and testing
- **Mocha/Chai**: Testing framework

#### Deployment
- **Algorand Testnet**: Development and testing
- **Algorand Mainnet**: Production deployment ready
- **Docker Support**: Containerized development environment

### Configuration

#### Environment Variables
- `MN`, `MN2`, `MN3`: Test account mnemonics
- Contract addresses and configuration parameters
- Network-specific settings

#### Pricing Configuration
- Base cost: 1,000,000 units (1 USDC equivalent)
- Cost multiplier: 5x
- Base period: 365 days (1 year)
- Grace period: 90 days

### Performance

#### Gas Optimization
- Efficient storage patterns
- Optimized contract calls
- Minimal transaction costs

#### Scalability
- Hierarchical domain structure
- Efficient resolution algorithms
- Batch operation support

### Security Audit

#### Code Review
- Comprehensive code review completed
- Security best practices implemented
- Access control validation
- Payment security verification

#### Testing Coverage
- Unit tests for all contract functions
- Integration tests for system components
- Edge case testing
- Security vulnerability testing

### Breaking Changes
- None (initial release)

### Dependencies
- Algorand Python
- ARC4 Contract Framework
- Node.js and npm/pnpm
- TypeScript
- Mocha and Chai testing frameworks

### Migration Guide
- N/A (initial release)

### Known Issues
- None identified at release

### Deprecations
- None (initial release)

---

## Version History

- **v1.1.1**: Subname registration & enhanced management release
  - Comprehensive subname registration capabilities
  - NFT minting functionality for name controllers
  - Enhanced name management with "Set as Default" feature
  - Dynamic payment token support based on parent domain
  - Improved UI components and dark mode styling
  - Enhanced client libraries and error handling

- **v1.1.0**: Major system enhancement release
  - Enhanced VNS Registrar contract with controller management
  - Expanded CLI tooling with new registrar commands
  - Comprehensive documentation overhaul
  - Improved client libraries and type safety
  - Better error handling and debug capabilities

- **v1.0.0**: Initial stable release with complete VNS functionality
  - Full ARC72 NFT integration
  - Complete CLI tooling
  - Comprehensive test coverage
  - Production-ready smart contracts
  - Complete documentation suite

---

## Contributing

When adding new features or making changes, please update this changelog following the format above. Include:
- Clear descriptions of what was added, changed, or removed
- Breaking changes and migration instructions
- Security updates and fixes
- Performance improvements
- Documentation updates
