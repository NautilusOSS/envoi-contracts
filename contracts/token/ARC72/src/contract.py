import typing
from algopy import (
    ARC4Contract,
    Application,
    Account,
    BigUInt,
    Box,
    BoxMap,
    BoxRef,
    Bytes,
    Global,
    OnCompleteAction,
    String,
    Txn,
    UInt64,
    arc4,
    itxn,
    op,
    subroutine,
)
from utils import require_payment, close_offline_on_delete

Bytes4: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[4]]
Bytes8: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[8]]
Bytes32: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[32]]
Bytes40: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[40]]
Bytes48: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[48]]
Bytes64: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[64]]
Bytes256: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[256]]

mint_fee = 0
mint_cost = 336700  # TODO update


class PartKeyInfo(arc4.Struct):
    address: arc4.Address
    vote_key: Bytes32
    selection_key: Bytes32
    vote_first: arc4.UInt64
    vote_last: arc4.UInt64
    vote_key_dilution: arc4.UInt64
    state_proof_key: Bytes64


##################################################
# Ownable
#   allows contract to be owned
##################################################


class OwnershipTransferred(arc4.Struct):
    previousOwner: arc4.Address
    newOwner: arc4.Address


class OwnableInterface(ARC4Contract):
    """
    Interface for all abimethods operated by owner.
    """

    def __init__(self) -> None:  # pragma: no cover
        self.owner = Account()

    @arc4.abimethod
    def transfer(self, new_owner: arc4.Address) -> None:  # pragma: no cover
        """
        Transfer ownership of the contract to a new owner. Emits OwnershipTransferred event.
        """
        pass


class Ownable(OwnableInterface):
    def __init__(self) -> None:  # pragma: no cover
        super().__init__()

    @arc4.abimethod
    def transfer(self, new_owner: arc4.Address) -> None:
        assert Txn.sender == self.owner, "must be owner"
        arc4.emit(OwnershipTransferred(arc4.Address(self.owner), new_owner))
        self.owner = new_owner.native


##################################################
# Stakeable
#   allows contract to participate in consensus,
#   stake
##################################################


class DelegateUpdated(arc4.Struct):
    previousDelegate: arc4.Address
    newDelegate: arc4.Address


class Participated(arc4.Struct):
    who: arc4.Address
    partkey: PartKeyInfo


class StakeableInterface(ARC4Contract):
    """
    Interface for all abimethods of stakeable contract.
    """

    def __init__(self) -> None:  # pragma: no cover
        self.delegate = Account()
        self.stakeable = bool(1)

    @arc4.abimethod
    def set_delegate(self, delegate: arc4.Address) -> None:  # pragma: no cover
        """
        Set delegate.
        """
        pass

    @arc4.abimethod
    def participate(
        self,
        vote_k: Bytes32,
        sel_k: Bytes32,
        vote_fst: arc4.UInt64,
        vote_lst: arc4.UInt64,
        vote_kd: arc4.UInt64,
        sp_key: Bytes64,
    ) -> None:  # pragma: no cover
        """
        Participate in consensus.
        """
        pass


class Stakeable(StakeableInterface, OwnableInterface):
    def __init__(self) -> None:  # pragma: no cover
        # ownable state
        self.owner = Account()
        # stakeable state
        self.delegate = Account()  # zero address
        self.stakeable = bool(1)  # 1 (Default unlocked)

    @arc4.abimethod
    def set_delegate(self, delegate: arc4.Address) -> None:
        assert (
            Txn.sender == self.owner or Txn.sender == Global.creator_address
        ), "must be owner or creator"
        arc4.emit(DelegateUpdated(arc4.Address(self.delegate), delegate))
        self.delegate = delegate.native

    @arc4.abimethod
    def participate(
        self,
        vote_k: Bytes32,
        sel_k: Bytes32,
        vote_fst: arc4.UInt64,
        vote_lst: arc4.UInt64,
        vote_kd: arc4.UInt64,
        sp_key: Bytes64,
    ) -> None:
        ###########################################
        assert (
            Txn.sender == self.owner or Txn.sender == self.delegate
        ), "must be owner or delegate"
        ###########################################
        key_reg_fee = Global.min_txn_fee
        # require payment of min fee to prevent draining
        assert require_payment(Txn.sender) == key_reg_fee, "payment amout accurate"
        ###########################################
        arc4.emit(
            Participated(
                arc4.Address(Txn.sender),
                PartKeyInfo(
                    address=arc4.Address(Txn.sender),
                    vote_key=vote_k,
                    selection_key=sel_k,
                    vote_first=vote_fst,
                    vote_last=vote_lst,
                    vote_key_dilution=vote_kd,
                    state_proof_key=sp_key,
                ),
            )
        )
        itxn.KeyRegistration(
            vote_key=vote_k.bytes,
            selection_key=sel_k.bytes,
            vote_first=vote_fst.native,
            vote_last=vote_lst.native,
            vote_key_dilution=vote_kd.native,
            state_proof_key=sp_key.bytes,
            fee=key_reg_fee,
        ).submit()


##################################################
# Upgradeable
#   allows contract to be updated
##################################################


class VersionUpdated(arc4.Struct):
    contract_version: arc4.UInt64
    deployment_version: arc4.UInt64


class UpdateApproved(arc4.Struct):
    who: arc4.Address
    approval: arc4.Bool


class UpgraderGranted(arc4.Struct):
    previousUpgrader: arc4.Address
    newUpgrader: arc4.Address


class UpgradeableInterface(ARC4Contract):
    """
    Interface for all abimethods of upgradeable contract.
    """

    def __init__(self) -> None:  # pragma: no cover
        self.contract_version = UInt64()
        self.deployment_version = UInt64()
        self.updatable = bool(1)
        self.upgrader = Account()

    @arc4.abimethod
    def set_version(
        self, contract_version: arc4.UInt64, deployment_version: arc4.UInt64
    ) -> None:  # pragma: no cover
        """
        Set contract and deployment version.
        """
        pass

    @arc4.abimethod
    def on_update(self) -> None:  # pragma: no cover
        """
        On update.
        """
        pass

    @arc4.abimethod
    def approve_update(self, approval: arc4.Bool) -> None:  # pragma: no cover
        """
        Approve update.
        """
        pass

    @arc4.abimethod
    def grant_upgrader(self, upgrader: arc4.Address) -> None:  # pragma: no cover
        """
        Grant upgrader.
        """
        pass

    ##############################################
    # @arc4.abimethod
    # def update(self) -> None:
    #      pass
    ##############################################


class Upgradeable(UpgradeableInterface, OwnableInterface):
    def __init__(self) -> None:  # pragma: no cover
        # ownable state
        self.owner = Account()
        # upgradeable state
        self.contract_version = UInt64()
        self.deployment_version = UInt64()
        self.updatable = bool(1)
        self.upgrader = Global.creator_address

    @arc4.abimethod
    def set_version(
        self, contract_version: arc4.UInt64, deployment_version: arc4.UInt64
    ) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        arc4.emit(VersionUpdated(contract_version, deployment_version))
        self.contract_version = contract_version.native
        self.deployment_version = deployment_version.native

    @arc4.baremethod(allow_actions=["UpdateApplication"])
    def on_update(self) -> None:
        ##########################################
        # WARNING: This app can be updated by the creator
        ##########################################
        assert Txn.sender == self.upgrader, "must be upgrader"
        assert self.updatable == UInt64(1), "not approved"
        ##########################################

    @arc4.abimethod
    def approve_update(self, approval: arc4.Bool) -> None:
        assert Txn.sender == self.owner, "must be owner"
        arc4.emit(UpdateApproved(arc4.Address(self.owner), approval))
        self.updatable = approval.native

    @arc4.abimethod
    def grant_upgrader(self, upgrader: arc4.Address) -> None:
        assert Txn.sender == Global.creator_address, "must be creator"
        arc4.emit(UpgraderGranted(arc4.Address(self.upgrader), upgrader))
        self.upgrader = upgrader.native


