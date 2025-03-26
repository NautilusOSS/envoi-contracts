import { Command } from "commander";
import axios from "axios";
import {
  VnsRegistryClient as VNSRegistryClient,
  APP_SPEC as VNSRegistrySpec,
} from "./clients/VNSRegistryClient.js";
import {
  VnsrsvpClient as VNSRSVPClient,
  APP_SPEC as VNSRSVPSpec,
} from "./clients/VNSRSVPClient.js";
import {
  VnsPublicResolverClient as VNSPublicResolverClient,
  APP_SPEC as VNSPublicResolverSpec,
} from "./clients/VNSPublicResolverClient.js";
import {
  Osarc200TokenClient as OSARC200TokenClient,
  APP_SPEC as OSARC200TokenSpec,
} from "./clients/OSARC200TokenClient.js";
import {
  Osarc200TokenFactoryClient as OSARC200TokenFactoryClient,
  APP_SPEC as OSARC200TokenFactorySpec,
} from "./clients/OSARC200TokenFactoryClient.js";
import {
  VnsRegistrarClient as VNSRegistrarClient,
  APP_SPEC as VNSRegistrarSpec,
} from "./clients/VNSRegistrarClient.js";
import {
  ReverseRegistrarClient as ReverseRegistrarClient,
  APP_SPEC as ReverseRegistrarSpec,
} from "./clients/ReverseRegistrarClient.js";
import {
  CollectionRegistrarClient as CollectionRegistrarClient,
  APP_SPEC as CollectionRegistrarSpec,
} from "./clients/CollectionRegistrarClient.js";
import {
  StakingRegistrarClient as StakingRegistrarClient,
  APP_SPEC as StakingRegistrarSpec,
} from "./clients/StakingRegistrarClient.js";
import algosdk, {
  AtomicTransactionComposer,
  makePaymentTxnWithSuggestedParamsFromObject,
  OnApplicationComplete,
  TransactionSigner,
  waitForConfirmation,
} from "algosdk";
import { CONTRACT, abi } from "ulujs";
import moment from "moment";
import * as dotenv from "dotenv";
import BigNumber from "bignumber.js";
import fs, { readFileSync } from "fs";
import { SendTransactionFrom } from "@algorandfoundation/algokit-utils/types/transaction.js";
import crypto from "crypto";
import pkg from "js-sha3";
import { resolve } from "path";
const { keccak256 } = pkg;
dotenv.config({ path: ".env" });

export const ALGORAND_ZERO_ADDRESS_STRING =
  "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ";

export const minBalance = 1000000;
const extraPages = 1;
export const extraPageCost = 100000 * (1 + extraPages);
export const recordBoxCost = 49300;

// function that takes string and returns a Uint8Array of size 256
export function stringToUint8Array(str: string, length: number): Uint8Array {
  const bytes = new Uint8Array(length);
  bytes.set(new Uint8Array(Buffer.from(str, "utf8")), 0);
  return bytes;
}

export function stripTrailingZeroBytes(str: string) {
  return str.replace(/\0+$/, ""); // Matches one or more '\0' at the end of the string and removes them
}

function padStringWithZeroBytes(input: string, length: number): string {
  const paddingLength = length - input.length;

  if (paddingLength > 0) {
    const zeroBytes = "\0".repeat(paddingLength);
    return input + zeroBytes;
  }

  return input; // Return the original string if it's already long enough
}

function uint8ArrayToBigInt(uint8Array: Uint8Array) {
  let result = BigInt(0); // Initialize the BigInt result
  for (let i = 0; i < uint8Array.length; i++) {
    result = (result << BigInt(8)) + BigInt(uint8Array[i]); // Shift 8 bits and add the current byte
  }
  return result;
}

function bigIntToUint8Array(bigInt: bigint) {
  const uint8Array = new Uint8Array(32);
  let tempBigInt = bigInt;
  // Find the highest non-zero byte
  for (let i = 31; i >= 0; i--) {
    uint8Array[i] = Number(tempBigInt & BigInt(0xff));
    tempBigInt >>= BigInt(8);
  }
  return uint8Array;
}

export function bytesToHex(bytes: Uint8Array): string {
  return bytes.reduce(
    (acc, byte) => acc + byte.toString(16).padStart(2, "0"),
    ""
  );
}

export function bytesToBase64(bytes: Uint8Array): string {
  return Buffer.from(bytes).toString("base64");
}

export function hash(
  label: string | Uint8Array,
  algorithm: string = "sha256"
): Uint8Array {
  const labelBytes =
    typeof label === "string" ? Buffer.from(label, "utf8") : label;
  return algorithm === "keccak256"
    ? new Uint8Array(keccak256.arrayBuffer(labelBytes))
    : new Uint8Array(crypto.createHash(algorithm).update(labelBytes).digest());
}

function isAlgorandAddress(address: string): boolean {
  // Check if the address length is correct
  if (address.length !== 58) {
    return false;
  }

  // Check if the address uses valid Base32 characters
  const base32Regex = /^[A-Z2-7]+$/;
  if (!base32Regex.test(address)) {
    return false;
  }

  return true;
}

export function namehash(
  name?: string,
  algorithm: string = "sha256"
): Uint8Array {
  if (!name) {
    return new Uint8Array(32); // Return 32 bytes of zeros for empty name
  }

  // Split the name into labels and reverse them
  const labels = name.split(".").reverse();

  // Start with empty hash (32 bytes of zeros)
  let node = new Uint8Array(32);

  // Hash each label
  for (const label of labels) {
    if (label) {
      // Skip empty labels
      // Hash the label
      const isNumber = !isNaN(Number(label));
      const labelHash = !isAlgorandAddress(label)
        ? !isNumber
          ? hash(label, algorithm)
          : hash(bigIntToUint8Array(BigInt(label)), algorithm)
        : hash(algosdk.decodeAddress(label).publicKey, algorithm);

      // Concatenate current node hash with label hash and hash again
      const combined = new Uint8Array([...node, ...labelHash]);
      node =
        algorithm === "keccak256"
          ? new Uint8Array(keccak256.arrayBuffer(combined))
          : new Uint8Array(
              crypto.createHash(algorithm).update(combined).digest()
            );
    }
  }

  return node;
}

export const program = new Command();

const { MN, MN2, MN3 } = process.env;

export const acc = algosdk.mnemonicToSecretKey(MN || "");
export const { addr, sk } = acc;

export const acc2 = algosdk.mnemonicToSecretKey(MN2 || "");
export const { addr: addr2, sk: sk2 } = acc2;

export const acc3 = algosdk.mnemonicToSecretKey(MN3 || "");
export const { addr: addr3, sk: sk3 } = acc3;

export const addresses = {
  deployer: addr,
  owner: addr2,
  registrar: addr3,
};

export const sks = {
  deployer: sk,
  owner: sk2,
  registrar: sk3,
};

// TESTNET
// const ALGO_SERVER = "https://testnet-api.voi.nodely.io";
// const ALGO_INDEXER_SERVER = "https://testnet-idx.voi.nodely.io";
// const ARC72_INDEXER_SERVER = "https://arc72-idx.nautilus.sh";

// MAINNET
const ALGO_SERVER = "https://mainnet-api.voi.nodely.dev";
const ALGO_INDEXER_SERVER = "https://mainnet-idx.voi.nodely.dev";
const ARC72_INDEXER_SERVER = "https://mainnet-idx.nautilus.sh";

const algodServerURL = process.env.ALGOD_SERVER || ALGO_SERVER;
export const algodClient = new algosdk.Algodv2(
  process.env.ALGOD_TOKEN || "",
  algodServerURL,
  process.env.ALGOD_PORT || ""
);

const indexerServerURL = process.env.INDEXER_SERVER || ALGO_INDEXER_SERVER;
const indexerClient = new algosdk.Indexer(
  process.env.INDEXER_TOKEN || "",
  indexerServerURL,
  process.env.INDEXER_PORT || ""
);

const arc72IndexerURL =
  process.env.ARC72_INDEXER_SERVER || ARC72_INDEXER_SERVER;

const makeSpec = (methods: any) => {
  return {
    name: "",
    desc: "",
    methods,
    events: [],
  };
};

const signSendAndConfirm = async (txns: string[], sk: any) => {
  const stxns = txns
    .map((t) => new Uint8Array(Buffer.from(t, "base64")))
    .map(algosdk.decodeUnsignedTransaction)
    .map((t: any) => algosdk.signTransaction(t, sk));
  await algodClient.sendRawTransaction(stxns.map((txn: any) => txn.blob)).do();
  return await Promise.all(
    stxns.map((res: any) =>
      algosdk.waitForConfirmation(algodClient, res.txID, 4)
    )
  );
};

type DeployType =
  | "vns-registry"
  // | "vns-rsvp"
  | "vns-resolver"
  | "vns-registrar"
  | "reverse-registrar"
  | "collection-registrar"
  | "staking-registrar"
  | "arc200";

interface DeployOptions {
  type: DeployType;
  name: string;
  debug?: boolean;
}

export const deploy: any = async (options: DeployOptions) => {
  if (options.debug) {
    console.log(options);
  }
  const deployer = {
    addr: addr,
    sk: sk,
  };
  let Client;
  switch (options.type) {
    case "vns-registry": {
      Client = VNSRegistryClient;
      break;
    }
    // case "vns-rsvp": {
    //   Client = VNSRSVPClient;
    //   break;
    // }
    case "vns-resolver": {
      Client = VNSPublicResolverClient;
      break;
    }
    case "vns-registrar": {
      Client = VNSRegistrarClient;
      break;
    }
    case "reverse-registrar": {
      Client = ReverseRegistrarClient;
      break;
    }
    case "arc200": {
      Client = OSARC200TokenClient;
      break;
    }
    case "collection-registrar": {
      Client = CollectionRegistrarClient;
      break;
    }
    case "staking-registrar": {
      Client = StakingRegistrarClient;
      break;
    }
    default: {
      console.log("Invalid type");
      return;
    }
  }
  const clientParams: any = {
    resolveBy: "creatorAndName",
    findExistingUsing: indexerClient,
    creatorAddress: deployer.addr,
    name: options.name || "",
    sender: deployer,
  };
  const appClient = Client ? new Client(clientParams, algodClient) : null;
  if (appClient) {
    const app = await appClient.deploy({
      deployTimeParams: {},
      onUpdate: "update",
      onSchemaBreak: "fail",
    });
    return app.appId;
  }
};
program
  .command("deploy")
  .requiredOption("-t, --type <string>", "Specify factory type")
  .requiredOption("-n, --name <string>", "Specify contract name")
  .option("--debug", "Debug the deployment", false)
  .description("Deploy a specific contract type")
  .action(async (options: DeployOptions) => {
    const apid = await deploy(options);
    if (!apid) {
      console.log("Failed to deploy contract");
      return;
    }
    console.log(apid);
  });

// begin arc200

