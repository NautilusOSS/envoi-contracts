import { expect } from "chai";
import {
  deploy,
  killApplication,
  killAccount,
  killReservation,
  reserve,
  release,
  price,
  addresses,
  sks,
  namehash,
  accountNode,
  bytesToBase64,
  rsvpEvents,
  adminRelease,
  adminReserve,
  reservationPrice,
  arc200Mint,
  arc200DeleteBalance,
  arc200DeleteApproval,
  arc200BalanceOf,
  arc200Approve,
  arc200Allowance,
  arc200Transfer,
  arc200TransferFrom,
  arc200TotalSupply,
  arc200Name,
  arc200Symbol,
  arc200Decimals,
} from "../command.js";

const baseFixtureData = {
  apps: {
    arc200: 0,
    appSeries: [],
  },
  context: {},
};

const stripTrailingZeroBytes = (str) => {
  return str.replace(/\0+$/, "");
};

// Path : VNSRSVP

describe("VNS:core:arc200 Test Suite", function () {
  this.timeout(60_000);
  let fixtureData = baseFixtureData;
  before(async function () {
    console.log("Once upon a time...");
    const token = await deploy({
      type: "arc200",
      name: "test-arc200",
    });
    fixtureData.apps.arc200 = token;
  });
  after(async function () {
    const deleteBalanceR = await Promise.all(
      Object.values(addresses).map((address) =>
        arc200DeleteBalance({
          apid: fixtureData.apps.arc200,
          owner: address,
        })
      )
    );
    expect(deleteBalanceR.reduce((acc, curr) => acc && curr, true)).to.be.eq(
      true
    );
    const deleteApprovalR = await arc200DeleteApproval({
      apid: fixtureData.apps.arc200,
      owner: addresses.deployer,
      spender: addresses.owner,
    });
    expect(deleteApprovalR).to.be.eq(true);
    const killApplicationR = await killApplication({
      apid: fixtureData.apps.arc200,
      delete: true,
    });
    expect(killApplicationR).to.be.eq(true);
    console.log("Happily ever after");
  });
  it("should deploy", async function () {
    expect(fixtureData.apps.arc200).to.be.gt(0);
  });
  it("can mint", async function () {
    const mintR = await arc200Mint({
      apid: fixtureData.apps.arc200,
      recipient: addresses.deployer,
      name: "TEST",
      symbol: "TEST",
      totalSupply: 1000,
      decimals: 6,
      sender: addresses.deployer,
      sk: sks.deployer,
    });
    expect(mintR).to.be.eq(true);
    // check global state
    // check balance of deployer is totalSupply
    // check events
  });
  it("can get decimals", async function () {
    const decimalsR = await arc200Decimals({
      apid: fixtureData.apps.arc200,
    });
    expect(decimalsR).to.be.eq("6");
  });
  it("can get symbol", async function () {
    const symbolR = await arc200Symbol({
      apid: fixtureData.apps.arc200,
    });
    expect(symbolR).to.be.eq("TEST");
  });
  it("can get name", async function () {
    const nameR = await arc200Name({
      apid: fixtureData.apps.arc200,
    });
    expect(nameR).to.be.eq("TEST");
  });
  it("can get symbol", async function () {
    const symbolR = await arc200Symbol({
      apid: fixtureData.apps.arc200,
    });
    expect(symbolR).to.be.eq("TEST");
  });
  it("can get total supply", async function () {
    const totalSupplyR = await arc200TotalSupply({
      apid: fixtureData.apps.arc200,
    });
    expect(totalSupplyR).to.be.eq("1000");
  });
  it("can get balance", async function () {
    const balanceR = await arc200BalanceOf({
      apid: fixtureData.apps.arc200,
      owner: addresses.deployer,
    });
    expect(balanceR).to.be.eq("1000");
    const balanceR2 = await arc200BalanceOf({
      apid: fixtureData.apps.arc200,
      owner: addresses.owner,
    });
    expect(balanceR2).to.be.eq("0");
  });
  it("can approve", async function () {
    const approveR = await arc200Approve({
      apid: fixtureData.apps.arc200,
      spender: addresses.owner,
      amount: 1,
    });
    expect(approveR).to.be.eq(true);
  });
  it("can get allowance", async function () {
    const allowanceR = await arc200Allowance({
      apid: fixtureData.apps.arc200,
      owner: addresses.deployer,
      spender: addresses.owner,
    });
    expect(allowanceR).to.be.eq("1");
  });
  it("can transfer", async function () {
    const transferR = await arc200Transfer({
      apid: fixtureData.apps.arc200,
      receiver: addresses.owner,
      amount: 1,
      sender: addresses.deployer,
      sk: sks.deployer,
    });
    expect(transferR).to.be.eq(true);
    const balanceR = await arc200BalanceOf({
      apid: fixtureData.apps.arc200,
      owner: addresses.deployer,
    });
    expect(balanceR).to.be.eq("999");
    const balanceR2 = await arc200BalanceOf({
      apid: fixtureData.apps.arc200,
      owner: addresses.owner,
    });
    expect(balanceR2).to.be.eq("1");
  });
  it("can transferFrom", async function () {
    const allowanceR = await arc200Allowance({
      apid: fixtureData.apps.arc200,
      owner: addresses.deployer,
      spender: addresses.owner,
    });
    expect(allowanceR).to.be.eq("1");
    const transferFromR = await arc200TransferFrom({
      apid: fixtureData.apps.arc200,
      owner: addresses.deployer,
      receiver: addresses.owner,
      amount: 1,
      sender: addresses.owner,
      sk: sks.owner,
    });
    expect(transferFromR).to.be.eq(true);
    const balanceR = await arc200BalanceOf({
      apid: fixtureData.apps.arc200,
      owner: addresses.deployer,
    });
    expect(balanceR).to.be.eq("998");
    const balanceR2 = await arc200BalanceOf({
      apid: fixtureData.apps.arc200,
      owner: addresses.owner,
    });
    expect(balanceR2).to.be.eq("2");
    const allowanceR2 = await arc200Allowance({
      apid: fixtureData.apps.arc200,
      owner: addresses.deployer,
      spender: addresses.owner,
    });
    expect(allowanceR2).to.be.eq("0");
  });
});
