# Creating Subnames Using CLI

This guide walks through the complete process of creating subnames using the command-line interface. The example demonstrates creating a subname `shelly` under the root domain `founder.voi`.

## Prerequisites

- Node.js environment with the CLI tools installed
- Access to Algorand testnet or mainnet
- Sufficient ALGO for transaction fees
- Payment tokens for registration fees

## TLDR - Quick Reference

For experienced users who want a compact version:

```bash
# 1. Deploy registrar
node main.js deploy -t vns-registrar -n vns-registrar-founder.voi

# 2. Configure registrar
node main.js vns set-owner --apid 797607 --node founder.voi --owner JLP2X7HEH3AJZ7IXE7AHNC2QAXG3PKUQMXZFGHTO4V3Y5EKFGIWC6BETTA  # Registrar app address
node main.js registrar get-app-id --apid 797607 --name founder.voi  # Get registrar app ID
node main.js registrar set-registry --apid 45291944 --registry 797607
node main.js registrar set-root-node --apid 45291944 --root-node founder.voi
node main.js registrar set-payment-token --apid 45291944 --payment-token 302222

# 3. Mint subname
node main.js registrar mint --apid 45291944 --to BRB3JP4LIW5Q755FJCGVAOA4W3THJ7BR3K6F26EVCGMETLEAZOQRHHJNLQ --name shelly

# 4. Reclaim for resolver access
node main.js registrar reclaim --apid 45291944 --name shelly

# 5. Use resolver
node main.js resolver set-text --apid 797608 --node shelly.founder.voi --key msg --value "hello world"
node main.js resolver get-text --apid 797608 --node shelly.founder.voi --key msg
```

**Key App IDs**: Registry: `797607`, Registrar: `45291944`, Payment Token: `302222`, Resolver: `797608`

## Step-by-Step Process

### 1. Deploy Registrar Contract

First, deploy the VNS registrar contract. The name parameter should match your parent domain for consistency:

```bash
node main.js deploy -t vns-registrar -n vns-registrar-founder.voi
```

This command deploys a new registrar contract and returns an application ID (e.g., `45291944`). Save this ID as you'll need it for subsequent steps.

**Note**: Replace `founder.voi` with your actual parent domain name. The registrar name should follow the pattern `vns-registrar-{parent-domain}` for consistency.

### 2. Configure Registrar Settings

The registrar needs to be properly configured before it can handle registrations.

#### 2.0 Set Owner in Registry

Set the registrar as the owner of the root domain in the VNS registry (797607 is the registry app ID, JLP2X7HEH3AJZ7IXE7AHNC2QAXG3PKUQMXZFGHTO4V3Y5EKFGIWC6BETTA is the registrar app address):

```bash
node main.js vns set-owner --apid 797607 --node founder.voi --owner JLP2X7HEH3AJZ7IXE7AHNC2QAXG3PKUQMXZFGHTO4V3Y5EKFGIWC6BETTA
```

Get the registrar's application ID:

```bash
node main.js registrar get-app-id --apid 797607 --name founder.voi
```

This should return the registrar's app ID (e.g., `45291944`).

#### 2.1 Set Registry Reference

Configure the registrar to reference the VNS registry (797607 is the registry app ID):

```bash
node main.js registrar set-registry --apid 45291944 --registry 797607
```

#### 2.2 Set Root Node

Set the root domain that this registrar will manage:

```bash
node main.js registrar set-root-node --apid 45291944 --root-node founder.voi
```

#### 2.3 Set Payment Token

Configure the payment token for registration fees (302222 is the Voi Founder Token app ID):

```bash
node main.js registrar set-payment-token --apid 45291944 --payment-token 302222
```

### 3. Mint and Verify Subname

#### 3.1 Mint Subname

Register a new subname (e.g., `shelly`):

```bash
node main.js registrar mint --apid 45291944 --to BRB3JP4LIW5Q755FJCGVAOA4W3THJ7BR3K6F26EVCGMETLEAZOQRHHJNLQ --name shelly
```

