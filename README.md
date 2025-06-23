# PHAROS BOT TESNET #

📋 Features
 
🚀 Automated. Swaps

🚀 Automated. Transfer 

🚀 Automated. Claim Faucet 

🚀 Automated Daily Check-in
 
🚀 Auto Mint NFT 

🚀 Multi-Wallet Support

🚀 Proxy Support

🚀 Support. VPS & Termux 

## 📦 Included Bots

| File Name | Bot Name      | Description                        |
| --------- | ------------- | ---------------------------------- |
| `bot1.py` | Pharos BOT    | DeFi automation for Pharos Testnet |
| `bot2.py` | Gotchipus BOT | NFT minting & wearable claiming    |
| `bot3.py` | OpenFi BOT    | Lending, borrowing & DeFi services |
| `bot4.py` | Brokex BOT    | Faucet claim and trade automation  |


# Create Screen for vps 
Install screen 

````
sudo apt update
sudo apt install git scree
n
````
# Create Screen 

````
screen -S pharosbot
````
Once the bot is running, press:

Ctrl + A then D to exit the screen and keep the bot running

Back to Screen Anytime

````
screen -r pharosbot
````

 # Installation

````markdown
git clone https://github.com/ZonaAirdrop/Pharos-Bot.git
````
````
cd Pharos-Bot
````

# 1.Install Dependencies
````
pip install -r requirements.txt
````
#  .Create accounts.txt `nano accounts.txt`

````
your_private_key_1
your_private_key_2
````

(Optional) Create `proxies.txt`:

Each proxy must be on a new line:

```
127.0.0.1:8080
http://127.0.0.1:8080
http://user:pass@127.0.0.1:8080
```

# Run Bot Start

````
python bot1.py  # Pharos
python bot2.py  # Gotchipus
python bot3.py  # OpenFi
python bot4.py  # Brokex
````

# Check thx PharosScann 

https://testnet.pharosscan.xyz/address/

⚠️Notes 

- ONLY use testnet wallets  
- NEVER paste mainnet private keys  
- This bot runs indefinitely (use `Ctrl + C` to stop)  
- Testnet = Zero gas cost  
- Randomized delays between operations for safety

👉 Join Chanel https://t.me/ZonaAirdr0p