##################################################
# Deployable
#   ensures that contract is created by factory
#   and recorded
##################################################


class DeployableInterface(ARC4Contract):
    """
    Interface for all abimethods of deployable contract.
    """

    def __init__(self) -> None:  # pragma: no cover
        self.parent_id = UInt64()
        self.deployer = Account()

    @arc4.abimethod(create="require")
    def on_create(self) -> None:  # pragma: no cover
        """
        Execute on create.
        """
        pass


class Deployable(DeployableInterface):
    def __init__(self) -> None:  # pragma: no cover
        super().__init__()

    @arc4.baremethod(create="require")
    def on_create(self) -> None:
        caller_id = Global.caller_application_id
        assert caller_id > 0, "must be created by factory"
        self.parent_id = caller_id


##################################################
# Lockable
#   allows contract to be lock network tokens
##################################################


class LockableInterface(ARC4Contract):
    """
    Interface for all methods of lockable contracts.
    This class defines the basic interface for all types of lockable contracts.
    Subclasses must implement these methods to provide concrete behavior
    """

    @arc4.abimethod
    def withdraw(self, amount: arc4.UInt64) -> UInt64:  # pragma: no cover
        """
        Withdraw funds from contract. Should be called by owner.
        """
        return UInt64()


##################################################
# ARC73
#   supports interface
##################################################


class ARC73SupportsInterfaceInterface(ARC4Contract):
    @arc4.abimethod(readonly=True)
    def supportsInterface(self, interface_id: Bytes4) -> arc4.Bool:
        return arc4.Bool(False)


class ARC73SupportsInterface(ARC73SupportsInterfaceInterface):
    @arc4.abimethod(readonly=True)
    def supportsInterface(self, interface_id: Bytes4) -> arc4.Bool:
        return arc4.Bool(self._supportsInterface(interface_id.bytes))

    @subroutine
    def _supportsInterface(self, interface_id: Bytes) -> bool:
        if interface_id == Bytes.from_hex("4e22a3ba"):  # ARC73 supports interface
            return True
        elif interface_id == Bytes.from_hex("ffffffff"):  # mask
            return False
        else:
            return False


##################################################
# ARC72Token
#   nft contract
##################################################


class arc72_nft_data(arc4.Struct):
    owner: arc4.Address
    approved: arc4.Address
    index: arc4.UInt256
    token_id: arc4.UInt256
    metadata: Bytes256
    node_name: arc4.DynamicBytes


class arc72_holder_data(arc4.Struct):
    holder: arc4.Address
    balance: arc4.UInt256


# {
#   "name": "ARC-72",
#   "desc": "Smart Contract NFT Base Interface",
#   "methods": [
#     {
#       "name": "arc72_ownerOf",
#       "desc": "Returns the address of the current owner of the NFT with the given tokenId",
#       "readonly": true,
#       "args": [
#         { "type": "uint256", "name": "tokenId", "desc": "The ID of the NFT" },
#       ],
#       "returns": { "type": "address", "desc": "The current owner of the NFT." }
#     },
#     {
#       "name": "arc72_transferFrom",
#       "desc": "Transfers ownership of an NFT",
#       "readonly": false,
#       "args": [
#         { "type": "address", "name": "from" },
#         { "type": "address", "name": "to" },
#         { "type": "uint256", "name": "tokenId" }
#       ],
#       "returns": { "type": "void" }
#     },
#   ],
#   "events": [
#     {
#       "name": "arc72_Transfer",
#       "desc": "Transfer ownership of an NFT",
#       "args": [
#         {
#           "type": "address",
#           "name": "from",
#           "desc": "The current owner of the NFT"
#         },
#         {
#           "type": "address",
#           "name": "to",
#           "desc": "The new owner of the NFT"
#         },
#         {
#           "type": "uint256",
#           "name": "tokenId",
#           "desc": "The ID of the transferred NFT"
#         }
#       ]
#     }
#   ]
# }


class arc72_Transfer(arc4.Struct):
    sender: arc4.Address
    recipient: arc4.Address
    tokenId: arc4.UInt256


class ARC72TokenCoreInterface(ARC4Contract):
    @arc4.abimethod(readonly=True)
    def arc72_ownerOf(self, tokenId: arc4.UInt256) -> arc4.Address:
        """
        Returns the address of the current owner of the NFT with the given tokenId
        """
        return arc4.Address(Global.zero_address)

    @arc4.abimethod
    def arc72_transferFrom(
        self, from_: arc4.Address, to: arc4.Address, tokenId: arc4.UInt256
    ) -> None:
        """
        Transfers ownership of an NFT
        """
        pass


# {
#   "name": "ARC-72 Metadata Extension",
#   "desc": "Smart Contract NFT Metadata Interface",
#   "methods": [
#     {
#       "name": "arc72_tokenURI",
#       "desc": "Returns a URI pointing to the NFT metadata",
#       "readonly": true,
#       "args": [
#         { "type": "uint256", "name": "tokenId", "desc": "The ID of the NFT" },
#       ],
#       "returns": { "type": "byte[256]", "desc": "URI to token metadata." }
#     }
#   ],
# }


class ARC72TokenMetadataInterface(ARC4Contract):
    @arc4.abimethod(readonly=True)
    def arc72_tokenURI(self, tokenId: arc4.UInt256) -> Bytes256:
        """
        Returns a URI pointing to the NFT metadata
        """
        return Bytes256.from_bytes(Bytes())


# {
#   "name": "ARC-72 Transfer Management Extension",
#   "desc": "Smart Contract NFT Transfer Management Interface",
#   "methods": [
#     {
#       "name": "arc72_approve",
#       "desc": "Approve a controller for a single NFT",
#       "readonly": false,
#       "args": [
#         { "type": "address", "name": "approved", "desc": "Approved controller address" },
#         { "type": "uint256", "name": "tokenId", "desc": "The ID of the NFT" },
#       ],
#       "returns": { "type": "void" }
#     },
#     {
#       "name": "arc72_setApprovalForAll",
#       "desc": "Approve an operator for all NFTs for a user",
#       "readonly": false,
#       "args": [
#         { "type": "address", "name": "operator", "desc": "Approved operator address" },
#         { "type": "bool", "name": "approved", "desc": "true to give approval, false to revoke" },
#       ],
#       "returns": { "type": "void" }
#     },
#     {
#       "name": "arc72_getApproved",
#       "desc": "Get the current approved address for a single NFT",
#       "readonly": true,
#       "args": [
#         { "type": "uint256", "name": "tokenId", "desc": "The ID of the NFT" },
#       ],
#       "returns": { "type": "address", "desc": "address of approved user or zero" }
#     },
#     {
#       "name": "arc72_isApprovedForAll",
#       "desc": "Query if an address is an authorized operator for another address",
#       "readonly": true,
#       "args": [
#         { "type": "address", "name": "owner" },
#         { "type": "address", "name": "operator" },
#       ],
#       "returns": { "type": "bool", "desc": "whether operator is authorized for all NFTs of owner" }
#     },
#   ],
#   "events": [
#     {
#       "name": "arc72_Approval",
#       "desc": "An address has been approved to transfer ownership of the NFT",
#       "args": [
#         {
#           "type": "address",
#           "name": "owner",
#           "desc": "The current owner of the NFT"
#         },
#         {
#           "type": "address",
#           "name": "approved",
#           "desc": "The approved user for the NFT"
#         },
#         {
#           "type": "uint256",
#           "name": "tokenId",
#           "desc": "The ID of the NFT"
#         }
#       ]
#     },
#     {
#       "name": "arc72_ApprovalForAll",
#       "desc": "Operator set or unset for all NFTs defined by this contract for an owner",
#       "args": [
#         {
#           "type": "address",
#           "name": "owner",
#           "desc": "The current owner of the NFT"
#         },
#         {
#           "type": "address",
#           "name": "operator",
#           "desc": "The approved user for the NFT"
#         },
#         {
#           "type": "bool",
#           "name": "approved",
#           "desc": "Whether operator is authorized for all NFTs of owner "
#         }
#       ]
#     },
#   ]
# }