const factory = new Command("factory").description(
  "Manage arc200 token factory"
);

interface FactoryCreateOptions {
  apid: number;

  debug?: boolean;
  simulate?: boolean;
}

export const factoryCreate: any = async (options: FactoryCreateOptions) => {
  if (options.debug) {
    console.log(options);
  }
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenFactorySpec.contract.methods),
    {
      addr,
      sk: new Uint8Array(0),
    }
  );
  ci.setPaymentAmount(1152300);
  ci.setFee(4000);
  const createR = await ci.create();
  if (options.debug) {
    console.log(createR);
  }
  if (createR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(createR.txns, sk);
    }
    return Number(createR.returnValue);
  }
  return 0;
};

factory
  .command("create")
  .description("Create a new arc200 token")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .option("--debug", "Debug the deployment", false)
  .option("-r, --simulate", "Simulate the deployment", false)
  .action(async (options: FactoryCreateOptions) => {
    const apid = await factoryCreate({
      ...options,
    });
    console.log("apid:", apid);
  });

const utilCmd = new Command("util").description("Utility commands");

interface UtilBigIntToUint8ArrayOptions {
  value: number;
}

export const utilBigIntToUint8Array: any = async (
  options: UtilBigIntToUint8ArrayOptions
) => {
  return bigIntToUint8Array(BigInt(options.value));
};

utilCmd
  .command("bigint-to-uint8array")
  .description("Convert a bigint to a uint8array")
  .requiredOption("-v, --value <number>", "The value to convert")
  .action(async (options: UtilBigIntToUint8ArrayOptions) => {
    const uint8array = await utilBigIntToUint8Array(options);
    console.log(Buffer.from(uint8array).toString("hex"));
  });

interface UtilNamehashOptions {
  name: string;
}

export const utilNamehash: any = async (options: UtilNamehashOptions) => {
  const namehashR = namehash(options.name);
  return namehashR
};

utilCmd
  .command("namehash")
  .description("Namehash a given name")
  .requiredOption("-n, --name <string>", "The name to namehash")
  .action(async (options: UtilNamehashOptions) => {
    const namehashR = await utilNamehash(options);
    console.log(namehashR);
  });

const arc200Cmd = new Command("arc200").description("Manage arc200 token");

interface ARC200PostUpdateOptions {
  apid: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: any;
}

export const arc200PostUpdate: any = async (
  options: ARC200PostUpdateOptions
) => {
  const sender = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: sender,
      sk: secretKey,
    }
  );
  const postUpdateR = await ci.post_update();
  if (options.debug) {
    console.log(postUpdateR);
  }
  if (postUpdateR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(postUpdateR.txns, secretKey);
    }
    return true;
  }
  return false;
};

arc200Cmd
  .command("post-update")
  .description("Post update to the arc200 token")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .option("--debug", "Debug the deployment", false)
  .option("-r, --simulate", "Simulate the deployment", false)
  .action(async (options: ARC200PostUpdateOptions) => {
    await arc200PostUpdate(options);
  });

interface ARC200DecimalsOptions {
  apid: number;
}

export const arc200Decimals: any = async (options: ARC200DecimalsOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const decimalsR = (await ci.arc200_decimals()).returnValue;
  return decimalsR.toString();
};

interface ARC200SymbolOptions {
  apid: number;
}

export const arc200Symbol: any = async (options: ARC200SymbolOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const symbolR = stripTrailingZeroBytes(
    new TextDecoder().decode(
      Buffer.from((await ci.arc200_symbol()).returnValue)
    )
  );
  return symbolR;
};

interface ARC200NameOptions {
  apid: number;
}

export const arc200Name: any = async (options: ARC200NameOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const nameR = stripTrailingZeroBytes(
    new TextDecoder().decode(Buffer.from((await ci.arc200_name()).returnValue))
  );
  return nameR;
};

interface ARC200TotalSupplyOptions {
  apid: number;
}

export const arc200TotalSupply: any = async (
  options: ARC200TotalSupplyOptions
) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const totalSupplyR = await ci.arc200_totalSupply();
  return totalSupplyR.returnValue.toString();
};

interface ARC200GlobalStateOptions {
  apid: number;
  lazy?: boolean;
}
export const arc200GetState: any = async (
  options: ARC200GlobalStateOptions
) => {
  const globalState = await new OSARC200TokenClient(
    { resolveBy: "id", id: Number(options.apid) },
    algodClient
  ).getGlobalState();
  if (options.lazy) {
    return { globalState };
  }
  const state = {
    contractVersion: globalState.contractVersion?.asNumber(),
    deploymentVersion: globalState.deploymentVersion?.asNumber(),
    owner: algosdk.encodeAddress(
      globalState.owner?.asByteArray() || new Uint8Array()
    ),
    updatable: globalState.updatable?.asNumber(),
    upgrader: algosdk.encodeAddress(
      globalState.upgrader?.asByteArray() || new Uint8Array()
    ),
    name: stripTrailingZeroBytes(globalState.name?.asString() || ""),
    symbol: stripTrailingZeroBytes(globalState.symbol?.asString() || ""),
    totalSupply: uint8ArrayToBigInt(
      globalState.totalSupply?.asByteArray() || new Uint8Array()
    ).toString(),
    decimals: globalState.decimals?.asNumber(),
  };
  return state;
};
arc200Cmd
  .command("get")
  .description("Get the state of the arc200 token")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .action(async (options: ARC200GlobalStateOptions) => {
    const globalState = await arc200GetState(options);
    console.log({ globalState });
    return globalState;
  });

//             _       _
//   _ __ ___ (_)_ __ | |_
//  | '_ ` _ \| | '_ \| __|
//  | | | | | | | | | | |_
//  |_| |_| |_|_|_| |_|\__|
//

interface ARC200DeleteApprovalOptions {
  apid: number;
  owner: string;
  spender: string;
  debug?: boolean;
  simulate?: boolean;
}

export const arc200DeleteApproval: any = async (
  options: ARC200DeleteApprovalOptions
) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: options.owner,
      sk: new Uint8Array(0),
    }
  );
  const deleteApprovalR = await ci.deleteApproval(
    options.owner,
    options.spender
  );
  if (options.debug) {
    console.log(deleteApprovalR);
  }
  if (deleteApprovalR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(deleteApprovalR.txns, sk);
    }
    return true;
  }
  return false;
};

interface ARC200DeleteBalanceOptions {
  apid: number;
  owner: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: any;
}
export const arc200DeleteBalance: any = async (
  options: ARC200DeleteBalanceOptions
) => {
  if (options.debug) {
    console.log(options);
  }
  const sender = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: sender,
      sk: secretKey,
    }
  );
  const deleteBalanceR = await ci.deleteBalance(options.owner);
  if (options.debug) {
    console.log(deleteBalanceR);
  }
  if (deleteBalanceR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(deleteBalanceR.txns, secretKey);
    }
    return true;
  }
  return false;
};

interface ARC200MintOptions {
  apid: number;
  recipient: string;
  name: string;
  symbol: string;
  totalSupply: number;
  decimals: number;
  sender?: string;
  sk?: any;
  simulate?: boolean;
  debug?: boolean;
}
export const arc200Mint: any = async (options: ARC200MintOptions) => {
  if (options.debug) {
    console.log(options);
    const globalState = await new OSARC200TokenClient(
      { resolveBy: "id", id: Number(options.apid) },
      algodClient
    ).getGlobalState();

    console.log("globalState", globalState);
  }
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: options.sender || addr,
      sk: options.sk || sk,
    }
  );
  ci.setFee(2000);
  ci.setPaymentAmount(1e6);
  const name = new Uint8Array(
    Buffer.from(padStringWithZeroBytes(options.name, 32), "utf8")
  );
  const symbol = new Uint8Array(
    Buffer.from(padStringWithZeroBytes(options.symbol, 8), "utf8")
  );
  const mintR = await ci.mint(
    options.recipient,
    name,
    symbol,
    options.decimals,
    options.totalSupply
  );
  if (options.debug) {
    console.log(mintR);
  }
  if (mintR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(mintR.txns, options.sk || sk);
    }
    return true;
  }
  return false;
};
arc200Cmd
  .command("mint")
  .description("Get the state of the arc200 token")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .requiredOption("-r, --recipient <string>", "Specify the recipient address")
  .requiredOption("-n, --name <string>", "Specify the name")
  .requiredOption("-s, --symbol <string>", "Specify the symbol")
  .requiredOption("-t, --total-supply <number>", "Specify the total supply")
  .requiredOption("-d, --decimals <number>", "Specify the decimals")
  .option("-v, --simulate", "Simulate the mint", false)
  .option("--debug", "Debug the deployment", false)
  .action(async (options) => {
    const success = await arc200Mint({
      ...options,
      //recipient: algosdk.decodeAddress(options.recipient).publicKey,
      name: new Uint8Array(
        Buffer.from(padStringWithZeroBytes(options.name, 32), "utf8")
      ),
      symbol: new Uint8Array(
        Buffer.from(padStringWithZeroBytes(options.symbol, 8), "utf8")
      ),
      decimals: Number(options.decimals),
      totalSupply: BigInt(
        new BigNumber(options.totalSupply)
          .multipliedBy(10 ** options.decimals)
          .toFixed(0)
      ),
    });
    console.log("Mint success:", success);
  });

//  _           _
// | |__   __ _| | __ _ _ __   ___ ___
// | '_ \ / _` | |/ _` | '_ \ / __/ _ \
// | |_) | (_| | | (_| | | | | (_|  __/
// |_.__/ \__,_|_|\__,_|_| |_|\___\___|
//

interface ARC200BalanceOfOptions {
  apid: number;
  owner: string;
}

export const arc200BalanceOf: any = async (options: ARC200BalanceOfOptions) => {
  const owner = options.owner || addr;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: owner,
      sk: new Uint8Array(0),
    }
  );
  const balanceR = (await ci.arc200_balanceOf(owner)).returnValue;
  return balanceR.toString();
};

arc200Cmd
  .command("balance")
  .description("Get the balance of the arc200 token")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .option("-o, --owner <string>", "Specify the owner address")
  .action(async (options) => {
    const balance = await arc200BalanceOf(options);
    console.log(balance);
  });

//        _ _
//   __ _| | | _____      ____ _ _ __   ___ ___
//  / _` | | |/ _ \ \ /\ / / _` | '_ \ / __/ _ \
// | (_| | | | (_) \ V  V / (_| | | | | (_|  __/
//  \__,_|_|_|\___/ \_/\_/ \__,_|_| |_|\___\___|
//

interface ARC200AllowanceOptions {
  apid: number;
  owner: string;
  spender: string;
}

export const arc200Allowance: any = async (options: ARC200AllowanceOptions) => {
  const owner = options.owner || addr;
  const spender = options.spender || addr;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: owner,
      sk: new Uint8Array(0),
    }
  );
  const allowanceR = await ci.arc200_allowance(owner, spender);
  return allowanceR.returnValue.toString();
};

