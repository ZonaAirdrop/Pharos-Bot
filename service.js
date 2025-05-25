const fs = require("fs");
const path = require("path");
const qs = require("querystring");
const { ethers: e } = require("ethers");
const chalk = require("chalk").default || require("chalk");
const axios = require("axios");
const FakeUserAgent = require("fake-useragent");
const chains = require("./chains");
const pharos = chains.testnet.pharos;
const etc = chains.utils.etc;
const abi = chains.utils.abi;
const contract = chains.utils.contract;

// Constants for Unlimited Faucet
const BASE_API = "https://api.pharosnetwork.xyz";
const REF_CODE = "fPE8bXZfQp25MHsz";
const RPC_URL = "https://testnet.dplabs-internal.com";

// Utility to generate random amount in range (inclusive, in PHRS)
function getRandomAmount(min, max) {
  // Pastikan nilai min dan max valid dan dalam format yang benar
  min = parseFloat(min);
  max = parseFloat(max);
  
  if (isNaN(min) || isNaN(max) || min < 0 || max <= min) {
    console.error("Invalid min/max values for random amount");
    return e.parseEther("0.01"); // Default fallback
  }
  
  const amount = (Math.random() * (max - min) + min).toFixed(6); // Gunakan 6 decimal places untuk presisi lebih tinggi
  console.log(`Generated random amount: ${amount} PHRS`); // Log untuk debugging
  return e.parseEther(amount);
}

// Utility to mask address
function maskAddress(address) {
  return address ? `${address.slice(0, 6)}${'*'.repeat(6)}${address.slice(-6)}` : "Unknown";
}

// Utility to ask for input (used for wallet generation)
async function askQuestion(question, logger) {
  const readline = require("readline");
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(chalk.greenBright(`${question}: `), (answer) => {
      rl.close();
      resolve(answer);
    });
  });
}

async function performSwapUSDC(logger) {
  for (let a of global.selectedWallets || []) {
    let { privatekey: t, name: $ } = a;
    if (!t) {
      logger(`System | Warning: Skipping ${$ || "wallet with missing data"} due to missing private key`);
      continue;
    }
    try {
      let r = new e.Wallet(t, pharos.provider());
      let o = r.address;
      
      // Gunakan nilai yang lebih kecil (0.01-0.02)
      let i = getRandomAmount(0.001, 0.002);
      let amountStr = e.formatEther(i);
      
      logger(`System | ${$} | Preparing to swap ${amountStr} PHRS to USDC`);
      
      let s = contract.WPHRS.slice(2).padStart(64, "0") + contract.USDC.slice(2).padStart(64, "0");
      let n = i.toString(16).padStart(64, "0");
      let l =
        "0x04e45aaf" +
        s +
        "0000000000000000000000000000000000000000000000000000000000000bb8" +
        o.toLowerCase().slice(2).padStart(64, "0") +
        n +
        "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000";
      let c = Math.floor(Date.now() / 1e3) + 600;
      let d = ["function multicall(uint256 deadline, bytes[] calldata data) payable"];
      let p = new e.Contract(contract.SWAP, d, r);
      let f = p.interface.encodeFunctionData("multicall", [c, [l]]);
      
      // Get latest fee data
      const feeData = await pharos.provider().getFeeData();
      logger(`System | ${$} | Current gas price: ${e.formatUnits(feeData.gasPrice || 0, 'gwei')} gwei`);
      
      for (let w = 1; w <= global.maxTransaction; w++) {
        logger(`System | ${$} | Initiating Swap ${amountStr} PHRS to USDC (${w}/${global.maxTransaction})`);
        
        // Persiapkan transaction
        let g = {
          to: p.target,
          data: f,
          value: i,
        };
        
        // Estimasi gas dengan error handling
        try {
          g.gasLimit = await pharos.provider().estimateGas(g);
          // Tambahkan margin 20% untuk gas limit
          g.gasLimit = g.gasLimit * 12n / 10n;
          logger(`System | ${$} | Estimated gas limit: ${g.gasLimit.toString()}`);
        } catch (gasError) {
          logger(`System | ${$} | Gas estimation failed: ${gasError.message}`);
          logger(`System | ${$} | Using default gas limit: 300000`);
          g.gasLimit = 300000;
        }
        
        try {
          let m = await r.sendTransaction(g);
          logger(`System | ${$} | Transaction sent: ${m.hash}`);
          await m.wait(1);
          logger(`System | ${$} | ${etc.timelog()} | Swap Confirmed: ${chalk.green(pharos.explorer.tx(m.hash))}`);
        } catch (txError) {
          logger(`System | ${$} | Transaction failed: ${txError.message}`);
          // Check if error contains useful information
          if (txError.reason) {
            logger(`System | ${$} | Reason: ${txError.reason}`);
          }
        }
        
        await etc.delay(5e3);
      }
    } catch (u) {
      logger(`System | ${$} | ${etc.timelog()} | Error: ${chalk.red(u.message)}`);
    }
  }
}

