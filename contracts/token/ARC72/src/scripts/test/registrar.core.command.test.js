import { expect } from "chai";
import {
  deploy,
  sks,
  addresses,
  killApplication,
  postUpdate,
  killNode,
  killOperator,
  killAddr,
  namehash,
  ownerOf,
  resolver,
  ttl,
  setResolver,
  setTTL,
  setRecord,
  setSubnodeOwner,
  setOwner,
  setApprovalForAll,
  isApprovedForAll,
  minBalance,
  recordBoxCost,
  bytesToHex,
  extraPageCost,
  ALGORAND_ZERO_ADDRESS_STRING,
  arc200DeleteBalance,
  arc200Mint,
  vnsRegistrarPostUpdate,
  register,
  deleteNFTData,
  deleteNFTIndex,
  deleteBox,
  deleteHolderData,
  deleteExpires,
  arc200Approve,
  arc200Allowance,
  arc200BalanceOf,
  getPrice,
  checkName,
  getLength,
  isExpired,
  arc72OwnerOf,
  arc72TransferFrom,
  renew,
  expiration,
  reclaim,
  resolveAddr,
  setAddr,
} from "../command.js";
import moment from "moment";
import algosdk from "algosdk";

// vnsRegistry: 797607,
// vnsResolver: 797608,
// vnsRegistrar: 797609,
// reverseRegistrar: 797610,
// arc200: 395614