class arc72_Approval(arc4.Struct):
    owner: arc4.Address
    approved: arc4.Address
    tokenId: arc4.UInt256


class arc72_ApprovalForAll(arc4.Struct):
    owner: arc4.Address
    operator: arc4.Address
    approved: arc4.Bool


class ARC72TokenTransferManagementInterface(ARC4Contract):
    @arc4.abimethod
    def arc72_approve(self, approved: arc4.Address, tokenId: arc4.UInt256) -> None:
        pass

    @arc4.abimethod
    def arc72_setApprovalForAll(
        self, operator: arc4.Address, approved: arc4.Bool
    ) -> None:
        pass

    @arc4.abimethod(readonly=True)
    def arc72_getApproved(self, tokenId: arc4.UInt256) -> arc4.Address:
        return arc4.Address(Global.zero_address)

    @arc4.abimethod(readonly=True)
    def arc72_isApprovedForAll(
        self, owner: arc4.Address, operator: arc4.Address
    ) -> arc4.Bool:
        return arc4.Bool(False)


# {
#   "name": "ARC-72 Enumeration Extension",
#   "desc": "Smart Contract NFT Enumeration Interface",
#   "methods": [
#     {
#       "name": "arc72_balanceOf",
#       "desc": "Returns the number of NFTs owned by an address",
#       "readonly": true,
#       "args": [
#         { "type": "address", "name": "owner" },
#       ],
#       "returns": { "type": "uint256" }
#     },
#     {
#       "name": "arc72_totalSupply",
#       "desc": "Returns the number of NFTs currently defined by this contract",
#       "readonly": true,
#       "args": [],
#       "returns": { "type": "uint256" }
#     },
#     {
#       "name": "arc72_tokenByIndex",
#       "desc": "Returns the token ID of the token with the given index among all NFTs defined by the contract",
#       "readonly": true,
#       "args": [
#         { "type": "uint256", "name": "index" },
#       ],
#       "returns": { "type": "uint256" }
#     },
#   ],
# }


class ARC72TokenEnumerationInterface(ARC4Contract):
    @arc4.abimethod(readonly=True)
    def arc72_balanceOf(self, owner: arc4.Address) -> arc4.UInt256:
        return arc4.UInt256(0)

    @arc4.abimethod(readonly=True)
    def arc72_totalSupply(self) -> arc4.UInt256:
        return arc4.UInt256(0)

    @arc4.abimethod(readonly=True)
    def arc72_tokenByIndex(self, index: arc4.UInt256) -> arc4.UInt256:
        return arc4.UInt256(0)


