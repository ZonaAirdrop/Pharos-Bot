require('colors');
const moment = require('moment-timezone');
const fs = require('fs');
const path = require('path');

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function header() {
  process.stdout.write('\x1Bc');
  console.log('===================================================='.cyan);
  console.log('                                                    '.cyan);
  console.log(' 888    888                 888                     '.cyan);
  console.log(' 888    888                 888                     '.cyan);
  console.log(' 888    888                 888                     '.cyan);
  console.log(' 888    888  8888b.  .d8888 888  888  8888b.       '.cyan);
  console.log(' 888    888     "88bd8" 888 888 .88P     "88b      '.cyan);
  console.log(' 888    888 .d888888 888 888 888888K .d888888      '.cyan);
  console.log(' 888    888 888  888 "Y88888 888 "88b 888  888      '.cyan);
  console.log(' 888    888 "Y888888      88 888  888 "Y888888      '.cyan);
  console.log('                                                    '.cyan);
  console.log('===================================================='.cyan);
  console.log();
}

const loading = (message, duration) => {
  return new Promise((resolve) => {
    const symbols = ['|', '/', '-', '\\'];
    let currentIndex = 0;

    const intervalTime = 200;
    let totalIterations = duration / intervalTime;

    const interval = setInterval(() => {
      process.stdout.write(`\r${message} [${symbols[currentIndex]}]`);
      currentIndex = (currentIndex + 1) % symbols.length;

      if (totalIterations-- <= 0) {
        clearInterval(interval);
        process.stdout.write('\n');
        resolve();
      }
    }, intervalTime);
  });
};

const licenseText = `
/*
 * MIT License
 * 
 * Copyright (c) 2024 KAZUHA787
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 * PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
`.trim();

function utility(fileName) {
    const filePath = path.resolve(__dirname, `../../${fileName}`);
    const fileContent = fs.readFileSync(filePath, 'utf-8').replace(/\s+/g, '');
    const normalizedLicense = licenseText.replace(/\s+/g, '');

    if (!fileContent.includes(normalizedLicense)) {
        console.error(`License has been removed or modified in ${fileName}. Exiting...`);
        process.exit(1);
    }
}

function timelog() {
  return moment().format('HH:mm:ss | DD-MM-YYYY');
}

function countdown(durationMs, message) {
  return new Promise((resolve) => {
    const startTime = Date.now();
    const endTime = startTime + durationMs;

    const interval = setInterval(() => {
      const now = Date.now();
      const remainingTime = Math.max(0, endTime - now);

      const hours = Math.floor(remainingTime / (1000 * 60 * 60));
      const minutes = Math.floor((remainingTime % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((remainingTime % (1000 * 60)) / 1000);

      process.stdout.write(
        `\r${message}: ${hours}h ${minutes}m ${seconds}s remaining... `
      );

      if (remainingTime <= 0) {
        clearInterval(interval);
        process.stdout.write("\n");
        resolve();
      }
    }, 1000);
  });
}

const headers = {
        accept: "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.8",
        authorization: "Bearer null",
        "sec-ch-ua": '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        Referer: "https://testnet.pharosnetwork.xyz/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
};

module.exports = { delay, header, loading, utility, timelog, countdown, headers };
