import { expect } from "chai";
import {
  ALGORAND_ZERO_ADDRESS_STRING,
  addresses,
  algodClient,
  arc200Allowance,
  arc200Approve,
  arc200BalanceOf,
  arc200DeleteBalance,
  arc200Mint,
  arc72OwnerOf,
  arc72TransferFrom,
  bytesToHex,
  checkName,
  deleteBox,
  deleteExpires,
  deleteHolderData,
  deleteNFTData,
  deleteNFTIndex,
  deploy,
  expiration,
  extraPageCost,
  getLength,
  getPrice,
  isApprovedForAll,
  isExpired,
  killAddr,
  killApplication,
  killNode,
  killOperator,
  minBalance,
  namehash,
  ownerOf,
  postUpdate,
  reclaim,
  recordBoxCost,
  register,
  registrarWithdraw,
  renew,
  resolveAddr,
  resolver,
  reverseCheckName,
  reverseGetLength,
  reverseRegister,
  setAddr,
  setApprovalForAll,
  setOwner,
  setRecord,
  setResolver,
  setSubnodeOwner,
  setTTL,
  sks,
  stringToUint8Array,
  ttl,
  vnsRegistrarPostUpdate,
  setName,
  getName,
  deleteName,
  stripTrailingZeroBytes,
} from "../command.js";
import moment from "moment";
import algosdk from "algosdk";

const baseFixtureData = {
  apps: {
    vnsRegistry: 0,
    vnsResolver: 0,
    vnsRegistrar: 0,
    reverseRegistrar: 0,
    // TESTNET
    //arc200: 6510,
    // MAINNET
    //arc200: 395614, // aUSD
    arc200: 780596,
  },
  context: {
    price: 0,
    duration: 365 * 24 * 60 * 60,
  },
};

// Path : VNSRegistrar

// mint only owner can mint root node
// mint duration must be greater than 0
// mint must not exist to mint
// mint payment must be accurate