class ARC72Token(
    ARC72TokenCoreInterface,
    ARC72TokenMetadataInterface,
    ARC72TokenTransferManagementInterface,
    ARC72TokenEnumerationInterface,
    ARC73SupportsInterface,
):
    def __init__(self) -> None:  # pragma: no cover
        # state (core, metadata)
        self.nft_data = BoxMap(BigUInt, arc72_nft_data)
        self.nft_operators = BoxMap(Bytes, bool)
        # enumeration state
        self.totalSupply = BigUInt()
        self.nft_index = BoxMap(BigUInt, BigUInt)
        self.holder_data = BoxMap(Account, arc72_holder_data)

    # core methods

    @arc4.abimethod(readonly=True)
    def arc72_ownerOf(self, tokenId: arc4.UInt256) -> arc4.Address:
        """
        Returns the address of the current owner of the NFT with the given tokenId
        """
        return self._ownerOf(tokenId.native)

    @subroutine
    def _ownerOf(self, tokenId: BigUInt) -> arc4.Address:
        return self._nft_owner(tokenId)

    @arc4.abimethod
    def arc72_transferFrom(
        self, from_: arc4.Address, to: arc4.Address, tokenId: arc4.UInt256
    ) -> None:
        """
        Transfers ownership of an NFT
        """
        self._transferFrom(from_.native, to.native, tokenId.native)

    @subroutine
    def _transferFrom(
        self, sender: Account, recipient: Account, tokenId: BigUInt
    ) -> None:
        assert self._nft_index(tokenId) != 0, "token id not exists"
        owner = self._ownerOf(tokenId)
        assert owner == sender, "sender must be owner"
        assert (
            Txn.sender == sender
            or Txn.sender == Account.from_bytes(self._getApproved(tokenId).bytes)
            or self._isApprovedForAll(Account.from_bytes(owner.bytes), Txn.sender)
        ), "sender must be owner or approved"
        nft = self.nft_data.get(key=tokenId, default=self._invalid_nft_data()).copy()
        nft.owner = arc4.Address(recipient)
        nft.approved = arc4.Address(Global.zero_address)
        self.nft_data[tokenId] = nft.copy()
        self._holder_increment_balance(recipient)
        self._holder_decrement_balance(sender)
        arc4.emit(
            arc72_Transfer(
                arc4.Address(sender),
                arc4.Address(recipient),
                arc4.UInt256(tokenId),
            )
        )

    # metadata methods

    @arc4.abimethod(readonly=True)
    def arc72_tokenURI(self, tokenId: arc4.UInt256) -> Bytes256:
        return self._tokenURI(tokenId.native)

    @subroutine
    def _tokenURI(self, tokenId: BigUInt) -> Bytes256:
        return self._nft_metadata(tokenId)

    # transfer management methods

    @arc4.abimethod
    def arc72_approve(self, approved: arc4.Address, tokenId: arc4.UInt256) -> None:
        self._approve(Txn.sender, approved.native, tokenId.native)

    @subroutine
    def _approve(self, owner: Account, approved: Account, tokenId: BigUInt) -> None:
        nft = self.nft_data.get(key=tokenId, default=self._invalid_nft_data()).copy()
        assert nft.owner == owner, "owner must be owner"
        nft.approved = arc4.Address(approved)
        self.nft_data[tokenId] = nft.copy()
        arc4.emit(
            arc72_Approval(
                arc4.Address(owner),
                arc4.Address(approved),
                arc4.UInt256(tokenId),
            )
        )

    @arc4.abimethod
    def arc72_setApprovalForAll(
        self, operator: arc4.Address, approved: arc4.Bool
    ) -> None:
        self._setApprovalForAll(Txn.sender, operator.native, approved.native)

    @arc4.abimethod(readonly=True)
    def arc72_getApproved(self, tokenId: arc4.UInt256) -> arc4.Address:
        return self._getApproved(tokenId.native)

    @arc4.abimethod(readonly=True)
    def arc72_isApprovedForAll(
        self, owner: arc4.Address, operator: arc4.Address
    ) -> arc4.Bool:
        return arc4.Bool(self._isApprovedForAll(owner.native, operator.native))

    @subroutine
    def _setApprovalForAll(
        self, owner: Account, approved: Account, approval: bool
    ) -> None:
        operator_key = op.sha256(approved.bytes + owner.bytes)
        self.nft_operators[operator_key] = approval
        arc4.emit(
            arc72_ApprovalForAll(
                arc4.Address(owner),
                arc4.Address(approved),
                arc4.Bool(approval),
            )
        )

    @subroutine
    def _getApproved(self, tokenId: BigUInt) -> arc4.Address:
        return self.nft_data.get(key=tokenId, default=self._invalid_nft_data()).approved

    @subroutine
    def _isApprovedForAll(self, owner: Account, operator: Account) -> bool:
        operator_key = op.sha256(operator.bytes + owner.bytes)
        return self.nft_operators.get(key=operator_key, default=False)

    # enumeration methods

    @arc4.abimethod(readonly=True)
    def arc72_balanceOf(self, owner: arc4.Address) -> arc4.UInt256:
        return self._balanceOf(owner.native)

    @subroutine
    def _balanceOf(self, owner: Account) -> arc4.UInt256:
        return self._holder_balance(owner)

    @arc4.abimethod(readonly=True)
    def arc72_totalSupply(self) -> arc4.UInt256:
        return arc4.UInt256(self._totalSupply())

    @subroutine
    def _totalSupply(self) -> BigUInt:
        return self.totalSupply

    @arc4.abimethod(readonly=True)
    def arc72_tokenByIndex(self, index: arc4.UInt256) -> arc4.UInt256:
        return arc4.UInt256(self._tokenByIndex(index.native))

    @subroutine
    def _tokenByIndex(self, index: BigUInt) -> BigUInt:
        return self.nft_index.get(key=index, default=BigUInt(0))

    # supports methods

    # override _supports_interface
    @subroutine
    def _supportsInterface(self, interface_id: Bytes) -> bool:
        if interface_id == Bytes.from_hex("4e22a3ba"):  # supports interface
            return True
        elif interface_id == Bytes.from_hex("ffffffff"):  # mask
            return False
        elif interface_id == Bytes.from_hex("53f02a40"):  # ARC72 core
            return True
        elif interface_id == Bytes.from_hex("c3c1fc00"):  # ARC72 metadata
            return True
        elif interface_id == Bytes.from_hex("b9c6f696"):  # ARC72 transfer management
            return True
        elif interface_id == Bytes.from_hex("a57d4679"):  # ARC72 enumeration
            return True
        else:
            return False

    # invalid methods

    @subroutine
    def _invalid_nft_data(self) -> arc72_nft_data:
        """
        Returns invalid NFT data
        """
        invalid_nft_data = arc72_nft_data(
            owner=arc4.Address(Global.zero_address),
            approved=arc4.Address(Global.zero_address),
            index=arc4.UInt256(0),
            token_id=arc4.UInt256(0),
            metadata=Bytes256.from_bytes(Bytes()),
            node_name=arc4.DynamicBytes.from_bytes(String("").bytes),
        )
        return invalid_nft_data

    @subroutine
    def _invalid_holder_data(self) -> arc72_holder_data:
        """
        Returns invalid holder data
        """
        invalid_holder_data = arc72_holder_data(
            holder=arc4.Address(Global.zero_address),
            balance=arc4.UInt256(0),
        )
        return invalid_holder_data

    # nft methods

    @subroutine
    def _nft_data(self, tokenId: BigUInt) -> arc72_nft_data:
        """
        Returns the NFT data
        """
        return self.nft_data.get(key=tokenId, default=self._invalid_nft_data())

    @subroutine
    def _nft_index(self, tokenId: BigUInt) -> BigUInt:
        """
        Returns the index of the NFT
        """
        return BigUInt.from_bytes(self._nft_data(tokenId).index.bytes)

    @subroutine
    def _nft_metadata(self, tokenId: BigUInt) -> Bytes256:
        """
        Returns the metadata of the NFT
        """
        return Bytes256.from_bytes(self._nft_data(tokenId).metadata.bytes[:256])

    @subroutine
    def _nft_owner(self, tokenId: BigUInt) -> arc4.Address:
        """
        Returns the owner of the NFT
        """
        return self._nft_data(tokenId).owner

    # holder methods

    @subroutine
    def _holder_data(self, holder: Account) -> arc72_holder_data:
        """
        Returns the holder data
        """
        return self.holder_data.get(key=holder, default=self._invalid_holder_data())

    @subroutine
    def _holder_balance(self, holder: Account) -> arc4.UInt256:
        """
        Returns the number of NFTs owned by an address
        """
        return self._holder_data(holder).balance

    @subroutine
    def _holder_increment_balance(self, holder: Account) -> BigUInt:
        """
        Increment balance of holder
        """
        previous_balance = BigUInt.from_bytes(self._holder_balance(holder).bytes)
        next_balance = previous_balance + 1
        new_holder_data = arc72_holder_data(
            holder=arc4.Address(holder),
            balance=arc4.UInt256(previous_balance + 1),
        )
        self.holder_data[holder] = new_holder_data.copy()
        return next_balance

    @subroutine
    def _holder_decrement_balance(self, holder: Account) -> BigUInt:
        """
        Decrement balance of holder
        """
        previous_balance = BigUInt.from_bytes(self._holder_balance(holder).bytes)
        next_balance = previous_balance - 1
        if next_balance == 0:
            del self.holder_data[holder]
        else:
            new_holder_data = arc72_holder_data(
                holder=arc4.Address(holder),
                balance=arc4.UInt256(next_balance),
            )
            self.holder_data[holder] = new_holder_data.copy()
        return next_balance

    # supply methods

    @subroutine
    def _increment_totalSupply(self) -> BigUInt:
        """
        Increment total supply
        """
        new_totalSupply = self.totalSupply + 1
        self.totalSupply = new_totalSupply
        return new_totalSupply

    @subroutine
    def _decrement_totalSupply(self) -> BigUInt:
        """
        Decrement total supply
        """
        new_totalSupply = self.totalSupply - 1
        self.totalSupply = new_totalSupply
        return new_totalSupply

    # counter methods

    @subroutine
    def _increment_counter(self) -> BigUInt:
        """
        Increment counter
        """
        counter_box = Box(BigUInt, key=b"arc72_counter")
        counter = counter_box.get(default=BigUInt(0))
        new_counter = counter + 1
        counter_box.value = new_counter
        return new_counter


class staking_data(arc4.Struct):
    delegate: arc4.Address


## dotNS


