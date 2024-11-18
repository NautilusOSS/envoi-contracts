import { expect } from "chai";
import {
  deploy,
  sks,
  addressses,
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
    appSeries: [],
  },
  context: {},
};

// Path : VNSRegistry

describe("VNSRegistry:core:resolver Test Suite", function () {
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
          sender: addressses.deployer,
          sk: sks.deployer,
        })
      )
    );
    expect(killNodeR.reduce((a, b) => a && b, true)).to.be.eq(true);
    const killOperatorR = await Promise.all(
      [
        {
          operator: addressses.registrar,
          owner: addressses.deployer,
        },
        {
          operator: addressses.owner,
          owner: addressses.deployer,
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
    expect(owner).to.be.eq(addressses.deployer);
  });
  it("root node resolver", async function () {
    const resolverR = await resolver({
      apid: fixtureData.apps.vnsRegistry,
    });
    expect(resolverR).to.be.eq(BigInt(0));
  });
  it("root node ttl", async function () {
    const ttlR = await ttl({
      apid: fixtureData.apps.vnsRegistry,
    });
    expect(ttlR).to.be.eq(BigInt(86400));
  });
  it("set resolver root", async function () {
    const setResolverR = await setResolver({
      apid: fixtureData.apps.vnsRegistry,
      resolver: 1,
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
      owner: addressses.deployer,
      resolver: 2,
      ttl: 2,
    });
    expect(setRecordR).to.be.eq(true);
    const ownerR2 = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
    });
    expect(ownerR2).to.be.eq(addressses.deployer);
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
          sender: addressses.deployer,
          sk: sks.deployer,
          extraPayment: recordBoxCost,
          node: "",
          label: "hi",
          owner: addressses.owner,
        })
      );
      const expectedSetSubnodeOwnerR = bytesToHex(namehash("hi"));
      expect(setSubnodeOwnerR).to.be.eq(expectedSetSubnodeOwnerR);
      const ownerR3 = await ownerOf({
        apid: fixtureData.apps.vnsRegistry,
        node: "hi",
      });
      expect(ownerR3).to.be.eq(addressses.owner);
    }
    {
      const setSubnodeOwnerR = bytesToHex(
        await setSubnodeOwner({
          apid: fixtureData.apps.vnsRegistry,
          sender: addressses.deployer,
          sk: sks.deployer,
          extraPayment: recordBoxCost,
          node: "",
          label: "voi",
          owner: addressses.deployer,
          extraPayment: recordBoxCost,
        })
      );
      const expectedSetSubnodeOwnerR = bytesToHex(namehash("voi"));
      expect(setSubnodeOwnerR).to.be.eq(expectedSetSubnodeOwnerR);
      const ownerR3 = await ownerOf({
        apid: fixtureData.apps.vnsRegistry,
        node: "voi",
      });
      expect(ownerR3).to.be.eq(addressses.deployer);
    }
  });

  it("set resolver as subnode owner hi", async function () {
    const setResolverR = await setResolver({
      apid: fixtureData.apps.vnsRegistry,
      node: "hi",
      resolver: 3,
      sender: addressses.owner,
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
      sender: addressses.owner,
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
    expect(ownerBefore).to.be.eq(addressses.owner);
    const setOwnerR = await setOwner({
      apid: fixtureData.apps.vnsRegistry,
      sender: addressses.owner,
      sk: sks.owner,
      node: "hi",
      owner: addressses.deployer,
    });
    expect(setOwnerR).to.be.eq(true);
    const ownerAfter = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "hi",
    });
    expect(ownerAfter).to.be.eq(addressses.deployer);
  });

  it("setApprovalForAll", async function () {
    {
      const isApprovedForAllR = await isApprovedForAll({
        apid: fixtureData.apps.vnsRegistry,
        operator: addressses.owner,
        owner: addressses.deployer,
      });
      expect(isApprovedForAllR).to.be.eq(false);
      const setApprovalForAllR = await setApprovalForAll({
        apid: fixtureData.apps.vnsRegistry,
        operator: addressses.owner,
        approved: true,
      });
      expect(setApprovalForAllR).to.be.eq(true);
      const isApprovedForAllR2 = await isApprovedForAll({
        apid: fixtureData.apps.vnsRegistry,
        operator: addressses.owner,
        owner: addressses.deployer,
      });
      expect(isApprovedForAllR2).to.be.eq(true);
    }
    {
      const setApprovalForAllR = await setApprovalForAll({
        apid: fixtureData.apps.vnsRegistry,
        node: "voi",
        operator: addressses.registrar,
        approved: true,
      });
      expect(setApprovalForAllR).to.be.eq(true);
      const isApprovedForAllR2 = await isApprovedForAll({
        apid: fixtureData.apps.vnsRegistry,
        node: "voi",
        operator: addressses.registrar,
        owner: addressses.deployer,
      });
      expect(isApprovedForAllR2).to.be.eq(true);
    }
  });

  it("operator can set owner", async function () {
    const ownerBefore = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "voi",
    });
    expect(ownerBefore).to.be.eq(addressses.deployer);
    const setOwnerR = await setOwner({
      apid: fixtureData.apps.vnsRegistry,
      sender: addressses.registrar,
      sk: sks.registrar,
      node: "voi",
      owner: addressses.registrar,
    });
    expect(setOwnerR).to.be.eq(true);
    const ownerAfter = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "voi",
    });
    expect(ownerAfter).to.be.eq(addressses.registrar);
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
            owner: addressses.owner,
            sender: addressses.registrar,
            sk: sks.registrar,
            extraPayment: recordBoxCost,
          })
        );
        expect(setSubnodeOwnerR).to.be.eq(bytesToHex(namehash(`${label}.voi`)));
        const ownerAfter = await ownerOf({
          apid: fixtureData.apps.vnsRegistry,
          node: `${label}.voi`,
        });
        expect(ownerAfter).to.be.eq(addressses.owner);
      })
    );
  });

  it("operator can set resolver", async function () {
    const setResolverR = await setResolver({
      apid: fixtureData.apps.vnsRegistry,
      node: "nshell.voi",
      resolver: 4,
      sender: addressses.registrar,
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
      sender: addressses.registrar,
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
        owner: addressses.deployer,
        sender: addressses.registrar,
        sk: sks.registrar,
        extraPayment: recordBoxCost,
      })
    );
    expect(setSubnodeOwnerR).to.be.eq(bytesToHex(namehash("a.nshell.voi")));
    const ownerR6 = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "a.nshell.voi",
    });
    expect(ownerR6).to.be.eq(addressses.deployer);
  });

  it("owner can set subnode owner level 4", async function () {
    const setSubnodeOwnerR = bytesToHex(
      await setSubnodeOwner({
        apid: fixtureData.apps.vnsRegistry,
        node: "a.nshell.voi",
        label: "b",
        owner: addressses.deployer,
        extraPayment: recordBoxCost,
      })
    );
    expect(setSubnodeOwnerR).to.be.eq(bytesToHex(namehash("b.a.nshell.voi")));
    const ownerR7 = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "b.a.nshell.voi",
    });
    expect(ownerR7).to.be.eq(addressses.deployer);
  });

  // owner can approve
  // approved can set owner
  // approved can set resolver
  // approved can set ttl
});