arc200Cmd
  .command("allowance")
  .description("Get the allowance of the arc200 token")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .option("-o, --owner <string>", "Specify the owner address")
  .option("-s, --spender <string>", "Specify the spender address")
  .action(async (options) => {
    const allowance = (await arc200Allowance(options)).returnValue.toString();
    console.log(allowance);
  });

//
//   __ _ _ __  _ __  _ __ _____   _____
//  / _` | '_ \| '_ \| '__/ _ \ \ / / _ \
// | (_| | |_) | |_) | | | (_) \ V /  __/
//  \__,_| .__/| .__/|_|  \___/ \_/ \___|
//       |_|   |_|
//

interface ARC200ApproveOptions {
  apid: number;
  spender: string;
  amount: number;
  simulate?: boolean;
  debug?: boolean;
  sender?: string;
  sk?: any;
  extraPayment?: number;
}

export const arc200Approve: any = async (options: ARC200ApproveOptions) => {
  if (options.debug) {
    console.log(options);
  }
  const sender = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: sender,
      sk: secretKey,
    }
  );
  ci.setPaymentAmount(28500 + (options.extraPayment || 0));
  const approveR = await ci.arc200_approve(options.spender, options.amount);
  if (options.debug) {
    console.log(approveR);
  }
  if (approveR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(approveR.txns, secretKey);
    }
    return true;
  }
  return false;
};

arc200Cmd
  .command("approve")
  .description("Approve the arc200 token")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .requiredOption("-s, --spender <string>", "Specify the spender address")
  .requiredOption("-m, --amount <number>", "Specify the amount")
  .option("-t, --simulate", "Simulate the approval", false)
  .option("--debug", "Debug the deployment", false)
  .action(async (options) => {
    const success = await arc200Approve({
      ...options,
      amount: BigInt(options.amount),
    });
    console.log("Approve success:", success);
  });

//  _                        __
// | |_ _ __ __ _ _ __  ___ / _| ___ _ __
// | __| '__/ _` | '_ \/ __| |_ / _ \ '__|
// | |_| | | (_| | | | \__ \  _|  __/ |
//  \__|_|  \__,_|_| |_|___/_|  \___|_|
//

interface ARC200TransferOptions {
  apid: number;
  receiver: string;
  amount: number;
  simulate?: boolean;
  debug?: boolean;
  sender?: string;
  sk?: any;
}

export const arc200Transfer: any = async (options: ARC200TransferOptions) => {
  if (options.debug) {
    console.log(options);
  }
  const sender = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: sender,
      sk: secretKey,
    }
  );
  ci.setPaymentAmount(28500);
  const transferR = await ci.arc200_transfer(options.receiver, options.amount);
  if (options.debug) {
    console.log(transferR);
  }
  if (transferR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(transferR.txns, secretKey);
    }
    return true;
  }
  return false;
};

arc200Cmd
  .command("transfer")
  .description("Transfer the arc200 token")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .requiredOption("-r, --receiver <string>", "Specify the receiver address")
  .requiredOption("-m, --amount <number>", "Specify the amount")
  .option("-s, --simulate", "Simulate the transfer", false)
  .option("--debug", "Debug the deployment", false)
  .action(async (options) => {
    const success = await arc200Transfer({
      ...options,
      amount: BigInt(options.amount),
    });
    console.log("Transfer success:", success);
  });

interface ARC200TransferFromOptions {
  apid: number;
  spender: string;
  owner: string;
  receiver: string;
  amount: number;
  simulate?: boolean;
  debug?: boolean;
  sender?: string;
  sk?: any;
}

export const arc200TransferFrom: any = async (
  options: ARC200TransferFromOptions
) => {
  if (options.debug) {
    console.log(options);
  }
  const sender = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: sender,
      sk: secretKey,
    }
  );
  const transferFromR = await ci.arc200_transferFrom(
    options.owner,
    options.receiver,
    options.amount
  );
  if (options.debug) {
    console.log(transferFromR);
  }
  if (transferFromR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(transferFromR.txns, secretKey);
    }
    return true;
  }
  return false;
};

//                   _       _
//   _   _ _ __   __| | __ _| |_ ___
//  | | | | '_ \ / _` |/ _` | __/ _ \
//  | |_| | |_) | (_| | (_| | ||  __/
//   \__,_| .__/ \__,_|\__,_|\__\___|
//        |_|
//

interface ARC200UpdateOptions {
  apid: number;
  simulate?: boolean;
  debug?: boolean;
}

arc200Cmd
  .command("update")
  .description("Update the arc200 token")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .option("-s, --simulate", "Simulate the update", false)
  .option("--debug", "Debug the deployment", false)
  .action(async (options: ARC200UpdateOptions) => {
    if (options.debug) {
      console.log("options", options);
    }
    const apid = Number(options.apid);
    const res = await new OSARC200TokenClient(
      {
        resolveBy: "id",
        id: apid,
        sender: {
          addr,
          sk,
        },
      },
      algodClient
    ).appClient.update();
    if (options.debug) {
      console.log(res);
    }
  });

//  _    _ _ _
// | | _(_) | |
// | |/ / | | |
// |   <| | | |
// |_|\_\_|_|_|
//

interface ARC200KillOptions {
  apid: number;
  simulate?: boolean;
  debug?: boolean;
}

export const arc200Kill: any = async (options: ARC200KillOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(OSARC200TokenSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  ci.setFee(3000);
  ci.setOnComplete(5); // deleteApplicationOC
  const killR = await ci.kill();
  if (options.debug) {
    console.log(killR);
  }
  if (killR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(killR.txns, sk);
    }
    return true;
  }
  return false;
};

arc200Cmd
  .command("kill")
  .description("Kill the arc200 token")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .option("-s, --simulate", "Simulate the kill", false)
  .option("--debug", "Debug the deployment", false)
  .action(async (options) => {
    const success = await arc200Kill(options);
    console.log("Kill success:", success);
  });

// end arc200

// vns
//   deploy
//     node main.js deploy --type "vns-registry" --name registry3 --debug
//   owner can upgrade (test manually because it requires a new version of the contract)
//     upgrade app
//       node main.js deploy --type "vns-registry" --name registry3 --debug
//   non-owner can't upgrade (test manually because it requires a new version of the contract)
//     upgrade app with other account
//       node main.js deploy --type "vns-registry" --name registry3 --debug
//   upgrader can post update
//     call post update
//       node main.js vns post-update --apid 7676 --debug --extra-payment 124500
//   anyone can not post update
//     call post update with other account
//       node main.js vns post-update --apid 7676 --debug --extra-payment 124500
//   ___
//   get root node owner
//   get root node resolver
//   get root node ttl
//   ___
//   test views
//   creator can create subnode from root node
//   owner can participate
//   owner can set delegate
//   owner can revoke delegate
//   owner can withdraw
//   creator is owner of root node
//   root node owner is creator
//   root node resolver is 0
//   root node ttl is default ttl
//   root owner can set record
//   root owner can set owner
//   root owner can set subnode owner
//   root owner can set resolver
//   root owner can set ttl
//   upgrader can kill

const vnsCmd = new Command("vns").description("Manage vns registry");

interface VNSKillApplicationOptions {
  apid: number;
  debug?: boolean;
  delete?: boolean;
  simulate?: boolean;
}
export const killApplication: any = async (
  options: VNSKillApplicationOptions
) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  ci.setPaymentAmount(101000);
  ci.setFee(3000);
  if (options.delete) {
    ci.setOnComplete(OnApplicationComplete.DeleteApplicationOC);
  }
  const killR = await ci.killApplication();
  if (options.debug) {
    console.log(killR);
  }
  if (killR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(killR.txns, sk);
    }
    return true;
  }
  return false;
};

vnsCmd
  .command("kill")
  .description("Kill the vns registry")
  .option("--debug", "Debug the deployment", false)
  .option("-d, --delete", "Delete the application", false)
  .option("-s, --simulate", "Simulate the kill", false)
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .action(async (options: VNSKillApplicationOptions) => {
    const ci = new CONTRACT(
      Number(options.apid),
      algodClient,
      indexerClient,
      makeSpec(VNSRegistrySpec.contract.methods),
      {
        addr: addr,
        sk: sk,
      }
    );
    ci.setPaymentAmount(101000);
    ci.setFee(3000);
    if (options.delete) {
      ci.setOnComplete(OnApplicationComplete.DeleteApplicationOC);
    }
    const killR = await ci.killApplication();
    if (options.debug) {
      console.log(killR);
    }
    if (killR.success) {
      if (!options.simulate) {
        await signSendAndConfirm(killR.txns, sk);
      }
    }
  });

interface VNSKillNodeOptions {
  apid: number;
  node: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}
export const killNode: any = async (options: VNSKillNodeOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: options.sender || addr,
      sk: options.sk || sk,
    }
  );
  const killNodeR = await ci.killNode(namehash(options.node));
  if (options.debug) {
    console.log(killNodeR);
  }
  if (killNodeR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(killNodeR.txns, sk);
    }
    return true;
  }
  return false;
};
vnsCmd
  .command("kill-node")
  .description("Kill a node from the vns registry")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .option("-n, --node <string>", "Specify the node")
  .option("--debug", "Debug the deployment", false)
  .action(killNode);

interface VNSKillOperatorOptions {
  apid: number;
  operator: string;
  owner: string;
  debug?: boolean;
  simulate?: boolean;
}
export const killOperator: any = async (options: VNSKillOperatorOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const killOperatorR = await ci.killOperator(options.operator, options.owner);
  if (options.debug) {
    console.log(killOperatorR);
  }
  if (killOperatorR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(killOperatorR.txns, sk);
    }
    return true;
  }
  return false;
};

interface VNSDeleteBoxOptions {
  apid: number;
  key: string;
  debug?: boolean;
  simulate?: boolean;
}
export const deleteBox: any = async (options: VNSDeleteBoxOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const deleteBoxR = await ci.deleteBox(
    new Uint8Array(Buffer.from(options.key, "base64"))
  );
  if (options.debug) {
    console.log(deleteBoxR);
  }
  if (deleteBoxR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(deleteBoxR.txns, sk);
    }
    return true;
  }
  return false;
};
vnsCmd
  .command("delete-box")
  .description("Delete a box from the vns registry")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .requiredOption("-k, --key <string>", "Specify the key")
  .option("--debug", "Debug the deployment", false)
  .action(deleteBox);