class OSARC72Token(ARC72Token, Upgradeable, Stakeable):
    def __init__(self) -> None:
        super().__init__()
        # ownable state
        self.owner = Global.creator_address
        # upgradeable state
        self.contract_version = UInt64()
        self.deployment_version = UInt64()
        self.updatable = bool(1)
        self.upgrader = Global.creator_address
        # stakeable state
        self.delegate = Account()
        self.stakeable = bool(1)

    @arc4.abimethod
    def mint(
        self,
        to: arc4.Address,
        nodeId: Bytes256,
        nodeName: arc4.String,
        duration: arc4.UInt64,
    ) -> arc4.UInt256:
        """
        Mint a new NFT
        """
        return arc4.UInt256(
            self._mint(to.native, nodeId.bytes, nodeName.native, duration.native)
        )

    @subroutine
    def _mint(
        self, to: Account, nodeId: Bytes, nodeName: String, duration: UInt64
    ) -> BigUInt:

        assert duration > 0, "duration must be greater than 0"
        assert duration <= 5, "duration must be less than or equal to 10"

        root_node_id = Bytes256.from_bytes(Bytes()).bytes
        if nodeId == root_node_id:
            assert Txn.sender == self.owner, "only owner can mint on root node"

        bigNodeId = BigUInt.from_bytes(nodeId)

        parent_nft_data = self._nft_data(bigNodeId)

        assert parent_nft_data.index != 0, "parent node must exist"

        assert "." not in nodeName, "node name must not contain a dot"
        assert nodeName.bytes.length > 0, "node name must not be empty"

        if nodeId == root_node_id:
            name = nodeName + "."
        else:
            name = nodeName + "." + String.from_bytes(parent_nft_data.node_name.bytes)

        bigTokenId = arc4.UInt256.from_bytes(op.sha256(name.bytes)).native

        nft_data = self._nft_data(bigTokenId)

        assert nft_data.index == 0, "token must not exist"

        payment_amount = require_payment(Txn.sender)
        mint_price = self._get_price(nodeName, duration)
        assert (
            payment_amount >= mint_cost + mint_fee + mint_price
        ), "payment amount accurate"

        index = arc4.UInt256(
            self._increment_counter()
        ).native  # BigUInt to BigUInt(UInt256)
        self._increment_totalSupply()
        self.nft_index[index] = bigTokenId
        self.nft_data[bigTokenId] = arc72_nft_data(
            owner=arc4.Address(to),
            approved=arc4.Address(Global.zero_address),
            index=arc4.UInt256(index),
            token_id=arc4.UInt256.from_bytes(bigTokenId.bytes),
            metadata=Bytes256.from_bytes(Bytes()),
            node_name=arc4.DynamicBytes.from_bytes(nodeName.bytes),
        )
        self._holder_increment_balance(to)
        arc4.emit(
            arc72_Transfer(
                arc4.Address(Global.zero_address),
                arc4.Address(to),
                arc4.UInt256(bigTokenId),
            )
        )
        return index

    @subroutine
    def _get_price(self, nodeName: String, duration: UInt64) -> BigUInt:
        """
        Returns the price of the node
        """
        bigDuration = BigUInt(duration)
        price1Letter = BigUInt(5000000)
        price2Letter = BigUInt(2500000)
        price3Letter = BigUInt(1500000)
        price4Letter = BigUInt(1000000)
        price5Letter = BigUInt(500000)
        length = nodeName.bytes.length
        if length > 5:
            base_price = price5Letter * bigDuration
        elif length == 4:
            base_price = price4Letter * bigDuration
        elif length == 3:
            base_price = price3Letter * bigDuration
        elif length == 2:
            base_price = price2Letter * bigDuration
        elif length == 1:
            base_price = price1Letter * bigDuration
        else:
            base_price = BigUInt(1000000000000000000000000000000)
        return base_price

    @arc4.abimethod
    def burn(self, nodeId: Bytes256) -> None:
        """
        Burn an NFT
        """
        self._burn(nodeId.bytes)

    @subroutine
    def _burn(self, nodeId: Bytes) -> None:
        bigNodeId = BigUInt.from_bytes(nodeId)
        nft_data = self._nft_data(bigNodeId)
        assert nft_data.index != 0, "token exists"
        owner = nft_data.owner
        assert owner == Txn.sender, "sender must be owner"
        del self.nft_index[BigUInt.from_bytes(self._nft_data(bigNodeId).index.bytes)]
        del self.nft_data[bigNodeId]
        self._holder_decrement_balance(owner.native)
        self._decrement_totalSupply()
        arc4.emit(
            arc72_Transfer(
                owner,
                arc4.Address(Global.zero_address),
                arc4.UInt256.from_bytes(bigNodeId.bytes),
            )
        )

    @arc4.abimethod(allow_actions=[OnCompleteAction.DeleteApplication])
    def kill(self) -> None:
        """
        Kill contract
        """
        assert Txn.sender == self.upgrader, "must be upgrader"
        close_offline_on_delete(Txn.sender)

    @arc4.abimethod
    def post_update(self) -> None:
        """
        Post update
        """
        assert Txn.sender == self.upgrader, "must be upgrader"
        self._post_update()

    @subroutine
    def _post_update(self) -> None:
        pass


# ENS.sol
# //SPDX-License-Identifier: MIT
# pragma solidity >=0.8.4;
#
# interface ENS {
#     // Logged when the owner of a node assigns a new owner to a subnode.
#     event NewOwner(bytes32 indexed node, bytes32 indexed label, address owner);
#
#     // Logged when the owner of a node transfers ownership to a new account.
#     event Transfer(bytes32 indexed node, address owner);
#
#     // Logged when the resolver for a node changes.
#     event NewResolver(bytes32 indexed node, address resolver);
#
#     // Logged when the TTL of a node changes
#     event NewTTL(bytes32 indexed node, uint64 ttl);
#
#     // Logged when an operator is added or removed.
#     event ApprovalForAll(
#         address indexed owner,
#         address indexed operator,
#         bool approved
#     );
#
#     function setRecord(
#         bytes32 node,
#         address owner,
#         address resolver,
#         uint64 ttl
#     ) external;
#
#     function setSubnodeRecord(
#         bytes32 node,
#         bytes32 label,
#         address owner,
#         address resolver,
#         uint64 ttl
#     ) external;
#
#     function setSubnodeOwner(
#         bytes32 node,
#         bytes32 label,
#         address owner
#     ) external returns (bytes32);
#
#     function setResolver(bytes32 node, address resolver) external;
#
#     function setOwner(bytes32 node, address owner) external;
#
#     function setTTL(bytes32 node, uint64 ttl) external;
#
#     function setApprovalForAll(address operator, bool approved) external;
#
#     function owner(bytes32 node) external view returns (address);
#
#     function resolver(bytes32 node) external view returns (address);
#
#     function ttl(bytes32 node) external view returns (uint64);
#
#     function recordExists(bytes32 node) external view returns (bool);
#
#     function isApprovedForAll(
#         address owner,
#         address operator
#     ) external view returns (bool);
# }

# contract ENS {
#     struct Record {
#         address owner;
#         address resolver;
#         uint64 ttl;
#     }

#     mapping(bytes32=>Record) records;

#     event NewOwner(bytes32 indexed node, bytes32 indexed label, address owner);
#     event Transfer(bytes32 indexed node, address owner);
#     event NewResolver(bytes32 indexed node, address resolver);

#     modifier only_owner(bytes32 node) {
#         if(records[node].owner != msg.sender) throw;
#         _
#     }

#     function ENS(address owner) {
#         records[0].owner = owner;
#     }

#     function owner(bytes32 node) constant returns (address) {
#         return records[node].owner;
#     }

#     function resolver(bytes32 node) constant returns (address) {
#         return records[node].resolver;
#     }

#     function ttl(bytes32 node) constant returns (uint64) {
#         return records[node].ttl;
#     }

#     function setOwner(bytes32 node, address owner) only_owner(node) {
#         Transfer(node, owner);
#         records[node].owner = owner;
#     }

#     function setSubnodeOwner(bytes32 node, bytes32 label, address owner) only_owner(node) {
#         var subnode = sha3(node, label);
#         NewOwner(node, label, owner);
#         records[subnode].owner = owner;
#     }

#     function setResolver(bytes32 node, address resolver) only_owner(node) {
#         NewResolver(node, resolver);
#         records[node].resolver = resolver;
#     }

#     function setTTL(bytes32 node, uint64 ttl) only_owner(node) {
#         NewTTL(node, ttl);
#         records[node].ttl = ttl;
#     }
# }

# constants

DEFAULT_TTL = 86400  # 1 day

# composite types
#   Record


class Record(arc4.Struct):
    owner: arc4.Address
    resolver: arc4.UInt64
    ttl: arc4.UInt64
    approved: arc4.Address


# Events
#   NewOwner
#     Logged when the owner of a node assigns a new owner to a subnode.
#   Transfer
#     Logged when the owner of a node transfers ownership to a new account.
#   NewResolver
#     Logged when the resolver for a node changes.
#   NewTTL
#     Logged when the TTL of a node changes
#   ApprovalForAll
#     Logged when an operator is added or removed.


class NewOwner(arc4.Struct):
    node: Bytes32
    label: Bytes32
    owner: arc4.Address


class Transfer(arc4.Struct):
    node: Bytes32
    owner: arc4.Address


class NewResolver(arc4.Struct):
    node: Bytes32
    resolver: arc4.UInt64


class NewTTL(arc4.Struct):
    node: Bytes32
    ttl: arc4.UInt64


class ApprovalForAll(arc4.Struct):
    owner: arc4.Address
    operator: arc4.Address
    approved: arc4.Bool