const baseFixtureData = {
  apps: {
    vnsRegistry: 0,
    vnsResolver: 0,
    vnsRegistrar: 0,
    reverseRegistrar: 0,
    arc200: 395614, //20438,
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

describe("VNSRegistry:core:registrar Test Suite", function () {
  this.timeout(60_000);
  let fixtureData = baseFixtureData;
  before(async function () {
    console.log("Once upon a time...");
    const vnsRegistry = await deploy({
      type: "vns-registry",
      name: "vns-registry",
    });
    fixtureData.apps.vnsRegistry = vnsRegistry;
    const vnsResolver = await deploy({
      type: "vns-resolver",
      name: "vns-resolver",
    });
    fixtureData.apps.vnsResolver = vnsResolver;
    const vnsRegistrar = await deploy({
      type: "vns-registrar",
      name: "vns-registrar",
    });
    fixtureData.apps.vnsRegistrar = vnsRegistrar;
    const reverseRegistrar = await deploy({
      type: "reverse-registrar",
      name: "vns-reverse-registrar",
    });
    fixtureData.apps.reverseRegistrar = reverseRegistrar;
    // const arc200 = await deploy({
    //   type: "arc200",
    //   name: "test-arc200-9",
    // });
    // fixtureData.apps.arc200 = arc200;
  });
  after(async function () {
    // resolver kill operations
    // const killAddrR = await killAddr({
    //   apid: fixtureData.apps.vnsResolver,
    //   node: "nshell.voi",
    // });
    // expect(killAddrR).to.be.eq(true);
    // arc200 kill operations
    // const deleteBalanceR = await Promise.all(
    //   [
    //     ...Object.values(addresses),
    //     algosdk.getApplicationAddress(fixtureData.apps.vnsRegistrar),
    //   ].map((address) =>
    //     arc200DeleteBalance({
    //       apid: fixtureData.apps.arc200,
    //       owner: address,
    //     })
    //   )
    // );
    // expect(deleteBalanceR.reduce((acc, curr) => acc && curr, true)).to.be.eq(
    //   true
    // );
    // const deleteApprovalR = await arc200DeleteApproval({
    //   apid: fixtureData.apps.arc200,
    //   owner: addresses.deployer,
    //   spender: addresses.owner,
    // });
    // expect(deleteApprovalR).to.be.eq(true);
    // ------------------------------------------------------------
    // registry kill operations
    // const killNodeR = await Promise.all(
    //   [
    //     "",
    //     "hi",
    //     "voi",
    //     ...["nshell", "shelly"].map((label) => `${label}.voi`),
    //     "a.nshell.voi",
    //     "b.a.nshell.voi",
    //   ].map((node) =>
    //     killNode({
    //       apid: fixtureData.apps.vnsRegistry,
    //       node,
    //       sender: addresses.deployer,
    //       sk: sks.deployer,
    //     })
    //   )
    // );
    // expect(killNodeR.reduce((a, b) => a && b, true)).to.be.eq(true);
    // const killOperatorR = await Promise.all(
    //   [
    //     {
    //       operator: addresses.registrar,
    //       owner: addresses.deployer,
    //     },
    //     {
    //       operator: addresses.owner,
    //       owner: addresses.deployer,
    //     },
    //   ].map(({ operator, owner }) =>
    //     killOperator({
    //       apid: fixtureData.apps.vnsRegistry,
    //       operator,
    //       owner,
    //     })
    //   )
    // );
    // expect(killOperatorR.reduce((a, b) => a && b, true)).to.be.eq(true);
    // const killApplicationR = await killApplication({
    //   apid: fixtureData.apps.vnsRegistry,
    //   delete: true,
    // });
    // resolver kill operations
    // Add check before deletion
    // const killNodeR = await Promise.all(
    //   ["", "voi", "nshell.voi"].map((node) =>
    //     killNode({
    //       apid: fixtureData.apps.vnsRegistry,
    //       node,
    //       sender: addresses.deployer,
    //       sk: sks.deployer,
    //     })
    //   )
    // );
    // expect(killNodeR.reduce((a, b) => a && b, true)).to.be.eq(true);
    // Add check after deletion
    // registrar kill operations
    // ------------------------------------------------------------
    // - register
    //   - increment counter
    //   - set nft index
    //   - set nft data
    //   - set holder data
    //   - increment expiration
    // ------------------------------------------------------------
    //   - increment counter
    // const deleteBoxR = await deleteBox({
    //   apid: fixtureData.apps.vnsRegistrar,
    //   key: "YXJjNzJfY291bnRlcg==",
    // });
    // expect(deleteBoxR).to.be.eq(true);
    // //   - set nft index
    // const deleteNFTIndexR = await deleteNFTIndex({
    //   apid: fixtureData.apps.vnsRegistrar,
    //   index: 1,
    // });
    // expect(deleteNFTIndexR).to.be.eq(true);
    // //   - set nft data
    // const deleteNFTDataR = await deleteNFTData({
    //   apid: fixtureData.apps.vnsRegistrar,
    //   name: "nshell.voi",
    // });
    // expect(deleteNFTDataR).to.be.eq(true);
    // //   - set holder data
    // const deleteHolderDataR = await deleteHolderData({
    //   apid: fixtureData.apps.vnsRegistrar,
    //   address: addresses.deployer,
    // });
    // expect(deleteHolderDataR).to.be.eq(true);
    // const deleteHolderDataR2 = await deleteHolderData({
    //   apid: fixtureData.apps.vnsRegistrar,
    //   address: addresses.owner,
    // });
    // expect(deleteHolderDataR).to.be.eq(true);

    // //   - increment expiration
    // const deleteExpiresR = await deleteExpires({
    //   apid: fixtureData.apps.vnsRegistrar,
    //   name: "nshell.voi",
    // });
    // expect(deleteExpiresR).to.be.eq(true);
    // // ------------------------------------------------------------
    // // application kill operations
    // const killApplicationR = await Promise.all(
    //   [
    //     fixtureData.apps.vnsRegistry,
    //     fixtureData.apps.vnsResolver,
    //     fixtureData.apps.vnsRegistrar,
    //   ].map((apid) =>
    //     killApplication({
    //       apid,
    //       delete: true,
    //     })
    //   )
    // );
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
  // setup registry and resolver
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
  // setup registry
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
  // setup resolver
  // setup registrar
  it("can post update registrar, set root node", async function () {
    const success = await vnsRegistrarPostUpdate({
      apid: fixtureData.apps.vnsRegistrar,
      registry: fixtureData.apps.vnsRegistry,
      rootNode: "voi",
      paymentToken: fixtureData.apps.arc200,
    });
    expect(success).to.be.eq(true);
  });

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

  it("set addr.reverse owner to deployer", async function () {
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
      registry: fixtureData.apps.reverseRegistrar,
      rootNode: "reverse",
      paymentToken: fixtureData.apps.arc200,
    });
    expect(success).to.be.eq(true);
  });

  // can get length
  // {
  //   const topic = "can get length";
  //   it(topic, async function () {
  //     const name = "nshell";
  //     const length = await getLength({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name,
  //     });
  //     expect(length).to.be.eq(BigInt(6));
  //   });
  // }
  // it("can check name that is valid", async function () {
  //   const checkNameR = await checkName({
  //     apid: fixtureData.apps.vnsRegistrar,
  //     name: "nshell",
  //   });
  //   expect(checkNameR).to.be.eq(true);
  // });
  // it("can check name that is invalid capital letters", async function () {
  //   const checkNameR = await checkName({
  //     apid: fixtureData.apps.vnsRegistrar,
  //     name: "Nshell",
  //   });
  //   expect(checkNameR).to.be.eq(false);
  // });
  // it("can check name that is invalid special characters", async function () {
  //   const checkNameR = await checkName({
  //     apid: fixtureData.apps.vnsRegistrar,
  //     name: "nshell!",
  //   });
  //   expect(checkNameR).to.be.eq(false);
  // });
  // it("can check name that is invalid spaces", async function () {
  //   const checkNameR = await checkName({
  //     apid: fixtureData.apps.vnsRegistrar,
  //     name: "n shell",
  //   });
  //   expect(checkNameR).to.be.eq(false);
  // });
  // it("can check name that is valid with 32 characters", async function () {
  //   const checkNameR = await checkName({
  //     apid: fixtureData.apps.vnsRegistrar,
  //     name: "a".repeat(32),
  //   });
  //   expect(checkNameR).to.be.eq(true);
  // });
  // it("can check name that is invalid with 33 characters", async function () {
  //   const checkNameR = await checkName({
  //     apid: fixtureData.apps.vnsRegistrar,
  //     name: "a".repeat(33),
  //   });
  //   expect(checkNameR).to.be.eq(false);
  // });
  // {
  //   const topic = "can get price";
  //   it(topic, async function () {
  //     const price = await getPrice({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name: "nshell",
  //       duration: 365 * 24 * 60 * 60,
  //     });
  //     expect(price).to.be.eq(BigInt(5e6));
  //     fixtureData.context.price = price;
  //   });
  // }
  // {
  //   const topic = "can check price based on name length and duration";
  //   it(topic, async function () {
  //     {
  //       const name = "a";
  //       const duration = fixtureData.context.duration;
  //       const price = await getPrice({
  //         apid: fixtureData.apps.vnsRegistrar,
  //         name,
  //         duration,
  //       });
  //       expect(price).to.be.eq(BigInt(160e6));
  //     }
  //     {
  //       const name = "ab";
  //       const duration = fixtureData.context.duration;
  //       const price = await getPrice({
  //         apid: fixtureData.apps.vnsRegistrar,
  //         name,
  //         duration,
  //       });
  //       expect(price).to.be.eq(BigInt(80e6));
  //     }
  //     {
  //       const name = "abc";
  //       const duration = fixtureData.context.duration;
  //       const price = await getPrice({
  //         apid: fixtureData.apps.vnsRegistrar,
  //         name,
  //         duration,
  //       });
  //       expect(price).to.be.eq(BigInt(40e6));
  //     }
  //     {
  //       const name = "abcd";
  //       const duration = fixtureData.context.duration;
  //       const price = await getPrice({
  //         apid: fixtureData.apps.vnsRegistrar,
  //         name,
  //         duration,
  //       });
  //       expect(price).to.be.eq(BigInt(20e6));
  //     }
  //     {
  //       const name = "abcde";
  //       const duration = fixtureData.context.duration;
  //       const price = await getPrice({
  //         apid: fixtureData.apps.vnsRegistrar,
  //         name,
  //         duration,
  //       });
  //       expect(price).to.be.eq(BigInt(10e6));
  //     }
  //     {
  //       const name = "abcdef";
  //       const duration = fixtureData.context.duration;
  //       const price = await getPrice({
  //         apid: fixtureData.apps.vnsRegistrar,
  //         name,
  //         duration,
  //       });
  //       expect(price).to.be.eq(BigInt(5e6));
  //     }
  //     {
  //       const name = "abcdefg";
  //       const duration = fixtureData.context.duration;
  //       const price = await getPrice({
  //         apid: fixtureData.apps.vnsRegistrar,
  //         name,
  //         duration,
  //       });
  //       expect(price).to.be.eq(BigInt(5e6));
  //     }
  //     {
  //       const name = "abcdefgh";
  //       const duration = 2 * fixtureData.context.duration;
  //       const price = await getPrice({
  //         apid: fixtureData.apps.vnsRegistrar,
  //         name,
  //         duration,
  //       });
  //       expect(price).to.be.eq(BigInt(10e6));
  //     }
  //     {
  //       const name = "abcdefgh";
  //       const duration = 5 * fixtureData.context.duration;
  //       const price = await getPrice({
  //         apid: fixtureData.apps.vnsRegistrar,
  //         name,
  //         duration,
  //       });
  //       expect(price).to.be.eq(BigInt(25e6));
  //     }
  //   });
  // }
  // can mint registrar root node
  // TODO write test
  // can not register subnode nshell.voi without valid duration
  // {
  //   const topic = "can not register subnode nshell.voi without valid duration";
  //   it(topic, async function () {
  //     const name = "nshell";
  //     const duration = 0;
  //     const success = await register({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name,
  //       owner: addresses.deployer,
  //       duration,
  //     });
  //     expect(success).to.be.eq(false);
  //   });
  // }
  // can not register subnode nshell.voi without payment
  // {
  //   const topic = "can not register subnode nshell.voi without payment";
  //   it(topic, async function () {
  //     const name = "nshell";
  //     const duration = 365 * 24 * 60 * 60 - 1;
  //     // ------------------------------------------------------------
  //     // approve spending
  //     //   expect success
  //     // ------------------------------------------------------------
  //     const approveR = await arc200Approve({
  //       apid: fixtureData.apps.arc200,
  //       spender: algosdk.getApplicationAddress(fixtureData.apps.vnsRegistrar),
  //       amount: 0,
  //       sender: addresses.deployer,
  //       sk: sks.deployer,
  //       extraPayment: 28500,
  //     });
  //     expect(approveR).to.be.eq(true);
  //     // ------------------------------------------------------------
  //     // register without payment
  //     //   expect failure
  //     // ------------------------------------------------------------
  //     const success = await register({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name,
  //       owner: addresses.deployer,
  //       duration,
  //     });
  //     expect(success).to.be.eq(false);
  //     // ------------------------------------------------------------
  //   });
  // }
  // can register subnode nshell.voi
  // {
  //   const topic = "can register subnode nshell.voi";
  //   it(topic, async function () {
  //     //console.log(topic);
  //     const name = "nshell";
  //     // Get root node before registration
  //     const rootNodeOwner = await ownerOf({
  //       apid: fixtureData.apps.vnsRegistry,
  //       node: "voi",
  //     });
  //     expect(rootNodeOwner).to.be.eq(
  //       algosdk.getApplicationAddress(fixtureData.apps.vnsRegistrar)
  //     );
  //     //console.log("  rootNodeOwner", rootNodeOwner);
  //     const ownerBeforeRegistration = await ownerOf({
  //       apid: fixtureData.apps.vnsRegistry,
  //       node: `${name}.voi`,
  //     });
  //     //console.log("  ownerBeforeRegistration", ownerBeforeRegistration);
  //     expect(ownerBeforeRegistration).to.be.eq(ALGORAND_ZERO_ADDRESS_STRING);
  //     // ------------------------------------------------------------
  //     // approve spending
  //     // ------------------------------------------------------------
  //     const balanceBefore = await arc200BalanceOf({
  //       apid: fixtureData.apps.arc200,
  //       owner: addresses.deployer,
  //     });
  //     //console.log("  balanceBefore", balanceBefore);
  //     const duration = 365 * 24 * 60 * 60;
  //     const price = fixtureData.context.price;
  //     const approveR = await arc200Approve({
  //       apid: fixtureData.apps.arc200,
  //       spender: algosdk.getApplicationAddress(fixtureData.apps.vnsRegistrar),
  //       amount: price,
  //       sender: addresses.deployer,
  //       sk: sks.deployer,
  //       extraPayment: 28500,
  //     });
  //     expect(approveR).to.be.eq(true);
  //     const approvalBefore = await arc200Allowance({
  //       apid: fixtureData.apps.arc200,
  //       owner: addresses.deployer,
  //       spender: algosdk.getApplicationAddress(fixtureData.apps.vnsRegistrar),
  //     });
  //     //console.log("  approvalBefore", approvalBefore);
  //     // ------------------------------------------------------------
  //     const success = await register({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name,
  //       owner: addresses.deployer,
  //       duration,
  //     });
  //     expect(success).to.be.eq(true);
  //     // ------------------------------------------------------------
  //     const ownerAfterRegistration = await ownerOf({
  //       apid: fixtureData.apps.vnsRegistry,
  //       node: `${name}.voi`,
  //     });
  //     expect(ownerAfterRegistration).to.be.eq(addresses.deployer);
  //     const approvalAfter = await arc200Allowance({
  //       apid: fixtureData.apps.arc200,
  //       owner: addresses.deployer,
  //       spender: algosdk.getApplicationAddress(fixtureData.apps.vnsRegistrar),
  //     });
  //     //console.log("  approvalAfter", approvalAfter);
  //     const balanceAfter = await arc200BalanceOf({
  //       apid: fixtureData.apps.arc200,
  //       owner: addresses.deployer,
  //     });
  //     //console.log("  balanceAfter", balanceAfter);
  //     // ------------------------------------------------------------
  //   });
  // }
  // can not register subnode nshell.voi if already registered
  // {
  //   const topic = "can not register subnode nshell.voi if already registered";
  //   it(topic, async function () {
  //     const name = "nshell";
  //     // ------------------------------------------------------------
  //     // approve spending
  //     // ------------------------------------------------------------
  //     const duration = 365 * 24 * 60 * 60;
  //     const price = fixtureData.context.price;
  //     const approveR = await arc200Approve({
  //       apid: fixtureData.apps.arc200,
  //       spender: algosdk.getApplicationAddress(fixtureData.apps.vnsRegistrar),
  //       amount: price,
  //       sender: addresses.deployer,
  //       sk: sks.deployer,
  //       extraPayment: 28500,
  //     });
  //     expect(approveR).to.be.eq(true);
  //     // ------------------------------------------------------------
  //     const success = await register({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name,
  //       owner: addresses.deployer,
  //       duration,
  //     });
  //     expect(success).to.be.eq(false);
  //     // ------------------------------------------------------------
  //     const approveR2 = await arc200Approve({
  //       apid: fixtureData.apps.arc200,
  //       spender: algosdk.getApplicationAddress(fixtureData.apps.vnsRegistrar),
  //       amount: 0,
  //       sender: addresses.deployer,
  //       sk: sks.deployer,
  //       extraPayment: 28500,
  //     });
  //     expect(approveR2).to.be.eq(true);
  //     // ------------------------------------------------------------
  //   });
  // }
  // check if expired valid
  // {
  //   const topic = "check if expired valid";
  //   it(topic, async function () {
  //     const isExpiredR = await isExpired({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name: "nshell",
  //     });
  //     expect(isExpiredR).to.be.eq(false);
  //   });
  // }
  // check if non-existent name is expired
  // non-existent name is not expired
  // {
  //   const topic = "check if expired expired";
  //   it(topic, async function () {
  //     const isExpiredR = await isExpired({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name: "nshella",
  //     });
  //     expect(isExpiredR).to.be.eq(false);
  //   });
  // }
  // check ARC72 owner of
  // {
  //   const topic = "check ARC72 owner of";
  //   it(topic, async function () {
  //     const owner = await arc72OwnerOf({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name: "nshell.voi",
  //     });
  //     expect(owner).to.be.eq(addresses.deployer);
  //   });
  // }
  // {
  //   const topic = "check ARC72 owner of";
  //   it(topic, async function () {
  //     const owner = await arc72OwnerOf({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name: "voi",
  //     });
  //     expect(owner).to.be.eq(ALGORAND_ZERO_ADDRESS_STRING);
  //   });
  // }
  // {
  //   const topic = "check ARC72 owner of";
  //   it(topic, async function () {
  //     const owner = await arc72OwnerOf({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name: "nshella.voi",
  //     });
  //     expect(owner).to.be.eq(ALGORAND_ZERO_ADDRESS_STRING);
  //   });
  // }
  // // owner accurate after arc72 transfer
  // {
  //   const topic = "owner accurate after arc72 transfer";
  //   it(topic, async function () {
  //     //console.log(topic);
  //     const ownerBefore = await arc72OwnerOf({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name: "nshell.voi",
  //     });
  //     //console.log("  ownerBefore", ownerBefore);
  //     expect(ownerBefore).to.be.eq(addresses.deployer);
  //     const transferR = await arc72TransferFrom({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name: "nshell.voi",
  //       from: addresses.deployer,
  //       to: addresses.owner,
  //       sender: addresses.deployer,
  //       sk: sks.deployer,
  //     });
  //     expect(transferR).to.be.eq(true);
  //     const ownerAfter = await arc72OwnerOf({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name: "nshell.voi",
  //     });
  //     //console.log("  ownerAfter", ownerAfter);
  //     expect(ownerAfter).to.be.eq(addresses.owner);
  //     // check registry owner after change
  //     //   expect registry owner unchanged
  //     const registryOwnerAfter = await ownerOf({
  //       apid: fixtureData.apps.vnsRegistry,
  //       node: "voi",
  //     });
  //     //console.log("  registryOwnerAfter", registryOwnerAfter);
  //     expect(registryOwnerAfter).to.be.eq(
  //       algosdk.getApplicationAddress(fixtureData.apps.vnsRegistrar)
  //     );
  //   });

  //   // can renew
  //   {
  //     const topic = "can renew";
  //     it(topic, async function () {
  //       const price = fixtureData.context.price;
  //       const duration = 365 * 24 * 60 * 60;
  //       const approveR = await arc200Approve({
  //         apid: fixtureData.apps.arc200,
  //         spender: algosdk.getApplicationAddress(fixtureData.apps.vnsRegistrar),
  //         amount: price,
  //         sender: addresses.deployer,
  //         sk: sks.deployer,
  //         extraPayment: 28500,
  //       });
  //       expect(approveR).to.be.eq(true);
  //       const expirationBefore = await expiration({
  //         apid: fixtureData.apps.vnsRegistrar,
  //         name: "nshell.voi",
  //       });
  //       //console.log("  expirationBefore", expirationBefore);
  //       const success = await renew({
  //         apid: fixtureData.apps.vnsRegistrar,
  //         name: "nshell",
  //         duration,
  //       });
  //       expect(success).to.be.eq(true);
  //       const expirationAfter = await expiration({
  //         apid: fixtureData.apps.vnsRegistrar,
  //         name: "nshell.voi",
  //       });
  //       //console.log("  expirationAfter", expirationAfter);
  //       expect(Number(expirationAfter)).to.be.gt(Number(expirationBefore));
  //       expect(Number(expirationAfter)).to.be.eq(
  //         Number(expirationBefore) + duration
  //       );
  //     });
  //   }
  // }
  // // can not reclaim if not nft owner
  // // can reclaim if nft owner
  // {
  //   const topic = "can reclaim if nft owner";
  //   it(topic, async function () {
  //     //console.log(topic);
  //     const name = "nshell";
  //     const nftOwnerBefore = await arc72OwnerOf({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name: `${name}.voi`,
  //     });
  //     const registryOwnerBefore = await ownerOf({
  //       apid: fixtureData.apps.vnsRegistry,
  //       node: `${name}.voi`,
  //     });
  //     //console.log("  registryOwnerBefore", registryOwnerBefore);
  //     //console.log("  nftOwnerBefore", nftOwnerBefore);
  //     expect(nftOwnerBefore).to.be.not.eq(registryOwnerBefore);
  //     const reclaimR = await reclaim({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name,
  //       sender: addresses.owner,
  //       sk: sks.owner,
  //     });
  //     expect(reclaimR).to.be.eq(true);
  //     const nftOwnerAfter = await arc72OwnerOf({
  //       apid: fixtureData.apps.vnsRegistrar,
  //       name: `${name}.voi`,
  //     });
  //     //console.log("  nftOwnerAfter", nftOwnerAfter);
  //     const registryOwnerAfter = await ownerOf({
  //       apid: fixtureData.apps.vnsRegistry,
  //       node: `${name}.voi`,
  //     });
  //     //console.log("  registryOwnerAfter", registryOwnerAfter);
  //     //console.log("  nftOwnerAfter", nftOwnerAfter);
  //     expect(nftOwnerAfter).to.be.eq(registryOwnerAfter);
  //   });
  // }
  // // resolver opts
  // // can set addr in resolver
  // {
  //   const topic = "can set addr in resolver";
  //   it(topic, async function () {
  //     const name = "nshell";
  //     console.log(topic);
  //     const resolveAddrBefore = await resolveAddr({
  //       apid: fixtureData.apps.vnsResolver,
  //       node: `${name}.voi`,
  //     });
  //     console.log("  resolveAddrBefore", resolveAddrBefore);
  //     //expect(resolveAddrBefore).to.be.eq(addresses.deployer);
  //     const setAddrR = await setAddr({
  //       apid: fixtureData.apps.vnsResolver,
  //       node: `${name}.voi`,
  //       addr: addresses.owner,
  //       sender: addresses.owner,
  //       sk: sks.owner,
  //     });
  //     expect(setAddrR).to.be.eq(true);
  //     const resolveAddrAfter = await resolveAddr({
  //       apid: fixtureData.apps.vnsResolver,
  //       node: `${name}.voi`,
  //     });
  //     console.log("  resolveAddrAfter", resolveAddrAfter);
  //     //expect(resolveAddrAfter).to.be.eq(addresses.owner);
  //   });
  // }
});
