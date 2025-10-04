# ARC72 Token Contract Documentation

## Overview

The ARC72 Token Contract is a comprehensive implementation of the ARC72 (NFT) standard for the Algorand blockchain, specifically designed for the Voi Name Service (VNS) system. This contract provides full NFT functionality including ownership, transfer management, metadata, and enumeration capabilities, while also integrating ARC200 token functionality for payment processing.

## Architecture

The contract is built using a modular architecture with multiple interfaces and implementations:

### Core Interfaces

1. **ARC72TokenCoreInterface** - Basic NFT ownership and transfer functionality
2. **ARC72TokenMetadataInterface** - Token metadata and URI management
3. **ARC72TokenTransferManagementInterface** - Approval and transfer control mechanisms
4. **ARC72TokenEnumerationInterface** - Token enumeration and balance tracking
5. **ARC73SupportsInterface** - Interface detection and compatibility
6. **ARC200TokenInterface** - Token functionality for payments

### Additional Features

- **Ownable** - Contract ownership management
- **Stakeable** - Staking and delegation capabilities
- **Upgradeable** - Contract upgrade management
- **ARC200 Integration** - Payment token functionality

## Key Features

### NFT Functionality (ARC72)

- **Token Ownership**: Track and manage NFT ownership
- **Transfer Management**: Controlled transfers with approval mechanisms
- **Metadata Support**: Rich metadata with URI support
- **Enumeration**: Balance tracking and token indexing
- **Interface Detection**: ARC73 compatibility for interface detection

### Payment Integration (ARC200)

- **Token Transfers**: Standard token transfer functionality
- **Approval System**: Spender approval for token transfers
- **Balance Management**: Account balance tracking
- **Supply Management**: Total supply and minting capabilities

### Advanced Features

- **Staking Support**: Delegate management and participation
- **Upgrade Management**: Controlled contract upgrades
- **Ownership Control**: Multi-level ownership and control
- **Box Storage**: Efficient data storage using Algorand boxes

## Contract Methods

### ARC72 Core Methods

#### `arc72_ownerOf(tokenId: UInt256) -> Address`
Returns the owner of a specific token ID.

**Parameters:**
- `tokenId`: The unique identifier of the token

**Returns:**
- `Address`: The address of the token owner

#### `arc72_transferFrom(from: Address, to: Address, tokenId: UInt256)`
Transfers a token from one address to another.

**Parameters:**
- `from`: Current owner of the token
- `to`: New owner of the token
- `tokenId`: The token to transfer

### ARC72 Metadata Methods

#### `arc72_tokenURI(tokenId: UInt256) -> Bytes256`
Returns the metadata URI for a specific token.

**Parameters:**
- `tokenId`: The token ID to get metadata for

**Returns:**
- `Bytes256`: The metadata URI

### ARC72 Transfer Management

#### `arc72_approve(approved: Address, tokenId: UInt256)`
Approves another address to transfer a specific token.

**Parameters:**
- `approved`: Address to approve for transfer
- `tokenId`: Token to approve for transfer

#### `arc72_setApprovalForAll(operator: Address, approved: Bool)`
Sets approval for all tokens owned by the caller.

**Parameters:**
- `operator`: Address to approve/disapprove
- `approved`: True to approve, false to revoke

#### `arc72_getApproved(tokenId: UInt256) -> Address`
Gets the approved address for a specific token.

**Parameters:**
- `tokenId`: Token to check approval for

**Returns:**
- `Address`: Approved address (zero address if none)

#### `arc72_isApprovedForAll(owner: Address, operator: Address) -> Bool`
Checks if an operator is approved for all tokens of an owner.

**Parameters:**
- `owner`: Token owner address
- `operator`: Operator address to check

**Returns:**
- `Bool`: True if approved for all tokens

### ARC72 Enumeration

#### `arc72_balanceOf(owner: Address) -> UInt256`
Returns the number of tokens owned by an address.

**Parameters:**
- `owner`: Address to check balance for

**Returns:**
- `UInt256`: Number of tokens owned

#### `arc72_totalSupply() -> UInt256`
Returns the total number of tokens in existence.

**Returns:**
- `UInt256`: Total token supply

#### `arc72_tokenByIndex(index: UInt256) -> UInt256`
Returns the token ID at a given index.

**Parameters:**
- `index`: Index position

**Returns:**
- `UInt256`: Token ID at the index

#### `arc72_tokenOfOwnerByIndex(owner: Address, index: UInt256) -> UInt256`
Returns the token ID owned by an address at a given index.

**Parameters:**
- `owner`: Token owner address
- `index`: Index position

**Returns:**
- `UInt256`: Token ID at the index

### ARC200 Token Methods

#### `arc200_transfer(recipient: Address, amount: UInt256) -> Bool`
Transfers tokens to another address.

**Parameters:**
- `recipient`: Address to receive tokens
- `amount`: Amount of tokens to transfer

**Returns:**
- `Bool`: Success status

#### `arc200_transferFrom(sender: Address, recipient: Address, amount: UInt256) -> Bool`
Transfers tokens from one address to another (with approval).

**Parameters:**
- `sender`: Address to transfer from
- `recipient`: Address to transfer to
- `amount`: Amount of tokens to transfer

**Returns:**
- `Bool`: Success status

#### `arc200_approve(spender: Address, amount: UInt256) -> Bool`
Approves another address to spend tokens.

**Parameters:**
- `spender`: Address to approve
- `amount`: Amount to approve

**Returns:**
- `Bool`: Success status

#### `arc200_balanceOf(account: Address) -> UInt256`
Returns the token balance of an account.

