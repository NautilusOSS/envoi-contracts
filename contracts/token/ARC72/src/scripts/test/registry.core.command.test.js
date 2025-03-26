import { expect } from "chai";
import {
  deploy,
  sks,
  addresses,
  killApplication,
  postUpdate,
  killNode,
  killOperator,
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
} from "../command.js";
import moment from "moment";
import algosdk from "algosdk";

const baseFixtureData = {
  apps: {
    vnsRegistry: 0,
    vnsResolver: 0,
    appSeries: [],
  },
  context: {},
};

// Path : VNSRegistry

describe("VNSRegistry:core:registry Test Suite", function () {
  this.timeout(60_000);
  let fixtureData = baseFixtureData;
  before(async function () {
    console.log("Once upon a time...");
    const vnsRegistry = await deploy({
      type: "vns-registry",
      name: "test-registry3",
    });
    console.log(vnsRegistry);
    fixtureData.apps.vnsRegistry = vnsRegistry;
    const vnsResolver = await deploy({
      type: "vns-resolver",
      name: "test-resolver",
    });
    fixtureData.apps.vnsResolver = vnsResolver;
  });
  after(async function () {
    const killNodeR = await Promise.all(
      [
        "",
        "hi",
        "voi",
        ...["nshell", "shelly"].map((label) => `${label}.voi`),
        "a.nshell.voi",
        "b.a.nshell.voi",
      ].map((node) =>
        killNode({
          apid: fixtureData.apps.vnsRegistry,
          node,
          sender: addresses.deployer,
          sk: sks.deployer,
        })
      )
    );
    expect(killNodeR.reduce((a, b) => a && b, true)).to.be.eq(true);
    const killOperatorR = await Promise.all(
      [
        {
          operator: addresses.registrar,
          owner: addresses.deployer,
        },
        {
          operator: addresses.owner,
          owner: addresses.deployer,
        },
      ].map(({ operator, owner }) =>
        killOperator({
          apid: fixtureData.apps.vnsRegistry,
          operator,
          owner,
        })
      )
    );
    expect(killOperatorR.reduce((a, b) => a && b, true)).to.be.eq(true);
    const killApplicationR = await killApplication({
      apid: fixtureData.apps.vnsRegistry,
      delete: true,
    });
    expect(killApplicationR).to.be.eq(true);
    console.log("Happily ever after");
  });
  it("should deploy", async function () {
    expect(fixtureData.apps.vnsRegistry).to.be.a("number");
    expect(fixtureData.apps.vnsRegistry).to.be.greaterThan(0);
  });
  // TODO test it global state accurate
  it("can post update, create root node", async function () {
    const success = await postUpdate({
      apid: fixtureData.apps.vnsRegistry,
      extraPayment: minBalance + extraPageCost + recordBoxCost,
    });
    expect(success).to.be.eq(true);
  });
  it("root node owner", async function () {
    const owner = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
    });
    expect(owner).to.be.eq(addresses.deployer);
  });
  it("root node rslvr", async function () {
    const resolverR = await resolver({
      apid: fixtureData.apps.vnsRegistry,
    });
    console.log(resolverR);
    //expect(resolverR).to.be.eq(BigInt(0));
  });
  it("root node ttl", async function () {
    const ttlR = await ttl({
      apid: fixtureData.apps.vnsRegistry,
    });
    expect(ttlR).to.be.eq(BigInt(86400));
  });
  it("root set rslvr", async function () {
    const setResolverR = await setResolver({
      apid: fixtureData.apps.vnsRegistry,
      resolver: 1,
      extraPayment: 147300,
    });
    expect(setResolverR).to.be.eq(true);
    const resolverR2 = await resolver({
      apid: fixtureData.apps.vnsRegistry,
    });
    expect(resolverR2).to.be.eq(BigInt(1));
  });
  it("set ttl root", async function () {
    const setTTLR = await setTTL({
      apid: fixtureData.apps.vnsRegistry,
      ttl: 1,
    });
    expect(setTTLR).to.be.eq(true);
    const ttlR2 = await ttl({
      apid: fixtureData.apps.vnsRegistry,
    });
    expect(ttlR2).to.be.eq(BigInt(1));
  });
  it("set record root", async function () {
    const setRecordR = await setRecord({
      apid: fixtureData.apps.vnsRegistry,
      owner: addresses.deployer,
      resolver: 2,
      ttl: 2,
    });
    expect(setRecordR).to.be.eq(true);
    const ownerR2 = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
    });
    expect(ownerR2).to.be.eq(addresses.deployer);
    const resolverR2 = await resolver({
      apid: fixtureData.apps.vnsRegistry,
    });
    expect(resolverR2).to.be.eq(BigInt(2));
    const ttlR2 = await ttl({
      apid: fixtureData.apps.vnsRegistry,
    });
    expect(ttlR2).to.be.eq(BigInt(2));
  });
  it("set subnode owner hi", async function () {
    {
      const setSubnodeOwnerR = bytesToHex(
        await setSubnodeOwner({
          apid: fixtureData.apps.vnsRegistry,
          sender: addresses.deployer,
          sk: sks.deployer,
          extraPayment: recordBoxCost,
          node: "",
          label: "hi",
          owner: addresses.owner,
          debug: true,
        })
      );
      const expectedSetSubnodeOwnerR = bytesToHex(namehash("hi"));
      expect(setSubnodeOwnerR).to.be.eq(expectedSetSubnodeOwnerR);
      const ownerR3 = await ownerOf({
        apid: fixtureData.apps.vnsRegistry,
        node: "hi",
      });
      expect(ownerR3).to.be.eq(addresses.owner);
    }
    {
      const setSubnodeOwnerR = bytesToHex(
        await setSubnodeOwner({
          apid: fixtureData.apps.vnsRegistry,
          sender: addresses.deployer,
          sk: sks.deployer,
          extraPayment: recordBoxCost,
          node: "",
          label: "voi",
          owner: addresses.deployer,
          extraPayment: recordBoxCost,
        })
      );
      const expectedSetSubnodeOwnerR = bytesToHex(namehash("voi"));
      expect(setSubnodeOwnerR).to.be.eq(expectedSetSubnodeOwnerR);
      const ownerR3 = await ownerOf({
        apid: fixtureData.apps.vnsRegistry,
        node: "voi",
      });
      expect(ownerR3).to.be.eq(addresses.deployer);
    }
  });

  it("set rslvr as subnode owner hi", async function () {
    const setResolverR = await setResolver({
      apid: fixtureData.apps.vnsRegistry,
      node: "hi",
      resolver: 3,
      sender: addresses.owner,
      sk: sks.owner,
    });
    expect(setResolverR).to.be.eq(true);
    const resolverR3 = await resolver({
      apid: fixtureData.apps.vnsRegistry,
      node: "hi",
    });
    expect(resolverR3).to.be.eq(BigInt(3));
  });

  it("set ttl as subnode owner hi", async function () {
    const setTTLR = await setTTL({
      apid: fixtureData.apps.vnsRegistry,
      node: "hi",
      ttl: 3,
      sender: addresses.owner,
      sk: sks.owner,
    });
    expect(setTTLR).to.be.eq(true);
    const ttlR3 = await ttl({
      apid: fixtureData.apps.vnsRegistry,
      node: "hi",
    });
    expect(ttlR3).to.be.eq(BigInt(3));
  });

  it("set owner as subnode owner hi", async function () {
    const ownerBefore = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "hi",
    });
    expect(ownerBefore).to.be.eq(addresses.owner);
    const setOwnerR = await setOwner({
      apid: fixtureData.apps.vnsRegistry,
      sender: addresses.owner,
      sk: sks.owner,
      node: "hi",
      owner: addresses.deployer,
    });
    expect(setOwnerR).to.be.eq(true);
    const ownerAfter = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "hi",
    });
    expect(ownerAfter).to.be.eq(addresses.deployer);
  });

  it("setApprovalForAll", async function () {
    {
      const isApprovedForAllR = await isApprovedForAll({
        apid: fixtureData.apps.vnsRegistry,
        operator: addresses.owner,
        owner: addresses.deployer,
      });
      expect(isApprovedForAllR).to.be.eq(false);
      const setApprovalForAllR = await setApprovalForAll({
        apid: fixtureData.apps.vnsRegistry,
        operator: addresses.owner,
        approved: true,
      });
      expect(setApprovalForAllR).to.be.eq(true);
      const isApprovedForAllR2 = await isApprovedForAll({
        apid: fixtureData.apps.vnsRegistry,
        operator: addresses.owner,
        owner: addresses.deployer,
      });
      expect(isApprovedForAllR2).to.be.eq(true);
    }
    {
      const setApprovalForAllR = await setApprovalForAll({
        apid: fixtureData.apps.vnsRegistry,
        node: "voi",
        operator: addresses.registrar,
        approved: true,
      });
      expect(setApprovalForAllR).to.be.eq(true);
      const isApprovedForAllR2 = await isApprovedForAll({
        apid: fixtureData.apps.vnsRegistry,
        node: "voi",
        operator: addresses.registrar,
        owner: addresses.deployer,
      });
      expect(isApprovedForAllR2).to.be.eq(true);
    }
  });

  it("operator can set owner", async function () {
    const ownerBefore = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "voi",
    });
    expect(ownerBefore).to.be.eq(addresses.deployer);
    const setOwnerR = await setOwner({
      apid: fixtureData.apps.vnsRegistry,
      sender: addresses.registrar,
      sk: sks.registrar,
      node: "voi",
      owner: addresses.registrar,
    });
    expect(setOwnerR).to.be.eq(true);
    const ownerAfter = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "voi",
    });
    expect(ownerAfter).to.be.eq(addresses.registrar);
  });

  it("operator can set subnode owner", async function () {
    const ownerBefore = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "nshell.voi",
    });
    expect(ownerBefore).to.be.eq(ALGORAND_ZERO_ADDRESS_STRING);
    await Promise.all(
      ["nshell", "shelly"].map(async (label) => {
        const setSubnodeOwnerR = bytesToHex(
          await setSubnodeOwner({
            apid: fixtureData.apps.vnsRegistry,
            node: "voi",
            label,
            owner: addresses.owner,
            sender: addresses.registrar,
            sk: sks.registrar,
            extraPayment: recordBoxCost,
          })
        );
        expect(setSubnodeOwnerR).to.be.eq(bytesToHex(namehash(`${label}.voi`)));
        const ownerAfter = await ownerOf({
          apid: fixtureData.apps.vnsRegistry,
          node: `${label}.voi`,
        });
        expect(ownerAfter).to.be.eq(addresses.owner);
      })
    );
  });

  it("operator can set resolver", async function () {
    const setResolverR = await setResolver({
      apid: fixtureData.apps.vnsRegistry,
      node: "nshell.voi",
      resolver: 4,
      sender: addresses.registrar,
      sk: sks.registrar,
    });
    expect(setResolverR).to.be.eq(true);
    const resolverR4 = await resolver({
      apid: fixtureData.apps.vnsRegistry,
      node: "nshell.voi",
    });
    expect(resolverR4).to.be.eq(BigInt(4));
  });

  it("operator can set ttl", async function () {
    const setTTLR = await setTTL({
      apid: fixtureData.apps.vnsRegistry,
      node: "nshell.voi",
      ttl: 5,
      sender: addresses.registrar,
      sk: sks.registrar,
    });
    expect(setTTLR).to.be.eq(true);
    const ttlR5 = await ttl({
      apid: fixtureData.apps.vnsRegistry,
      node: "nshell.voi",
    });
    expect(ttlR5).to.be.eq(BigInt(5));
  });

  it("owner can set subnode owner level 3", async function () {
    const setSubnodeOwnerR = bytesToHex(
      await setSubnodeOwner({
        apid: fixtureData.apps.vnsRegistry,
        node: "nshell.voi",
        label: "a",
        owner: addresses.deployer,
        sender: addresses.registrar,
        sk: sks.registrar,
        extraPayment: recordBoxCost,
      })
    );
    expect(setSubnodeOwnerR).to.be.eq(bytesToHex(namehash("a.nshell.voi")));
    const ownerR6 = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "a.nshell.voi",
    });
    expect(ownerR6).to.be.eq(addresses.deployer);
  });

  it("owner can set subnode owner level 4", async function () {
    const setSubnodeOwnerR = bytesToHex(
      await setSubnodeOwner({
        apid: fixtureData.apps.vnsRegistry,
        node: "a.nshell.voi",
        label: "b",
        owner: addresses.deployer,
        extraPayment: recordBoxCost,
      })
    );
    expect(setSubnodeOwnerR).to.be.eq(bytesToHex(namehash("b.a.nshell.voi")));
    const ownerR7 = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "b.a.nshell.voi",
    });
    expect(ownerR7).to.be.eq(addresses.deployer);
  });

  // owner can approve
  // approved can set owner
  // approved can set resolver
  // approved can set ttl
});