class Approval(arc4.Struct):
    owner: arc4.Address
    approved: arc4.Address
    node: Bytes32


# class arc72_Transfer(arc4.Struct):
#     sender: arc4.Address
#     recipient: arc4.Address
#     tokenId: arc4.UInt256
#
# class arc72_Approval(arc4.Struct):
#     owner: arc4.Address
#     approved: arc4.Address
#     tokenId: arc4.UInt256
#
# class arc72_ApprovalForAll(arc4.Struct):
#     owner: arc4.Address
#     operator: arc4.Address
#     approved: arc4.Bool


#                  _
# __   ___ __  ___(_) ___
# \ \ / / '_ \/ __| |/ __|
#  \ V /| | | \__ \ | (__
#   \_/ |_| |_|___/_|\___|
#
# References:
# https://github.com/ensdomains/ens-contracts/blob/staging/contracts/registry/ENS.sol
#


class VNSCoreInterface(ARC4Contract):

    @arc4.abimethod
    def setRecord(
        self,
        node: Bytes32,
        owner: arc4.Address,
        resolver: arc4.UInt64,
        ttl: arc4.UInt64,
    ) -> None:
        self._setRecord(node.bytes, owner.native, resolver.native, ttl.native)

    @subroutine
    def _setRecord(
        self,
        node: Bytes,
        owner: Account,
        resolver: UInt64,
        ttl: UInt64,
    ) -> None:
        """
        Set the record for a node
        """
        pass

    @arc4.abimethod
    def setSubnodeRecord(
        self,
        node: Bytes32,
        label: Bytes32,
        owner: arc4.Address,
        resolver: arc4.UInt64,
        ttl: arc4.UInt64,
    ) -> None:
        self._setSubnodeRecord(
            node.bytes, label.bytes, owner.native, resolver.native, ttl.native
        )

    @subroutine
    def _setSubnodeRecord(
        self, node: Bytes, label: Bytes, owner: Account, resolver: UInt64, ttl: UInt64
    ) -> None:
        """
        Set the record for a subnode
        """
        pass

    @subroutine
    def setSubnodeOwner(
        self, node: Bytes32, label: Bytes32, owner: arc4.Address
    ) -> Bytes32:
        return Bytes32.from_bytes(
            self._setSubnodeOwner(node.bytes, label.bytes, owner.native)
        )

    @subroutine
    def _setSubnodeOwner(self, node: Bytes, label: Bytes, owner: Account) -> Bytes:
        """
        Set the owner of a subnode
        """
        return Bytes()

    @subroutine
    def setResolver(self, node: Bytes32, resolver: arc4.UInt64) -> None:
        self._setResolver(node.bytes, resolver.native)

    @subroutine
    def _setResolver(self, node: Bytes, resolver: UInt64) -> None:
        """/
        Set the resolver for a node
        """
        pass

    @subroutine
    def setOwner(self, node: Bytes32, owner: arc4.Address) -> None:
        self._setOwner(node.bytes, owner.native)

    @subroutine
    def _setOwner(self, node: Bytes, owner: Account) -> None:
        """
        Set the owner of a node
        """
        pass

    @arc4.abimethod
    def setTTL(self, node: Bytes32, ttl: arc4.UInt64) -> None:
        self._setTTL(node.bytes, ttl.native)

    @subroutine
    def _setTTL(self, node: Bytes, ttl: UInt64) -> None:
        """
        Set the TTL for a node
        """
        pass

    @arc4.abimethod
    def setApprovalForAll(self, operator: arc4.Address, approved: arc4.Bool) -> None:
        self._setApprovalForAll(operator.native, approved.native)

    @subroutine
    def _setApprovalForAll(self, operator: Account, approved: bool) -> None:
        """
        Set the approval for all operator
        """
        pass

    @arc4.abimethod
    def approve(self, to: arc4.Address, node: Bytes32) -> None:
        """
        Approve an address for a node
        """
        self._approve(to.native, node.bytes)

    @subroutine
    def _approve(self, to: Account, node: Bytes) -> None:
        """
        Approve an address for a node
        """
        pass

    @arc4.abimethod
    def getApproved(self, node: Bytes32) -> arc4.Address:
        return arc4.Address(self._getApproved(node.bytes))

    @subroutine
    def _getApproved(self, node: Bytes) -> Account:
        """
        Get the approved address for a node
        """
        return Global.zero_address

    @arc4.abimethod(readonly=True)
    def ownerOf(self, node: Bytes32) -> arc4.Address:
        return arc4.Address(self._ownerOf(node.bytes))

    @subroutine
    def _ownerOf(self, node: Bytes) -> Account:
        """
        Get the owner of a node
        """
        return Global.zero_address

    @arc4.abimethod(readonly=True)
    def resolver(self, node: Bytes32) -> arc4.UInt64:
        return arc4.UInt64(self._resolver(node.bytes))

    @subroutine
    def _resolver(self, node: Bytes) -> UInt64:
        """
        Get the resolver for a node
        """
        return UInt64(0)

    @arc4.abimethod(readonly=True)
    def ttl(self, node: Bytes32) -> arc4.UInt64:
        return arc4.UInt64(self._ttl(node.bytes))

    @subroutine
    def _ttl(self, node: Bytes) -> UInt64:
        """
        Get the TTL for a node
        """
        return UInt64(0)

    @arc4.abimethod(readonly=True)
    def recordExists(self, node: Bytes32) -> arc4.Bool:
        return arc4.Bool(self._recordExists(node.bytes))

    @subroutine
    def _recordExists(self, node: Bytes) -> bool:
        """
        Check if a record exists for a node
        """
        return False

    @arc4.abimethod(readonly=True)
    def isApprovedForAll(
        self, owner: arc4.Address, operator: arc4.Address
    ) -> arc4.Bool:
        """
        Check if an operator is approved for all
        """
        return arc4.Bool(self._isApprovedForAll(owner.native, operator.native))

    @subroutine
    def _isApprovedForAll(self, owner: Account, operator: Account) -> bool:
        """
        Check if an operator is approved for all
        """
        return False


#                  _
# __   ___ __  ___(_)_ __ ___
# \ \ / / '_ \/ __| | '__/ _ \
#  \ V /| | | \__ \ | | |  __/
#   \_/ |_| |_|___/_|_|  \___|
#


class VNSRecordInterface(ARC4Contract):

    @subroutine
    def _record(self, node: Bytes32) -> Record:
        """
        Returns the record
        """
        return Record(
            owner=arc4.Address(Global.zero_address),
            resolver=arc4.UInt64(0),
            ttl=arc4.UInt64(0),
            approved=arc4.Address(Global.zero_address),
        )

    @subroutine
    def _record_owner(self, node: Bytes32) -> Account:
        """
        Returns the owner of a record
        """
        return self._record(node).owner.native

    @subroutine
    def _record_resolver(self, node: Bytes32) -> UInt64:
        """
        Returns the resolver of a record
        """
        return self._record(node).resolver.native

    @subroutine
    def _record_ttl(self, node: Bytes32) -> UInt64:
        """
        Returns the TTL of a record
        """
        return self._record(node).ttl.native

    @subroutine
    def _record_approved(self, node: Bytes32) -> Account:
        """
        Returns the approved address for a record
        """
        return self._record(node).approved.native

    @subroutine
    def _invalid_record(self) -> Record:
        invalid_record = Record(
            owner=arc4.Address(Global.zero_address),
            resolver=arc4.UInt64(0),
            ttl=arc4.UInt64(0),
            approved=arc4.Address(Global.zero_address),
        )
        return invalid_record


# __   ___ __  ___
# \ \ / / '_ \/ __|
#  \ V /| | | \__ \
#   \_/ |_| |_|___/
#
# References:
# https://github.com/ensdomains/ens-contracts/blob/staging/contracts/registry/ENSRegistry.sol
#


