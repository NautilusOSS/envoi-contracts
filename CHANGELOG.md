# Changelog

All notable changes to the OpenSubmarine ARC72 VNS project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