This command:

- Creates the subname `shelly.founder.voi`
- Assigns ownership to the specified address
- **Note**: `mint` does not charge registration fees and can only be used by authorized controllers

#### 3.2 Verify Ownership

Verify that the subname was successfully registered:

```bash
node main.js registrar owner-of --apid 45291944 --name shelly.founder.voi
```

This should return the owner address that was specified in the mint command.

### 4. Reclaim Subname (Required for Resolver)

Reclaim syncs the registry with the owner of the NFT. This must be called by the owner of the name and is required to utilize the resolver to set key-value pairs such as those holding avatar or Twitter handle in profile:

#### 4.1 Check Current Owner

First, check who currently owns the subname in the VNS registry (797607 is the registry app ID):

```bash
node main.js vns owner-of --apid 797607 --node shelly.founder.voi
```

This will return the current owner address.

#### 4.2 Reclaim Ownership

Sync the registry with the NFT owner (must be called by the name owner):

```bash
node main.js registrar reclaim --apid 45291944 --name shelly
```

#### 4.3 Verify Reclaim

Verify that the registry has been synced with the NFT owner (797607 is the registry app ID):

```bash
node main.js vns owner-of --apid 797607 --node shelly.founder.voi
```

### 5. Use Resolver

After reclaiming the subname, you can use the resolver to set and get name and text values:

#### 5.0 Set Name

Set the name record for the subname (797608 is the resolver app ID):

```bash
node main.js resolver set-name --apid 797608 --node shelly.founder.voi --name shelly.founder.voi
```

#### 5.0 Get Name

Retrieve the name record from the subname:

```bash
node main.js resolver get-name --apid 797608 --node shelly.founder.voi
```

#### 5.1 Set Text Value

Set a text record for the subname (797608 is the resolver app ID):

```bash
node main.js resolver set-text --apid 797608 --node shelly.founder.voi --key msg --value "hello world"
```

#### 5.2 Get Text Value

Retrieve a text record from the subname:

```bash
node main.js resolver get-text --apid 797608 --node shelly.founder.voi --key msg
```

This should now return the NFT owner's address instead of the registrar's address.

## Important Notes

- **Application IDs**: Replace the example application IDs (`45291944`, `797607`, `302222`) with your actual deployed contract IDs
  - `797607` is the VNS registry app ID (used in vns commands)
  - `45291944` is the registrar app ID (used in registrar commands)
  - `302222` is the Voi Founder Token app ID (payment token)
- **Application Addresses**: Replace the example addresses with your actual addresses
  - `JLP2X7HEH3AJZ7IXE7AHNC2QAXG3PKUQMXZFGHTO4V3Y5EKFGIWC6BETTA` is the registrar app address (returned from deploy command)
- **Addresses**: Replace the example addresses with your actual Algorand addresses
- **Payment Tokens**: Ensure you have sufficient balance of the payment token before attempting registration
- **Transaction Fees**: Each command requires ALGO for transaction fees
- **Network**: Make sure you're connected to the correct Algorand network (testnet/mainnet)

## Troubleshooting

- **Insufficient Balance**: Ensure you have enough payment tokens and ALGO for fees
- **Permission Errors**: Verify that the calling account has the necessary permissions
- **Invalid Names**: Check that the subname follows the naming conventions
- **Contract Not Found**: Verify that all application IDs are correct and contracts are deployed

## Next Steps

After successfully creating a subname, you can:

1. **Set Address Resolution**: Use the resolver contract to map the subname to an Algorand address
2. **Set Text Records**: Add arbitrary text data to the subname
3. **Transfer Ownership**: Transfer the subname to another address
4. **Renew Registration**: Extend the registration period when needed

## Related Documentation

- [Main Documentation](../index.md) - Overview of the VNS system
- [Registrar Documentation](REGISTRAR.md) - Detailed registrar contract information