interface VNSPostUpdateOptions {
  apid: number;
  rapid?: number;
  debug?: boolean;
  simulate?: boolean;
  extraPayment?: number;
}
export const postUpdate: any = async (options: VNSPostUpdateOptions) => {
  if (options.debug) {
    console.log(options);
  }
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    !options.rapid
      ? makeSpec(VNSRegistrySpec.contract.methods)
      : makeSpec(VNSPublicResolverSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  if (options.extraPayment) {
    const amountBI = BigInt(options.extraPayment);
    ci.setPaymentAmount(Number(amountBI));
  }
  const postUpdateR = await (!options.rapid
    ? ci.post_update()
    : ci.post_update(options.rapid));
  if (options.debug) {
    console.log(postUpdateR);
  }
  if (postUpdateR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(postUpdateR.txns, sk);
    }
    return true;
  }
  return false;
};
vnsCmd
  .command("post-update")
  .description("Post update the arc72 token")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .option("-s, --simulate", "Simulate the post update", false)
  .option("--debug", "Debug the deployment", false)
  .option("-e, --extra-payment <number>", "Specify the extra payment", false)
  .action(postUpdate);

interface VNSSetRegistryResolverOptions {
  apid: number;
  resolver: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}
export const setRegistryResolver: any = async (
  options: VNSSetRegistryResolverOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const setRegistryResolverR = await ci.setRegistryResolver(options.resolver);
  if (options.debug) {
    if (setRegistryResolverR.success) {
      await signSendAndConfirm(setRegistryResolverR.txns, secretKey);
    }
    return true;
  }
  return false;
};

vnsCmd
  .command("set-registry-resolver")
  .description("Set the registry resolver of the vns registry")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .requiredOption("-r, --resolver <number>", "Specify the resolver")
  .option("--debug", "Debug the deployment", false)
  .action(setRegistryResolver);

interface VNSOwnerOfOptions {
  apid: number;
  node?: string;
  nodeBytes?: Uint8Array;
  debug?: boolean;
}
export const ownerOf: any = async (options: VNSOwnerOfOptions) => {
  if (options.debug) {
    console.log(options);
  }
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const node = namehash(options?.node || "");
  const ownerOfR = await ci.ownerOf(node);
  if (options.debug) {
    console.log(ownerOfR);
  }
  return ownerOfR.returnValue;
};
vnsCmd
  .command("owner-of")
  .description("Get the owner of the arc72 token")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .option("-t, --node <string>", "Specify the node")
  .option("-d, --debug", "Debug the deployment", false)
  .action(async (options: VNSOwnerOfOptions) => {
    const res = await ownerOf(options);
    console.log(res);
  });

interface VNSResolverOptions {
  apid: number;
  node?: string;
  debug?: boolean;
}
export const resolver: any = async (options: VNSResolverOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const resolverR = await ci.resolver(namehash(options?.node || ""));
  if (options.debug) {
    console.log(resolverR);
  }
  return resolverR.returnValue;
};
vnsCmd
  .command("resolver")
  .description("Get the resolver of the vns registry")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .option("-t, --node <string>", "Specify the node")
  .option("-d, --debug", "Debug the deployment", false)
  .action(resolver);

interface VNSTTLOptions {
  apid: number;
  node?: string;
  debug?: boolean;
}
export const ttl: any = async (options: VNSTTLOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const ttlR = await ci.ttl(namehash(options?.node || ""));
  if (options.debug) {
    console.log(ttlR);
  }
  return ttlR.returnValue;
};
vnsCmd
  .command("ttl")
  .description("Get the ttl of the vns registry")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .option("-t, --node <string>", "Specify the node")
  .option("-d, --debug", "Debug the deployment", false)
  .action(ttl);

interface VNSSetResolverOptions {
  apid: number;
  node: string;
  resolver: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}
export const setResolver: any = async (options: VNSSetResolverOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const setResolverR = await ci.setResolver(
    namehash(options.node),
    options.resolver
  );
  if (options.debug) {
    console.log(setResolverR);
  }
  if (setResolverR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(setResolverR.txns, secretKey);
    }
    return true;
  }
  return false;
};
vnsCmd
  .command("set-resolver")
  .description("Set the resolver of the vns registry")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .action(setResolver);

interface VNSSetTTLOptions {
  apid: number;
  node: string;
  ttl: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}
export const setTTL: any = async (options: VNSSetTTLOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const setTTLR = await ci.setTTL(namehash(options.node), options.ttl);
  if (options.debug) {
    console.log(setTTLR);
  }
  if (setTTLR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(setTTLR.txns, secretKey);
    }
    return true;
  }
  return false;
};
vnsCmd
  .command("set-ttl")
  .description("Set the ttl of the vns registry")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .requiredOption("-t, --ttl <number>", "Specify the ttl")
  .option("-s, --simulate", "Simulate the set ttl", false)
  .option("-d, --debug", "Debug the deployment", false)
  .action(setTTL);

interface VNSSetRecordOptions {
  apid: number;
  node: string;
  owner: string;
  resolver: number;
  ttl: number;
  debug?: boolean;
  simulate?: boolean;
}
export const setRecord: any = async (options: VNSSetRecordOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const setRecordR = await ci.setRecord(
    namehash(options.node),
    options.owner,
    options.resolver,
    options.ttl
  );
  if (options.debug) {
    console.log(setRecordR);
  }
  if (setRecordR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(setRecordR.txns, sk);
    }
    return true;
  }
  return false;
};
vnsCmd
  .command("set-record")
  .description("Set the record of the vns registry")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .requiredOption("-n, --node <string>", "Specify the node")
  .requiredOption("-o, --owner <string>", "Specify the owner")
  .requiredOption("-r, --resolver <number>", "Specify the resolver")
  .requiredOption("-t, --ttl <number>", "Specify the ttl")
  .option("-s, --simulate", "Simulate the set record", false)
  .option("-d, --debug", "Debug the deployment", false)
  .action(setRecord);

interface VNSSetSubnodeOwnerOptions {
  apid: number;
  sender?: string;
  sk?: Uint8Array;
  node?: string;
  label: string;
  owner: string;
  debug?: boolean;
  simulate?: boolean;
  extraPayment?: number;
}
export const setSubnodeOwner: any = async (
  options: VNSSetSubnodeOwnerOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  if (options.extraPayment) {
    const amountBI = BigInt(options.extraPayment);
    ci.setPaymentAmount(Number(amountBI));
  }
  const setSubnodeOwnerR = await ci.setSubnodeOwner(
    namehash(options.node),
    hash(options.label),
    options.owner
  );
  if (options.debug) {
    console.log(setSubnodeOwnerR);
  }
  if (setSubnodeOwnerR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(setSubnodeOwnerR.txns, secretKey);
    }
    return setSubnodeOwnerR.returnValue;
  }
  return new Uint8Array(32);
};
vnsCmd
  .command("set-subnode-owner")
  .description("Set the subnode owner of the vns registry")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .requiredOption("-l, --label <string>", "Specify the label")
  .requiredOption("-o, --owner <string>", "Specify the owner")
  .option("-n, --node <string>", "Specify the node")
  .option("-s, --simulate", "Simulate the set subnode owner", false)
  .option("-d, --debug", "Debug the deployment", false)
  .action(setSubnodeOwner);

interface VNSSetOwnerOptions {
  apid: number;
  node: string;
  owner: string;
  sender?: string;
  sk?: Uint8Array;
  debug?: boolean;
  simulate?: boolean;
}
export const setOwner: any = async (options: VNSSetOwnerOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const setOwnerR = await ci.setOwner(namehash(options.node), options.owner);
  if (options.debug) {
    console.log(setOwnerR);
  }
  if (setOwnerR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(setOwnerR.txns, secretKey);
    }
    return true;
  }
  return false;
};
vnsCmd
  .command("set-owner")
  .description("Set the owner of the vns registry")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .action(setOwner);

interface VNSSetApprovalForAllOptions {
  apid: number;
  operator: string;
  approved: boolean;
  sender?: string;
  sk?: Uint8Array;
  debug?: boolean;
  simulate?: boolean;
}
export const setApprovalForAll: any = async (
  options: VNSSetApprovalForAllOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const setApprovalForAllR = await ci.setApprovalForAll(
    options.operator,
    options.approved
  );
  if (options.debug) {
    console.log(setApprovalForAllR);
  }
  if (setApprovalForAllR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(setApprovalForAllR.txns, secretKey);
    }
    return true;
  }
  return false;
};
vnsCmd
  .command("set-approval-for-all")
  .description("Set the approval for all of the arc72 token")
  .action(setApprovalForAll);

interface VNSIsApprovedForAllOptions {
  apid: number;
  operator: string;
  owner: string;
  debug?: boolean;
}
export const isApprovedForAll: any = async (
  options: VNSIsApprovedForAllOptions
) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrySpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const isApprovedForAllR = await ci.isApprovedForAll(
    options.owner,
    options.operator
  );
  if (options.debug) {
    console.log(isApprovedForAllR);
  }
  return isApprovedForAllR.returnValue;
};
vnsCmd
  .command("is-approved-for-all")
  .description("Check if the operator is approved for all of the vns registry")
  .action(isApprovedForAll);

const rsvp = new Command("rsvp").description("Manage rsvp");

rsvp
  .command("kill-application")
  .description("Kill the rsvp application")
  .option("-a, --apid <number>", "Specify the application ID")
  .option("-d, --debug", "Debug the deployment", false)
  .option("-x, --delete", "Delete the application", false)
  .option("-s, --simulate", "Simulate the deployment", false)
  .action(killApplication);

interface VNSRSVPPriceOptions {
  apid: number;
  length: number;
  debug?: boolean;
  extraPayment?: number;
}
export const price: any = async (options: VNSRSVPPriceOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRSVPSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );

  const priceR = await ci.price(options.length);
  if (options.debug) {
    console.log(priceR);
  }
  return priceR.returnValue;
};

rsvp
  .command("price")
  .description("Get the price of the rsvp application")
  .action(price);

interface VNSRSVPReserveOptions {
  apid: number;
  node: string;
  name: string;
  debug?: boolean;
  simulate?: boolean;
  extraPayment?: number;
  sender?: string;
  sk?: Uint8Array;
}
export const reserve: any = async (options: VNSRSVPReserveOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRSVPSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  if (options.extraPayment) {
    const amountBI = BigInt(options.extraPayment);
    ci.setPaymentAmount(Number(amountBI));
  }
  const reserveR = await ci.reserve(
    namehash(options.node),
    stringToUint8Array(options.name, 256),
    options.name.length
  );
  if (options.debug) {
    console.log(reserveR);
  }
  if (reserveR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(reserveR.txns, secretKey);
    }
    return true;
  }
  return false;
};

interface VNSRSVPAccountNodeOptions {
  apid: number;
  account: string;
  debug?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const accountNode: any = async (options: VNSRSVPAccountNodeOptions) => {
  if (options.debug) {
    console.log({ options });
  }
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRSVPSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const accountNodeR = await ci.account_node(options.account);
  if (options.debug) {
    console.log(accountNodeR);
  }
  return accountNodeR.returnValue;
};
rsvp
  .command("account-node")
  .description("Get the account node of the rsvp application")
  .action(accountNode);

interface VNSRSVPReservationPriceOptions {
  apid: number;
  node: string;
  debug?: boolean;
}
export const reservationPrice: any = async (
  options: VNSRSVPReservationPriceOptions
) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRSVPSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const reservationPriceR = await ci.reservation_price(namehash(options.node));
  if (options.debug) {
    console.log(reservationPriceR);
  }
  return reservationPriceR.returnValue;
};
rsvp
  .command("reservation-price")
  .description("Get the reservation price of the rsvp application")
  .action(reservationPrice);

