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
  setAddr,
  resolveAddr,
  resolveName,
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

describe("VNSRegistry:core:resolver Test Suite", function () {
  this.timeout(60_000);
  let fixtureData = baseFixtureData;
  before(async function () {
    console.log("Once upon a time...");
    const vnsRegistry = await deploy({
      type: "vns-registry",
      name: "test-registry5",
    });
    console.log(vnsRegistry);
    fixtureData.apps.vnsRegistry = vnsRegistry;
    const vnsResolver = await deploy({
      type: "vns-resolver",
      name: "test-resolver5",
    });
    fixtureData.apps.vnsResolver = vnsResolver;
  });
  after(async function () {
    const killNodeR = await Promise.all(
      ["", "voi"].map((node) =>
        killNode({
          apid: fixtureData.apps.vnsRegistry,
          node,
          sender: addresses.deployer,
          sk: sks.deployer,
        })
      )
    );
    expect(killNodeR.reduce((a, b) => a && b, true)).to.be.eq(true);
    const killAddrR = await killAddr({
      apid: fixtureData.apps.vnsResolver,
      node: "voi",
    });
    const killApplicationR = await killApplication({
      apid: fixtureData.apps.vnsRegistry,
      delete: true,
    });
    const killApplicationR2 = await killApplication({
      apid: fixtureData.apps.vnsResolver,
      delete: true,
    });
    expect(killAddrR).to.be.eq(true);
    expect(killApplicationR).to.be.eq(true);
    expect(killApplicationR2).to.be.eq(true);
    console.log("Happily ever after");
  });
  it("should deploy", async function () {
    console.log(fixtureData.apps);
    expect(fixtureData.apps.vnsRegistry).to.be.a("number");
    expect(fixtureData.apps.vnsRegistry).to.be.greaterThan(0);
    expect(fixtureData.apps.vnsResolver).to.be.a("number");
    expect(fixtureData.apps.vnsResolver).to.be.greaterThan(0);
  });
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
  it("set subnode owner voi", async function () {
    const setSubnodeOwnerR = bytesToHex(
      await setSubnodeOwner({
        apid: fixtureData.apps.vnsRegistry,
        sender: addresses.deployer,
        sk: sks.deployer,
        extraPayment: recordBoxCost,
        node: "",
        label: "voi",
        owner: addresses.deployer,
      })
    );
    const expectedSetSubnodeOwnerR = bytesToHex(namehash("voi"));
    expect(setSubnodeOwnerR).to.be.eq(expectedSetSubnodeOwnerR);
    const ownerR = await ownerOf({
      apid: fixtureData.apps.vnsRegistry,
      node: "voi",
    });
    expect(ownerR).to.be.eq(addresses.deployer);
    const resolverR = await resolver({
      apid: fixtureData.apps.vnsRegistry,
      node: "voi",
    });
    expect(resolverR).to.be.eq(BigInt(fixtureData.apps.vnsResolver));
  });
  it("owner can set addr", async function () {
    const resolveAddrR = await resolveAddr({
      apid: fixtureData.apps.vnsResolver,
      node: "voi",
    });
    expect(resolveAddrR).to.be.eq(ALGORAND_ZERO_ADDRESS_STRING);
    const setAddrR = await setAddr({
      apid: fixtureData.apps.vnsResolver,
      node: "voi",
      addr: addresses.deployer,
      sender: addresses.deployer,
      sk: sks.deployer,
    });
    expect(setAddrR).to.be.eq(true);
    const resolveAddrR2 = await resolveAddr({
      apid: fixtureData.apps.vnsResolver,
      node: "voi",
    });
    expect(resolveAddrR2).to.be.eq(addresses.deployer);
  });
  // default name
  it("can resolve name", async function () {
    const resolveNameR = await resolveName({
      apid: fixtureData.apps.vnsResolver,
      registry: fixtureData.apps.vnsRegistry,
      node: "voi",
    });
    console.log(resolveNameR);
  });
  // set name
});
