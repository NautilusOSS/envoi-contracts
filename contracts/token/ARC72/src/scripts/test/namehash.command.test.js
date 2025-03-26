import { expect } from "chai";
import { namehash, bytesToBase64, bytesToHex } from "../command.js";

const baseFixtureData = {
  apps: {
    vnsRegistry: 1,
    appSeries: [],
  },
  context: {},
};

// Path : VNSRegistry:namehash

describe("VNSRegistry:namehash Test Suite", function () {
  this.timeout(60_000);
  let fixtureData = baseFixtureData;
  before(async function () {
    console.log("Once upon a time...");
  });
  after(async function () {
    console.log("Happily ever after");
  });
  it("namhash root accurate", async function () {
    const root = bytesToHex(namehash(""));
    expect(root).to.be.eq(
      "0000000000000000000000000000000000000000000000000000000000000000"
    );
  });
  it("namehash single hi accurate", async function () {
    const root = bytesToHex(namehash("hi"));
    expect(root).to.be.eq(
      "cf785791e1e0a0c644540a083666e8f82524edd2abab893e95ed03dacfe838c3"
    );
  });
  it("namehash single voi accurate", async function () {
    const root = bytesToHex(namehash("voi"));
    expect(root).to.be.eq(
      "b450c7e69b509b3d8c47d59c1cf8f6b141fe78244c5fd37df696a8bda7b0d541"
    );
  });
  it("namehash single nshell.voi accurate", async function () {
    const root = bytesToHex(namehash("nshell.voi"));
    expect(root).to.be.eq(
      "fc2a2092c76b2020fa47eba60c78705bf7d307aafac450f34959e0e63c8a4323"
    );
  });
  it("namehash single asdfasdf.voi accurate", async function () {
    const root = bytesToHex(namehash("asdfasdf.voi"));
    expect(root).to.be.eq(
      "9bae76fafbe6308850e646cdc45b750a9f5a52ea10fd03d20adae116ac0c188d"
    );
  });
  // namehashe('G3MSA75OZEJTCCENOJDLDJK7UD7E2K5DNC7FVHCNOV7E3I4DTXTOWDUIFQ.addr.reverse') = ...
  it("namehashe G3MSA75OZEJTCCENOJDLDJK7UD7E2K5DNC7FVHCNOV7E3I4DTXTOWDUIFQ.addr.reverse accurate", async function () {
    const root = bytesToHex(
      namehash(
        "G3MSA75OZEJTCCENOJDLDJK7UD7E2K5DNC7FVHCNOV7E3I4DTXTOWDUIFQ.addr.reverse"
      )
    );
    expect(root).to.be.eq(
      "de9b09fd7c5f901e23a3f19fecc54828e9c848539801e86591bd9801b019f84f"
    );
  });
  // namehashe('addr.reverse') = ...
  it("namehashe addr.reverse accurate", async function () {
    const root = bytesToHex(namehash("addr.reverse"));
    expect(root).to.be.eq(
      "de9b09fd7c5f901e23a3f19fecc54828e9c848539801e86591bd9801b019f84f"
    );
  });
  it("namehash keccak256 root accurate", async function () {
    const root = bytesToBase64(namehash("", "keccak256"));
    expect(root).to.be.eq("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=");
  });
  // namehash('eth') = 0x93cdeb708b7545dc668eb9280176169d1c33cfd8ed6f04690a0bcc88a93fc4ae
  it("namehash keccak256 eth accurate", async function () {
    const root = bytesToHex(namehash("eth", "keccak256"));
    expect(root).to.be.eq(
      "93cdeb708b7545dc668eb9280176169d1c33cfd8ed6f04690a0bcc88a93fc4ae"
    );
  });
  // namehash('foo.eth') = 0xde9b09fd7c5f901e23a3f19fecc54828e9c848539801e86591bd9801b019f84f
  it("namehash keccak256 foo.eth accurate", async function () {
    const root = bytesToHex(namehash("foo.eth", "keccak256"));
    expect(root).to.be.eq(
      "de9b09fd7c5f901e23a3f19fecc54828e9c848539801e86591bd9801b019f84f"
    );
  });
});