interface VNSRSVPReleaseOptions {
  apid: number;
  node: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}
export const release: any = async (options: VNSRSVPReleaseOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRSVPSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  ci.setFee(2000);
  const releaseR = await ci.release(namehash(options.node));
  if (options.debug) {
    console.log(releaseR);
  }
  if (releaseR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(releaseR.txns, secretKey);
    }
    return true;
  }
  return false;
};
rsvp
  .command("release")
  .description("Release the reservation of the rsvp application")
  .action(release);

interface VNSRSVPKillReservationOptions {
  apid: number;
  node: string;
  debug?: boolean;
  simulate?: boolean;
}
export const killReservation: any = async (
  options: VNSRSVPKillReservationOptions
) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRSVPSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const killReservationR = await ci.killReservation(namehash(options.node));
  if (options.debug) {
    console.log(killReservationR);
  }
  if (killReservationR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(killReservationR.txns, sk);
    }
    return true;
  }
  return false;
};
rsvp
  .command("kill-reservation")
  .description("Kill the reservation of the rsvp application")
  .action(killReservation);

interface VNSRSVPKillAccountOptions {
  apid: number;
  account: string;
  debug?: boolean;
  simulate?: boolean;
}
export const killAccount: any = async (options: VNSRSVPKillAccountOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRSVPSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const killAccountR = await ci.killAccount(options.account);
  if (options.debug) {
    console.log(killAccountR);
  }
  if (killAccountR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(killAccountR.txns, sk);
    }
    return true;
  }
  return false;
};
rsvp
  .command("kill-account")
  .description("Kill the account of the rsvp application")
  .action(killAccount);

interface VNSRSVPEvents {
  apid: number;
  debug?: boolean;
}

export const rsvpEvents: any = async (options: VNSRSVPEvents) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    {
      name: "rsvp",
      description: "rsvp",
      methods: VNSRSVPSpec.contract.methods,
      events: [
        {
          name: "ReservationSet",
          args: [
            {
              name: "node",
              type: "byte[32]",
            },
            {
              name: "owner",
              type: "address",
            },
            {
              name: "name",
              type: "byte[256]",
            },
            {
              name: "length",
              type: "uint64",
            },
            {
              name: "price",
              type: "uint64",
            },
          ],
        },
        {
          name: "ReservationReleased",
          args: [
            {
              name: "node",
              type: "byte[32]",
            },
          ],
        },
      ],
    },
    {
      addr: addr,
      sk: sk,
    }
  );
  const rsvpEventsR = await ci.getEvents({});
  if (options.debug) {
    console.log(rsvpEventsR);
  }
  return rsvpEventsR;
};
rsvp
  .command("events")
  .description("Get the events of the rsvp application")
  .action(rsvpEvents);

interface VNSRSVPAdminReleaseOptions {
  apid: number;
  owner: string;
  node: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const adminRelease: any = async (
  options: VNSRSVPAdminReleaseOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRSVPSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  ci.setFee(2000);
  const adminReleaseR = await ci.admin_release(
    options.owner,
    namehash(options.node)
  );
  if (options.debug) {
    console.log(adminReleaseR);
  }
  if (adminReleaseR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(adminReleaseR.txns, secretKey);
    }
    return true;
  }
  return false;
};
rsvp
  .command("admin-release")
  .description("Admin release the reservation of the rsvp application")
  .action(adminRelease);

interface VNSRSVPAdminReserveOptions {
  apid: number;
  owner: string;
  node: string;
  name: string;
  length: number;
  price: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}
export const adminReserve: any = async (
  options: VNSRSVPAdminReserveOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRSVPSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const adminReserveR = await ci.admin_reserve(
    options.owner,
    namehash(options.node),
    stringToUint8Array(options.name, 256),
    options.length,
    options.price
  );
  if (options.debug) {
    console.log(adminReserveR);
  }
  if (adminReserveR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(adminReserveR.txns, secretKey);
    }
    return true;
  }
  return false;
};
rsvp
  .command("admin-reserve")
  .description("Admin reserve the reservation of the rsvp application")
  .action(adminReserve);

interface VNSRSVPAdminReserveBatchOptions {
  apid: number;
  input: string; // path to csv file
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const adminReserveBatch: any = async (
  options: VNSRSVPAdminReserveBatchOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  if (options.debug) {
    console.log({ options });
  }
  const input = readFileSync(options.input, "utf8");
  const lines = input.split("\n");
  for (const line of lines) {
    const [nfd, addr] = line.split(",");
    const length = nfd.split(".")[0].length;
    const cleanAddr = addr.match(/^0x[a-fA-F0-9]{40}$/)?.[0] || addr;
    const price = 0;
    const payload = {
      apid: options.apid,
      owner: addr,
      node: nfd,
      name: nfd,
      length,
      price,
    };
    console.log(payload);
    const ci = new CONTRACT(
      Number(options.apid),
      algodClient,
      indexerClient,
      makeSpec(VNSRSVPSpec.contract.methods),
      {
        addr: address,
        sk: secretKey,
      }
    );
    const adminReserveR = await ci.admin_reserve(
      cleanAddr,
      namehash(nfd),
      stringToUint8Array(nfd, 256),
      length,
      price
    );
    if (options.debug) {
      console.log(adminReserveR);
    }
    if (!adminReserveR.success) {
      console.log(`Failed to reserve ${nfd}`);
      continue;
    }
    if (!options.simulate) {
      await signSendAndConfirm(adminReserveR.txns, secretKey);
    }
  }
};
rsvp
  .command("admin-reserve-batch")
  .description("Admin reserve batch the reservation of the rsvp application")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .requiredOption("-i, --input <path>", "Specify the input file")
  .option("-d, --debug", "Debug the deployment", false)
  .option("-s, --simulate", "Simulate the deployment", false)
  .action(adminReserveBatch);

rsvp
  .command("delete-box")
  .description("Delete a box from the vns registry")
  .requiredOption("-a, --apid <number>", "Specify the application ID")
  .requiredOption("-k, --key <string>", "Specify the key")
  .option("--debug", "Debug the deployment", false)
  .option("-s, --simulate", "Simulate the deployment", false)
  .action(deleteBox);

const resolverCmd = new Command("resolver").description("Manage resolver");

interface VNSResolverSetTextOptions {
  apid: number;
  node: string;
  key: string;
  value: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const setText: any = async (options: VNSResolverSetTextOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSPublicResolverSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  ci.setFee(2000);
  const setTextR = await ci.setText(
    namehash(options.node),
    stringToUint8Array(options.key, 22),
    stringToUint8Array(options.value, 256)
  );
  if (options.debug) {
    console.log(setTextR);
  }
  if (setTextR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(setTextR.txns, secretKey);
    }
    return true;
  }
  return false;
};

resolverCmd
  .command("set-text")
  .description("Set the text of the resolver")
  .requiredOption("-a, --apid <number>", "The resolver ID")
  .requiredOption("-n, --node <string>", "The node to set the text of")
  .requiredOption("-k, --key <string>", "The key to set the text of")
  .requiredOption("-v, --value <string>", "The value to set the text of")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: VNSResolverSetTextOptions) => {
    const res = await setText(options);
    console.log(res);
  });

interface VNSResolverGetTextOptions {
  apid: number;
  node: string;
  key: string;
  debug?: boolean;
}

export const getText: any = async (options: VNSResolverGetTextOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSPublicResolverSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const getTextR = await ci.text(
    namehash(options.node),
    stringToUint8Array(options.key, 22)
  );
  if (options.debug) {
    console.log(getTextR);
  }
  return stripTrailingZeroBytes(
    Buffer.from(getTextR.returnValue).toString("utf8")
  );
};

resolverCmd
  .command("get-text")
  .description("Get the text of the resolver")
  .requiredOption("-a, --apid <number>", "The resolver ID")
  .requiredOption("-n, --node <string>", "The node to get the text of")
  .requiredOption("-k, --key <string>", "The key to get the text of")
  .option("-d, --debug", "Debug mode")
  .action(async (options: VNSResolverGetTextOptions) => {
    const res = await getText(options);
    console.log(res);
  });

interface VNSResolverUpdateOptions {
  apid: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const resolverUpdate: any = async (
  options: VNSResolverUpdateOptions
) => {
  const apid = Number(options.apid);
  const res = await new VNSPublicResolverClient(
    {
      resolveBy: "id",
      id: apid,
      sender: {
        addr,
        sk,
      },
    },
    algodClient
  ).appClient.update();
  if (options.debug) {
    console.log(res);
  }
};

resolverCmd
  .command("update")
  .description("Update the resolver")
  .requiredOption("-a, --apid <number>", "The resolver ID")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: VNSResolverUpdateOptions) => {
    const res = await resolverUpdate(options);
    console.log(res);
  });

interface VNSResolverSetNameOptions {
  apid: number;
  node: string;
  name: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const setName: any = async (options: VNSResolverSetNameOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSPublicResolverSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  ci.setFee(2000);
  const setNameR = await ci.setName(
    namehash(options.node),
    stringToUint8Array(options.name, 256)
  );
  if (options.debug) {
    console.log(setNameR);
  }
  if (setNameR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(setNameR.txns, secretKey);
    }
    return true;
  }
  return false;
};

resolverCmd
  .command("set-name")
  .description("Set the name of the resolver")
  .requiredOption("-a, --apid <number>", "The resolver ID")
  .requiredOption("-n, --node <string>", "The node to set the name of")
  .requiredOption("-d, --name <string>", "The name to set")
  .option("-e, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: VNSResolverSetNameOptions) => {
    const res = await setName(options);
    console.log(res);
  });

interface VNSResolverDeleteNameOptions {
  apid: number;
  node: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const deleteName: any = async (
  options: VNSResolverDeleteNameOptions
) => {
  if (options.debug) {
    console.log({ options });
  }
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSPublicResolverSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  ci.setFee(2000);
  const deleteNameR = await ci.deleteName(namehash(options.node));
  if (options.debug) {
    console.log(deleteNameR);
  }
  if (deleteNameR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(deleteNameR.txns, secretKey);
    }
    return true;
  }
  return false;
};

interface VNSResolverGetNameOptions {
  apid: number;
  node: string;
  debug?: boolean;
}

export const getName: any = async (options: VNSResolverGetNameOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSPublicResolverSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const node = namehash(options.node);
  const getNameR = await ci.name(namehash(options.node));
  if (options.debug) {
    console.log("node", Buffer.from(node).toString("hex"));
    console.log(getNameR);
  }
  if (getNameR.success) {
    return getNameR.returnValue;
  }
  return "";
};