class VNS(
    VNSCoreInterface,
    VNSRecordInterface,
    # ARC72TokenCoreInterface,
    # ARC72TokenMetadataInterface,
    # ARC72TokenTransferManagementInterface,
    # ARC72TokenEnumerationInterface,
    # ARC73SupportsInterface,
):
    def __init__(self) -> None:
        self.records = BoxMap(Bytes32, Record, key_prefix=b"")
        self.operators = BoxMap(Bytes64, bool, key_prefix=b"")

    # vns extended record methods

    # override
    @subroutine
    def _record(self, node: Bytes32) -> Record:
        """
        Returns the record
        """
        return self.records.get(key=node, default=self._invalid_record())

    # vms operator methods

    @subroutine
    def _operator(self, operator_key: Bytes64) -> bool:
        """
        Returns the operator for a node
        """
        return self.operators.get(key=operator_key, default=False)

    # vns access control methods

    #   Permits only the owner of the specified node

    @subroutine
    def only_owner(self, node: Bytes32) -> None:
        """
        Only the owner can call this function
        """
        assert self._record_owner(node) == Txn.sender, "sender must be owner"

    #   Permits only the owner of the specified node or approved operator

    @subroutine
    def authorized(self, node: Bytes32) -> bool:
        """
        Check if the sender is authorized to call this function
        """
        owner = self._record_owner(node)
        return (
            owner == Txn.sender
            or self._operator(Bytes64.from_bytes(Txn.sender.bytes + owner.bytes))
            or self._record_approved(node) == Txn.sender
        )

    # vns core methods

    @arc4.abimethod
    def setRecord(
        self,
        node: Bytes32,
        owner: arc4.Address,
        resolver: arc4.UInt64,
        ttl: arc4.UInt64,
    ) -> None:
        self.only_owner(node)
        self._setRecord(node.bytes, owner.native, resolver.native, ttl.native)

    @subroutine
    def _setRecord(
        self, node: Bytes, owner: Account, resolver: UInt64, ttl: UInt64
    ) -> None:
        """
        Set the record for a node
        """
        arc4.emit(Transfer(Bytes32.from_bytes(node), arc4.Address(owner)))
        arc4.emit(NewResolver(Bytes32.from_bytes(node), arc4.UInt64(resolver)))
        arc4.emit(NewTTL(Bytes32.from_bytes(node), arc4.UInt64(ttl)))
        record = self._record(Bytes32.from_bytes(node))
        record.owner = arc4.Address(owner)
        record.resolver = arc4.UInt64(resolver)
        record.ttl = arc4.UInt64(ttl)
        self.records[Bytes32.from_bytes(node)] = record.copy()

    @arc4.abimethod
    def setSubnodeRecord(
        self,
        node: Bytes32,
        label: Bytes32,
        owner: arc4.Address,
        resolver: arc4.UInt64,
        ttl: arc4.UInt64,
    ) -> None:
        """
        Set the record for a subnode
        """
        self.only_owner(node)
        self._setSubnodeRecord(
            node.bytes, label.bytes, owner.native, resolver.native, ttl.native
        )

    @subroutine
    def _setSubnodeRecord(
        self, node: Bytes, label: Bytes, owner: Account, resolver: UInt64, ttl: UInt64
    ) -> None:
        """
        Set the record for a subnode
        """
        # bytes32 subnode = setSubnodeOwner(node, label, owner);
        # _setResolverAndTTL(subnode, resolver, ttl);
        self._setSubnodeOwner(node, label, owner)
        # here

    # override
    @arc4.abimethod
    def setSubnodeOwner(
        self, node: Bytes32, label: Bytes32, owner: arc4.Address
    ) -> Bytes32:
        """
        Set the owner of a subnode
        """
        self.authorized(node)
        return Bytes32.from_bytes(
            self._setSubnodeOwner(node.bytes, label.bytes, owner.native)
        )

    # override
    @subroutine
    def _setSubnodeOwner(self, node: Bytes, label: Bytes, owner: Account) -> Bytes:
        """
        Set the owner of a subnode
        """
        subnode = op.sha256(node + label)
        arc4.emit(
            NewOwner(
                Bytes32.from_bytes(node), Bytes32.from_bytes(label), arc4.Address(owner)
            )
        )
        record = self._record(Bytes32.from_bytes(subnode))
        record.owner = arc4.Address(owner)
        self.records[Bytes32.from_bytes(subnode)] = record.copy()
        return subnode

    # override
    @arc4.abimethod
    def setResolver(self, node: Bytes32, resolver: arc4.UInt64) -> None:
        """
        Set the resolver for a node
        """
        self.authorized(node)
        self._setResolver(node.bytes, resolver.native)

    # override
    @subroutine
    def _setResolver(self, node: Bytes, resolver: UInt64) -> None:
        """
        Set the resolver for a node
        """
        record = self._record(Bytes32.from_bytes(node))
        if record.resolver.native != resolver:
            arc4.emit(NewResolver(Bytes32.from_bytes(node), arc4.UInt64(resolver)))
            record.resolver = arc4.UInt64(resolver)
            self.records[Bytes32.from_bytes(node)] = record.copy()

    # override
    @arc4.abimethod
    def setOwner(self, node: Bytes32, owner: arc4.Address) -> None:
        """
        Set the owner of a node
        """
        self.authorized(node)
        self._setOwner(node.bytes, owner.native)

    # override
    @subroutine
    def _setOwner(self, node: Bytes, owner: Account) -> None:
        """
        Set the owner of a node
        """
        arc4.emit(Transfer(Bytes32.from_bytes(node), arc4.Address(owner)))
        record = self._record(Bytes32.from_bytes(node))
        record.owner = arc4.Address(owner)
        self.records[Bytes32.from_bytes(node)] = record.copy()

    # override
    @arc4.abimethod
    def setTTL(self, node: Bytes32, ttl: arc4.UInt64) -> None:
        """
        Set the TTL for a node
        """
        self.authorized(node)
        self._setTTL(node.bytes, ttl.native)

    # override
    @subroutine
    def _setTTL(self, node: Bytes, ttl: UInt64) -> None:
        """
        Set the TTL for a node
        """
        record = self._record(Bytes32.from_bytes(node))
        if record.ttl.native != ttl:
            arc4.emit(NewTTL(Bytes32.from_bytes(node), arc4.UInt64(ttl)))
            record.ttl = arc4.UInt64(ttl)
            self.records[Bytes32.from_bytes(node)] = record.copy()

    # override
    @subroutine
    def _setApprovalForAll(self, operator: Account, approved: bool) -> None:
        """
        Set the approval for all operator
        """
        # TODO emit ApprovalForAll
        self.operators[Bytes64.from_bytes(operator.bytes + Txn.sender.bytes)] = approved

    # override
    @subroutine
    def _approve(self, to: Account, node: Bytes) -> None:
        """
        Approve an address for a node
        """
        self.only_owner(Bytes32.from_bytes(node))
        record = self._record(Bytes32.from_bytes(node))
        record.approved = arc4.Address(to)
        self.records[Bytes32.from_bytes(node)] = record.copy()

    # override
    @subroutine
    def _getApproved(self, node: Bytes) -> Account:
        """
        Get the approved address for a node
        """
        return self._record_approved(Bytes32.from_bytes(node))

    # override
    @subroutine
    def _ownerOf(self, node: Bytes) -> Account:
        """
        Get the owner of a node
        """
        return self._record_owner(Bytes32.from_bytes(node))

    # override
    @subroutine
    def _resolver(self, node: Bytes) -> UInt64:
        return self._record_resolver(Bytes32.from_bytes(node))

    # override
    @subroutine
    def _ttl(self, node: Bytes) -> UInt64:
        return self._record_ttl(Bytes32.from_bytes(node))

    # override
    @subroutine
    def _recordExists(self, node: Bytes) -> bool:
        return self._record(Bytes32.from_bytes(node)).owner != Global.zero_address

    # override
    @subroutine
    def _isApprovedForAll(self, owner: Account, operator: Account) -> bool:
        return self._operator(Bytes64.from_bytes(operator.bytes + owner.bytes))

    # vns utility methods

    @subroutine
    def setResolverAndTTL(
        self, node: Bytes32, resolver: arc4.UInt64, ttl: arc4.UInt64
    ) -> None:
        """
        Set the resolver and TTL for a node
        """
        self._setResolver(node.bytes, resolver.native)
        self._setTTL(node.bytes, ttl.native)


