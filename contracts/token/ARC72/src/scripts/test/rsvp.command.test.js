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
} from "../command.js";

const baseFixtureData = {
  apps: {
    vnsRegistry: 0,
    vnsRsvp: 0,
    appSeries: [],
  },
  context: {},
};

// Path : VNSRSVP

describe("VNS:rsvp Test Suite", function () {
  this.timeout(60_000);
  let fixtureData = baseFixtureData;
  before(async function () {
    console.log("Once upon a time...");
    const vnsRsvp = await deploy({
      type: "vns-rsvp",
      name: "test-rsvp",
    });
    console.log(vnsRsvp);
    fixtureData.apps.vnsRsvp = vnsRsvp;
  });
  after(async function () {
    await Promise.all(
      Object.values(addresses).map(async (addr) => {
        return killAccount({
          apid: fixtureData.apps.vnsRsvp,
          account: addr,
        });
      })
    );
    //
    await Promise.all(
      [
        ...["test", "test2", "test3", "test4"].map((name) =>
          [name, "voi"].join(".")
        ),
      ].map(async (node) => {
        return killReservation({
          apid: fixtureData.apps.vnsRsvp,
          node,
        });
      })
    );
    //
    const killApplicationR = await killApplication({
      apid: fixtureData.apps.vnsRsvp,
      delete: true,
    });
    expect(killApplicationR).to.be.eq(true);
    console.log("Happily ever after");
  });
  it("should deploy", async function () {
    expect(fixtureData.apps.vnsRsvp).to.be.gt(0);
  });
  it("can lookup account node", async function () {
    const accountNodeR = bytesToBase64(
      await accountNode({
        apid: fixtureData.apps.vnsRsvp,
        account: addresses.deployer,
      })
    );
    expect(accountNodeR).to.be.eq(bytesToBase64(namehash("")));
  });
  it("can lookup price 4", async function () {
    const priceR = await price({
      apid: fixtureData.apps.vnsRsvp,
      length: 4,
    });
    expect(priceR).to.be.eq(BigInt(10000));
  });
  it("can lookup price 5", async function () {
    const priceR = await price({
      apid: fixtureData.apps.vnsRsvp,
      length: 5,
    });
    expect(priceR).to.be.eq(BigInt(5000));
  });
  it("can reserve test.voi by deployer", async function () {
    const reservationPriceBefore = await reservationPrice({
      apid: fixtureData.apps.vnsRsvp,
      node: "test.voi",
    });
    const deployerNodeBefore = bytesToBase64(
      await accountNode({
        apid: fixtureData.apps.vnsRsvp,
        account: addresses.deployer,
      })
    );
    const ownerNodeBefore = bytesToBase64(
      await accountNode({
        apid: fixtureData.apps.vnsRsvp,
        account: addresses.owner,
      })
    );
    const reserveR = await reserve({
      apid: fixtureData.apps.vnsRsvp,
      node: "test.voi",
      name: "test.voi",
      length: 4,
      extraPayment: BigInt(10000 + 200000 + 69000),
      sender: addresses.deployer,
      sk: sks.deployer,
    });
    const reservationPriceAfter = await reservationPrice({
      apid: fixtureData.apps.vnsRsvp,
      node: "test.voi",
    });
    const deployerNodeAfter = bytesToBase64(
      await accountNode({
        apid: fixtureData.apps.vnsRsvp,
        account: addresses.deployer,
      })
    );
    const ownerNodeAfter = bytesToBase64(
      await accountNode({
        apid: fixtureData.apps.vnsRsvp,
        account: addresses.owner,
      })
    );
    //expect(deployerNodeAfter).to.be.eq(bytesToBase64(namehash("test.voi")));
    //expect(ownerNodeAfter).to.be.eq(bytesToBase64(namehash("")));
    expect(reserveR).to.be.eq(true);
    //expect(deployerNodeAfter).to.be.eq(bytesToBase64(namehash("test.voi")));
    //expect(ownerNodeAfter).to.be.eq(bytesToBase64(namehash("")));
    console.log({
      account: addresses.deployer,
      node: "test.voi",
      owner: addresses.owner,
      deployer: addresses.deployer,
      reservationPriceBefore,
      reservationPriceAfter,
      deployerNodeBefore,
      deployerNodeAfter,
      ownerNodeBefore,
      ownerNodeAfter,
    });
  });
  it("can not reserve test2.voi by deployer", async function () {
    const deployerNodeBefore = bytesToBase64(
      await accountNode({
        apid: fixtureData.apps.vnsRsvp,
        account: addresses.deployer,
      })
    );
    const ownerNodeBefore = bytesToBase64(
      await accountNode({
        apid: fixtureData.apps.vnsRsvp,
        account: addresses.owner,
      })
    );
    const reserveR = await reserve({
      apid: fixtureData.apps.vnsRsvp,
      node: "test2.voi",
      name: "test2.voi",
      length: 4,
      extraPayment: BigInt(10000 + 200000 + 69000),
      sender: addresses.deployer,
      sk: sks.deployer,
    });
    const deployerNodeAfter = bytesToBase64(
      await accountNode({
        apid: fixtureData.apps.vnsRsvp,
        account: addresses.deployer,
      })
    );
    const ownerNodeAfter = bytesToBase64(
      await accountNode({
        apid: fixtureData.apps.vnsRsvp,
        account: addresses.owner,
      })
    );
    //expect(deployerNodeAfter).to.be.eq(bytesToBase64(namehash("test.voi")));
    //expect(ownerNodeAfter).to.be.eq(bytesToBase64(namehash("")));
    expect(reserveR).to.be.eq(false);
    //expect(deployerNodeAfter).to.be.eq(bytesToBase64(namehash("test.voi")));
    //expect(ownerNodeAfter).to.be.eq(bytesToBase64(namehash("")));
    console.log({
      account: addresses.deployer,
      node: "test2.voi",
      owner: addresses.owner,
      deployer: addresses.deployer,
      deployerNodeBefore,
      deployerNodeAfter,
      ownerNodeBefore,
      ownerNodeAfter,
    });
  });

  // it("can not reserve again test2.voi", async function () {
  //   const reserveR = await reserve({
  //     apid: fixtureData.apps.vnsRsvp,
  //     node: "test2.voi",
  //     name: "test2.voi",
  //     length: 5,
  //     extraPayment: BigInt(5000),
  //   });
  //   expect(reserveR).to.be.eq(false);
  // });
  // it("can reserve test2.voi with other acc", async function () {
  //   const accountNodeBefore = bytesToBase64(
  //     await accountNode({
  //       apid: fixtureData.apps.vnsRsvp,
  //       account: addresses.owner,
  //     })
  //   );
  //   const reserveR = await reserve({
  //     apid: fixtureData.apps.vnsRsvp,
  //     node: "test2.voi",
  //     name: "test2.voi",
  //     length: 5,
  //     extraPayment: BigInt(259800),
  //     sender: addresses.owner,
  //     sk: sks.owner,
  //   });
  //   expect(reserveR).to.be.eq(true);
  //   const accountNodeAfter = bytesToBase64(
  //     await accountNode({
  //       apid: fixtureData.apps.vnsRsvp,
  //       account: addresses.owner,
  //     })
  //   );
  //   console.log({
  //     account: addresses.owner,
  //     node: "test2.voi",
  //     before: accountNodeBefore,
  //     after: accountNodeAfter,
  //   });
  // });
  // it("can not reserve again as other acc test3.voi", async function () {
  //   const reserveR = await reserve({
  //     apid: fixtureData.apps.vnsRsvp,
  //     node: "test3.voi",
  //     name: "test3.voi",
  //     length: 5,
  //     extraPayment: BigInt(259800),
  //     sender: addresses.owner,
  //     sk: sks.owner,
  //   });
  //   expect(reserveR).to.be.eq(false);
  // });
  // it("can not release test2.voi", async function () {
  //   const releaseR = await release({
  //     apid: fixtureData.apps.vnsRsvp,
  //     node: "test2.voi",
  //   });
  //   expect(releaseR).to.be.eq(false);
  // });
  // it("can release test.voi", async function () {
  //   const releaseR = await release({
  //     apid: fixtureData.apps.vnsRsvp,
  //     node: "test.voi",
  //   });
  //   expect(releaseR).to.be.eq(true);
  // });
  // it("can release test2.voi", async function () {
  //   const accountNodeBefore = bytesToBase64(
  //     await accountNode({
  //       apid: fixtureData.apps.vnsRsvp,
  //       account: addresses.owner,
  //     })
  //   );
  //   const releaseR = await release({
  //     apid: fixtureData.apps.vnsRsvp,
  //     node: "test2.voi",
  //     sender: addresses.owner,
  //     sk: sks.owner,
  //   });
  //   expect(releaseR).to.be.eq(true);
  //   const accountNodeAfter = bytesToBase64(
  //     await accountNode({
  //       apid: fixtureData.apps.vnsRsvp,
  //       account: addresses.owner,
  //     })
  //   );
  //   console.log({
  //     account: addresses.owner,
  //     node: "test2.voi",
  //     before: accountNodeBefore,
  //     after: accountNodeAfter,
  //   });
  // });
  // it("can reserve test.voi as other acc after release", async function () {
  //   const accountNodeBefore = bytesToBase64(
  //     await accountNode({
  //       apid: fixtureData.apps.vnsRsvp,
  //       account: addresses.owner,
  //     })
  //   );
  //   const reserveR = await reserve({
  //     apid: fixtureData.apps.vnsRsvp,
  //     node: "test.voi",
  //     name: "test.voi",
  //     length: 4,
  //     extraPayment: BigInt(259800),
  //     sender: addresses.owner,
  //     sk: sks.owner,
  //   });
  //   expect(reserveR).to.be.eq(true);
  //   const accountNodeAfter = bytesToBase64(
  //     await accountNode({
  //       apid: fixtureData.apps.vnsRsvp,
  //       account: addresses.owner,
  //     })
  //   );
  //   console.log({
  //     account: addresses.owner,
  //     node: "test.voi",
  //     before: accountNodeBefore,
  //     after: accountNodeAfter,
  //   });
  // });
  // it("can get events", async function () {
  //   const eventsR = await rsvpEvents({
  //     apid: fixtureData.apps.vnsRsvp,
  //   });
  //   const reservationSet = eventsR.find((e) => e.name === "ReservationSet");
  //   expect(reservationSet).to.be.not.undefined;
  //   expect(reservationSet.events.length).to.be.gt(0);
  //   const reservationReleased = eventsR.find(
  //     (e) => e.name === "ReservationReleased"
  //   );
  //   expect(reservationReleased).to.be.not.undefined;
  //   expect(reservationSet.events.length).to.be.gt(0);
  // });
  // it("admin can release", async function () {
  //   const adminReleaseR = await adminRelease({
  //     apid: fixtureData.apps.vnsRsvp,
  //     owner: addresses.owner,
  //     node: "test.voi",
  //     sender: addresses.deployer,
  //     sk: sks.deployer,
  //     debug: true,
  //   });
  //   expect(adminReleaseR).to.be.eq(true);
  // });
  // it("admin can reserve", async function () {
  //   const adminReserveR = await adminReserve({
  //     apid: fixtureData.apps.vnsRsvp,
  //     owner: addresses.owner,
  //     node: "test4.voi",
  //     name: "test4.voi",
  //     length: 5,
  //     price: 0,
  //     sender: addresses.deployer,
  //     sk: sks.deployer,
  //     debug: true,
  //   });
  //   expect(adminReserveR).to.be.eq(true);
  // });
});