resolverCmd
  .command("get-name")
  .description("Get the name of the resolver")
  .requiredOption("-a, --apid <number>", "The resolver ID")
  .requiredOption("-n, --node <string>", "The node to get the name of")
  .option("-d, --debug", "Debug mode")
  .action(async (options: VNSResolverGetNameOptions) => {
    const res = await getName(options);
    console.log(stripTrailingZeroBytes(Buffer.from(res).toString("utf8")));
  });

interface VNSResolverSetAddrOptions {
  apid: number;
  node: string;
  addr: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const setAddr: any = async (options: VNSResolverSetAddrOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSPublicResolverSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  ci.setFee(2000);
  const setAddrR = await ci.setAddr(namehash(options.node), options.addr);
  if (options.debug) {
    console.log(setAddrR);
  }
  if (setAddrR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(setAddrR.txns, secretKey);
    }
    return true;
  }
  return false;
};

interface VNSResolverKillAddrOptions {
  apid: number;
  node: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const killAddr: any = async (options: VNSResolverKillAddrOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSPublicResolverSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const killAddrR = await ci.deleteAddr(namehash(options.node));
  if (options.debug) {
    console.log(killAddrR);
  }
  if (killAddrR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(killAddrR.txns, secretKey);
    }
    return true;
  }
  return false;
};

interface VNSResolverNameOptions {
  apid: number;
  node: string;
  debug?: boolean;
}

export const resolveName: any = async (options: VNSResolverNameOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSPublicResolverSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const resolveNameR = await ci.name(namehash(options.node));
  if (options.debug) {
    console.log(resolveNameR);
  }
  if (resolveNameR.success) {
    return resolveNameR.returnValue;
  }
  return "";
};

interface VNSResolverAddrOptions {
  apid: number;
  node: string;
  debug?: boolean;
}

export const resolveAddr: any = async (options: VNSResolverAddrOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSPublicResolverSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const resolveAddrR = await ci.addr(namehash(options.node));
  if (options.debug) {
    console.log(resolveAddrR);
  }
  return resolveAddrR.returnValue;
};

const registrarCmd = new Command("registrar").description("Manage registrar");

interface registrarSetNameOptions {
  apid: number;
  name: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const registrarSetName: any = async (
  options: registrarSetNameOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  ci.setFee(4000);
  const registrarSetNameR = await ci.setName(
    stringToUint8Array(options.name, 256)
  );
  if (options.debug) {
    console.log(registrarSetNameR);
  }
  if (registrarSetNameR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(registrarSetNameR.txns, secretKey);
    }
    return true;
  }
  return false;
};

registrarCmd
  .command("set-name")
  .description("Set the name of the registrar")
  .requiredOption("-a, --apid <number>", "The registrar ID")
  .requiredOption("-n, --name <string>", "The name to set")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: registrarSetNameOptions) => {
    const res = await registrarSetName(options);
    console.log(res);
  });

interface setCostMultiplierOptions {
  apid: number;
  costMultiplier: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const setCostMultiplier: any = async (
  options: setCostMultiplierOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const costMultiplier = Number(options.costMultiplier);
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const setCostMultiplierR = await ci.set_cost_multiplier(costMultiplier);
  if (options.debug) {
    console.log(setCostMultiplierR);
  }
  if (setCostMultiplierR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(setCostMultiplierR.txns, secretKey);
    }
    return true;
  }
  return false;
};

registrarCmd
  .command("set-cost-multiplier")
  .description("Set the cost multiplier of the registrar")
  .requiredOption("-a, --apid <number>", "The registrar ID")
  .requiredOption("-c, --cost-multiplier <number>", "The cost multiplier")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: setCostMultiplierOptions) => {
    const res = await setCostMultiplier(options);
    console.log(res);
  });

interface setBaseCostOptions {
  apid: number;
  baseCost: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const setBaseCost: any = async (options: setBaseCostOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const baseCost = Number(options.baseCost) * 1e6;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const setBaseCostR = await ci.set_base_cost(baseCost);
  if (options.debug) {
    console.log(setBaseCostR);
  }
  if (setBaseCostR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(setBaseCostR.txns, secretKey);
    }
    return true;
  }
  return false;
};

registrarCmd
  .command("set-base-cost")
  .description("Set the base cost of the registrar")
  .requiredOption("-a, --apid <number>", "The registrar ID")
  .requiredOption("-b, --base-cost <number>", "The base cost")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: setBaseCostOptions) => {
    const res = await setBaseCost(options);
    console.log(res);
  });

interface VNSRegistrarGetLengthOptions {
  apid: number;
  name: string;
  debug?: boolean;
}

export const vnsRegistrarGetLength: any = async (
  options: VNSRegistrarGetLengthOptions
) => {
  if (options.debug) {
    console.log({ options });
  }
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const vnsRegistrarGetLengthR = await ci.get_length(
    stringToUint8Array(options.name, 32)
  );
  if (options.debug) {
    console.log(vnsRegistrarGetLengthR);
  }
  return vnsRegistrarGetLengthR.returnValue;
};

registrarCmd
  .command("get-length")
  .description("Get the length of the registrar")
  .requiredOption("-a, --apid <number>", "The registrar ID")
  .requiredOption("-n, --name <string>", "The name to get the length of")
  .option("-d, --debug", "Debug mode")
  .action(async (options: VNSRegistrarGetLengthOptions) => {
    const res = await vnsRegistrarGetLength(options);
    console.log(res);
  });

interface VNSRegistrarSetRootNodeOptions {
  apid: number;
  rootNode: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const vnsRegistrarSetRootNode: any = async (
  options: VNSRegistrarSetRootNodeOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const vnsRegistrarSetRootNodeR = await ci.set_root_node(
    namehash(options.rootNode)
  );
  if (options.debug) {
    console.log(vnsRegistrarSetRootNodeR);
  }
  if (vnsRegistrarSetRootNodeR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(vnsRegistrarSetRootNodeR.txns, secretKey);
    }
    return true;
  }
  return false;
};

registrarCmd
  .command("set-root-node")
  .description("Set the root node of the registrar")
  .requiredOption("-a, --apid <number>", "The registrar ID")
  .requiredOption("-n, --root-node <string>", "The root node to set")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: VNSRegistrarSetRootNodeOptions) => {
    const res = await vnsRegistrarSetRootNode(options);
    console.log(res);
  });

interface VNSRegistrarSetPaymentTokenOptions {
  apid: number;
  paymentToken: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const vnsRegistrarSetPaymentToken: any = async (
  options: VNSRegistrarSetPaymentTokenOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const vnsRegistrarSetPaymentTokenR = await ci.set_payment_token(
    Number(options.paymentToken)
  );
  if (options.debug) {
    console.log(vnsRegistrarSetPaymentTokenR);
  }
  if (vnsRegistrarSetPaymentTokenR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(vnsRegistrarSetPaymentTokenR.txns, secretKey);
    }
    return true;
  }
  return false;
};

registrarCmd
  .command("set-payment-token")
  .description("Set the payment token of the registrar")
  .requiredOption("-a, --apid <number>", "The registrar ID")
  .requiredOption("-p, --payment-token <number>", "The payment token ID")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: VNSRegistrarSetPaymentTokenOptions) => {
    const res = await vnsRegistrarSetPaymentToken(options);
    console.log(res);
  });

interface VNSRegistrarUpdateOptions {
  apid: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const vnsRegistrarUpdate: any = async (
  options: VNSRegistrarUpdateOptions
) => {
  const apid = Number(options.apid);
  const res = await new VNSRegistrarClient(
    {
      resolveBy: "id",
      id: apid,
      sender: {
        addr,
        sk,
      },
    },
    algodClient
  ).appClient.update();
  if (options.debug) {
    console.log(res);
  }
};

registrarCmd
  .command("update")
  .description("Update the registrar")
  .requiredOption("-a, --apid <number>", "The registrar ID")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: VNSRegistrarUpdateOptions) => {
    const res = await vnsRegistrarUpdate(options);
    console.log(res);
  });

interface VNSRegistrarPostUpdateOptions {
  apid: number;
  registry: number;
  rootNode: string;
  paymentToken: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const vnsRegistrarPostUpdate: any = async (
  options: VNSRegistrarPostUpdateOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const vnsRegistrarPostUpdateR = await ci.post_update(
    Number(options.registry),
    namehash(options.rootNode),
    Number(options.paymentToken)
  );
  if (options.debug) {
    console.log(vnsRegistrarPostUpdateR);
  }
  if (vnsRegistrarPostUpdateR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(vnsRegistrarPostUpdateR.txns, secretKey);
    }
    return true;
  }
  return false;
};

registrarCmd
  .command("post-update")
  .description("Post update the registrar")
  .requiredOption("-a, --apid <number>", "The registrar ID")
  .requiredOption("-r, --registry <number>", "The registry ID")
  .requiredOption("-n, --root-node <string>", "The root node to set")
  .requiredOption("-p, --payment-token <number>", "The payment token ID")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: VNSRegistrarPostUpdateOptions) => {
    const res = await vnsRegistrarPostUpdate(options);
    console.log(res);
  });

interface VNSRegistrarIsExpiredOptions {
  apid: number;
  name: string;
  debug?: boolean;
}

export const isExpired: any = async (options: VNSRegistrarIsExpiredOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const isExpiredR = await ci.is_expired(
    uint8ArrayToBigInt(namehash(options.name))
  );

  if (options.debug) {
    console.log("isExpiredR", isExpiredR);
  }
  return isExpiredR.returnValue;
};

interface VNSRegistrarRegisterOptions {
  apid: number;
  name: string;
  owner: string;
  duration: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const register: any = async (options: VNSRegistrarRegisterOptions) => {
  if (options.debug) {
    console.log({ options });
  }
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    abi.custom,
    {
      addr: address,
      sk: secretKey,
    }
  );
  const builder = {
    arc200: new CONTRACT(
      780596,
      algodClient,
      indexerClient,
      abi.nt200,
      {
        addr: address,
        sk: secretKey,
      },
      true,
      false,
      true
    ),
    registrar: new CONTRACT(
      Number(options.apid),
      algodClient,
      indexerClient,
      makeSpec(VNSRegistrarSpec.contract.methods),
      {
        addr: address,
        sk: secretKey,
      },
      true,
      false,
      true
    ),
    resolver: new CONTRACT(
      797608,
      algodClient,
      indexerClient,
      makeSpec(VNSPublicResolverSpec.contract.methods),
      {
        addr: address,
        sk: secretKey,
      },
      true,
      false,
      true
    ),
  };
  const buildN = [];
  {
    const txnO = (
      await builder.arc200.arc200_approve(
        algosdk.getApplicationAddress(797609),
        1000e6
      )
    )?.obj;
    buildN.push({
      ...txnO,
      payment: 28500,
    });
  }
  {
    const txnO = (
      await builder.registrar.register(
        stringToUint8Array(options.name, 32),
        options.owner,
        Number(options.duration) * 365 * 24 * 60 * 60 // Convert years to seconds
      )
    )?.obj;
    buildN.push({
      ...txnO,
      payment: 336700,
    });
  }
  {
    const txnO = (
      await builder.resolver.setName(
        namehash(`${options.name}.voi`),
        stringToUint8Array(`${options.name}.voi`, 256)
      )
    )?.obj;
    buildN.push({
      ...txnO,
    });
  }
  ci.setFee(15000);
  ci.setBeaconId(Number(options.apid));
  ci.setEnableGroupResourceSharing(true);
  ci.setExtraTxns(buildN);
  const customR = await ci.custom();
  if (options.debug) {
    console.log(customR);
  }
  if (customR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(customR.txns, secretKey);
    }
    return true;
  }
  return false;
};