class VNSRegistry(VNS, Stakeable, Upgradeable):
    def __init__(self) -> None:
        # ownable state (in Stakeable and Upgradeable)
        self.owner = Global.creator_address
        # upgradable state
        self.contract_version = UInt64()
        self.deployment_version = UInt64()
        self.updatable = bool(1)
        self.upgrader = Global.creator_address
        # stakeable state
        self.delegate = Account()  # zero address
        self.stakeable = bool(1)  # 1 (Default unlocked)
        # records state
        self.registry_ttl = UInt64(DEFAULT_TTL)
        self.registry_resolver = UInt64(0)

    @arc4.abimethod
    def post_update(self) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        # initialize root node
        self.records[
            Bytes32.from_bytes(
                Bytes.from_base64("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="),
            )
        ] = Record(
            owner=arc4.Address(Global.creator_address),
            resolver=arc4.UInt64(0),
            ttl=arc4.UInt64(DEFAULT_TTL),
            approved=arc4.Address(Global.zero_address),
        )

    # terminal methods for testing

    @arc4.abimethod(allow_actions=[OnCompleteAction.DeleteApplication])
    def killApplication(self) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        close_offline_on_delete(Txn.sender)

    @arc4.abimethod
    def killNode(self, node: Bytes32) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        del self.records[node]

    @arc4.abimethod
    def killOperator(self, operator: arc4.Address, owner: arc4.Address) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        del self.operators[Bytes64.from_bytes(operator.bytes + owner.bytes)]

    @arc4.abimethod
    def deleteBox(self, key: Bytes) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        box = BoxRef(key=key)
        box.delete()

    # override
    @subroutine
    def _invalid_record(self) -> Record:
        """
        Returns invalid record
        """
        invalid_record = Record(
            owner=arc4.Address(Global.zero_address),
            resolver=arc4.UInt64(self.registry_resolver),
            ttl=arc4.UInt64(self.registry_ttl),
            approved=arc4.Address(Global.zero_address),
        )
        return invalid_record


class VersionChanged(arc4.Struct):
    node: Bytes32
    newVersion: arc4.UInt64


class VNSVersionableResolverInterface(ARC4Contract):
    @arc4.abimethod
    def recordVersions(self, node: Bytes32) -> arc4.UInt64:
        """
        Get the version for a node
        """
        return arc4.UInt64(self._recordVersions(node.bytes))

    @subroutine
    def _recordVersions(self, node: Bytes) -> UInt64:
        """
        Get the version for a node
        """
        return UInt64(0)


class VNSBaseResolver(VNSVersionableResolverInterface):
    def __init__(self) -> None:
        self.record_versions = BoxMap(Bytes32, UInt64, key_prefix=b"versions_")
        self.vns = UInt64(0)

    @subroutine
    def authorized(self, node: Bytes32) -> None:
        app = Application(self.vns)
        owner, _txn = arc4.abi_call(VNS.ownerOf, node, app_id=app)
        assert owner == Txn.sender, "sender must be owner"

    @subroutine
    def _recordVersions(self, node: Bytes) -> UInt64:
        return self.record_versions.get(key=Bytes32.from_bytes(node), default=UInt64(0))

    @arc4.abimethod
    def clearRecords(self, node: Bytes32) -> None:
        self.authorized(node)
        newVersion = self._recordVersions(node.bytes) + UInt64(1)
        arc4.emit(VersionChanged(node, arc4.UInt64(newVersion)))
        self.record_versions[node] = newVersion

    # supports interface


class AddrChanged(arc4.Struct):
    node: Bytes32
    addr: arc4.Address


class VNSAddrResolverInterface(ARC4Contract):
    @arc4.abimethod
    def addr(self, node: Bytes32) -> arc4.Address:
        """
        Get the address for a node
        """
        return arc4.Address(self._addr(node.bytes))

    @subroutine
    def _addr(self, node: Bytes) -> Account:
        """
        Get the address for a node
        """
        return Global.zero_address


class VNSAddrResolver(VNSAddrResolverInterface, VNSBaseResolver):
    def __init__(self) -> None:
        self.versionable_addrs = BoxMap(Bytes40, Account, key_prefix=b"addrs_")

    @subroutine
    def _addr(self, node: Bytes) -> Account:
        record_version_bytes = arc4.UInt64(self._recordVersions(node)).bytes
        return self.versionable_addrs.get(
            key=Bytes40.from_bytes(record_version_bytes + node),
            default=Global.zero_address,
        )

    @arc4.abimethod
    def setAddr(self, node: Bytes32, newAddress: arc4.Address) -> None:
        self.authorized(node)
        arc4.emit(AddrChanged(node, newAddress))
        self._setAddr(node.bytes, newAddress.native)

    @subroutine
    def _setAddr(self, node: Bytes, newAddress: Account) -> None:
        record_version_bytes = arc4.UInt64(self._recordVersions(node)).bytes
        self.versionable_addrs[Bytes40.from_bytes(record_version_bytes + node)] = (
            newAddress
        )


class AddressChanged(arc4.Struct):
    node: Bytes32
    coinType: arc4.UInt64  # Application ID
    newAddress: arc4.Address


class VNSAddressResolverInterface(ARC4Contract):
    @arc4.abimethod
    def addresss(self, node: Bytes32, coinType: arc4.UInt64) -> arc4.Address:
        """
        Get the address for a node
        """
        return arc4.Address(self._address(node.bytes, coinType.native))

    @subroutine
    def _address(self, node: Bytes, coinType: UInt64) -> Account:
        """
        Get the address for a node
        """
        return Global.zero_address


class VNSAddressResolver(VNSAddressResolverInterface, VNSBaseResolver):
    def __init__(self) -> None:
        self.versionable_addresses = BoxMap(Bytes48, Account, key_prefix=b"addrs_")

    @subroutine
    def _address(self, node: Bytes, coinType: UInt64) -> Account:
        record_version_bytes = arc4.UInt64(self._recordVersions(node)).bytes
        return self.versionable_addresses.get(
            key=Bytes48.from_bytes(record_version_bytes + node + op.itob(coinType)),
            default=Global.zero_address,
        )

    @arc4.abimethod
    def setAddress(
        self, node: Bytes32, coinType: arc4.UInt64, newAddress: arc4.Address
    ) -> None:
        self.authorized(node)
        arc4.emit(AddressChanged(node, coinType, newAddress))
        self._setAddress(node.bytes, coinType.native, newAddress.native)

    @subroutine
    def _setAddress(self, node: Bytes, coinType: UInt64, newAddress: Account) -> None:
        record_version_bytes = arc4.UInt64(self._recordVersions(node)).bytes
        self.versionable_addresses[
            Bytes48.from_bytes(record_version_bytes + node + op.itob(coinType))
        ] = newAddress


class VNSPublicResolver(VNSAddrResolver, VNSAddressResolver):
    def __init__(self) -> None:
        self.vns = UInt64(0)

    @arc4.abimethod
    def post_update(self, vns: arc4.UInt64) -> None:
        self.vns = vns.native