describe("VNSRegistry:core:reverse Test Suite", function () {
  this.timeout(120_000);
  let fixtureData = baseFixtureData;
  before(async function () {
    console.log("Once upon a time...");
    const vnsRegistry = await deploy({
      type: "vns-registry",
      name: "test-registry-13",
    });
    fixtureData.apps.vnsRegistry = vnsRegistry;
    const vnsResolver = await deploy({
      type: "vns-resolver",
      name: "test-resolver-13",
    });
    fixtureData.apps.vnsResolver = vnsResolver;
    const vnsRegistrar = await deploy({
      type: "vns-registrar",
      name: "test-registrar-13",
    });
    fixtureData.apps.vnsRegistrar = vnsRegistrar;
    const reverseRegistrar = await deploy({
      type: "reverse-registrar",
      name: "test-reverse-registrar-13",
    });
    fixtureData.apps.reverseRegistrar = reverseRegistrar;
    // const arc200 = await deploy({
    //   type: "arc200",
    //   name: "test-arc200-12",
    // });
    // fixtureData.apps.arc200 = arc200;
  });
  after(async function () {
    // // resolver kill operations
    // await deleteName({
    //   apid: fixtureData.apps.vnsResolver,
    //   node: `${addresses.deployer}.addr.reverse`,
    //   sender: addresses.deployer,
    //   sk: sks.deployer,
    //   debug: true,
    // });
    // // registry kill operations
    // await Promise.all(
    //   [
    //     "",
    //     "voi",
    //     "reverse",
    //     "addr.reverse",
    //     `${addresses.deployer}.addr.reverse`,
    //     `${addresses.deployer}.reverse`,
    //   ].map((node) =>
    //     killNode({
    //       apid: fixtureData.apps.vnsRegistry,
    //       node,
    //       sender: addresses.deployer,
    //       sk: sks.deployer,
    //     })
    //   )
    // );
    // // registrar kill operations
    // // counter
    // const deleteBoxR = await deleteBox({
    //   apid: fixtureData.apps.vnsRegistrar,
    //   key: "YXJjNzJfY291bnRlcg==",
    // });
    // // holder data
    // const deleteHolderDataR = await deleteHolderData({
    //   apid: fixtureData.apps.vnsRegistrar,
    //   address: addresses.deployer,
    // });
    // // index data
    // // reverse registrar kill operations
    // //   counter
    // const deleteBoxR2 = await deleteBox({
    //   apid: fixtureData.apps.reverseRegistrar,
    //   key: "YXJjNzJfY291bnRlcg==",
    // });
    // //   holder data
    // const deleteHolderDataR2 = await deleteHolderData({
    //   apid: fixtureData.apps.reverseRegistrar,
    //   address: addresses.deployer,
    // });
    // //   delete nft data
    // await deleteNFTData({
    //   apid: fixtureData.apps.reverseRegistrar,
    //   name: `${addresses.deployer}.addr.reverse`,
    // });
    // await deleteNFTData({
    //   apid: fixtureData.apps.reverseRegistrar,
    //   name: `${addresses.deployer}.reverse`,
    // });

    // // delete nft index
    // await deleteNFTIndex({
    //   apid: fixtureData.apps.reverseRegistrar,
    //   index: 0,
    // });
    // await deleteNFTIndex({
    //   apid: fixtureData.apps.reverseRegistrar,
    //   index: 1,
    // });
    // await deleteNFTIndex({
    //   apid: fixtureData.apps.reverseRegistrar,
    //   index: 2,
    // });
    // // application kill operations
    // const killApplicationR = await Promise.all(
    //   [
    //     fixtureData.apps.vnsRegistry,
    //     fixtureData.apps.vnsResolver,
    //     fixtureData.apps.vnsRegistrar,
    //     fixtureData.apps.reverseRegistrar,
    //     //fixtureData.apps.arc200,
    //   ].map((apid) =>
    //     killApplication({
    //       apid,
    //       delete: true,
    //     })
    //   )
    // );
    // console.log(killApplicationR);
    // expect(killApplicationR.reduce((acc, curr) => acc && curr, true)).to.be.eq(
    //   true
    // );
    console.log(fixtureData.apps);
    console.log("Happily ever after");
  });
  it("should deploy", async function () {
    expect(fixtureData.apps.vnsRegistry).to.be.a("number");
    expect(fixtureData.apps.vnsRegistry).to.be.greaterThan(0);
    expect(fixtureData.apps.vnsResolver).to.be.a("number");
    expect(fixtureData.apps.vnsResolver).to.be.greaterThan(0);
    expect(fixtureData.apps.vnsRegistrar).to.be.a("number");
    expect(fixtureData.apps.vnsRegistrar).to.be.greaterThan(0);
    expect(fixtureData.apps.reverseRegistrar).to.be.a("number");
    expect(fixtureData.apps.reverseRegistrar).to.be.greaterThan(0);
    expect(fixtureData.apps.arc200).to.be.a("number");
    expect(fixtureData.apps.arc200).to.be.greaterThan(0);
  });
  // setup arc200
  // it("mint arc200", async function () {
  //   const mintR = await arc200Mint({
  //     apid: fixtureData.apps.arc200,
  //     recipient: addresses.deployer,
  //     name: "USDC",
  //     symbol: "USDC",
  //     totalSupply: 1_000_000_000_000,
  //     decimals: 6,
  //     sender: addresses.deployer,
  //     sk: sks.deployer,
  //   });
  //   expect(mintR).to.be.eq(true);
  // });
  it("can post update registry, create root node", async function () {
    const success = await postUpdate({
      apid: fixtureData.apps.vnsRegistry,
      extraPayment: minBalance + extraPageCost + recordBoxCost,
      rapid: fixtureData.apps.vnsResolver,
    });
    expect(success).to.be.eq(true);
    // TODO: check resolver
  });
  it("can post update resolver, set registry", async function () {
    const success = await postUpdate({
      apid: fixtureData.apps.vnsResolver,
      rapid: fixtureData.apps.vnsRegistry,
      extraPayment: minBalance + extraPageCost,
    });
    expect(success).to.be.eq(true);
    // TODO: check registry
  });

  // setup voi registrar

  it("set voi owner to registrar", async function () {
    const setSubnodeOwnerR = bytesToHex(
      await setSubnodeOwner({
        apid: fixtureData.apps.vnsRegistry,
        sender: addresses.deployer,
        sk: sks.deployer,
        extraPayment: recordBoxCost,
        node: "",
        label: "voi",
        owner: algosdk.getApplicationAddress(fixtureData.apps.vnsRegistrar),
      })
    );
    const expectedSetSubnodeOwnerR = bytesToHex(namehash("voi"));
    expect(setSubnodeOwnerR).to.be.eq(expectedSetSubnodeOwnerR);
    const ownerR3 = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "voi",
    });
    expect(ownerR3).to.be.eq(
      algosdk.getApplicationAddress(fixtureData.apps.vnsRegistrar)
    );
  });

  it("can post update registrar, set root node", async function () {
    const success = await vnsRegistrarPostUpdate({
      apid: fixtureData.apps.vnsRegistrar,
      registry: fixtureData.apps.vnsRegistry,
      rootNode: "voi",
      paymentToken: fixtureData.apps.arc200,
    });
    expect(success).to.be.eq(true);
  });

  // setup reverse registrar

  it("set reverse owner to deployer", async function () {
    const setSubnodeOwnerR = bytesToHex(
      await setSubnodeOwner({
        apid: fixtureData.apps.vnsRegistry,
        sender: addresses.deployer,
        sk: sks.deployer,
        extraPayment: recordBoxCost,
        node: "",
        label: "reverse",
        owner: addresses.deployer,
      })
    );
    const expectedSetSubnodeOwnerR = bytesToHex(namehash("reverse"));
    expect(setSubnodeOwnerR).to.be.eq(expectedSetSubnodeOwnerR);
    const ownerR3 = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "reverse",
    });
    expect(ownerR3).to.be.eq(addresses.deployer);
  });

  it("set addr.reverse owner to reverse registrar", async function () {
    const setSubnodeOwnerR = bytesToHex(
      await setSubnodeOwner({
        apid: fixtureData.apps.vnsRegistry,
        sender: addresses.deployer,
        sk: sks.deployer,
        extraPayment: recordBoxCost,
        node: "reverse",
        label: "addr",
        owner: algosdk.getApplicationAddress(fixtureData.apps.reverseRegistrar),
      })
    );
    const expectedSetSubnodeOwnerR = bytesToHex(namehash("addr.reverse"));
    expect(setSubnodeOwnerR).to.be.eq(expectedSetSubnodeOwnerR);
    const ownerR3 = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "addr.reverse",
    });
    expect(ownerR3).to.be.eq(
      algosdk.getApplicationAddress(fixtureData.apps.reverseRegistrar)
    );
  });
  it("can post update registrar, set root node", async function () {
    const success = await vnsRegistrarPostUpdate({
      apid: fixtureData.apps.reverseRegistrar,
      registry: fixtureData.apps.vnsRegistry,
      rootNode: "addr.reverse",
      paymentToken: fixtureData.apps.arc200,
    });
    expect(success).to.be.eq(true);
  });

  it("can get length", async function () {
    const name = "nshell";
    const length = await reverseGetLength({
      apid: fixtureData.apps.reverseRegistrar,
      name,
    });
    expect(length).to.be.eq(BigInt(58));
  });
  // it("readonly can check name addr should", async function () {
  //   const name = "nshell";
  //   const checkNameR = await reverseCheckName({
  //     apid: fixtureData.apps.reverseRegistrar,
  //     //name: new Uint8Array(stringToUint8Array(name, 32)),
  //     name: "G3MSA75OZEJTCCENOJDLDJK7UD7E2K5DNC7FVHCNOV7E3I4DTXTOWDUIFQ",
  //     debug: true,
  //   });
  //   expect(checkNameR).to.be.eq(false);
  // });
  // it("readonly can check name address should pass", async function () {
  //   const checkNameR = await reverseCheckName({
  //     apid: fixtureData.apps.reverseRegistrar,
  //     name: algosdk.decodeAddress(addresses.deployer).publicKey,
  //   });
  //   expect(checkNameR).to.be.eq(true);
  // });
  it("check ownerOf before register", async function () {
    const ownerOfR = await arc72OwnerOf({
      apid: fixtureData.apps.reverseRegistrar,
      name: `${addresses.deployer}.addr.reverse`,
    });
    expect(ownerOfR).to.be.eq(ALGORAND_ZERO_ADDRESS_STRING);
  });
  it("can approve spending before register", async function () {
    const approveR = await arc200Approve({
      apid: fixtureData.apps.arc200,
      spender: algosdk.getApplicationAddress(fixtureData.apps.reverseRegistrar),
      amount: 10e10,
    });
    expect(approveR).to.be.eq(true);
  });
  // registering as treasury
  // expect no change in balance of payment token
  it("can register", async function () {
    const balanceBefore = await arc200BalanceOf({
      apid: fixtureData.apps.arc200,
      owner: addresses.deployer,
    });
    console.log("balanceBefore", balanceBefore);
    const registerR = await reverseRegister({
      apid: fixtureData.apps.reverseRegistrar,
      owner: addresses.deployer,
      duration: 365 * 24 * 60 * 60,
    });
    expect(registerR).to.be.eq(true);
    const balanceAfter = await arc200BalanceOf({
      apid: fixtureData.apps.arc200,
      owner: addresses.deployer,
    });
    console.log("balanceAfter", balanceAfter);
    expect(Number(balanceAfter)).to.be.eq(Number(balanceBefore)); // tokens are sent to self
    const balanceAfter2 = await arc200BalanceOf({
      apid: fixtureData.apps.arc200,
      owner: algosdk.getApplicationAddress(fixtureData.apps.reverseRegistrar),
    });
    console.log("balanceAfter2", balanceAfter2);
    expect(Number(balanceAfter2)).to.be.eq(0);
  });
  // registering as treasury
  it("check ownerOf after register", async function () {
    const ownerOfR = await arc72OwnerOf({
      apid: fixtureData.apps.reverseRegistrar,
      name: `${addresses.deployer}.addr.reverse`,
    });
    expect(ownerOfR).to.be.eq(addresses.deployer);
  });
  // --------------------------------
  // register as non-treasury account
  //   expect change in balance of payment token
  // --------------------------------
  // do the thing you would do with the name
  // ie set name in resolver
  // --------------------------------
  it("can get name", async function () {
    const name = await getName({
      apid: fixtureData.apps.vnsResolver,
      node: `${addresses.deployer}.addr.reverse`,
    });
    expect(
      stripTrailingZeroBytes(Buffer.from(name).toString("utf-8"))
    ).to.be.eq("");
  });
  it("can set name in resolver", async function () {
    const setNameR = await setName({
      apid: fixtureData.apps.vnsResolver,
      node: `${addresses.deployer}.addr.reverse`,
      name: "nshell.voi",
      debug: true,
    });
    expect(setNameR).to.be.eq(true);
    const name = await getName({
      apid: fixtureData.apps.vnsResolver,
      node: `${addresses.deployer}.addr.reverse`,
    });
    expect(
      stripTrailingZeroBytes(Buffer.from(name).toString("utf-8"))
    ).to.be.eq("nshell.voi");
  });
  it("can update name in resolver", async function () {
    const updateNameR = await setName({
      apid: fixtureData.apps.vnsResolver,
      node: `${addresses.deployer}.addr.reverse`,
      name: "shelly.voi",
    });
    expect(updateNameR).to.be.eq(true);
    const name = await getName({
      apid: fixtureData.apps.vnsResolver,
      node: `${addresses.deployer}.addr.reverse`,
    });
    expect(
      stripTrailingZeroBytes(Buffer.from(name).toString("utf-8"))
    ).to.be.eq("shelly.voi");
  });
});