registrarCmd
  .command("register")
  .description("Register a name")
  .requiredOption("-a, --apid <number>", "The registrar ID")
  .requiredOption("-n, --name <string>", "The name to register")
  .requiredOption("-o, --owner <string>", "The owner of the name")
  .requiredOption("-d, --duration <number>", "The duration of the registration")
  .option("-e, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: VNSRegistrarRegisterOptions) => {
    const res = await register(options);
    console.log(res);
  });

interface VNSRegistrarDeleteNFTDataOptions {
  apid: number;
  name: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const deleteNFTData: any = async (
  options: VNSRegistrarDeleteNFTDataOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const deleteNFTDataR = await ci.deleteNFTData(
    uint8ArrayToBigInt(namehash(options.name))
  );
  if (options.debug) {
    console.log("deleteNFTDataR", deleteNFTDataR);
  }
  if (deleteNFTDataR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(deleteNFTDataR.txns, secretKey);
    }
    return true;
  }
  return false;
};

interface VNSRegistrarDeleteNFTIndexOptions {
  apid: number;
  index: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const deleteNFTIndex: any = async (
  options: VNSRegistrarDeleteNFTIndexOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const deleteNFTIndexR = await ci.deleteNFTIndex(options.index);
  if (options.debug) {
    console.log("deleteNFTIndexR", deleteNFTIndexR);
  }
  if (deleteNFTIndexR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(deleteNFTIndexR.txns, secretKey);
    }
    return true;
  }
  return false;
};

interface VNSRegistrarDeleteHolderDataOptions {
  apid: number;
  address: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const deleteHolderData: any = async (
  options: VNSRegistrarDeleteHolderDataOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const deleteHolderDataR = await ci.deleteHolderData(options.address);
  if (options.debug) {
    console.log("deleteHolderDataR", deleteHolderDataR);
  }
  if (deleteHolderDataR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(deleteHolderDataR.txns, secretKey);
    }
    return true;
  }
  return false;
};

interface VNSRegistrarDeleteExpiresOptions {
  apid: number;
  name: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const deleteExpires: any = async (
  options: VNSRegistrarDeleteExpiresOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const deleteExpiresR = await ci.deleteExpires(
    uint8ArrayToBigInt(namehash(options.name))
  );
  if (options.debug) {
    console.log("deleteExpiresR", deleteExpiresR);
  }
  if (deleteExpiresR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(deleteExpiresR.txns, secretKey);
    }
    return true;
  }
  return false;
};

interface VNSRegistrarGetPriceOptions {
  apid: number;
  name: string;
  duration: number;
}

export const getPrice: any = async (options: VNSRegistrarGetPriceOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const getPriceR = await ci.get_price(
    stringToUint8Array(options.name, 32),
    options.duration
  );
  return getPriceR.returnValue;
};

interface VNSGetLengthOptions {
  apid: number;
  name: string;
  debug?: boolean;
}

export const getLength: any = async (options: VNSGetLengthOptions) => {
  if (options.debug) {
    console.log({ options });
  }
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const getLengthR = await ci.get_length(stringToUint8Array(options.name, 32));
  if (options.debug) {
    console.log("getLengthR", getLengthR);
  }
  return getLengthR.returnValue;
};

interface VNSCheckNameOptions {
  apid: number;
  name: string;
  length: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const checkName: any = async (options: VNSCheckNameOptions) => {
  try {
    if (options.debug) {
      console.log({ options });
    }
    const address = options.sender || addr;
    const secretKey = options.sk || sk;
    const ci = new CONTRACT(
      Number(options.apid),
      algodClient,
      indexerClient,
      makeSpec(VNSRegistrarSpec.contract.methods),
      {
        addr: address,
        sk: secretKey,
      }
    );
    ci.setFee(15000);
    const checkNameR = await ci.check_name(
      stringToUint8Array(options.name, 32)
    );
    if (options.debug) {
      console.log("checkNameR", checkNameR);
    }
    return checkNameR.returnValue;
  } catch (e) {
    return false;
  }
};

interface VNSRenewOptions {
  apid: number;
  name: string;
  duration: number;
  sender?: string;
  sk?: Uint8Array;
  debug?: boolean;
  simulate?: boolean;
}

export const renew: any = async (options: VNSRenewOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  ci.setFee(2000);
  ci.setPaymentAmount(100000);
  const renewR = await ci.renew(options.name, options.duration);
  if (options.debug) {
    console.log("renewR", renewR);
  }
  if (renewR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(renewR.txns, secretKey);
    }
    return true;
  }
  return false;
};

interface VNSExpirationOptions {
  apid: number;
  name: string;
  debug?: boolean;
}

export const expiration: any = async (options: VNSExpirationOptions) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const expirationR = await ci.expiration(
    uint8ArrayToBigInt(namehash(options.name))
  );
  return expirationR.returnValue;
};

interface VNSReclaimOptions {
  apid: number;
  name: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const reclaim: any = async (options: VNSReclaimOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  ci.setFee(2000);
  const reclaimR = await ci.reclaim(stringToUint8Array(options.name, 32));
  if (options.debug) {
    console.log("reclaimR", reclaimR);
  }
  if (reclaimR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(reclaimR.txns, secretKey);
    }
    return true;
  }
  return false;
};

const stakingCmd = new Command("staking").description(
  "Manage staking registrar"
);

interface StakingRegistrarRegisterOptions {
  apid: number;
  stakingId: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const stakingRegister: any = async (
  options: StakingRegistrarRegisterOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    abi.custom,
    {
      addr: address,
      sk: secretKey,
    }
  );
  const builder = {
    stakingRegistrar: new CONTRACT(
      Number(options.apid),
      algodClient,
      indexerClient,
      makeSpec(StakingRegistrarSpec.contract.methods),
      {
        addr: address,
        sk: secretKey,
      },
      true,
      false,
      true
    ),
  };
  const buildN = [];
  {
    const txnO = (
      await builder.stakingRegistrar.register(
        bigIntToUint8Array(BigInt(options.stakingId)),
        address,
        0
      )
    ).obj;
    buildN.push({ ...txnO, apps: [Number(options.stakingId)] });
  }
  ci.setFee(2000);
  ci.setPaymentAmount(284000);
  ci.setExtraTxns(buildN);
  ci.setEnableGroupResourceSharing(true);
  const customR = await ci.custom();
  if (options.debug) {
    console.log("customR", customR);
  }
  if (customR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(customR.txns, secretKey);
    }
    return true;
  }
  return false;
};

stakingCmd
  .command("register")
  .requiredOption("-a, --apid <number>", "The ARC72 contract ID")
  .requiredOption("-t, --staking-id <number>", "The staking ID")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: StakingRegistrarRegisterOptions) => {
    console.log({ options });
    const res = await stakingRegister(options);
    console.log(res);
  });

interface StakingRegistrarUpdateOptions {
  apid: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const stakingUpdate: any = async (
  options: StakingRegistrarUpdateOptions
) => {
  if (options.debug) {
    console.log("options", options);
  }
  const apid = Number(options.apid);
  const res = await new StakingRegistrarClient(
    {
      resolveBy: "id",
      id: apid,
      sender: {
        addr,
        sk,
      },
    },
    algodClient
  ).appClient.update();
  if (options.debug) {
    console.log(res);
  }
};

stakingCmd
  .command("update")
  .requiredOption("-a, --apid <number>", "The ARC72 contract ID")
  .option("-d, --debug", "Debug mode")
  .action(async (options: StakingRegistrarUpdateOptions) => {
    console.log({ options });
    const res = await stakingUpdate(options);
    console.log(res);
  });

const collectionCmd = new Command("collection").description(
  "Manage collection registrar"
);

interface CollectionRegistrarCheckNameOptions {
  apid: number;
  collectionId: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

interface CollectionRegistrarUpdateOptions {
  apid: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const collectionUpdate: any = async (
  options: CollectionRegistrarUpdateOptions
) => {
  if (options.debug) {
    console.log("options", options);
  }
  const apid = Number(options.apid);
  const res = await new CollectionRegistrarClient(
    {
      resolveBy: "id",
      id: apid,
      sender: {
        addr,
        sk,
      },
    },
    algodClient
  ).appClient.update();
  if (options.debug) {
    console.log(res);
  }
};

collectionCmd
  .command("update")
  .requiredOption("-a, --apid <number>", "The ARC72 contract ID")
  .option("-d, --debug", "Debug mode")
  .action(async (options: CollectionRegistrarUpdateOptions) => {
    console.log({ options });
    const res = await collectionUpdate(options);
    console.log(res);
  });

interface CollectionRegistrarRegisterOptions {
  apid: number;
  collectionId: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const collectionRegister: any = async (
  options: CollectionRegistrarRegisterOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    abi.custom,
    {
      addr: address,
      sk: secretKey,
    }
  );
  const builder = {
    collectionRegistrar: new CONTRACT(
      Number(options.apid),
      algodClient,
      indexerClient,
      makeSpec(CollectionRegistrarSpec.contract.methods),
      {
        addr: address,
        sk: secretKey,
      },
      true,
      false,
      true
    ),
  };
  const buildN = [];
  {
    const txnO = (
      await builder.collectionRegistrar.register(
        bigIntToUint8Array(BigInt(options.collectionId)),
        address,
        0
      )
    ).obj;
    buildN.push({
      ...txnO,
      apps: [Number(options.collectionId)],
    });
  }
  ci.setFee(2000);
  ci.setEnableGroupResourceSharing(true);
  ci.setExtraTxns(buildN);
  const customR = await ci.custom();
  if (options.debug) {
    console.log("customR", customR);
  }
  if (customR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(customR.txns, secretKey);
    }
    return true;
  }
  return false;
};

collectionCmd
  .command("register")
  .requiredOption("-a, --apid <number>", "The ARC72 contract ID")
  .requiredOption("-c, --collection-id <number>", "The collection ID")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: CollectionRegistrarRegisterOptions) => {
    console.log({ options });
    const res = await collectionRegister(options);
    console.log(res);
  });