async function performSwapUSDT(logger) {
  for (let a of global.selectedWallets || []) {
    let { privatekey: t, name: $ } = a;
    if (!t) {
      logger(`System | Warning: Skipping ${$ || "wallet with missing data"} due to missing private key`);
      continue;
    }
    try {
      let r = new e.Wallet(t, pharos.provider());
      let o = r.address;
      
      // Gunakan nilai yang lebih kecil (0.01-0.02) 
      let i = getRandomAmount(0.001, 0.005);
      let amountStr = e.formatEther(i);
      
      logger(`System | ${$} | Preparing to swap ${amountStr} PHRS to USDT`);
      
      let s = contract.WPHRS.slice(2).padStart(64, "0") + contract.USDT.slice(2).padStart(64, "0");
      let n = i.toString(16).padStart(64, "0");
      let l =
        "0x04e45aaf" +
        s +
        "0000000000000000000000000000000000000000000000000000000000000bb8" +
        o.toLowerCase().slice(2).padStart(64, "0") +
        n +
        "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000";
      let c = Math.floor(Date.now() / 1e3) + 600;
      let d = ["function multicall(uint256 deadline, bytes[] calldata data) payable"];
      let p = new e.Contract(contract.SWAP, d, r);
      let f = p.interface.encodeFunctionData("multicall", [c, [l]]);
      
      // Get latest fee data
      const feeData = await pharos.provider().getFeeData();
      logger(`System | ${$} | Current gas price: ${e.formatUnits(feeData.gasPrice || 0, 'gwei')} gwei`);
      
      for (let w = 1; w <= global.maxTransaction; w++) {
        logger(`System | ${$} | Initiating Swap ${amountStr} PHRS to USDT (${w}/${global.maxTransaction})`);
        
        // Persiapkan transaction
        let g = {
          to: p.target,
          data: f,
          value: i,
        };
        
        // Estimasi gas dengan error handling
        try {
          g.gasLimit = await pharos.provider().estimateGas(g);
          // Tambahkan margin 20% untuk gas limit
          g.gasLimit = g.gasLimit * 12n / 10n;
          logger(`System | ${$} | Estimated gas limit: ${g.gasLimit.toString()}`);
        } catch (gasError) {
          logger(`System | ${$} | Gas estimation failed: ${gasError.message}`);
          logger(`System | ${$} | Using default gas limit: 300000`);
          g.gasLimit = 300000;
        }
        
        try {
          let m = await r.sendTransaction(g);
          logger(`System | ${$} | Transaction sent: ${m.hash}`);
          await m.wait(1);
          logger(`System | ${$} | ${etc.timelog()} | Swap Confirmed: ${chalk.green(pharos.explorer.tx(m.hash))}`);
        } catch (txError) {
          logger(`System | ${$} | Transaction failed: ${txError.message}`);
          // Check if error contains useful information
          if (txError.reason) {
            logger(`System | ${$} | Reason: ${txError.reason}`);
          }
        }
        
        await etc.delay(5e3);
      }
    } catch (u) {
      logger(`System | ${$} | ${etc.timelog()} | Error: ${chalk.red(u.message)}`);
    }
  }
}

