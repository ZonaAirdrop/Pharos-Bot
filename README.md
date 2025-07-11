# PHAROS BOT TESNET #

----------------------------
📋 Features
----------------------------
🚀 Automated Swaps  
🚀 Automated Transfer  
🚀 Automated Claim Faucet  
🚀 Automated Daily Check-in  
🚀 Auto Mint NFT  
🚀 Multi-Wallet Support  
🚀 Proxy Support  
🚀 Support VPS & Termux
----------------------------

## 🤖 Bot Files Overview

| File      | Platform  | Functionality                           |
| --------- | --------- | --------------------------------------- |
| `bot1.py` | Zenith    | Automated DeFi actions (swap/liquidity) |
| `bot2.py` | OpenFi    | Lending, borrowing & DeFi ops           |
| `bot3.py` | Brokex    | Auto faucet claim & trade operations    |
| `bot4.py` | Gotchipus | NFT minting, wearable claiming          |
| `bot5.py` | Zentra    | General DeFi utilities & automation     |
| `bot6.py` | FaroSwap  | Swap and liquidity automation           |


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
python bot2.py  # OpenFi
python bot3.py  # Brokek
python bot4.py  # Gotchipus
python bot5.py  # Zentra
Python bot6.py  # Faroswap
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

[![IMG-20250711-033454.jpg](https://i.postimg.cc/L6K7C37N/IMG-20250711-033454.jpg)](https://postimg.cc/JtxPtZRk)

[![IMG-20250711-033524.jpg](https://i.postimg.cc/gJ15PV0c/IMG-20250711-033524.jpg)](https://postimg.cc/wycFXsJn)

## ☕ Buy Me a Coffee

* **EVM:** `0x1B19167193553f125338d42432f61CBEAd2d4339`

  
# Check thx PharosScann 

https://testnet.pharosscan.xyz/address/

⚠️Notes 

- ONLY use testnet wallets  
- NEVER paste mainnet private keys  
- This bot runs indefinitely (use `Ctrl + C` to stop)  
- Testnet = Zero gas cost  
- Randomized delays between operations for safety

👉 Join Chanel https://t.me/ZonaAirdr0p