const reverseCmd = new Command("reverse").description(
  "Manage reverse registrar"
);

interface ReverseSetRootNodeOptions {
  apid: number;
  rootNode: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const reverseSetRootNode: any = async (
  options: ReverseSetRootNodeOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(ReverseRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const reverseSetRootNodeR = await ci.set_root_node(
    namehash(options.rootNode)
  );
  if (options.debug) {
    console.log("reverseSetRootNodeR", reverseSetRootNodeR);
  }
  if (reverseSetRootNodeR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(reverseSetRootNodeR.txns, secretKey);
    }
    return true;
  }
  return false;
};

reverseCmd
  .command("set-root-node")
  .requiredOption("-a, --apid <number>", "The ARC72 contract ID")
  .requiredOption("-r, --root-node <string>", "The root node to set")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: ReverseSetRootNodeOptions) => {
    console.log({ options });
    const res = await reverseSetRootNode(options);
    console.log(res);
  });

interface ReverseSetRegistryOptions {
  apid: number;
  registry: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const reverseSetRegistry: any = async (
  options: ReverseSetRegistryOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(ReverseRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const reverseSetRegistryR = await ci.set_registry(Number(options.registry));
  if (options.debug) {
    console.log("reverseSetRegistryR", reverseSetRegistryR);
  }
  if (reverseSetRegistryR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(reverseSetRegistryR.txns, secretKey);
    }
    return true;
  }
  return false;
};

reverseCmd
  .command("set-registry")
  .requiredOption("-a, --apid <number>", "The ARC72 contract ID")
  .requiredOption("-r, --registry <number>", "The registry to set")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: ReverseSetRegistryOptions) => {
    console.log({ options });
    const res = await reverseSetRegistry(options);
    console.log(res);
  });

interface ReverseSetPaymentTokenOptions {
  apid: number;
  token: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const reverseSetPaymentToken: any = async (
  options: ReverseSetPaymentTokenOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(ReverseRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const reverseSetPaymentTokenR = await ci.set_payment_token(
    Number(options.token)
  );
  if (options.debug) {
    console.log("reverseSetPaymentTokenR", reverseSetPaymentTokenR);
  }
  if (reverseSetPaymentTokenR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(reverseSetPaymentTokenR.txns, secretKey);
    }
    return true;
  }
  return false;
};

reverseCmd
  .command("set-payment-token")
  .requiredOption("-a, --apid <number>", "The ARC72 contract ID")
  .requiredOption("-t, --token <number>", "The token to set")
  .option("-d, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: ReverseSetPaymentTokenOptions) => {
    console.log({ options });
    const res = await reverseSetPaymentToken(options);
    console.log(res);
  });

interface ReverseRegisterUpdateOptions {
  apid: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const reverseRegisterUpdate: any = async (
  options: ReverseRegisterUpdateOptions
) => {
  if (options.debug) {
    console.log("options", options);
  }
  const apid = Number(options.apid);
  const res = await new ReverseRegistrarClient(
    {
      resolveBy: "id",
      id: apid,
      sender: {
        addr,
        sk,
      },
    },
    algodClient
  ).appClient.update();
  if (options.debug) {
    console.log(res);
  }
};

reverseCmd
  .command("update")
  .requiredOption("-a, --apid <number>", "The ARC72 contract ID")
  .option("-d, --debug", "Debug mode")
  .action(async (options: ReverseRegisterUpdateOptions) => {
    console.log({ options });
    const res = await reverseRegisterUpdate(options);
    console.log(res);
  });

interface ReverseRegisterOptions {
  apid: number;
  papid: number;
  owner: string;
  duration: number;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const reverseRegister: any = async (options: ReverseRegisterOptions) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    abi.custom,
    {
      addr: address,
      sk: secretKey,
    }
  );
  const builder = {
    arc200: new CONTRACT(
      Number(options.papid),
      algodClient,
      indexerClient,
      makeSpec(OSARC200TokenSpec.contract.methods),
      {
        addr: address,
        sk: secretKey,
      },
      true,
      false,
      true
    ),
    reverseRegistrar: new CONTRACT(
      Number(options.apid),
      algodClient,
      indexerClient,
      makeSpec(ReverseRegistrarSpec.contract.methods),
      {
        addr: address,
        sk: secretKey,
      },
      true,
      false,
      true
    ),
  };
  const buildN = [];
  {
    const txnO = (
      await builder.arc200.arc200_approve(
        algosdk.getApplicationAddress(Number(options.apid)),
        1e6
      )
    ).obj;
    buildN.push({
      ...txnO,
      payment: 28500,
    });
  }
  {
    const txnO = (
      await builder.reverseRegistrar.register(
        algosdk.decodeAddress(options.owner).publicKey,
        options.owner,
        Number(options.duration)
      )
    ).obj;
    buildN.push({
      ...txnO,
      payment: 336700,
    });
  }
  ci.setBeaconId(Number(options.apid));
  ci.setFee(3000);
  ci.setEnableGroupResourceSharing(true);
  ci.setExtraTxns(buildN);
  const customR = await ci.custom();
  if (options.debug) {
    console.log("customR", customR);
  }
  if (customR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(customR.txns, secretKey);
    }
    return true;
  }
  return false;
};

reverseCmd
  .command("register")
  .requiredOption("-a, --apid <number>", "The ARC72 contract ID")
  .requiredOption("-p, --papid <number>", "The ARC200 contract ID")
  .requiredOption("-o, --owner <string>", "The owner to register")
  .requiredOption("-d, --duration <number>", "The duration to register")
  .option("-e, --debug", "Debug mode")
  .option("-s, --simulate", "Simulate the transaction")
  .action(async (options: ReverseRegisterOptions) => {
    console.log({ options });
    const res = await reverseRegister(options);
    console.log(res);
  });

interface ReverseCheckNameOptions {
  apid: number;
  name: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const reverseCheckName: any = async (
  options: ReverseCheckNameOptions
) => {
  if (options.debug) {
    console.log({ options });
  }
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(ReverseRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const reverseCheckNameR = await ci.check_name(options.name);
  if (options.debug) {
    console.log("reverseCheckNameR", reverseCheckNameR);
  }
  if (reverseCheckNameR.success) {
    return reverseCheckNameR.returnValue;
  }
  return false;
};

reverseCmd
  .command("check-name")
  .requiredOption("-a, --apid <number>", "The ARC72 contract ID")
  .requiredOption("-n, --name <string>", "The name to check")
  .option("-d, --debug", "Debug mode")
  .action(async (options: ReverseCheckNameOptions) => {
    console.log({ options });
    const res = await reverseCheckName({
      ...options,
      apid: Number(options.apid),
      name: algosdk.decodeAddress(options.name).publicKey,
    });
    console.log(res);
  });

interface ReverseGetLengthOptions {
  apid: number;
  debug?: boolean;
}

export const reverseGetLength: any = async (
  options: ReverseGetLengthOptions
) => {
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(ReverseRegistrarSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const getLengthReverseR = await ci.get_length();
  return getLengthReverseR.returnValue;
};

interface ReverseRegistrarRegisterOptions {
  apid: number;
  name: string;
  debug?: boolean;
  simulate?: boolean;
  sender?: string;
  sk?: Uint8Array;
}

export const registerReverse: any = async (
  options: ReverseRegistrarRegisterOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(ReverseRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const registerReverseR = await ci.register(
    stringToUint8Array(options.name, 58)
  );
  if (options.debug) {
    console.log("registerReverseR", registerReverseR);
  }
  if (registerReverseR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(registerReverseR.txns, secretKey);
    }
    return true;
  }
  return false;
};

interface RegistrarWithdrawOptions {
  apid: number;
  sender: string;
  sk: Uint8Array;
  debug?: boolean;
  simulate?: boolean;
}

export const registrarWithdraw: any = async (
  options: RegistrarWithdrawOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  //ci.setPaymentAmount(2e6);
  ci.setFee(4000);
  const withdrawR = await ci.withdraw();
  if (options.debug) {
    console.log("withdrawR", withdrawR);
  }
  if (withdrawR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(withdrawR.txns, secretKey);
    }
    return true;
  }
  return false;
};

const arc72Cmd = new Command("arc72").description("Manage ARC72");

interface ARC72OwnerOfOptions {
  apid: number;
  name: string;
  debug?: boolean;
}

export const arc72OwnerOf: any = async (options: ARC72OwnerOfOptions) => {
  if (options.debug) {
    console.log({ options });
  }
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: addr,
      sk: sk,
    }
  );
  const nodeId = namehash(options.name);
  const tokenId = uint8ArrayToBigInt(nodeId);
  const mtid = BigInt("0x" + Buffer.from(nodeId).toString("hex"));
  console.log("tokenId", tokenId);
  console.log("mtid", mtid);
  const arc72OwnerOfR = await ci.arc72_ownerOf(mtid);
  if (options.debug) {
    console.log("arc72OwnerOfR", arc72OwnerOfR);
  }
  return arc72OwnerOfR.returnValue;
};

arc72Cmd
  .command("owner-of")
  .requiredOption("-a, --apid <number>", "The ARC72 contract ID")
  .requiredOption("-n, --name <string>", "The name to get the owner of")
  .option("-d, --debug", "Debug mode")
  .action(async (options: ARC72OwnerOfOptions) => {
    console.log({ options });
    const res = await arc72OwnerOf(options);
    console.log(res);
  });

interface ARC72TransferFromOptions {
  apid: number;
  name: string;
  from: string;
  to: string;
  sender: string;
  sk: Uint8Array;
  debug?: boolean;
  simulate?: boolean;
}

export const arc72TransferFrom: any = async (
  options: ARC72TransferFromOptions
) => {
  const address = options.sender || addr;
  const secretKey = options.sk || sk;
  const ci = new CONTRACT(
    Number(options.apid),
    algodClient,
    indexerClient,
    makeSpec(VNSRegistrarSpec.contract.methods),
    {
      addr: address,
      sk: secretKey,
    }
  );
  const arc72TransferFromR = await ci.arc72_transferFrom(
    options.from,
    options.to,
    uint8ArrayToBigInt(namehash(options.name))
  );
  if (options.debug) {
    console.log("arc72TransferFromR", arc72TransferFromR);
  }
  if (arc72TransferFromR.success) {
    if (!options.simulate) {
      await signSendAndConfirm(arc72TransferFromR.txns, secretKey);
    }
    return true;
  }
  return false;
};

program.command("whoami").action(async () => {
  console.log(addresses.deployer);
});

program.addCommand(utilCmd);
program.addCommand(reverseCmd);
program.addCommand(collectionCmd);
program.addCommand(registrarCmd);
program.addCommand(stakingCmd);
program.addCommand(arc72Cmd);
program.addCommand(arc200Cmd);
program.addCommand(resolverCmd);
program.addCommand(vnsCmd);
program.addCommand(rsvp);

//program.addCommand(arc200);

// program.addCommand(factory);
