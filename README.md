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

## 🤖 Bot Files Overview

| File       | Platform   | Functionality                            |
|------------|------------|------------------------------------------|
| `bot1.py`  | Zenith     | Automated DeFi actions (swap/liquidity) |
| `bot2.py`  | FaroSwap   | Swap and liquidity automation            |
| `bot3.py`  | OpenFi     | Lending, borrowing & DeFi ops            |
| `bot4.py`  | Brokex     | Auto faucet claim & trade operations     |
| `bot5.py`  | Gotchipus  | NFT minting, wearable claiming           |

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
# accounts.txt `nano accounts.txt`
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
python bot1.py  # Zenith 
python bot2.py  # Faroswap 
python bot3.py  # OpenFi
python bot4.py  # Brokex
python bot5.py  # Gotchipus
````

# pools.json Edit with your Pools 

````
[    
    {
        "USDC_USDT": "Your USDC_USDT PMM Pool Address",
        "USDT_USDC": "Your USDT_USDC PMM Pool Address"
    }
]
````
# Tutorial 

[![IMG-20250711-033414.jpg](https://i.postimg.cc/59FTSRPX/IMG-20250711-033414.jpg)](https://postimg.cc/Dmnx2B3h)

# Check thx PharosScann 

https://testnet.pharosscan.xyz/address/

⚠️Notes 

- ONLY use testnet wallets  
- NEVER paste mainnet private keys  
- This bot runs indefinitely (use `Ctrl + C` to stop)  
- Testnet = Zero gas cost  
- Randomized delays between operations for safety

👉 Join Chanel https://t.me/ZonaAirdr0p