async function checkBalanceAndApprove(a, t, $, logger) {
  let r = new e.Contract(t, abi.ERC20, a);
  let o = await r.allowance(a.address, $);
  if (0n === o) {
    logger(`System | Approving token for ${a.address}`);
    let i = e.MaxUint256;
    try {
      let s = await r.approve($, i);
      await s.wait(1);
      await etc.delay(3e3);
      logger(`System | Approval successful for ${a.address}`);
    } catch (n) {
      logger(`System | Approval failed: ${chalk.red(n.message)}`);
      return false;
    }
  }
  return true;
}

async function addLpUSDC(logger) {
  for (let a of global.selectedWallets || []) {
    let { privatekey: t, name: $ } = a;
    if (!t) {
      logger(`System | Warning: Skipping ${$ || "wallet with missing data"} due to missing private key`);
      continue;
    }
    try {
      let r = new e.Wallet(t, pharos.provider());
      let o = new e.Contract(contract.ROUTER, abi.ROUTER, r);
      let i = Math.floor(Date.now() / 1e3) + 1800;
      
      // Check and approve USDC
      let l = await checkBalanceAndApprove(r, contract.USDC, contract.ROUTER, logger);
      if (!l) {
        continue;
      }
      
      // Gunakan nilai yang lebih kecil (0.01-0.02)
      let amount = getRandomAmount(0.001, 0.002);
      let amountStr = e.formatEther(amount);
      
      logger(`System | ${$} | Preparing to add liquidity with ${amountStr} PHRS + USDC`);
      
      let c = {
        token0: contract.WPHRS,
        token1: contract.USDC,
        fee: 500,
        tickLower: -887220,
        tickUpper: 887220,
        amount0Desired: amount.toString(),
        amount1Desired: amount.toString(),
        amount0Min: "0",
        amount1Min: "0",
        recipient: r.address,
        deadline: i,
      };
      
      let d = o.interface.encodeFunctionData("mint", [c]);
      let p = o.interface.encodeFunctionData("refundETH", []);
      let f = [d, p];
      
      for (let w = 1; w <= global.maxTransaction; w++) {
        logger(
          `System | ${$} | Initiating Add Liquidity ${amountStr} PHRS + ${amountStr} USDC (${w}/${global.maxTransaction})`
        );
        
        try {
          let g = await o.multicall(f, {
            value: amount,
            gasLimit: 5e5, // Use fixed gas limit for add liquidity
          });
          
          logger(`System | ${$} | Transaction sent: ${g.hash}`);
          await g.wait(1);
          logger(`System | ${$} | ${etc.timelog()} | Liquidity Added: ${chalk.green(pharos.explorer.tx(g.hash))}`);
        } catch (txError) {
          logger(`System | ${$} | Transaction failed: ${txError.message}`);
          // Check if error contains useful information
          if (txError.reason) {
            logger(`System | ${$} | Reason: ${txError.reason}`);
          }
        }
        
        await etc.delay(5e3);
      }
    } catch (m) {
      logger(`System | ${$} | ${etc.timelog()} | Error: ${chalk.red(m.message)}`);
    }
  }
}

async function addLpUSDT(logger) {
  for (let a of global.selectedWallets || []) {
    let { privatekey: t, name: $ } = a;
    if (!t) {
      logger(`System | Warning: Skipping ${$ || "wallet with missing data"} due to missing private key`);
      continue;
    }
    try {
      let r = new e.Wallet(t, pharos.provider());
      let o = new e.Contract(contract.ROUTER, abi.ROUTER, r);
      let i = Math.floor(Date.now() / 1e3) + 1800;
      
      // Check and approve USDT
      let l = await checkBalanceAndApprove(r, contract.USDT, contract.ROUTER, logger);
      if (!l) {
        continue;
      }
      
      // Gunakan nilai yang lebih kecil (0.01-0.02)
      let amount = getRandomAmount(0.001, 0.002);
      let amountStr = e.formatEther(amount);
      
      logger(`System | ${$} | Preparing to add liquidity with ${amountStr} PHRS + USDT`);
      
      let c = {
        token0: contract.WPHRS,
        token1: contract.USDT,
        fee: 500,
        tickLower: -887220,
        tickUpper: 887220,
        amount0Desired: amount.toString(),
        amount1Desired: amount.toString(),
        amount0Min: "0",
        amount1Min: "0",
        recipient: r.address,
        deadline: i,
      };
      
      let d = o.interface.encodeFunctionData("mint", [c]);
      let p = o.interface.encodeFunctionData("refundETH", []);
      let f = [d, p];
      
      for (let w = 1; w <= global.maxTransaction; w++) {
        logger(
          `System | ${$} | Initiating Add Liquidity ${amountStr} PHRS + ${amountStr} USDT (${w}/${global.maxTransaction})`
        );
        
        try {
          let g = await o.multicall(f, {
            value: amount,
            gasLimit: 5e5, // Use fixed gas limit for add liquidity
          });
          
          logger(`System | ${$} | Transaction sent: ${g.hash}`);
          await g.wait(1);
          logger(`System | ${$} | ${etc.timelog()} | Liquidity Added: ${chalk.green(pharos.explorer.tx(g.hash))}`);
        } catch (txError) {
          logger(`System | ${$} | Transaction failed: ${txError.message}`);
          // Check if error contains useful information
          if (txError.reason) {
            logger(`System | ${$} | Reason: ${txError.reason}`);
          }
        }
        
        await etc.delay(5e3);
      }
    } catch (m) {
      logger(`System | ${$} | ${etc.timelog()} | Error: ${chalk.red(m.message)}`);
    }
  }
}