**Parameters:**
- `account`: Address to check balance for

**Returns:**
- `UInt256`: Token balance

#### `arc200_totalSupply() -> UInt256`
Returns the total token supply.

**Returns:**
- `UInt256`: Total supply

### Ownership and Management

#### `transfer(new_owner: Address)`
Transfers contract ownership to a new address.

**Parameters:**
- `new_owner`: New owner address

#### `set_delegate(delegate: Address)`
Sets a delegate for staking operations.

**Parameters:**
- `delegate`: Delegate address

#### `participate(vote_key: Bytes32, selection_key: Bytes32, vote_first: UInt64, vote_last: UInt64, vote_key_dilution: UInt64, state_proof_key: Bytes64)`
Participates in consensus with the provided keys.

**Parameters:**
- `vote_key`: Voting key
- `selection_key`: Selection key
- `vote_first`: First voting round
- `vote_last`: Last voting round
- `vote_key_dilution`: Key dilution parameter
- `state_proof_key`: State proof key

### Upgrade Management

#### `set_version(contract_version: UInt64, deployment_version: UInt64)`
Sets the contract and deployment versions.

**Parameters:**
- `contract_version`: Contract version number
- `deployment_version`: Deployment version number

#### `approve_update(approval: Bool)`
Approves or denies contract updates.

**Parameters:**
- `approval`: True to approve updates, false to deny

#### `grant_upgrader(upgrader: Address)`
Grants upgrade permissions to an address.

**Parameters:**
- `upgrader`: Address to grant upgrade permissions

## Usage Examples

### Basic Token Operations

```typescript
// Check token ownership
const owner = await contract.arc72_ownerOf(tokenId);

// Transfer a token
await contract.arc72_transferFrom(fromAddress, toAddress, tokenId);

// Approve token transfer
await contract.arc72_approve(approvedAddress, tokenId);

// Check token balance
const balance = await contract.arc72_balanceOf(ownerAddress);
```

### Payment Token Operations

```typescript
// Transfer payment tokens
await contract.arc200_transfer(recipientAddress, amount);

// Approve token spending
await contract.arc200_approve(spenderAddress, amount);

// Check token balance
const balance = await contract.arc200_balanceOf(accountAddress);
```

### Metadata Operations

```typescript
// Get token metadata URI
const tokenURI = await contract.arc72_tokenURI(tokenId);

// Check interface support
const supportsInterface = await contract.supportsInterface(interfaceId);
```

## Integration Guide

### Prerequisites

- Algorand SDK (algosdk)
- Contract deployment and configuration
- Proper account setup with sufficient ALGO for transaction fees

### Contract Deployment

1. Deploy the contract using the provided deployment scripts
2. Configure initial parameters (owner, upgrader, etc.)
3. Set up payment token integration if needed

### Client Integration

```typescript
import { Osarc72TokenClient } from './clients/OSARC72TokenClient';

// Initialize client
const client = new Osarc72TokenClient({
  resolveBy: 'id',
  id: contractId,
  sender: senderAccount
});

// Use contract methods
const result = await client.arc72_ownerOf({ tokenId });
```

## Security Considerations

- **Access Control**: Only authorized addresses can perform administrative functions
- **Transfer Validation**: All transfers are validated for proper authorization
- **Upgrade Safety**: Contract upgrades require multiple approvals
- **Box Storage**: Efficient and secure data storage using Algorand boxes

## Events

The contract emits several events for tracking important state changes:

- `OwnershipTransferred`: When contract ownership changes
- `DelegateUpdated`: When delegate information is updated
- `Transfer`: When tokens are transferred
- `Approval`: When token approvals are granted/revoked

## Error Handling

The contract includes comprehensive error handling with descriptive error messages:

- `"must be owner"`: Unauthorized access to owner-only functions
- `"must be upgrader"`: Unauthorized access to upgrade functions
- `"invalid token"`: Invalid token ID or operation
- `"insufficient balance"`: Insufficient token balance for operation

## Testing

The contract includes comprehensive test coverage:

- Unit tests for all major functions
- Integration tests for complex workflows
- Edge case testing for error conditions
- Performance testing for gas optimization

Run tests using:
```bash
arc72-pytest
```

## Deployment

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

## Support

For technical support and questions:

- Check the main project documentation
- Review the contract source code
- Submit issues to the project repository
- Join the community discussions

## VNSRegistrar Contract

The VNSRegistrar is a specialized implementation of the ARC72 Token Contract designed specifically for domain name registration in the Voi Name Service (VNS) system. It extends the base ARC72 functionality to create domain NFTs that can be registered, renewed, and transferred.

For comprehensive documentation on VNSRegistrar, including detailed method descriptions, usage examples, and integration guides, please see the dedicated [VNSRegistrar Documentation](vns-registrar.md).

### Quick Overview

VNSRegistrar inherits from:
- **ARC72Token**: Core NFT functionality
- **Upgradeable**: Contract upgrade management  
- **Stakeable**: Staking and delegation capabilities

This creates a comprehensive domain management system where each registered domain becomes a transferable NFT with built-in expiration and renewal mechanisms.

### Key Features

- **Domain Registration**: Hierarchical structure with NFT integration
- **Dynamic Pricing**: Cost varies based on domain length and duration
- **Expiration Management**: Built-in expiration tracking with grace periods
- **Payment System**: Dual payment (VOI + ARC200 tokens)
- **Controller System**: Authorized controllers for administrative functions

## License

This contract is part of the OpenSub ARC72 VNS project. Please refer to the project license for usage terms and conditions.
