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
    ensure_budget,
    OpUpFeeSource,
)
from utils import require_payment, close_offline_on_delete

Bytes4: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[4]]
Bytes8: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[8]]
Bytes22: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[22]]
Bytes26: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[26]]
Bytes32: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[32]]
Bytes40: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[40]]
Bytes48: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[48]]
Bytes58: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[58]]
Bytes54: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[54]]
Bytes59: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[59]]
Bytes62: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[62]]
Bytes64: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[64]]
Bytes128: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[128]]
Bytes168: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[166]]
Bytes256: typing.TypeAlias = arc4.StaticArray[arc4.Byte, typing.Literal[256]]

mint_fee = 0
mint_cost = 336700

#                            _     _
#   _____      ___ __   __ _| |__ | | ___
#  / _ \ \ /\ / / '_ \ / _` | '_ \| |/ _ \
# | (_) \ V  V /| | | | (_| | |_) | |  __/
#  \___/ \_/\_/ |_| |_|\__,_|_.__/|_|\___|


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


#      _        _              _     _
#  ___| |_ __ _| | _____  __ _| |__ | | ___
# / __| __/ _` | |/ / _ \/ _` | '_ \| |/ _ \
# \__ \ || (_| |   <  __/ (_| | |_) | |  __/
# |___/\__\__,_|_|\_\___|\__,_|_.__/|_|\___|


class PartKeyInfo(arc4.Struct):
    address: arc4.Address
    vote_key: Bytes32
    selection_key: Bytes32
    vote_first: arc4.UInt64
    vote_last: arc4.UInt64
    vote_key_dilution: arc4.UInt64
    state_proof_key: Bytes64


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


#                                  _       _     _
#  _   _ _ __   __ _ _ __ __ _  __| | __ _| |__ | | ___
# | | | | '_ \ / _` | '__/ _` |/ _` |/ _` | '_ \| |/ _ \
# | |_| | |_) | (_| | | | (_| | (_| | (_| | |_) | |  __/
#  \__,_| .__/ \__, |_|  \__,_|\__,_|\__,_|_.__/|_|\___|
#       |_|    |___/


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


#      _            _                   _     _
#   __| | ___ _ __ | | ___  _   _  __ _| |__ | | ___
#  / _` |/ _ \ '_ \| |/ _ \| | | |/ _` | '_ \| |/ _ \
# | (_| |  __/ |_) | | (_) | |_| | (_| | |_) | |  __/
#  \__,_|\___| .__/|_|\___/ \__, |\__,_|_.__/|_|\___|
#            |_|            |___/


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


#  _            _         _     _
# | | ___   ___| | ____ _| |__ | | ___
# | |/ _ \ / __| |/ / _` | '_ \| |/ _ \
# | | (_) | (__|   < (_| | |_) | |  __/
# |_|\___/ \___|_|\_\__,_|_.__/|_|\___|


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


#                 ____   ___   ___
#   __ _ _ __ ___|___ \ / _ \ / _ \
#  / _` | '__/ __| __) | | | | | | |
# | (_| | | | (__ / __/| |_| | |_| |
#  \__,_|_|  \___|_____|\___/ \___/
#


class arc200_Transfer(arc4.Struct):
    sender: arc4.Address
    recipient: arc4.Address
    amount: arc4.UInt256


class arc200_Approval(arc4.Struct):
    owner: arc4.Address
    spender: arc4.Address
    amount: arc4.UInt256


class arc200_approval(arc4.Struct):
    owner: arc4.Address
    spender: arc4.Address


class ARC200TokenInterface(ARC4Contract):

    @arc4.abimethod(readonly=True)
    def arc200_name(self) -> Bytes32:
        """
        Get name of token.
        """
        return Bytes32.from_bytes(Bytes())

    @arc4.abimethod(readonly=True)
    def arc200_symbol(self) -> Bytes8:
        """
        Get symbol of token.
        """
        return Bytes8.from_bytes(Bytes())

    @arc4.abimethod(readonly=True)
    def arc200_decimals(self) -> arc4.UInt8:
        """
        Get decimals of token.
        """
        return arc4.UInt8(UInt64())

    @arc4.abimethod(readonly=True)
    def arc200_totalSupply(self) -> arc4.UInt256:
        """
        Get total supply of token.
        """
        return arc4.UInt256(0)

    @arc4.abimethod(readonly=True)
    def arc200_balanceOf(self, account: arc4.Address) -> arc4.UInt256:
        """
        Get balance of account.
        """
        return arc4.UInt256(0)

    @arc4.abimethod
    def arc200_transferFrom(
        self, sender: arc4.Address, recipient: arc4.Address, amount: arc4.UInt256
    ) -> arc4.Bool:
        """
        Transfer tokens from sender to recipient.
        """
        return arc4.Bool(True)

    @arc4.abimethod
    def arc200_approve(self, spender: arc4.Address, amount: arc4.UInt256) -> arc4.Bool:
        """
        Approve spender to spend amount.
        """
        return arc4.Bool(True)

    @arc4.abimethod(readonly=True)
    def arc200_allowance(
        self, owner: arc4.Address, spender: arc4.Address
    ) -> arc4.UInt256:
        """
        Get allowance of spender.
        """
        return arc4.UInt256(0)


class ARC200Token(ARC200TokenInterface):
    def __init__(self) -> None:
        # arc200 state
        self.name = String()
        self.symbol = String()
        self.decimals = UInt64()
        self.totalSupply = BigUInt()
        self.balances = BoxMap(Account, BigUInt)
        self.approvals = BoxMap(Bytes, BigUInt)

    # @subroutine
    # def _pad_right(self, string: String, char: Bytes, length: UInt64) -> Bytes:
    # return Bytes(string.bytes + char * (length - len(string.bytes)))

    @arc4.abimethod(readonly=True)
    def arc200_name(self) -> Bytes32:
        return Bytes32.from_bytes((self.name.bytes + Bytes.from_hex("00" * 32))[0:32])

    @arc4.abimethod(readonly=True)
    def arc200_symbol(self) -> Bytes8:
        return Bytes8.from_bytes((self.symbol.bytes + Bytes.from_hex("00" * 8))[0:8])

    @arc4.abimethod(readonly=True)
    def arc200_decimals(self) -> arc4.UInt8:
        return arc4.UInt8(self.decimals)

    @arc4.abimethod(readonly=True)
    def arc200_totalSupply(self) -> arc4.UInt256:
        return arc4.UInt256(self.totalSupply)

    @arc4.abimethod(readonly=True)
    def arc200_balanceOf(self, account: arc4.Address) -> arc4.UInt256:
        return arc4.UInt256(self._balanceOf(account.native))

    @subroutine
    def _balanceOf(self, account: Account) -> BigUInt:
        return self.balances.get(key=account, default=BigUInt(0))

    @arc4.abimethod(readonly=True)
    def arc200_allowance(
        self, owner: arc4.Address, spender: arc4.Address
    ) -> arc4.UInt256:
        return arc4.UInt256(self._allowance(owner.native, spender.native))

    @subroutine
    def _allowance(self, owner: Account, spender: Account) -> BigUInt:
        return self.approvals.get(
            key=op.sha256(owner.bytes + spender.bytes),
            default=BigUInt(0),
        )

    @arc4.abimethod
    def arc200_transferFrom(
        self, sender: arc4.Address, recipient: arc4.Address, amount: arc4.UInt256
    ) -> arc4.Bool:
        self._transferFrom(sender.native, recipient.native, amount.native)
        return arc4.Bool(True)

    @subroutine
    def _transferFrom(
        self, sender: Account, recipient: Account, amount: BigUInt
    ) -> None:
        spender = Txn.sender
        spender_allowance = self._allowance(sender, spender)
        assert spender_allowance >= amount, "insufficient approval"
        new_spender_allowance = spender_allowance - amount
        self._approve(sender, spender, new_spender_allowance)
        self._transfer(sender, recipient, amount)

    @arc4.abimethod
    def arc200_transfer(
        self, recipient: arc4.Address, amount: arc4.UInt256
    ) -> arc4.Bool:
        self._transfer(Txn.sender, recipient.native, amount.native)
        return arc4.Bool(True)

    @subroutine
    def _transfer(self, sender: Account, recipient: Account, amount: BigUInt) -> None:
        sender_balance = self._balanceOf(sender)
        recipient_balance = self._balanceOf(recipient)
        assert sender_balance >= amount, "insufficient balance"
        if sender == recipient:
            self.balances[sender] = sender_balance  # current balance or zero
        else:
            self.balances[sender] = sender_balance - amount
            self.balances[recipient] = recipient_balance + amount
        arc4.emit(
            arc200_Transfer(
                arc4.Address(sender), arc4.Address(recipient), arc4.UInt256(amount)
            )
        )

    @arc4.abimethod
    def arc200_approve(self, spender: arc4.Address, amount: arc4.UInt256) -> arc4.Bool:
        self._approve(Txn.sender, spender.native, amount.native)
        return arc4.Bool(True)

    @subroutine
    def _approve(self, owner: Account, spender: Account, amount: BigUInt) -> None:
        self.approvals[op.sha256(owner.bytes + spender.bytes)] = amount
        arc4.emit(
            arc200_Approval(
                arc4.Address(owner), arc4.Address(spender), arc4.UInt256(amount)
            )
        )


class OSARC200Token(ARC200Token, Upgradeable, Stakeable):
    def __init__(self) -> None:  # pragma: no cover
        # arc200 state
        self.name = String()
        self.symbol = String()
        self.decimals = UInt64()
        self.totalSupply = BigUInt()
        # balances
        # approvals
        # deployable state
        # self.parent_id = UInt64()
        # self.deployer = Account()
        # ownable state
        self.owner = Account()
        # upgradeable state
        self.contract_version = UInt64()
        self.deployment_version = UInt64()
        self.updatable = bool(1)
        self.upgrader = Global.creator_address
        # stakeable state
        self.delegate = Account()
        self.stakeable = bool(1)

    @arc4.abimethod
    def post_update(self) -> None:
        self.delegate = Account(
            "RTKWX3FTDNNIHMAWHK5SDPKH3VRPPW7OS5ZLWN6RFZODF7E22YOBK2OGPE"
        )

    @subroutine
    def _get_length(self, bytes: Bytes) -> UInt64:
        i = UInt64(0)
        while True:
            b = bytes[i]
            if b == Bytes.from_hex("00"):
                break
            i += 1
        return i

    @arc4.abimethod
    def mint(
        self,
        receiver: arc4.Address,
        name: Bytes32,
        symbol: Bytes8,
        decimals: arc4.UInt8,
        totalSupply: arc4.UInt256,
    ) -> None:
        """
        Mint tokens
        """
        assert self.owner == Global.zero_address, "owner not initialized"
        assert self.name == "", "name not initialized"
        assert self.symbol == "", "symbol not initialized"
        assert self.totalSupply == 0, "total supply not initialized"
        payment_amount = require_payment(Txn.sender)
        assert payment_amount >= mint_fee, "payment amount accurate"
        self.owner = Txn.sender
        self.name = String.from_bytes(name.bytes[: self._get_length(name.bytes)])
        self.symbol = String.from_bytes(symbol.bytes[: self._get_length(symbol.bytes)])
        self.decimals = decimals.native
        self.totalSupply = totalSupply.native
        self.balances[receiver.native] = totalSupply.native
        arc4.emit(
            arc200_Transfer(
                arc4.Address(Global.zero_address),
                receiver,
                totalSupply,
            )
        )

    # terminal methods

    @arc4.abimethod(allow_actions=[OnCompleteAction.DeleteApplication])
    def killApplication(self) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        close_offline_on_delete(Txn.sender)

    @arc4.abimethod
    def deleteBalance(self, address: arc4.Address) -> None:
        del self.balances[address.native]

    @arc4.abimethod
    def deleteApproval(self, owner: arc4.Address, spender: arc4.Address) -> None:
        del self.approvals[op.sha256(owner.bytes + spender.bytes)]

    @arc4.abimethod
    def deleteBox(self, key: Bytes) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        box = BoxRef(key=key)
        box.delete()


#   __            _
#  / _| __ _  ___| |_ ___  _ __ _   _
# | |_ / _` |/ __| __/ _ \| '__| | | |
# |  _| (_| | (__| || (_) | |  | |_| |
# |_|  \__,_|\___|\__\___/|_|   \__, |
#                               |___/

# class FactoryCreated(arc4.Struct):
#     created_app: arc4.UInt64


# class BaseFactory(Upgradeable):
#     """
#     Base factory for all factories.
#     """

#     def __init__(self) -> None:  # pragma: no cover
#         """
#         Initialize factory.
#         """
#         # upgradeable state
#         self.contract_version = UInt64()
#         self.deployment_version = UInt64()
#         self.updatable = bool(1)
#         self.upgrader = Global.creator_address

#         ##############################################
#         # @arc4.abimethod
#         # def create(self, *args) -> UInt64:
#         #    return UInt64()
#         ##############################################

#     @subroutine
#     def get_initial_payment(self) -> UInt64:
#         """
#         Get initial payment.
#         """
#         payment_amount = require_payment(Txn.sender)
#         mbr_increase = UInt64(mint_cost)
#         min_balance = op.Global.min_balance  # 100000
#         assert (
#             payment_amount >= mbr_increase + min_balance
#         ), "payment amount accurate"  # 131300
#         initial = payment_amount - mbr_increase - min_balance
#         return initial