async function randomTransfer(logger) {
  for (let a of global.selectedWallets || []) {
    let { privatekey: t, name: $ } = a;
    if (!t) {
      logger(`System | Warning: Skipping ${$ || "wallet with missing private key"} due to missing private key`);
      continue;
    }
    try {
      let r = new e.Wallet(t, pharos.provider());
      let o = pharos.provider();
      let s = e.parseEther("0.000001");
      let n = await o.getBalance(r.address);
      if (n < s * BigInt(global.maxTransaction)) {
        logger(
          `System | Warning: ${$} | Insufficient balance (${e.formatEther(
            n
          )}) to transfer 0.000001 PHRS x ${global.maxTransaction} times`
        );
        continue;
      }
      for (let l = 1; l <= global.maxTransaction; l++) {
        let c = e.Wallet.createRandom();
        let d = c.address;
        logger(`System | ${$} | Initiating Transfer 0.000001 PHRS to ${d} (${l}/${global.maxTransaction})`);
        let p = await r.sendTransaction({
          to: d,
          value: s,
          gasLimit: 21e3,
          gasPrice: 0,
        });
        await p.wait(1);
        logger(`System | ${$} | ${etc.timelog()} | Transfer Confirmed: ${chalk.green(pharos.explorer.tx(p.hash))}`);
        await etc.delay(5e3);
      }
    } catch (f) {
      logger(`System | ${$} | ${etc.timelog()} | Transfer Error: ${chalk.red(f.message)}`);
    }
  }
}

async function accountCheck(logger) {
  for (let a of global.selectedWallets || []) {
    let { privatekey: t, token: $, name: r } = a;
    if (!t || !$) {
      logger(`System | Warning: Skipping ${r || "wallet with missing data"} due to missing data`);
      continue;
    }
    try {
      let o = new e.Wallet(t, pharos.provider());
      logger(`System | ${r} | Checking Profile Stats for ${o.address}`);
      let s = {
        ...etc.headers,
        authorization: `Bearer ${$}`,
      };
      let n = await axios.get(`https://api.pharosnetwork.xyz/user/profile?address=${o.address}`, {
        headers: s,
      });
      let l = n.data;
      if (0 !== l.code || !l.data.user_info) {
        logger(`System | ${r} | Profile check failed: ${chalk.red(l.msg)}`);
        continue;
      }
      let { ID: c, TotalPoints: d, TaskPoints: p, InvitePoints: f } = l.data.user_info;
      logger(
        `System | ${r} | ${etc.timelog()} | ID: ${c}, TotalPoints: ${d}, TaskPoints: ${p}, InvitePoints: ${f}`
      );
      await etc.delay(5e3);
    } catch (w) {
      if (axios.isAxiosError(w)) {
        logger(
          `System | ${r} | ${etc.timelog()} | HTTP Error: ${chalk.red(
            `${w.response?.status} - ${w.response?.data?.message || w.message}`
          )}`
        );
      } else {
        logger(`System | ${r} | ${etc.timelog()} | Error: ${chalk.red(w.message)}`);
      }
    }
    await etc.delay(5e3);
  }
}

