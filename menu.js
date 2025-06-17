cat << 'EOF' > menu.js
const readline = require("readline");
const { exec } = require("child_process");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log("\n===== MENU PHAROS =====");
console.log("1. Run Bot (index.js)");
console.log("2. Mint NFT (gotchipus.js)");
console.log("3. Exit\n");

rl.question("Pilih opsi [1/2/3]: ", (jawaban) => {
  if (jawaban === "1") {
    console.log("Menjalankan Bot utama...");
    exec("node index.js", (err, stdout, stderr) => {
      if (err) {
        console.error(`Gagal menjalankan bot: ${err}`);
      } else {
        console.log(stdout);
      }
      rl.close();
    });
  } else if (jawaban === "2") {
    console.log("Menjalankan Mint NFT...");
    exec("node gotchipus.js", (err, stdout, stderr) => {
      if (err) {
        console.error(`Gagal mint NFT: ${err}`);
      } else {
        console.log(stdout);
      }
      rl.close();
    });
  } else {
    console.log("Keluar.");
    rl.close();
  }
});
EOF