# class OSARC200TokenFactory(BaseFactory):
#     def __init__(self) -> None:
#         super().__init__()

#     @arc4.abimethod
#     def create(
#         self,
#         # name: Bytes32,
#         # symbol: Bytes8,
#         # decimals: arc4.UInt8,
#         # totalSupply: arc4.UInt256,
#     ) -> UInt64:
#         """
#         Create airdrop.

#         Arguments:
#         - owner, who is the beneficiary
#         - funder, who funded the contract
#         - deadline, funding deadline
#         - initial, initial funded value not including lockup bonus

#         Returns:
#         - app id
#         """
#         ##########################################
#         self.get_initial_payment()
#         ##########################################
#         compiled = compile_contract(
#             OSARC200Token, extra_program_pages=3
#         )  # max extra pages
#         base_app = arc4.arc4_create(OSARC200Token, compiled=compiled).created_app
#         arc4.emit(FactoryCreated(arc4.UInt64(base_app.id)))
#         arc4.abi_call(  # inherit upgrader
#             OSARC200Token.grant_upgrader,
#             Global.creator_address,
#             app_id=base_app,
#         )
#         itxn.Payment(
#             receiver=base_app.address, amount=op.Global.min_balance + 31300, fee=0
#         ).submit()
#         ##########################################
#         return base_app.id


#                _____ _____
#   __ _ _ __ __|___  |___ /
#  / _` | '__/ __| / /  |_ \
# | (_| | | | (__ / /  ___) |
#  \__,_|_|  \___/_/  |____/
#


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
    node: Bytes32  # VNS Namehash or Node
    valid: arc4.Bool  # Indicates whether the domain is still valid
    registration_date: arc4.UInt64  # Timestamp of when the domain was registered
    label: Bytes256  # Custom label or additional identifier (optional)


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
        return arc4.Address(self._ownerOf(tokenId.native))

    @subroutine
    def _ownerOf(self, tokenId: BigUInt) -> Account:
        return self._nft_owner(tokenId).native

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
            node=Bytes32.from_bytes(Bytes()),
            valid=arc4.Bool(False),
            registration_date=arc4.UInt64(0),
            label=Bytes256.from_bytes(Bytes()),
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

    @arc4.abimethod
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
    def post_update(self, resolver: arc4.UInt64) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        self.registry_resolver = resolver.native
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

    # registry methods

    @arc4.abimethod
    def setRegistryResolver(self, resolver: arc4.UInt64) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        self.registry_resolver = resolver.native

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


#  _            _                         _
# | |_ _____  _| |_   _ __ ___  ___  ___ | |_   _____ _ __
# | __/ _ \ \/ / __| | '__/ _ \/ __|/ _ \| \ \ / / _ \ '__|
# | ||  __/>  <| |_  | | |  __/\__ \ (_) | |\ V /  __/ |
#  \__\___/_/\_\\__| |_|  \___||___/\___/|_| \_/ \___|_|
#


class TextChanged(arc4.Struct):
    node: Bytes32
    key: Bytes22
    value: Bytes256


class VNSTextResolverInterface(ARC4Contract):
    @arc4.abimethod
    def text(self, node: Bytes32, key: Bytes22) -> Bytes256:
        """
        Get the text for a node
        """
        return Bytes256.from_bytes(self._text(node.bytes, key.bytes))

    @subroutine
    def _text(self, node: Bytes, key: Bytes) -> Bytes:
        """
        Get the text for a node
        """
        return Bytes(b"\x00" * 256)


class VNSTextResolver(VNSTextResolverInterface, VNSBaseResolver):
    def __init__(self) -> None:
        self.versionable_texts = BoxMap(Bytes62, Bytes256, key_prefix=b"t_")

    @subroutine
    def _text(self, node: Bytes, key: Bytes) -> Bytes:
        record_version_bytes = arc4.UInt64(self._recordVersions(node)).bytes
        return self.versionable_texts.get(
            key=Bytes62.from_bytes(record_version_bytes + node + key),
            default=Bytes256.from_bytes(Bytes(b"\x00" * 256)),
        ).bytes

    @arc4.abimethod
    def setText(self, node: Bytes32, key: Bytes22, value: Bytes256) -> None:
        self.authorized(node)
        arc4.emit(TextChanged(node, key, value))
        self._setText(node.bytes, key.bytes, value.bytes)

    @subroutine
    def _setText(self, node: Bytes, key: Bytes, value: Bytes) -> None:
        record_version_bytes = arc4.UInt64(self._recordVersions(node)).bytes
        self.versionable_texts[
            Bytes62.from_bytes(record_version_bytes + node + key)
        ] = Bytes256.from_bytes(value)

    @arc4.abimethod
    def deleteText(self, node: Bytes32, key: Bytes22) -> None:
        self.authorized(node)
        self._deleteText(node.bytes, key.bytes)

    @subroutine
    def _deleteText(self, node: Bytes, key: Bytes) -> None:
        del self.versionable_texts[Bytes62.from_bytes(node + key)]


#                                                   _
#  _ __   __ _ _ __ ___   ___   _ __ ___  ___  ___ | |_   _____ _ __
# | '_ \ / _` | '_ ` _ \ / _ \ | '__/ _ \/ __|/ _ \| \ \ / / _ \ '__|
# | | | | (_| | | | | | |  __/ | | |  __/\__ \ (_) | |\ V /  __/3|
# |_| |_|\__,_|_| |_| |_|\___| |_|  \___||___/\___/|_| \_/ \___|_|
#


class NameChanged(arc4.Struct):
    node: Bytes32
    name: Bytes256


class VNSNameResolverInterface(ARC4Contract):
    @arc4.abimethod(readonly=True)
    def name(self, node: Bytes32) -> Bytes256:
        """
        Get the name for a node
        """
        return Bytes256.from_bytes(self._name(node.bytes))

    @subroutine
    def _name(self, node: Bytes) -> Bytes:
        """
        Get the name for a node
        """
        return Bytes(b"\x00" * 256)


class VNSNameResolver(VNSNameResolverInterface, VNSBaseResolver):
    def __init__(self) -> None:
        self.versionable_names = BoxMap(Bytes40, Bytes256, key_prefix=b"names_")

    @subroutine
    def _name(self, node: Bytes) -> Bytes:
        record_version_bytes = arc4.UInt64(self._recordVersions(node)).bytes
        return self.versionable_names.get(
            key=Bytes40.from_bytes(record_version_bytes + node),
            default=Bytes256.from_bytes(Bytes(b"\x00" * 256)),
        ).bytes

    @arc4.abimethod
    def setName(self, node: Bytes32, newName: Bytes256) -> None:
        self.authorized(node)
        arc4.emit(NameChanged(node, newName))
        self._setName(node.bytes, newName.bytes)

    @subroutine
    def _setName(self, node: Bytes, newName: Bytes) -> None:
        record_version_bytes = arc4.UInt64(self._recordVersions(node)).bytes
        self.versionable_names[Bytes40.from_bytes(record_version_bytes + node)] = (
            Bytes256.from_bytes(newName)
        )

    @arc4.abimethod
    def deleteName(self, node: Bytes32) -> None:
        self.authorized(node)
        self._deleteName(node.bytes)

    @subroutine
    def _deleteName(self, node: Bytes) -> None:
        record_version_bytes = arc4.UInt64(self._recordVersions(node)).bytes
        del self.versionable_names[Bytes40.from_bytes(record_version_bytes + node)]


#            _     _                            _
#   __ _  __| | __| |_ __   _ __ ___  ___  ___ | |_   _____ _ __
#  / _` |/ _` |/ _` | '__| | '__/ _ \/ __|/ _ \| \ \ / / _ \ '__|
# | (_| | (_| | (_| | |    | | |  __/\__ \ (_) | |\ V /  __/ |
#  \__,_|\__,_|\__,_|_|    |_|  \___||___/\___/|_| \_/ \___|_|
#


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

    @arc4.abimethod
    def addr(self, node: Bytes32) -> arc4.Address:
        return arc4.Address(self._addr(node.bytes))

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


#                      _
#  _ __ ___  ___  ___ | |_   _____ _ __
# | '__/ _ \/ __|/ _ \| \ \ / / _ \ '__|
# | | |  __/\__ \ (_) | |\ V /  __/ |
# |_|  \___||___/\___/|_| \_/ \___|_|
#


class VNSPublicResolver(
    VNSNameResolver, VNSAddrResolver, VNSTextResolver, Stakeable, Upgradeable
):
    def __init__(self) -> None:
        self.vns = UInt64(0)
        # ownable state
        self.owner = Global.creator_address
        # upgradable state
        self.contract_version = UInt64()
        self.deployment_version = UInt64()
        self.updatable = bool(1)
        self.upgrader = Global.creator_address
        # stakeable state
        self.delegate = Account()  # zero address
        self.stakeable = bool(1)  # 1 (Default unlocked)

    @arc4.abimethod
    def post_update(self, vns: arc4.UInt64) -> None:
        self.vns = vns.native

    # terminal methods for testing

    @arc4.abimethod(allow_actions=[OnCompleteAction.DeleteApplication])
    def killApplication(self) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        close_offline_on_delete(Txn.sender)

    @arc4.abimethod
    def deleteAddr(self, node: Bytes32) -> None:
        version = arc4.UInt64(self._recordVersions(node.bytes))
        assert Txn.sender == self.upgrader, "must be upgrader"
        del self.versionable_addrs[Bytes40.from_bytes(version.bytes + node.bytes)]


class Reservation(arc4.Struct):
    owner: arc4.Address
    length: arc4.UInt64
    price: arc4.UInt64
    name: Bytes256


class ReservationSet(arc4.Struct):
    node: Bytes32
    owner: arc4.Address
    name: Bytes256
    length: arc4.UInt64
    price: arc4.UInt64


# RSVP-1 FCFS

# class RSVP(ARC4Contract):
#     def __init__(self) -> None:
#         self.reservations = BoxMap(Bytes32, Reservation, key_prefix=b"rsvp_")
#         self.accounts = BoxMap(Account, Bytes32, key_prefix=b"addr_")

#     @subroutine
#     def _reservation(self, node: Bytes) -> Reservation:
#         return self.reservations.get(
#             key=Bytes32.from_bytes(node),
#             default=Reservation(
#                 owner=arc4.Address(Global.zero_address),
#                 length=arc4.UInt64(0),
#                 price=arc4.UInt64(0),
#                 name=Bytes256.from_bytes(
#                     Bytes.from_base64(
#                         "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
#                     ),
#                 ),
#             ),
#         )

#     @arc4.abimethod(readonly=True)
#     def reservation_owner(self, node: Bytes32) -> arc4.Address:
#         return arc4.Address(self._reservation_owner(node.bytes))

#     @subroutine
#     def _reservation_owner(self, node: Bytes) -> Account:
#         return self._reservation(node).owner.native

#     @arc4.abimethod(readonly=True)
#     def reservation_price(self, node: Bytes32) -> arc4.UInt64:
#         return arc4.UInt64(self._reservation_price(node.bytes))

#     @subroutine
#     def _reservation_price(self, node: Bytes) -> UInt64:
#         return self._reservation(node).price.native

#     @arc4.abimethod(readonly=True)
#     def reservation_name(self, node: Bytes32) -> Bytes256:
#         return Bytes256.from_bytes(self._reservation_name(node.bytes))

#     @subroutine
#     def _reservation_name(self, node: Bytes) -> Bytes:
#         return self._reservation(node).name.bytes

#     @arc4.abimethod(readonly=True)
#     def account_node(self, account: arc4.Address) -> Bytes32:
#         return Bytes32.from_bytes(self._account_node(account.native))

#     @subroutine
#     def _account_node(self, account: Account) -> Bytes:
#         return self.accounts.get(
#             key=account,
#             default=Bytes32.from_bytes(
#                 Bytes.from_base64("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
#             ),
#         ).bytes

#     @arc4.abimethod(readonly=True)
#     def price(self, length: arc4.UInt64) -> arc4.UInt64:
#         return arc4.UInt64(self._price(length.native))

#     @subroutine
#     def _price(self, length: UInt64) -> UInt64:
#         # 1 character name 50,000 VOI (~100 USD)
#         if length == UInt64(1):
#             return UInt64(50000)
#         # 2 character name 30,000 VOI (~75 USD)
#         elif length == UInt64(2):
#             return UInt64(30000)
#         # 3 character name 20,000 VOI (~50 USD)
#         elif length == UInt64(3):
#             return UInt64(20000)
#         # 4 character name 10,000 VOI (~25 USD)
#         elif length == UInt64(4):
#             return UInt64(10000)
#         # 5 character name 5,000 VOI (~10 USD)
#         elif length == UInt64(5):
#             return UInt64(5000)
#         # 6 character name 2,000 VOI (~5 USD)
#         elif length == UInt64(6):
#             return UInt64(2000)
#         # 7 or more character name 1,000 VOI (~1 USD)
#         else:
#             return UInt64(1000)

#     @subroutine
#     def _setReservation(
#         self, owner: Account, node: Bytes, name: Bytes, length: UInt64
#     ) -> None:
#         self.reservations[Bytes32.from_bytes(node)] = Reservation(
#             owner=arc4.Address(owner),
#             length=arc4.UInt64(length),
#             price=arc4.UInt64(self._price(length)),
#             name=Bytes256.from_bytes(name),
#         )
#         self.accounts[Txn.sender] = Bytes32.from_bytes(node)