async function accountLogin(logger) {
  for (let a of global.selectedWallets || []) {
    let { privatekey: t, token: $, name: r } = a;
    if (!t) {
      logger(`System | Warning: Skipping ${r || "wallet with missing private key"} due to missing private key`);
      continue;
    }
    if (!$) {
      logger(`System | ${r} | No token found. Attempting login`);
      await etc.delay(3e3);
      try {
        let o = new e.Wallet(t, pharos.provider());
        let i = await o.signMessage("pharos");
        logger(`System | ${r} | Logging in to Pharos for ${o.address}`);
        let n = {
          ...etc.headers,
        };
        let l = await axios.post(
          `https://api.pharosnetwork.xyz/user/login?address=${o.address}&signature=${i}&invite_code=rmKeUmr3VL7bLeva`,
          null,
          { headers: n }
        );
        let c = l.data;
        if (0 !== c.code || !c.data?.jwt) {
          logger(`System | ${r} | Login failed: ${chalk.red(c.msg)}`);
          continue;
        }
        a.token = c.data.jwt;
        logger(`System | ${r} | Login successful`);
      } catch (p) {
        logger(`System | ${r} | ${etc.timelog()} | Login error: ${chalk.red(p.message)}`);
      }
    }
  }
  let f = path.join(__dirname, "./wallet.json");
  try {
    let w = JSON.parse(fs.readFileSync(f, "utf8"));
    let g = w.wallets || [];
    for (let m of global.selectedWallets) {
      if (!m.privatekey && !m.name) {
        continue;
      }
      let u = g.findIndex((e) => e.privatekey.trim().toLowerCase() === m.privatekey.trim().toLowerCase());
      if (-1 !== u) {
        g[u].token = m.token || "";
      }
    }
    fs.writeFileSync(f, JSON.stringify({ wallets: g }, null, 2), "utf8");
    logger(`System | Updated wallet.json with new tokens`);
  } catch (h) {
    logger(`System | Failed to update wallet.json: ${chalk.red(h.message)}`);
  }
  await etc.delay(5e3);
}

async function accountCheckIn(logger) {
  for (let a of global.selectedWallets || []) {
    let { privatekey: t, token: $, name: r } = a;
    if (!t || !$) {
      logger(`System | Warning: Skipping ${r || "wallet with missing data"} due to missing data`);
      continue;
    }
    try {
      let o = new e.Wallet(t, pharos.provider());
      logger(`System | ${r} | Checking in for ${o.address}`);
      let s = {
        ...etc.headers,
        authorization: `Bearer ${$}`,
      };
      let n = await axios.post(`https://api.pharosnetwork.xyz/sign/in?address=${o.address}`, null, {
        headers: s,
      });
      let l = n.data;
      if (0 === l.code) {
        logger(`System | ${r} | ${etc.timelog()} | Check-in successful: ${l.msg}`);
      } else if (l.msg?.toLowerCase().includes("already")) {
        logger(`System | ${r} | ${etc.timelog()} | Already checked in`);
      } else {
        logger(`System | ${r} | ${etc.timelog()} | Check-in failed: ${chalk.red(l.msg || "Unknown error")}`);
      }
    } catch (c) {
      if (axios.isAxiosError(c)) {
        logger(
          `System | ${r} | ${etc.timelog()} | HTTP Error: ${chalk.red(
            `${c.response?.status} - ${c.response?.data?.message || c.message}`
          )}`
        );
      } else {
        logger(`System | ${r} | ${etc.timelog()} | Error: ${chalk.red(c.message)}`);
      }
    }
    await etc.delay(5e3);
  }
}

async function claimFaucetUSDC(logger) {
  for (let a of global.selectedWallets || []) {
    let { privatekey: t, name: $ } = a;
    if (!t) {
      logger(`System | Warning: Skipping ${$ || "wallet with missing private key"} due to missing private key`);
      continue;
    }
    let r = new e.Wallet(t, pharos.provider());
    try {
      logger(`System | ${$} | Claiming USDC for ${r.address}`);
      let o = await axios.post(
        "https://testnet-router.zenithswap.xyz/api/v1/faucet",
       