#     @arc4.abimethod
#     def reserve(self, node: Bytes32, name: Bytes256, length: arc4.UInt64) -> None:
#         assert Bytes32.from_bytes(self._account_node(Txn.sender)) == Bytes32.from_bytes(
#             Bytes.from_base64("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
#         ), "sender must not be registered"
#         assert (
#             self._reservation(node.bytes).owner.native == Global.zero_address
#         ), "node must be available"
#         assert length.native <= UInt64(256), "name must be less than 256 bytes"
#         payment = require_payment(Txn.sender)
#         price = self._price(length.native)
#         assert payment >= price, "payment must be greater than price"
#         arc4.emit(
#             ReservationSet(
#                 node=node,
#                 owner=arc4.Address(Txn.sender),
#                 name=name,
#                 length=length,
#                 price=arc4.UInt64(price),
#             )
#         )
#         self._setReservation(Txn.sender, node.bytes, name.bytes, length.native)

#     @arc4.abimethod
#     def release(self, node: Bytes32) -> None:
#         self._release(Txn.sender, node.bytes)

#     @subroutine
#     def _release(self, owner: Account, node: Bytes) -> None:
#         assert self._account_node(owner) == node, "sender must be registered"
#         assert self._reservation_owner(node) == owner, "sender must be owner"
#         arc4.emit(
#             ReservationSet(
#                 node=Bytes32.from_bytes(node),
#                 owner=arc4.Address(Global.zero_address),
#                 name=Bytes256.from_bytes(self._reservation_name(node)),
#                 length=arc4.UInt64(self._reservation_length(node)),
#                 price=arc4.UInt64(UInt64(0)),
#             )
#         )
#         itxn.Payment(
#             amount=self._reservation_price(node),
#             receiver=self._reservation_owner(node),
#             fee=0,
#         ).submit()
#         del self.reservations[Bytes32.from_bytes(node)]
#         del self.accounts[owner]

# RSVP-2 Auctions


class RSVP(ARC4Contract):
    def __init__(self) -> None:
        self.reservations = BoxMap(Bytes32, Reservation, key_prefix=b"rsvp_")
        self.accounts = BoxMap(Account, Bytes32, key_prefix=b"addr_")

    @subroutine
    def _reservation(self, node: Bytes) -> Reservation:
        return self.reservations.get(
            key=Bytes32.from_bytes(node),
            default=Reservation(
                owner=arc4.Address(Global.zero_address),
                length=arc4.UInt64(0),
                price=arc4.UInt64(0),
                name=Bytes256.from_bytes(
                    Bytes.from_base64(
                        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                    ),
                ),
            ),
        )

    @arc4.abimethod(readonly=True)
    def reservation_owner(self, node: Bytes32) -> arc4.Address:
        return arc4.Address(self._reservation_owner(node.bytes))

    @subroutine
    def _reservation_owner(self, node: Bytes) -> Account:
        return self._reservation(node).owner.native

    @arc4.abimethod(readonly=True)
    def reservation_price(self, node: Bytes32) -> arc4.UInt64:
        return arc4.UInt64(self._reservation_price(node.bytes))

    @subroutine
    def _reservation_price(self, node: Bytes) -> UInt64:
        return self._reservation(node).price.native

    @arc4.abimethod(readonly=True)
    def reservation_name(self, node: Bytes32) -> Bytes256:
        return Bytes256.from_bytes(self._reservation_name(node.bytes))

    @subroutine
    def _reservation_name(self, node: Bytes) -> Bytes:
        return self._reservation(node).name.bytes

    @arc4.abimethod(readonly=True)
    def reservation_length(self, node: Bytes32) -> arc4.UInt64:
        return arc4.UInt64(self._reservation_length(node.bytes))

    @subroutine
    def _reservation_length(self, node: Bytes) -> UInt64:
        return self._reservation(node).length.native

    @arc4.abimethod(readonly=True)
    def account_node(self, account: arc4.Address) -> Bytes32:
        return Bytes32.from_bytes(self._account_node(account.native))

    @subroutine
    def _account_node(self, account: Account) -> Bytes:
        return self.accounts.get(
            key=account,
            default=Bytes32.from_bytes(
                Bytes.from_base64("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
            ),
        ).bytes

    @subroutine
    def _setReservation(
        self, owner: Account, node: Bytes, name: Bytes, length: UInt64, price: UInt64
    ) -> None:
        previous_owner = self._reservation_owner(node)
        self.reservations[Bytes32.from_bytes(node)] = Reservation(
            owner=arc4.Address(owner),
            name=Bytes256.from_bytes(name),
            length=arc4.UInt64(length),
            price=arc4.UInt64(price),
        )
        del self.accounts[previous_owner]
        self.accounts[Txn.sender] = Bytes32.from_bytes(node)

    @arc4.abimethod
    def reserve(self, node: Bytes32, name: Bytes256, length: arc4.UInt64) -> None:
        sender_account_node = Bytes32.from_bytes(self._account_node(Txn.sender))
        reservation = self._reservation(node.bytes)
        # ensure up to single registration
        assert sender_account_node == Bytes32.from_bytes(
            Bytes.from_base64("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        ), "sender must not be registered"
        # use for FIFO
        # assert (
        #     self._reservation(node.bytes).owner.native == Global.zero_address
        # ), "node must be available"
        assert length.native <= UInt64(256), "name must be less than 256 bytes"
        new_price = require_payment(Txn.sender)
        price = reservation.price.native
        assert new_price > price, "payment must be greater than price"
        arc4.emit(
            ReservationSet(
                node=node,
                owner=arc4.Address(Txn.sender),
                name=name,
                length=length,
                price=arc4.UInt64(new_price),
            )
        )
        self._setReservation(
            Txn.sender, node.bytes, name.bytes, length.native, new_price
        )

    @arc4.abimethod
    def release(self, node: Bytes32) -> None:
        self._release(Txn.sender, node.bytes)

    @subroutine
    def _release(self, owner: Account, node: Bytes) -> None:
        assert self._account_node(owner) == node, "sender must be registered"
        arc4.emit(
            ReservationSet(
                node=Bytes32.from_bytes(node),
                owner=arc4.Address(Global.zero_address),
                name=Bytes256.from_bytes(self._reservation_name(node)),
                length=arc4.UInt64(self._reservation_length(node)),
                price=arc4.UInt64(UInt64(0)),
            )
        )
        # itxn.Payment(
        #     amount=self._reservation_price(node),
        #     receiver=self._reservation_owner(node),
        #     fee=0,
        # ).submit()
        del self.reservations[Bytes32.from_bytes(node)]
        del self.accounts[owner]


#  _ __ _____   ___ __
# | '__/ __\ \ / / '_ \
# | |  \__ \\ V /| |_) |
# |_|  |___/ \_/ | .__/
#                |_|


class VNSRSVP(RSVP, Stakeable, Upgradeable):
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

    # admin methods

    @arc4.abimethod
    def admin_reserve(
        self,
        owner: arc4.Address,
        node: Bytes32,
        name: Bytes256,
        length: arc4.UInt64,
        price: arc4.UInt64,
    ) -> None:
        assert self.owner == Txn.sender, "sender must be owner"
        assert Bytes32.from_bytes(
            self._account_node(owner.native)
        ) == Bytes32.from_bytes(
            Bytes.from_base64("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        ), "sender must not be registered"
        assert (
            self._reservation(node.bytes).owner.native == Global.zero_address
        ), "node must be available"
        assert length.native <= UInt64(256), "name must be less than 256 bytes"
        arc4.emit(
            ReservationSet(
                node=node,
                owner=owner,
                name=name,
                length=length,
                price=price,
            )
        )
        self._setReservation(
            Txn.sender, node.bytes, name.bytes, length.native, price.native
        )

    # @arc4.abimethod
    # def admin_release(self, owner: arc4.Address, node: Bytes32) -> None:
    #     assert self.owner == Txn.sender, "sender must be owner"
    #     self._release(owner.native, node.bytes)

    # terminal methods

    @arc4.abimethod(allow_actions=[OnCompleteAction.DeleteApplication])
    def killApplication(self) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        close_offline_on_delete(Txn.sender)

    @arc4.abimethod
    def killReservation(self, node: Bytes32) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        del self.reservations[node]

    @arc4.abimethod
    def killAccount(self, account: arc4.Address) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        del self.accounts[account.native]

    @arc4.abimethod
    def deleteBox(self, key: Bytes) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        box = BoxRef(key=key)
        box.delete()


#                 _     _
#  _ __ ___  __ _(_)___| |_ _ __ __ _ _ __
# | '__/ _ \/ _` | / __| __| '__/ _` | '__|
# | | |  __/ (_| | \__ \ |_| | | (_| | |
# |_|  \___|\__, |_|___/\__|_|  \__,_|_|
#           |___/

# class arc72_nft_data(arc4.Struct):
#     owner: arc4.Address
#     approved: arc4.Address
#     index: arc4.UInt256
#     token_id: arc4.UInt256
#     metadata: Bytes256
#     node: arc4.Bytes32  # VNS Namehash or Node
#     expiration: arc4.UInt64  # Expiration timestamp
#     valid: arc4.Bool  # Indicates whether the domain is still valid
#     registration_date: arc4.UInt64  # Timestamp of when the domain was registered
#     label: arc4.Bytes32  # Custom label or additional identifier (optional)

# class arc72_holder_data(arc4.Struct):
#     holder: arc4.Address
#     balance: arc4.UInt256

# https://github.com/ensdomains/ens-contracts/blob/staging/contracts/ethregistrar/BaseRegistrarImplementation.sol


class VNSRegistrar(ARC72Token, Upgradeable, Stakeable):
    def __init__(self) -> None:
        super().__init__()
        # state (core, metadata)
        # self.nft_data = BoxMap(BigUInt, arc72_nft_data)
        # self.nft_operators = BoxMap(Bytes, bool)
        # enumeration state
        self.totalSupply = BigUInt()  # total supply
        # self.nft_index = BoxMap(BigUInt, BigUInt)
        # self.holder_data = BoxMap(Account, arc72_holder_data)
        # registrar state
        self.treasury = Global.creator_address  # treasury address
        self.registry = UInt64(0)  # vns registrar id
        self.payment_token = UInt64(0)  # arc200 token id
        self.root_node = Bytes32.from_bytes(  # root node
            Bytes.from_base64("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        )
        self.grace_period = UInt64(90)  # grace period
        self.controllers = BoxMap(Account, bool)  # controllers
        self.expires = BoxMap(BigUInt, BigUInt)  # expiration timestamps
        self.renewal_base_fee = UInt64(1)  # renewal base fee
        self.base_cost = BigUInt(1_000_000)  # base cost (1 USDC)
        self.cost_multiplier = BigUInt(5)  # cost multiplier (5x)
        self.base_period = UInt64(365 * 24 * 60 * 60)  # base period (1 year)
        # ownable state
        self.owner = Global.creator_address  # owner address
        # upgradeable state
        self.contract_version = UInt64()  # contract version
        self.deployment_version = UInt64()  # deployment version
        self.updatable = bool(1)  # updatable
        self.upgrader = Global.creator_address  # upgrader address
        # stakeable state
        self.delegate = Account()  # delegate address
        self.stakeable = bool(1)  # stakeable

    @arc4.abimethod
    def post_update(
        self, registry: arc4.UInt64, root_node: Bytes32, payment_token: arc4.UInt64
    ) -> None:
        self.registry = registry.native
        self.root_node = root_node.copy()
        self.payment_token = payment_token.native

    # override
    @arc4.abimethod(readonly=True)
    def arc72_ownerOf(self, tokenId: arc4.UInt256) -> arc4.Address:
        """
        Returns the address of the current owner of the NFT with the given tokenId
        """
        return arc4.Address(self._ownerOf(tokenId.native))

    @subroutine
    def _ownerOf(self, tokenId: BigUInt) -> Account:
        if self._expiration(tokenId) < BigUInt(Global.latest_timestamp):
            return Global.current_application_address
        return self._nft_owner(tokenId).native

    # expiration methods

    @arc4.abimethod(readonly=True)
    def expiration(self, tokenId: arc4.UInt256) -> arc4.UInt256:
        return arc4.UInt256(self._expiration(tokenId.native))

    @subroutine
    def _expiration(self, tokenId: BigUInt) -> BigUInt:
        return self.expires.get(key=tokenId, default=BigUInt(0))

    @subroutine
    def _set_expiration(self, tokenId: BigUInt, expiration: BigUInt) -> None:
        self.expires[tokenId] = expiration

    @subroutine
    def _increment_expiration(self, tokenId: BigUInt, duration: BigUInt) -> None:
        expiration = self._expiration(tokenId)
        if expiration <= Global.latest_timestamp:
            self._set_expiration(tokenId, Global.latest_timestamp + duration)
        else:
            self._set_expiration(tokenId, expiration + duration)

    # vns methods

    @arc4.abimethod
    def setResolver(self, resolver: arc4.UInt64) -> None:
        assert Txn.sender == self.owner, "sender must be owner"
        app = Application(resolver.native)
        arc4.abi_call(VNS.setResolver, self.root_node, resolver, app_id=app)

    @subroutine
    def is_live(self, node: Bytes32) -> bool:
        """
        Check if the registrar is live
        """
        owner, _txn = arc4.abi_call(
            VNS.ownerOf, node, app_id=Application(self.registry)
        )
        assert (
            owner == Global.current_application_address
        ), "VNS must be owned by registrar"
        return True

    @subroutine
    def _only_controller(self) -> None:
        """
        Only the controller can call this method
        """
        pass

    @arc4.abimethod
    def get_length(self, name: Bytes32) -> arc4.UInt64:
        return arc4.UInt64(self._get_length(name.bytes))

    @subroutine
    def _get_length(self, bytes: Bytes) -> UInt64:
        i = UInt64(0)
        while i < UInt64(32):
            b = bytes[i]
            if b == Bytes.from_hex("00"):
                break
            i += 1
        return i

    @arc4.abimethod
    def check_name(self, name: Bytes32) -> arc4.Bool:
        ensure_budget(10000, OpUpFeeSource.GroupCredit)  # ensure budget up to 32 chars
        return arc4.Bool(self._check_name(name.bytes[: self.get_length(name).native]))

    @subroutine
    def _check_name(self, bytes: Bytes) -> bool:
        i = UInt64(0)
        while i < bytes.length:
            b = bytes[i]
            if b not in Bytes(b"0123456789abcdefghijklmnopqrstuvwxyz-"):
                return False
            i += 1
        return True

    @arc4.abimethod
    def register(
        self, name: Bytes32, owner: arc4.Address, duration: arc4.UInt256
    ) -> Bytes32:
        """Register a new name"""
        assert self.check_name(name).native, "name must be valid"
        unit = self.base_cost * self.cost_multiplier
        return Bytes32.from_bytes(
            self._register(
                String.from_bytes(name.bytes[: self.get_length(name).native]),
                owner.native,
                duration.native,
                self.payment_token,
                unit,
            )
        )

    @arc4.abimethod
    def register_unit(
        self, name: Bytes32, owner: arc4.Address, duration: arc4.UInt256
    ) -> Bytes32:
        "Register a new name with UNIT"
        assert self.check_name(name).native, "name must be valid"
        payment_token = UInt64(420069)
        unit = BigUInt(5_000_000_000)
        return Bytes32.from_bytes(
            self._register(
                String.from_bytes(name.bytes[: self.get_length(name).native]),
                owner.native,
                duration.native,
                payment_token,
                unit,
            )
        )

    # @arc4.abimethod
    # def register_ausd(
    #     self, name: Bytes32, owner: arc4.Address, duration: arc4.UInt256
    # ) -> Bytes32:
    #     "Register a new name with aUSDC"
    #     payment_token = UInt64(395614)  # USDC
    #     unit = BigUInt(5_000_000)  # 5 USDC
    #     return Bytes32.from_bytes(
    #         self._register(
    #             name.bytes, owner.native, duration.native, payment_token, unit
    #         )
    #     )

    # ------------------------------------------------------------
    # Register a new name (internal)
    # - validate registration
    # - create node hash
    # - calculate costs
    # - mint node as nft
    # - set up DNS records
    # - set expiration
    # ------------------------------------------------------------
    @subroutine
    def _register(
        self,
        name: String,
        owner: Account,
        duration: BigUInt,
        payment_token: UInt64,
        unit: BigUInt,
    ) -> Bytes:
        # ------------------------------------------------------------
        # Validate registration
        # ------------------------------------------------------------
        assert duration >= self.base_period, "duration must be at least 1 year"
        assert duration // self.base_period > BigUInt(
            0
        ), "duration must be a multiple of 1 year"
        # name validation done in check_name ie [0-9a-z-]
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # Create node hash using namehash
        # ------------------------------------------------------------
        label = op.sha256(name.bytes)
        new_node = self._namehash(name)
        # expiration = Global.latest_timestamp + duration
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # check if name is already registered
        #   if name is registered err on mint
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # Calculate costs
        # - pay for storage (network)
        # - pay for registration (arc200)
        # ------------------------------------------------------------
        payment_amount = require_payment(Txn.sender)  # pay min amount for storage
        assert (
            payment_amount >= mint_cost + mint_fee  # 336700 + 0
        ), "payment amount accurate"
        # requires allowance from Txn.sender to this contract

        registration_fee = self._get_price(unit, name.bytes, duration)
        arc4.abi_call(
            ARC200Token.arc200_transferFrom,
            arc4.Address(Txn.sender),
            arc4.Address(self.treasury),
            arc4.UInt256(registration_fee),
            app_id=Application(payment_token),
        )
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # mint node as nft, fails if already minted
        # token_id =
        # ------------------------------------------------------------
        self._mint(
            owner,
            new_node,
            name,
        )
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # Set up record
        # ------------------------------------------------------------
        rnode, _txn = arc4.abi_call(
            VNS.setSubnodeOwner,
            self.root_node,
            Bytes32.from_bytes(label),
            arc4.Address(owner),
            app_id=Application(self.registry),
        )
        # ------------------------------------------------------------
        # setSubnodeOwner returns the new node hash computed remotely
        # assert it matches the one we calculated locally
        assert rnode.bytes == new_node, "node mismatch"
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # set expiration
        # ------------------------------------------------------------
        self._increment_expiration(BigUInt.from_bytes(new_node), duration)
        # ------------------------------------------------------------

        return new_node

    # renewal methods
    #  anyone can renew (extend lease)
    #  should be able to renew even if expired
    #  should be able to renew even if not expired
    #  should be able to renew even if expired but grace period not over
    #  should not be able to renew if grace period over

    @arc4.abimethod
    def renew(self, name: arc4.String, duration: arc4.UInt256) -> None:
        """Renew an existing registration"""
        unit = self.base_cost * self.cost_multiplier
        self._renew(name.native, duration.native, unit)

    @subroutine
    def _renew(self, name: String, duration: BigUInt, unit: BigUInt) -> None:
        node = self._namehash(name)
        token_id = BigUInt.from_bytes(node)

        # do not require owner to renew

        # Verify token exists
        nft = self._nft_data(token_id)
        assert nft.index != 0, "name not registered"
        # why not let anyone renew as long as they pay?

        # Calculate renewal fee
        renewal_fee = self._get_price(unit, name.bytes, duration)

        # Receive payment
        payment = require_payment(Txn.sender)
        assert payment >= self.renewal_base_fee, "insufficient payment"
        arc4.abi_call(  # receive payment
            ARC200Token.arc200_transferFrom,
            Txn.sender,
            self.treasury,
            arc4.UInt256(renewal_fee),
            app_id=Application(self.payment_token),
        )

        # Update expiration
        self._increment_expiration(token_id, duration)

    # mint methods

    @arc4.abimethod
    def mint(
        self,
        to: arc4.Address,
        nodeId: Bytes32,
        nodeName: arc4.String,
        # duration: arc4.UInt256,
    ) -> arc4.UInt256:
        """
        Mint a new NFT
        arguments:
            to: address
            nodeId: node
            nodeName: label
            duration: duration
        returns:
            tokenId: tokenId
        """
        self._only_controller()
        return arc4.UInt256(
            self._mint(
                to.native,
                nodeId.bytes,
                nodeName.native,
            )
        )

    @subroutine
    def _mint(
        self,
        to: Account,
        nodeId: Bytes,
        nodeName: String,
        # duration: BigUInt
    ) -> BigUInt:
        """
        Mint a new NFT
        """
        # assert duration > 0, "duration must be greater than 0"

        if nodeId == self.root_node.bytes:
            assert Txn.sender == self.owner, "only owner can mint on root node"

        # bigNodeId = BigUInt.from_bytes(nodeId)

        # parent_nft_data = self._nft_data(bigNodeId)

        # assert parent_nft_data.index != 0, "parent node must exist"

        # assert "." not in nodeName, "node name must not contain a dot"
        # assert nodeName.bytes.length > 0, "node name must not be empty"

        # if nodeId == root_node_id:
        #     name = nodeName + "."
        # else:
        #     name = nodeName + "." + String.from_bytes(parent_nft_data.node_name.bytes)

        bigTokenId = arc4.UInt256.from_bytes(
            nodeId
        ).native  # simply convert nodeId to tokenId

        nft_data = self._nft_data(bigTokenId)

        # prevent re-registration
        assert nft_data.index == 0, "token must not exist"

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
            node=Bytes32.from_bytes(nodeId),
            valid=arc4.Bool(True),
            registration_date=arc4.UInt64(Global.latest_timestamp),
            label=Bytes256.from_bytes(nodeName.bytes),
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

    # check availability using owner of

    # expiration methods

    @arc4.abimethod
    def is_expired(self, token_id: arc4.UInt256) -> arc4.Bool:
        """
        Check if a name has expired
        arguments:
            token_id: tokenId
        returns:
            expired: bool
        """
        return arc4.Bool(self._is_expired(token_id.native))

    @subroutine
    def _is_expired(self, token_id: BigUInt) -> bool:
        """
        Check if a name has expired
        arguments:
            token_id: tokenId
        returns:
            expired: bool
        """
        expiration = self._expiration(token_id)
        is_expired = expiration + self.grace_period > Global.latest_timestamp
        return is_expired

    @arc4.abimethod
    def reclaim(self, name: Bytes32) -> None:
        """
        Sync the name with the registry (external)
        arguments:
            name: name
        returns:
            None
        """
        self._reclaim(String.from_bytes(name.bytes[: self.get_length(name).native]))

    @subroutine
    def _reclaim(self, name: String) -> None:
        """
        Sync the name with the registry (internal)
        arguments:
            name: name
        returns:
            None
        """

        label = op.sha256(name.bytes)
        node = self._namehash(name)

        token_id = BigUInt.from_bytes(node)

        assert Txn.sender == self._ownerOf(token_id), "only owner"

        rnode, _txn = arc4.abi_call(
            VNS.setSubnodeOwner,
            self.root_node,
            Bytes32.from_bytes(label),
            arc4.Address(Txn.sender),
            app_id=Application(self.registry),
        )

        assert rnode.bytes == node, "node mismatch"

    # reposession methods

    # TODO: implement
    # if registered name is expired, transfer ownership to be made available for registration
    @arc4.abimethod
    def reclaimExpiredName(self, nameHash: Bytes32) -> None:
        """Reclaim an expired name"""
        # assert self._is_expired(BigUInt.from_bytes(nameHash.bytes)), "name not expired"
        # self.clearResolver(nameHash)
        # self.markAvailableForRegistration(nameHash)
        pass

    # price methods

    @arc4.abimethod
    def set_cost_multiplier(self, cost_multiplier: arc4.UInt256) -> None:
        """
        Set cost multiplier for registration/renewal
        """
        assert Txn.sender == self.owner, "only owner"
        self.cost_multiplier = cost_multiplier.native

    @arc4.abimethod
    def set_base_cost(self, base_cost: arc4.UInt256) -> None:
        """
        Set base cost for registration/renewal
        sets the number of AUs in the smallest unit of cost
        ex) 1 USDC = 1000000 AUs
        """
        assert Txn.sender == self.owner, "only owner"
        self.base_cost = base_cost.native

    @subroutine
    def _base_cost(self, unit: BigUInt, name_length: UInt64) -> BigUInt:
        """
        Calculate base registration cost based on name length
        arguments:
            name_length: name length
        returns:
            base_cost: base cost
        """
        # unit = self.base_cost * self.cost_multiplier
        if name_length == UInt64(1):
            return unit * BigUInt(32)  # 32x for 1 char
        elif name_length == UInt64(2):
            return unit * BigUInt(16)  # 16x for 2 chars
        elif name_length == UInt64(3):
            return unit * BigUInt(8)  # 8x for 3 chars
        elif name_length == UInt64(4):
            return unit * BigUInt(4)  # 4x for 4 chars
        elif name_length == UInt64(5):
            return unit * BigUInt(2)  # 2x for 5 chars
        else:
            return unit * BigUInt(1)  # 1x for 5+ chars

    @arc4.abimethod
    def get_price(self, name: Bytes32, duration: arc4.UInt256) -> arc4.UInt64:
        """Calculate total price for registration/renewal"""
        unit = self.base_cost * self.cost_multiplier
        return arc4.UInt64(
            self._get_price(
                unit,
                name.bytes[: self._get_length(name.bytes)],
                duration.native,
            )
        )

    @arc4.abimethod
    def get_price_unit(self, name: Bytes32, duration: arc4.UInt256) -> arc4.UInt256:
        """Calculate total price for registration/renewal"""
        unit = BigUInt(5_000_000_000)
        return arc4.UInt256(
            self._get_price(
                unit,
                name.bytes[: self._get_length(name.bytes)],
                duration.native,
            )
        )

    # @arc4.abimethod
    # def get_price_ausd(self, name: Bytes32, duration: arc4.UInt256) -> arc4.UInt256:
    #     """Calculate total price for registration/renewal"""
    #     unit = BigUInt(5_000_000)
    #     return arc4.UInt256(
    #         self._get_price(
    #             unit,
    #             name.bytes[: self._get_length(name.bytes)],
    #             duration.native,
    #         )
    #     )

    @subroutine
    def _get_price(self, unit: BigUInt, name: Bytes, duration: BigUInt) -> BigUInt:
        """Calculate total price for registration/renewal"""
        base = self._base_cost(unit, name.length)
        years = duration // self.base_period
        return base * years

    # terminal methods

    @arc4.abimethod(allow_actions=[OnCompleteAction.DeleteApplication])
    def killApplication(self) -> None:
        """
        Kill contract
        """
        assert Txn.sender == self.upgrader, "must be upgrader"
        close_offline_on_delete(Txn.sender)

    @arc4.abimethod
    def deleteNFTData(self, token_id: arc4.UInt256) -> None:
        self._deleteNFTData(token_id.native)

    @subroutine
    def _deleteNFTData(self, token_id: BigUInt) -> None:
        del self.nft_data[token_id]

    @arc4.abimethod
    def deleteNFTOperators(self, label: arc4.UInt256) -> None:
        self._deleteNFTOperators(label.native)

    @subroutine
    def _deleteNFTOperators(self, label: BigUInt) -> None:
        del self.nft_operators[label.bytes]

    @arc4.abimethod
    def deleteNFTIndex(self, index: arc4.UInt256) -> None:
        self._deleteNFTIndex(index.native)

    @subroutine
    def _deleteNFTIndex(self, index: BigUInt) -> None:
        del self.nft_index[index]

    @arc4.abimethod
    def deleteHolderData(self, holder: arc4.Address) -> None:
        self._deleteHolderData(holder.native)

    @subroutine
    def _deleteHolderData(self, holder: Account) -> None:
        del self.holder_data[holder]

    @arc4.abimethod
    def deleteExpires(self, token_id: arc4.UInt256) -> None:
        self._deleteExpires(token_id.native)

    @subroutine
    def _deleteExpires(self, token_id: BigUInt) -> None:
        del self.expires[token_id]

    @arc4.abimethod
    def deleteBox(self, key: Bytes) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        box = BoxRef(key=key)
        box.delete()

    # admin methods

    @arc4.abimethod
    def set_grace_period(self, period: arc4.UInt64) -> None:
        """Set grace period for expired names"""
        assert Txn.sender == self.owner, "only owner"
        self.grace_period = period.native

    @arc4.abimethod
    def set_treasury(self, treasury: arc4.Address) -> None:
        """
        Set the treasury address that receives registration fees

        Args:
            treasury: The new treasury address to receive fees
        """
        assert Txn.sender == self.owner, "only owner"
        self.treasury = treasury.native

    @subroutine
    def _namehash(self, name: String) -> Bytes:
        """
        Compute namehash relative to registrar's root node
        For example if root node is "voi":
            "foo" -> sha256(root_node + sha256("foo"))
        """
        # Hash the label
        label_hash = op.sha256(name.bytes)

        # Combine with root node
        return op.sha256(self.root_node.bytes + label_hash)

    # beacon methods

    @arc4.abimethod
    def nop(self) -> None:
        """No operation"""
        pass

    # override metadata arc72_tokenURI
    @arc4.abimethod(readonly=True)
    def arc72_tokenURI(self, tokenId: arc4.UInt256) -> Bytes256:
        box_b = Box(Bytes256, key=b"arc72_tokenURI")
        return box_b.get(
            default=Bytes256.from_bytes(
                String(
                    "ipfs://QmQikwY11MqV5YgQeEMcDbtfaDfqYNdB8PYx3eY1osAov4#arc3"
                ).bytes
            )
        )

    # payment methods

    @arc4.abimethod
    def set_payment_token(self, token: arc4.UInt64) -> None:
        """
        Set the payment token
        """
        assert Txn.sender == self.owner, "only owner"
        self.payment_token = token.native

    # registrar methods

    @arc4.abimethod
    def set_root_node(self, root_node: Bytes32) -> None:
        """
        Set the root node
        """
        assert Txn.sender == self.owner, "only owner"
        self.root_node = root_node.copy()

    # resolver methods
    # setName
    # setText

    @arc4.abimethod
    def setName(self, name: Bytes256) -> None:
        """
        Set the name of the resolver
        """
        assert Txn.sender == self.owner, "only owner"
        resolver, txn = arc4.abi_call(
            VNS.resolver,
            self.root_node,
            app_id=Application(self.registry),
        )
        arc4.abi_call(
            VNSNameResolver.setName,
            self.root_node,
            name,
            app_id=Application(resolver.native),
        )


class ReverseRegistrar(ARC72Token, Upgradeable, Stakeable):
    def __init__(self) -> None:
        super().__init__()
        # state (core, metadata)
        # self.nft_data = BoxMap(BigUInt, arc72_nft_data)
        # self.nft_operators = BoxMap(Bytes, bool)
        # enumeration state
        self.totalSupply = BigUInt()  # total supply
        # self.nft_index = BoxMap(BigUInt, BigUInt)
        # self.holder_data = BoxMap(Account, arc72_holder_data)
        # registrar state
        self.treasury = Global.creator_address  # treasury address
        self.registry = UInt64(0)  # vns registrar id
        self.payment_token = UInt64(0)  # arc200 token id
        self.root_node = Bytes32.from_bytes(  # root node
            Bytes.from_base64("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        )
        self.grace_period = UInt64(90)  # grace period
        self.controllers = BoxMap(Account, bool)  # controllers
        # self.expires = BoxMap(BigUInt, BigUInt)  # expiration timestamps
        self.renewal_base_fee = UInt64(1)  # renewal base fee
        self.base_cost = BigUInt(1_000_000)  # base cost (1 USDC)
        self.cost_multiplier = BigUInt(1)  # cost multiplier (5x)
        self.base_period = UInt64(365 * 24 * 60 * 60)  # base period (1 year)
        # ownable state
        self.owner = Global.creator_address  # owner address
        # upgradeable state
        self.contract_version = UInt64()  # contract version
        self.deployment_version = UInt64()  # deployment version
        self.updatable = bool(1)  # updatable
        self.upgrader = Global.creator_address  # upgrader address
        # stakeable state
        self.delegate = Account()  # delegate address
        self.stakeable = bool(1)  # stakeable

    @arc4.abimethod
    def post_update(
        self, registry: arc4.UInt64, root_node: Bytes32, payment_token: arc4.UInt64
    ) -> None:
        self.registry = registry.native
        self.root_node = root_node.copy()
        self.payment_token = payment_token.native

    # override
    @arc4.abimethod(readonly=True)
    def arc72_ownerOf(self, tokenId: arc4.UInt256) -> arc4.Address:
        """
        Returns the address of the current owner of the NFT with the given tokenId
        """
        return arc4.Address(self._ownerOf(tokenId.native))

    @subroutine
    def _ownerOf(self, tokenId: BigUInt) -> Account:
        if self._expiration(tokenId) > BigUInt(Global.latest_timestamp):
            return Global.current_application_address
        return self._nft_owner(tokenId).native

    # expiration methods
    #   no expiration

    @arc4.abimethod(readonly=True)
    def expiration(self, tokenId: arc4.UInt256) -> arc4.UInt256:
        return arc4.UInt256(self._expiration(tokenId.native))

    @subroutine
    def _expiration(self, tokenId: BigUInt) -> BigUInt:
        return BigUInt(0)

    @subroutine
    def _set_expiration(self, tokenId: BigUInt, expiration: BigUInt) -> None:
        pass

    @subroutine
    def _increment_expiration(self, tokenId: BigUInt, duration: BigUInt) -> None:
        pass

    # vns methods

    @arc4.abimethod
    def setResolver(self, resolver: arc4.UInt64) -> None:
        assert Txn.sender == self.owner, "sender must be owner"
        app = Application(resolver.native)
        arc4.abi_call(VNS.setResolver, self.root_node, resolver, app_id=app)

    @subroutine
    def is_live(self, node: Bytes32) -> bool:
        """
        Check if the registrar is live
        """
        owner, _txn = arc4.abi_call(
            VNS.ownerOf, node, app_id=Application(self.registry)
        )
        assert (
            owner == Global.current_application_address
        ), "VNS must be owned by registrar"
        return True

    @subroutine
    def _only_controller(self) -> None:
        """
        Only the controller can call this method
        """
        pass

    @arc4.abimethod
    def get_length(self) -> arc4.UInt64:
        return arc4.UInt64(self._get_length())

    @subroutine
    def _get_length(self) -> UInt64:
        return UInt64(58)

    @arc4.abimethod
    def check_name(self, name: Bytes32) -> arc4.Bool:
        """
        Check if a name matches transaction sender
        """
        return arc4.Bool(self._check_name(name.bytes))

    @subroutine
    def _check_name(self, bytes: Bytes) -> bool:
        """
        Check if a name matches transaction sender
        """
        if bytes.length != 32:
            return False
        m_account = Account.from_bytes(bytes)
        if Txn.sender != m_account:
            return False
        return True

    @arc4.abimethod
    def register(
        self, name: Bytes32, owner: arc4.Address, duration: arc4.UInt256
    ) -> Bytes32:
        """
        Register a new name
        arguments:
            name: name
            owner: owner
            duration: duration
        returns:
            node: node
        """
        assert self.check_name(name).native, "name must match sender"
        return Bytes32.from_bytes(
            self._register(String.from_bytes(name.bytes), Txn.sender, BigUInt(0)),
        )

    # ------------------------------------------------------------
    # Register a new name (internal)
    # - validate registration
    # - create node hash
    # - calculate costs
    # - mint node as nft
    # - set up DNS records
    # - set expiration
    # ------------------------------------------------------------
    @subroutine
    def _register(self, name: String, owner: Account, duration: BigUInt) -> Bytes:
        # ------------------------------------------------------------
        # Validate registration
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # Create node hash using namehash
        # ------------------------------------------------------------
        label = op.sha256(name.bytes)
        new_node = self._namehash(name)
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # check if name is already registered
        #   if name is registered err on mint
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # Calculate costs
        # - pay for storage (network)
        # - pay for registration (arc200)
        # ------------------------------------------------------------
        # payment_amount = require_payment(Txn.sender)  # pay min amount for storage
        # assert (
        #     payment_amount >= mint_cost + mint_fee  # 336700 + 0
        # ), "payment amount accurate"
        # user pays initial setup fee (1 USDC)
        # requires allowance from Txn.sender to this contract
        # registration_fee = self._get_price()
        # arc4.abi_call(
        #     ARC200Token.arc200_transferFrom,
        #     arc4.Address(Txn.sender),
        #     arc4.Address(self.treasury),
        #     arc4.UInt256(registration_fee),
        #     app_id=Application(self.payment_token),
        # )
        # # ------------------------------------------------------------

        # ------------------------------------------------------------
        # mint node as nft, fails if already minted
        # token_id =
        # ------------------------------------------------------------
        self._mint(
            Txn.sender,
            new_node,
            name,
            # expiration
        )
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # Set up DNS records
        # ------------------------------------------------------------
        rnode, _txn = arc4.abi_call(
            VNS.setSubnodeOwner,
            self.root_node,
            Bytes32.from_bytes(label),
            arc4.Address(owner),
            app_id=Application(self.registry),
        )
        # setSubnodeOwner returns the new node hash computed remotely
        # assert it matches the one we calculated locally
        assert rnode.bytes == new_node, "node mismatch"
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # set expiration
        # ------------------------------------------------------------

        return new_node

    # renewal methods
    #  no expiration, no renewal

    # @arc4.abimethod
    # def renew(self, name: arc4.String, duration: arc4.UInt256) -> None:
    #     """Renew an existing registration"""
    #     self._renew(name.native, duration.native)

    # @subroutine
    # def _renew(self, name: String, duration: BigUInt) -> None:
    #     pass

    # mint methods

    @arc4.abimethod
    def mint(
        self,
        to: arc4.Address,
        nodeId: Bytes32,
        nodeName: arc4.String,
        # duration: arc4.UInt256,
    ) -> arc4.UInt256:
        """
        Mint a new NFT
        arguments:
            to: address
            nodeId: node
            nodeName: label
            duration: duration
        returns:
            tokenId: tokenId
        """
        self._only_controller()
        return arc4.UInt256(
            self._mint(
                to.native,
                nodeId.bytes,
                nodeName.native,
                # duration.native
            )
        )

    @subroutine
    def _mint(
        self,
        to: Account,
        nodeId: Bytes,
        nodeName: String,
        # duration: BigUInt
    ) -> BigUInt:
        """
        Mint a new NFT
        """
        # assert duration > 0, "duration must be greater than 0"

        if nodeId == self.root_node.bytes:
            assert Txn.sender == self.owner, "only owner can mint on root node"

        # bigNodeId = BigUInt.from_bytes(nodeId)

        # parent_nft_data = self._nft_data(bigNodeId)

        # assert parent_nft_data.index != 0, "parent node must exist"

        # assert "." not in nodeName, "node name must not contain a dot"
        # assert nodeName.bytes.length > 0, "node name must not be empty"

        # if nodeId == root_node_id:
        #     name = nodeName + "."
        # else:
        #     name = nodeName + "." + String.from_bytes(parent_nft_data.node_name.bytes)

        bigTokenId = arc4.UInt256.from_bytes(
            nodeId
        ).native  # simply convert nodeId to tokenId

        nft_data = self._nft_data(bigTokenId)

        # prevent re-registration
        assert nft_data.index == 0, "token must not exist"

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
            node=Bytes32.from_bytes(nodeId),
            valid=arc4.Bool(True),
            registration_date=arc4.UInt64(Global.latest_timestamp),
            label=Bytes256.from_bytes(nodeName.bytes),
        )
        self._holder_increment_balance(to)
        arc4.emit(
            arc72_Transfer(
                arc4.Address(Global.zero_address),
                arc4.Address(to),
                arc4.UInt256(bigTokenId),
            )
        )
        # return index
        return BigUInt(0)

    # check availability using owner of

    # expiration methods

    @arc4.abimethod
    def is_expired(self, token_id: arc4.UInt256) -> arc4.Bool:
        """
        Check if a name has expired
        arguments:
            token_id: tokenId
        returns:
            expired: bool
        """
        return arc4.Bool(self._is_expired(token_id.native))

    @subroutine
    def _is_expired(self, token_id: BigUInt) -> bool:
        """
        Check if a name has expired
        arguments:
            token_id: tokenId
        returns:
            expired: bool
        """
        return False

    @arc4.abimethod
    def reclaim(self, name: Bytes58) -> None:
        """
        Sync the name with the registry (external)
        arguments:
            name: name
        returns:
            None
        """
        self._reclaim(String.from_bytes(name.bytes))

    @subroutine
    def _reclaim(self, name: String) -> None:
        """
        Sync the name with the registry (internal)
        arguments:
            name: name
        returns:
            None
        """

        label = op.sha256(name.bytes)
        node = self._namehash(name)

        token_id = BigUInt.from_bytes(node)

        assert Txn.sender == self._ownerOf(token_id), "only owner"

        rnode, _txn = arc4.abi_call(
            VNS.setSubnodeOwner,
            self.root_node,
            Bytes32.from_bytes(label),
            arc4.Address(Txn.sender),
            app_id=Application(self.registry),
        )

        assert rnode.bytes == node, "node mismatch"

    # methods to to reclaim in registrar

    # reposession methods

    @arc4.abimethod
    def reclaimExpiredName(self, nameHash: Bytes32) -> None:
        """Reclaim an expired name"""
        pass

    # price methods

    @arc4.abimethod
    def set_cost_multiplier(self, cost_multiplier: arc4.UInt256) -> None:
        """
        Set cost multiplier for registration/renewal
        """
        assert Txn.sender == self.owner, "only owner"
        self.cost_multiplier = cost_multiplier.native

    @arc4.abimethod
    def set_base_cost(self, base_cost: arc4.UInt256) -> None:
        """
        Set base cost for registration/renewal
        sets the number of AUs in the smallest unit of cost
        ex) 1 USDC = 1000000 AUs
        """
        assert Txn.sender == self.owner, "only owner"
        self.base_cost = base_cost.native

    @subroutine
    def _base_cost(self) -> BigUInt:
        """
        Calculate base registration cost based on name length
        arguments:
            name_length: name length
        returns:
            base_cost: base cost
        """
        unit = self.base_cost * self.cost_multiplier
        return unit

    @arc4.abimethod
    def get_price(self, name: Bytes32, duration: arc4.UInt256) -> arc4.UInt64:
        """Calculate total price for registration/renewal"""
        return arc4.UInt64(self._get_price())

    @subroutine
    def _get_price(self) -> BigUInt:
        """Calculate total price for registration/renewal"""
        base = self._base_cost()
        return base

    # terminal methods

    @arc4.abimethod(allow_actions=[OnCompleteAction.DeleteApplication])
    def killApplication(self) -> None:
        """
        Kill contract
        """
        assert Txn.sender == self.upgrader, "must be upgrader"
        close_offline_on_delete(Txn.sender)

    @arc4.abimethod
    def deleteNFTData(self, token_id: arc4.UInt256) -> None:
        self._deleteNFTData(token_id.native)

    @subroutine
    def _deleteNFTData(self, token_id: BigUInt) -> None:
        del self.nft_data[token_id]

    @arc4.abimethod
    def deleteNFTOperators(self, label: arc4.UInt256) -> None:
        self._deleteNFTOperators(label.native)

    @subroutine
    def _deleteNFTOperators(self, label: BigUInt) -> None:
        del self.nft_operators[label.bytes]

    @arc4.abimethod
    def deleteNFTIndex(self, index: arc4.UInt256) -> None:
        self._deleteNFTIndex(index.native)

    @subroutine
    def _deleteNFTIndex(self, index: BigUInt) -> None:
        del self.nft_index[index]

    @arc4.abimethod
    def deleteHolderData(self, holder: arc4.Address) -> None:
        self._deleteHolderData(holder.native)

    @subroutine
    def _deleteHolderData(self, holder: Account) -> None:
        del self.holder_data[holder]

    # @arc4.abimethod
    # def deleteExpires(self, token_id: arc4.UInt256) -> None:
    # self._deleteExpires(token_id.native)

    # @subroutine
    # def _deleteExpires(self, token_id: BigUInt) -> None:
    #    del self.expires[token_id]

    @arc4.abimethod
    def deleteBox(self, key: Bytes) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        box = BoxRef(key=key)
        box.delete()

    # admin methods

    @arc4.abimethod
    def set_grace_period(self, period: arc4.UInt64) -> None:
        """Set grace period for expired names"""
        pass

    @arc4.abimethod
    def set_treasury(self, treasury: arc4.Address) -> None:
        """
        Set the treasury address that receives registration fees

        Args:
            treasury: The new treasury address to receive fees
        """
        assert Txn.sender == self.owner, "only owner"
        self.treasury = treasury.native

    @subroutine
    def _namehash(self, name: String) -> Bytes:
        """
        Compute namehash relative to registrar's root node
        For example if root node is "voi":
            "foo" -> sha256(root_node + sha256("foo"))
        """
        # Hash the label
        label_hash = op.sha256(name.bytes)

        # Combine with root node
        return op.sha256(self.root_node.bytes + label_hash)

    # beacon methods

    @arc4.abimethod
    def nop(self) -> None:
        """No operation"""
        pass

    # arc72 method overrides

    # override transferFrom to make non-transferable
    @arc4.abimethod
    def arc72_transferFrom(
        self, from_: arc4.Address, to: arc4.Address, tokenId: arc4.UInt256
    ) -> None:
        """
        Transfers ownership of an NFT
        """
        pass

    # payment methods

    @arc4.abimethod
    def set_payment_token(self, token: arc4.UInt64) -> None:
        """
        Set the payment token
        """
        assert Txn.sender == self.owner, "only owner"
        self.payment_token = token.native

    # registry method

    @arc4.abimethod
    def set_registry(self, registry: arc4.UInt64) -> None:
        """
        Set the registry
        """
        assert Txn.sender == self.owner, "only owner"
        self.registry = registry.native

    @arc4.abimethod
    def set_root_node(self, root_node: Bytes32) -> None:
        """
        Set the root node
        """
        assert Txn.sender == self.owner, "only owner"
        self.root_node = root_node.copy()

    # override metadata arc72_tokenURI
    @arc4.abimethod(readonly=True)
    def arc72_tokenURI(self, tokenId: arc4.UInt256) -> Bytes256:
        box_b = Box(Bytes256, key=b"arc72_tokenURI")
        return box_b.get(
            default=Bytes256.from_bytes(
                String(
                    "ipfs://QmQikwY11MqV5YgQeEMcDbtfaDfqYNdB8PYx3eY1osAov4#arc3"
                ).bytes
            )
        )


class CollectionRegistrar(ARC72Token, Upgradeable, Stakeable):
    def __init__(self) -> None:
        super().__init__()
        # state (core, metadata)
        # self.nft_data = BoxMap(BigUInt, arc72_nft_data)
        # self.nft_operators = BoxMap(Bytes, bool)
        # enumeration state
        self.totalSupply = BigUInt()  # total supply
        # self.nft_index = BoxMap(BigUInt, BigUInt)
        # self.holder_data = BoxMap(Account, arc72_holder_data)
        # registrar state
        self.treasury = Global.creator_address  # treasury address
        self.registry = UInt64(0)  # vns registrar id
        self.payment_token = UInt64(0)  # arc200 token id
        self.root_node = Bytes32.from_bytes(  # root node
            Bytes.from_base64("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        )
        self.grace_period = UInt64(90)  # grace period
        self.controllers = BoxMap(Account, bool)  # controllers
        # self.expires = BoxMap(BigUInt, BigUInt)  # expiration timestamps
        self.renewal_base_fee = UInt64(1)  # renewal base fee
        self.base_cost = BigUInt(1_000_000)  # base cost (1 USDC)
        self.cost_multiplier = BigUInt(1)  # cost multiplier (5x)
        self.base_period = UInt64(365 * 24 * 60 * 60)  # base period (1 year)
        # ownable state
        self.owner = Global.creator_address  # owner address
        # upgradeable state
        self.contract_version = UInt64()  # contract version
        self.deployment_version = UInt64()  # deployment version
        self.updatable = bool(1)  # updatable
        self.upgrader = Global.creator_address  # upgrader address
        # stakeable state
        self.delegate = Account()  # delegate address
        self.stakeable = bool(1)  # stakeable

    @arc4.abimethod
    def post_update(
        self, registry: arc4.UInt64, root_node: Bytes32, payment_token: arc4.UInt64
    ) -> None:
        self.registry = registry.native
        self.root_node = root_node.copy()
        self.payment_token = payment_token.native

    # override
    @arc4.abimethod(readonly=True)
    def arc72_ownerOf(self, tokenId: arc4.UInt256) -> arc4.Address:
        """
        Returns the address of the current owner of the NFT with the given tokenId
        """
        return arc4.Address(self._ownerOf(tokenId.native))

    @subroutine
    def _ownerOf(self, tokenId: BigUInt) -> Account:
        if self._expiration(tokenId) > BigUInt(Global.latest_timestamp):
            return Global.current_application_address
        return self._nft_owner(tokenId).native

    # expiration methods
    #   no expiration

    @arc4.abimethod(readonly=True)
    def expiration(self, tokenId: arc4.UInt256) -> arc4.UInt256:
        return arc4.UInt256(self._expiration(tokenId.native))

    @subroutine
    def _expiration(self, tokenId: BigUInt) -> BigUInt:
        return BigUInt(0)

    @subroutine
    def _set_expiration(self, tokenId: BigUInt, expiration: BigUInt) -> None:
        pass

    @subroutine
    def _increment_expiration(self, tokenId: BigUInt, duration: BigUInt) -> None:
        pass

    # vns methods

    @arc4.abimethod
    def setResolver(self, resolver: arc4.UInt64) -> None:
        assert Txn.sender == self.owner, "sender must be owner"
        app = Application(resolver.native)
        arc4.abi_call(VNS.setResolver, self.root_node, resolver, app_id=app)

    @subroutine
    def is_live(self, node: Bytes32) -> bool:
        """
        Check if the registrar is live
        """
        owner, _txn = arc4.abi_call(
            VNS.ownerOf, node, app_id=Application(self.registry)
        )
        assert (
            owner == Global.current_application_address
        ), "VNS must be owned by registrar"
        return True

    @subroutine
    def _only_controller(self) -> None:
        """
        Only the controller can call this method
        """
        pass

    @arc4.abimethod
    def get_length(self) -> arc4.UInt64:
        return arc4.UInt64(self._get_length())

    @subroutine
    def _get_length(self) -> UInt64:
        return UInt64(58)

    @arc4.abimethod
    def check_name(self, name: Bytes32) -> arc4.Bool:
        """
        Check if a name matches transaction sender
        """
        return arc4.Bool(self._check_name(name.bytes))

    @subroutine
    def _check_name(self, bytes: Bytes) -> bool:
        """
        Check if a name matches transaction sender
        """
        if bytes.length != 32:
            return False
        uint64_bytes = bytes[-8:]
        uint64_value = arc4.UInt64.from_bytes(uint64_bytes).native
        mapp = Application(uint64_value)
        if mapp.creator != Txn.sender:
            return False
        return True

    @arc4.abimethod
    def register(
        self, name: Bytes32, owner: arc4.Address, duration: arc4.UInt256
    ) -> Bytes32:
        """
        Register a new name
        arguments:
            name: name
            owner: owner
            duration: duration
        returns:
            node: node
        """
        assert self.check_name(name).native, "name must be valid"
        return Bytes32.from_bytes(
            self._register(
                String.from_bytes(name.bytes),
                Txn.sender,
                BigUInt(0),
            ),
        )

    # ------------------------------------------------------------
    # Register a new name (internal)
    # - validate registration
    # - create node hash
    # - calculate costs
    # - mint node as nft
    # - set up DNS records
    # - set expiration
    # ------------------------------------------------------------
    @subroutine
    def _register(self, name: String, owner: Account, duration: BigUInt) -> Bytes:
        # ------------------------------------------------------------
        # Validate registration
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # Create node hash using namehash
        # ------------------------------------------------------------
        label = op.sha256(name.bytes)
        new_node = self._namehash(name)
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # check if name is already registered
        #   if name is registered err on mint
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # Calculate costs
        # - pay for storage (network)
        # - pay for registration (arc200)
        # ------------------------------------------------------------
        # payment_amount = require_payment(Txn.sender)  # pay min amount for storage
        # assert (
        #     payment_amount >= mint_cost + mint_fee  # 336700 + 0
        # ), "payment amount accurate"
        # user pays initial setup fee (1 USDC)
        # requires allowance from Txn.sender to this contract
        # registration_fee = self._get_price()
        # arc4.abi_call(
        #     ARC200Token.arc200_transferFrom,
        #     arc4.Address(Txn.sender),
        #     arc4.Address(self.treasury),
        #     arc4.UInt256(registration_fee),
        #     app_id=Application(self.payment_token),
        # )
        # # ------------------------------------------------------------

        # ------------------------------------------------------------
        # mint node as nft, fails if already minted
        # token_id =
        # ------------------------------------------------------------
        self._mint(
            Txn.sender,
            new_node,
            name,
            # expiration
        )
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # Set up DNS records
        # ------------------------------------------------------------
        rnode, _txn = arc4.abi_call(
            VNS.setSubnodeOwner,
            self.root_node,
            Bytes32.from_bytes(label),
            arc4.Address(owner),
            app_id=Application(self.registry),
        )
        # setSubnodeOwner returns the new node hash computed remotely
        # assert it matches the one we calculated locally
        assert rnode.bytes == new_node, "node mismatch"
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # set expiration
        # ------------------------------------------------------------

        return new_node

    # renewal methods
    #  no expiration, no renewal

    # @arc4.abimethod
    # def renew(self, name: arc4.String, duration: arc4.UInt256) -> None:
    #     """Renew an existing registration"""
    #     self._renew(name.native, duration.native)

    # @subroutine
    # def _renew(self, name: String, duration: BigUInt) -> None:
    #     pass

    # mint methods

    @arc4.abimethod
    def mint(
        self,
        to: arc4.Address,
        nodeId: Bytes32,
        nodeName: arc4.String,
        # duration: arc4.UInt256,
    ) -> arc4.UInt256:
        """
        Mint a new NFT
        arguments:
            to: address
            nodeId: node
            nodeName: label
            duration: duration
        returns:
            tokenId: tokenId
        """
        self._only_controller()
        return arc4.UInt256(
            self._mint(
                to.native,
                nodeId.bytes,
                nodeName.native,
                # duration.native
            )
        )

    @subroutine
    def _mint(
        self,
        to: Account,
        nodeId: Bytes,
        nodeName: String,
        # duration: BigUInt
    ) -> BigUInt:
        """
        Mint a new NFT
        """
        # assert duration > 0, "duration must be greater than 0"

        if nodeId == self.root_node.bytes:
            assert Txn.sender == self.owner, "only owner can mint on root node"

        # bigNodeId = BigUInt.from_bytes(nodeId)

        # parent_nft_data = self._nft_data(bigNodeId)

        # assert parent_nft_data.index != 0, "parent node must exist"

        # assert "." not in nodeName, "node name must not contain a dot"
        # assert nodeName.bytes.length > 0, "node name must not be empty"

        # if nodeId == root_node_id:
        #     name = nodeName + "."
        # else:
        #     name = nodeName + "." + String.from_bytes(parent_nft_data.node_name.bytes)

        bigTokenId = arc4.UInt256.from_bytes(
            nodeId
        ).native  # simply convert nodeId to tokenId

        nft_data = self._nft_data(bigTokenId)

        # prevent re-registration
        assert nft_data.index == 0, "token must not exist"

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
            node=Bytes32.from_bytes(nodeId),
            valid=arc4.Bool(True),
            registration_date=arc4.UInt64(Global.latest_timestamp),
            label=Bytes256.from_bytes(nodeName.bytes),
        )
        self._holder_increment_balance(to)
        arc4.emit(
            arc72_Transfer(
                arc4.Address(Global.zero_address),
                arc4.Address(to),
                arc4.UInt256(bigTokenId),
            )
        )
        # return index
        return BigUInt(0)

    # check availability using owner of

    # expiration methods

    @arc4.abimethod
    def is_expired(self, token_id: arc4.UInt256) -> arc4.Bool:
        """
        Check if a name has expired
        arguments:
            token_id: tokenId
        returns:
            expired: bool
        """
        return arc4.Bool(self._is_expired(token_id.native))

    @subroutine
    def _is_expired(self, token_id: BigUInt) -> bool:
        """
        Check if a name has expired
        arguments:
            token_id: tokenId
        returns:
            expired: bool
        """
        return False

    @arc4.abimethod
    def reclaim(self, name: Bytes58) -> None:
        """
        Sync the name with the registry (external)
        arguments:
            name: name
        returns:
            None
        """
        self._reclaim(String.from_bytes(name.bytes))

    @subroutine
    def _reclaim(self, name: String) -> None:
        """
        Sync the name with the registry (internal)
        arguments:
            name: name
        returns:
            None
        """

        label = op.sha256(name.bytes)
        node = self._namehash(name)

        token_id = BigUInt.from_bytes(node)

        assert Txn.sender == self._ownerOf(token_id), "only owner"

        rnode, _txn = arc4.abi_call(
            VNS.setSubnodeOwner,
            self.root_node,
            Bytes32.from_bytes(label),
            arc4.Address(Txn.sender),
            app_id=Application(self.registry),
        )

        assert rnode.bytes == node, "node mismatch"

    # methods to to reclaim in registrar

    # reposession methods

    @arc4.abimethod
    def reclaimExpiredName(self, nameHash: Bytes32) -> None:
        """Reclaim an expired name"""
        pass

    # price methods

    @arc4.abimethod
    def set_cost_multiplier(self, cost_multiplier: arc4.UInt256) -> None:
        """
        Set cost multiplier for registration/renewal
        """
        assert Txn.sender == self.owner, "only owner"
        self.cost_multiplier = cost_multiplier.native

    @arc4.abimethod
    def set_base_cost(self, base_cost: arc4.UInt256) -> None:
        """
        Set base cost for registration/renewal
        sets the number of AUs in the smallest unit of cost
        ex) 1 USDC = 1000000 AUs
        """
        assert Txn.sender == self.owner, "only owner"
        self.base_cost = base_cost.native

    @subroutine
    def _base_cost(self) -> BigUInt:
        """
        Calculate base registration cost based on name length
        arguments:
            name_length: name length
        returns:
            base_cost: base cost
        """
        unit = self.base_cost * self.cost_multiplier
        return unit

    @arc4.abimethod
    def get_price(self, name: Bytes32, duration: arc4.UInt256) -> arc4.UInt64:
        """Calculate total price for registration/renewal"""
        return arc4.UInt64(self._get_price())

    @subroutine
    def _get_price(self) -> BigUInt:
        """Calculate total price for registration/renewal"""
        base = self._base_cost()
        return base

    # terminal methods

    @arc4.abimethod(allow_actions=[OnCompleteAction.DeleteApplication])
    def killApplication(self) -> None:
        """
        Kill contract
        """
        assert Txn.sender == self.upgrader, "must be upgrader"
        close_offline_on_delete(Txn.sender)

    @arc4.abimethod
    def deleteNFTData(self, token_id: arc4.UInt256) -> None:
        self._deleteNFTData(token_id.native)

    @subroutine
    def _deleteNFTData(self, token_id: BigUInt) -> None:
        del self.nft_data[token_id]

    @arc4.abimethod
    def deleteNFTOperators(self, label: arc4.UInt256) -> None:
        self._deleteNFTOperators(label.native)

    @subroutine
    def _deleteNFTOperators(self, label: BigUInt) -> None:
        del self.nft_operators[label.bytes]

    @arc4.abimethod
    def deleteNFTIndex(self, index: arc4.UInt256) -> None:
        self._deleteNFTIndex(index.native)

    @subroutine
    def _deleteNFTIndex(self, index: BigUInt) -> None:
        del self.nft_index[index]

    @arc4.abimethod
    def deleteHolderData(self, holder: arc4.Address) -> None:
        self._deleteHolderData(holder.native)

    @subroutine
    def _deleteHolderData(self, holder: Account) -> None:
        del self.holder_data[holder]

    # @arc4.abimethod
    # def deleteExpires(self, token_id: arc4.UInt256) -> None:
    # self._deleteExpires(token_id.native)

    # @subroutine
    # def _deleteExpires(self, token_id: BigUInt) -> None:
    #    del self.expires[token_id]

    @arc4.abimethod
    def deleteBox(self, key: Bytes) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        box = BoxRef(key=key)
        box.delete()

    # admin methods

    @arc4.abimethod
    def set_grace_period(self, period: arc4.UInt64) -> None:
        """Set grace period for expired names"""
        pass

    @arc4.abimethod
    def set_treasury(self, treasury: arc4.Address) -> None:
        """
        Set the treasury address that receives registration fees

        Args:
            treasury: The new treasury address to receive fees
        """
        assert Txn.sender == self.owner, "only owner"
        self.treasury = treasury.native

    @subroutine
    def _namehash(self, name: String) -> Bytes:
        """
        Compute namehash relative to registrar's root node
        For example if root node is "voi":
            "foo" -> sha256(root_node + sha256("foo"))
        """
        # Hash the label
        label_hash = op.sha256(name.bytes)

        # Combine with root node
        return op.sha256(self.root_node.bytes + label_hash)

    # beacon methods

    @arc4.abimethod
    def nop(self) -> None:
        """No operation"""
        pass

    # arc72 method overrides

    # override transferFrom to make non-transferable
    @arc4.abimethod
    def arc72_transferFrom(
        self, from_: arc4.Address, to: arc4.Address, tokenId: arc4.UInt256
    ) -> None:
        """
        Transfers ownership of an NFT
        """
        pass

    # payment methods

    @arc4.abimethod
    def set_payment_token(self, token: arc4.UInt64) -> None:
        """
        Set the payment token
        """
        assert Txn.sender == self.owner, "only owner"
        self.payment_token = token.native

    # registry method

    @arc4.abimethod
    def set_registry(self, registry: arc4.UInt64) -> None:
        """
        Set the registry
        """
        assert Txn.sender == self.owner, "only owner"
        self.registry = registry.native

    @arc4.abimethod
    def set_root_node(self, root_node: Bytes32) -> None:
        """
        Set the root node
        """
        assert Txn.sender == self.owner, "only owner"
        self.root_node = root_node.copy()

    # override metadata arc72_tokenURI
    @arc4.abimethod(readonly=True)
    def arc72_tokenURI(self, tokenId: arc4.UInt256) -> Bytes256:
        box_b = Box(Bytes256, key=b"arc72_tokenURI")
        return box_b.get(
            default=Bytes256.from_bytes(
                String(
                    "ipfs://QmQikwY11MqV5YgQeEMcDbtfaDfqYNdB8PYx3eY1osAov4#arc3"
                ).bytes
            )
        )


class StakingRegistrar(ARC72Token, Upgradeable, Stakeable):
    def __init__(self) -> None:
        super().__init__()
        # state (core, metadata)
        # self.nft_data = BoxMap(BigUInt, arc72_nft_data)
        # self.nft_operators = BoxMap(Bytes, bool)
        # enumeration state
        self.totalSupply = BigUInt()  # total supply
        # self.nft_index = BoxMap(BigUInt, BigUInt)
        # self.holder_data = BoxMap(Account, arc72_holder_data)
        # registrar state
        self.treasury = Global.creator_address  # treasury address
        self.registry = UInt64(0)  # vns registrar id
        self.payment_token = UInt64(0)  # arc200 token id
        self.root_node = Bytes32.from_bytes(  # root node
            Bytes.from_base64("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        )
        self.grace_period = UInt64(90)  # grace period
        self.controllers = BoxMap(Account, bool)  # controllers
        # self.expires = BoxMap(BigUInt, BigUInt)  # expiration timestamps
        self.renewal_base_fee = UInt64(1)  # renewal base fee
        self.base_cost = BigUInt(1_000_000)  # base cost (1 USDC)
        self.cost_multiplier = BigUInt(1)  # cost multiplier (5x)
        self.base_period = UInt64(365 * 24 * 60 * 60)  # base period (1 year)
        # ownable state
        self.owner = Global.creator_address  # owner address
        # upgradeable state
        self.contract_version = UInt64()  # contract version
        self.deployment_version = UInt64()  # deployment version
        self.updatable = bool(1)  # updatable
        self.upgrader = Global.creator_address  # upgrader address
        # stakeable state
        self.delegate = Account()  # delegate address
        self.stakeable = bool(1)  # stakeable

    @arc4.abimethod
    def post_update(
        self, registry: arc4.UInt64, root_node: Bytes32, payment_token: arc4.UInt64
    ) -> None:
        self.registry = registry.native
        self.root_node = root_node.copy()
        self.payment_token = payment_token.native

    # override
    @arc4.abimethod(readonly=True)
    def arc72_ownerOf(self, tokenId: arc4.UInt256) -> arc4.Address:
        """
        Returns the address of the current owner of the NFT with the given tokenId
        """
        return arc4.Address(self._ownerOf(tokenId.native))

    @subroutine
    def _ownerOf(self, tokenId: BigUInt) -> Account:
        if self._expiration(tokenId) > BigUInt(Global.latest_timestamp):
            return Global.current_application_address
        return self._nft_owner(tokenId).native

    # expiration methods
    #   no expiration

    @arc4.abimethod(readonly=True)
    def expiration(self, tokenId: arc4.UInt256) -> arc4.UInt256:
        return arc4.UInt256(self._expiration(tokenId.native))

    @subroutine
    def _expiration(self, tokenId: BigUInt) -> BigUInt:
        return BigUInt(0)

    @subroutine
    def _set_expiration(self, tokenId: BigUInt, expiration: BigUInt) -> None:
        pass

    @subroutine
    def _increment_expiration(self, tokenId: BigUInt, duration: BigUInt) -> None:
        pass

    # vns methods

    @arc4.abimethod
    def setResolver(self, resolver: arc4.UInt64) -> None:
        assert Txn.sender == self.owner, "sender must be owner"
        app = Application(resolver.native)
        arc4.abi_call(VNS.setResolver, self.root_node, resolver, app_id=app)

    @subroutine
    def is_live(self, node: Bytes32) -> bool:
        """
        Check if the registrar is live
        """
        owner, _txn = arc4.abi_call(
            VNS.ownerOf, node, app_id=Application(self.registry)
        )
        assert (
            owner == Global.current_application_address
        ), "VNS must be owned by registrar"
        return True

    @subroutine
    def _only_controller(self) -> None:
        """
        Only the controller can call this method
        """
        pass

    @arc4.abimethod
    def get_length(self) -> arc4.UInt64:
        return arc4.UInt64(self._get_length())

    @subroutine
    def _get_length(self) -> UInt64:
        return UInt64(58)

    @arc4.abimethod
    def check_name(self, name: Bytes32) -> arc4.Bool:
        """
        Check if a name matches transaction sender
        """
        return arc4.Bool(self._check_name(name.bytes))

    @subroutine
    def get_name_app(self, name: Bytes) -> Application:
        uint64_bytes = name[-8:]
        uint64_value = arc4.UInt64.from_bytes(uint64_bytes).native
        mapp = Application(uint64_value)
        return mapp

    @subroutine
    def _check_name(self, bytes: Bytes) -> bool:
        """
        Check if a name (apid) matches transaction sender
        such that the name is owned by the transaction sender
        """
        if bytes.length != 32:
            return False
        mapp = self.get_name_app(bytes)
        mowner, owner_exists = op.AppGlobal.get_ex_bytes(mapp, b"owner")
        if not owner_exists:
            return False
        if mowner != Txn.sender.bytes:
            return False
        return True

    @arc4.abimethod
    def register(
        self, name: Bytes32, owner: arc4.Address, duration: arc4.UInt256
    ) -> Bytes32:
        """
        Register a new name
        arguments:
            name: name
            owner: owner
            duration: duration
        returns:
            node: node
        """
        assert self.check_name(name).native, "name must be valid"
        mapp = self.get_name_app(name.bytes)
        return Bytes32.from_bytes(
            self._register(
                String.from_bytes(mapp.address.bytes),
                Txn.sender,
                BigUInt(0),
            ),
        )

    # ------------------------------------------------------------
    # Register a new name (internal)
    # - validate registration
    # - create node hash
    # - calculate costs
    # - mint node as nft
    # - set up DNS records
    # - set expiration
    # ------------------------------------------------------------
    @subroutine
    def _register(self, name: String, owner: Account, duration: BigUInt) -> Bytes:
        # ------------------------------------------------------------
        # Validate registration
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # Create node hash using namehash
        # ------------------------------------------------------------
        label = op.sha256(name.bytes)
        new_node = self._namehash(name)
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # check if name is already registered
        #   if name is registered err on mint
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # Calculate costs
        # - pay for storage (network)
        # - pay for registration (arc200)
        # ------------------------------------------------------------
        # payment_amount = require_payment(Txn.sender)  # pay min amount for storage
        # assert (
        #     payment_amount >= mint_cost + mint_fee  # 336700 + 0
        # ), "payment amount accurate"
        # user pays initial setup fee (1 USDC)
        # requires allowance from Txn.sender to this contract
        # registration_fee = self._get_price()
        # arc4.abi_call(
        #     ARC200Token.arc200_transferFrom,
        #     arc4.Address(Txn.sender),
        #     arc4.Address(self.treasury),
        #     arc4.UInt256(registration_fee),
        #     app_id=Application(self.payment_token),
        # )
        # # ------------------------------------------------------------

        # ------------------------------------------------------------
        # mint node as nft, fails if already minted
        # token_id =
        # ------------------------------------------------------------
        self._mint(
            Txn.sender,
            new_node,
            name,
            # expiration
        )
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # Set up DNS records
        # ------------------------------------------------------------
        rnode, _txn = arc4.abi_call(
            VNS.setSubnodeOwner,
            self.root_node,
            Bytes32.from_bytes(label),
            arc4.Address(owner),
            app_id=Application(self.registry),
        )
        # setSubnodeOwner returns the new node hash computed remotely
        # assert it matches the one we calculated locally
        assert rnode.bytes == new_node, "node mismatch"
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # set expiration
        # ------------------------------------------------------------

        return new_node

    # renewal methods
    #  no expiration, no renewal

    # @arc4.abimethod
    # def renew(self, name: arc4.String, duration: arc4.UInt256) -> None:
    #     """Renew an existing registration"""
    #     self._renew(name.native, duration.native)

    # @subroutine
    # def _renew(self, name: String, duration: BigUInt) -> None:
    #     pass

    # mint methods

    @arc4.abimethod
    def mint(
        self,
        to: arc4.Address,
        nodeId: Bytes32,
        nodeName: arc4.String,
        # duration: arc4.UInt256,
    ) -> arc4.UInt256:
        """
        Mint a new NFT
        arguments:
            to: address
            nodeId: node
            nodeName: label
            duration: duration
        returns:
            tokenId: tokenId
        """
        self._only_controller()
        return arc4.UInt256(
            self._mint(
                to.native,
                nodeId.bytes,
                nodeName.native,
                # duration.native
            )
        )

    @subroutine
    def _mint(
        self,
        to: Account,
        nodeId: Bytes,
        nodeName: String,
        # duration: BigUInt
    ) -> BigUInt:
        """
        Mint a new NFT
        """
        # assert duration > 0, "duration must be greater than 0"

        if nodeId == self.root_node.bytes:
            assert Txn.sender == self.owner, "only owner can mint on root node"

        # bigNodeId = BigUInt.from_bytes(nodeId)

        # parent_nft_data = self._nft_data(bigNodeId)

        # assert parent_nft_data.index != 0, "parent node must exist"

        # assert "." not in nodeName, "node name must not contain a dot"
        # assert nodeName.bytes.length > 0, "node name must not be empty"

        # if nodeId == root_node_id:
        #     name = nodeName + "."
        # else:
        #     name = nodeName + "." + String.from_bytes(parent_nft_data.node_name.bytes)

        bigTokenId = arc4.UInt256.from_bytes(
            nodeId
        ).native  # simply convert nodeId to tokenId

        nft_data = self._nft_data(bigTokenId)

        # prevent re-registration
        assert nft_data.index == 0, "token must not exist"

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
            node=Bytes32.from_bytes(nodeId),
            valid=arc4.Bool(True),
            registration_date=arc4.UInt64(Global.latest_timestamp),
            label=Bytes256.from_bytes(nodeName.bytes),
        )
        self._holder_increment_balance(to)
        arc4.emit(
            arc72_Transfer(
                arc4.Address(Global.zero_address),
                arc4.Address(to),
                arc4.UInt256(bigTokenId),
            )
        )
        # return index
        return BigUInt(0)

    # check availability using owner of

    # expiration methods

    @arc4.abimethod
    def is_expired(self, token_id: arc4.UInt256) -> arc4.Bool:
        """
        Check if a name has expired
        arguments:
            token_id: tokenId
        returns:
            expired: bool
        """
        return arc4.Bool(self._is_expired(token_id.native))

    @subroutine
    def _is_expired(self, token_id: BigUInt) -> bool:
        """
        Check if a name has expired
        arguments:
            token_id: tokenId
        returns:
            expired: bool
        """
        return False

    @arc4.abimethod
    def reclaim(self, name: Bytes58) -> None:
        """
        Sync the name with the registry (external)
        arguments:
            name: name
        returns:
            None
        """
        self._reclaim(String.from_bytes(name.bytes))

    @subroutine
    def _reclaim(self, name: String) -> None:
        """
        Sync the name with the registry (internal)
        arguments:
            name: name
        returns:
            None
        """

        label = op.sha256(name.bytes)
        node = self._namehash(name)

        token_id = BigUInt.from_bytes(node)

        assert Txn.sender == self._ownerOf(token_id), "only owner"

        rnode, _txn = arc4.abi_call(
            VNS.setSubnodeOwner,
            self.root_node,
            Bytes32.from_bytes(label),
            arc4.Address(Txn.sender),
            app_id=Application(self.registry),
        )

        assert rnode.bytes == node, "node mismatch"

    # methods to to reclaim in registrar

    # reposession methods

    @arc4.abimethod
    def reclaimExpiredName(self, nameHash: Bytes32) -> None:
        """Reclaim an expired name"""
        pass

    # price methods

    @arc4.abimethod
    def set_cost_multiplier(self, cost_multiplier: arc4.UInt256) -> None:
        """
        Set cost multiplier for registration/renewal
        """
        assert Txn.sender == self.owner, "only owner"
        self.cost_multiplier = cost_multiplier.native

    @arc4.abimethod
    def set_base_cost(self, base_cost: arc4.UInt256) -> None:
        """
        Set base cost for registration/renewal
        sets the number of AUs in the smallest unit of cost
        ex) 1 USDC = 1000000 AUs
        """
        assert Txn.sender == self.owner, "only owner"
        self.base_cost = base_cost.native

    @subroutine
    def _base_cost(self) -> BigUInt:
        """
        Calculate base registration cost based on name length
        arguments:
            name_length: name length
        returns:
            base_cost: base cost
        """
        unit = self.base_cost * self.cost_multiplier
        return unit

    @arc4.abimethod
    def get_price(self, name: Bytes32, duration: arc4.UInt256) -> arc4.UInt64:
        """Calculate total price for registration/renewal"""
        return arc4.UInt64(self._get_price())

    @subroutine
    def _get_price(self) -> BigUInt:
        """Calculate total price for registration/renewal"""
        base = self._base_cost()
        return base

    # terminal methods

    @arc4.abimethod(allow_actions=[OnCompleteAction.DeleteApplication])
    def killApplication(self) -> None:
        """
        Kill contract
        """
        assert Txn.sender == self.upgrader, "must be upgrader"
        close_offline_on_delete(Txn.sender)

    @arc4.abimethod
    def deleteNFTData(self, token_id: arc4.UInt256) -> None:
        self._deleteNFTData(token_id.native)

    @subroutine
    def _deleteNFTData(self, token_id: BigUInt) -> None:
        del self.nft_data[token_id]

    @arc4.abimethod
    def deleteNFTOperators(self, label: arc4.UInt256) -> None:
        self._deleteNFTOperators(label.native)

    @subroutine
    def _deleteNFTOperators(self, label: BigUInt) -> None:
        del self.nft_operators[label.bytes]

    @arc4.abimethod
    def deleteNFTIndex(self, index: arc4.UInt256) -> None:
        self._deleteNFTIndex(index.native)

    @subroutine
    def _deleteNFTIndex(self, index: BigUInt) -> None:
        del self.nft_index[index]

    @arc4.abimethod
    def deleteHolderData(self, holder: arc4.Address) -> None:
        self._deleteHolderData(holder.native)

    @subroutine
    def _deleteHolderData(self, holder: Account) -> None:
        del self.holder_data[holder]

    # @arc4.abimethod
    # def deleteExpires(self, token_id: arc4.UInt256) -> None:
    # self._deleteExpires(token_id.native)

    # @subroutine
    # def _deleteExpires(self, token_id: BigUInt) -> None:
    #    del self.expires[token_id]

    @arc4.abimethod
    def deleteBox(self, key: Bytes) -> None:
        assert Txn.sender == self.upgrader, "must be upgrader"
        box = BoxRef(key=key)
        box.delete()

    # admin methods

    @arc4.abimethod
    def set_grace_period(self, period: arc4.UInt64) -> None:
        """Set grace period for expired names"""
        pass

    @arc4.abimethod
    def set_treasury(self, treasury: arc4.Address) -> None:
        """
        Set the treasury address that receives registration fees

        Args:
            treasury: The new treasury address to receive fees
        """
        assert Txn.sender == self.owner, "only owner"
        self.treasury = treasury.native

    @subroutine
    def _namehash(self, name: String) -> Bytes:
        """
        Compute namehash relative to registrar's root node
        For example if root node is "voi":
            "foo" -> sha256(root_node + sha256("foo"))
        """
        # Hash the label
        label_hash = op.sha256(name.bytes)

        # Combine with root node
        return op.sha256(self.root_node.bytes + label_hash)

    # beacon methods

    @arc4.abimethod
    def nop(self) -> None:
        """No operation"""
        pass

    # arc72 method overrides

    # override transferFrom to make non-transferable
    @arc4.abimethod
    def arc72_transferFrom(
        self, from_: arc4.Address, to: arc4.Address, tokenId: arc4.UInt256
    ) -> None:
        """
        Transfers ownership of an NFT
        """
        pass

    # payment methods

    @arc4.abimethod
    def set_payment_token(self, token: arc4.UInt64) -> None:
        """
        Set the payment token
        """
        assert Txn.sender == self.owner, "only owner"
        self.payment_token = token.native

    # registry method

    @arc4.abimethod
    def set_registry(self, registry: arc4.UInt64) -> None:
        """
        Set the registry
        """
        assert Txn.sender == self.owner, "only owner"
        self.registry = registry.native

    @arc4.abimethod
    def set_root_node(self, root_node: Bytes32) -> None:
        """
        Set the root node
        """
        assert Txn.sender == self.owner, "only owner"
        self.root_node = root_node.copy()

    # override metadata arc72_tokenURI
    @arc4.abimethod(readonly=True)
    def arc72_tokenURI(self, tokenId: arc4.UInt256) -> Bytes256:
        box_b = Box(Bytes256, key=b"arc72_tokenURI")
        return box_b.get(
            default=Bytes256.from_bytes(
                String(
                    "ipfs://QmQikwY11MqV5YgQeEMcDbtfaDfqYNdB8PYx3eY1osAov4#arc3"
                ).bytes
            )
        )
