from web3 import Web3
from eth_account import Account
from aiohttp import ClientSession, ClientTimeout
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Gotchipus:
    def __init__(self) -> None:
        self.RPC_URL = "https://testnet.dplabs-internal.com"
        self.NFT_CONTRACT_ADDRESS = "0x0000000038f050528452D6Da1E7AACFA7B3Ec0a8"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]}
        ]''')
        self.MINT_CONTRACT_ABI = [
            {
                "inputs": [],
                "name": "freeMint",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs":[],
                "name":"claimWearable",
                "outputs":[],
                "stateMutability":"nonpayable",
                "type":"function"
            }
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        logo = r"""
    \033[36m┌─┐┬ ┬┌┐┌┌─┐┌─┐  ┌─┐┬┌┬┐┌─┐┬─┐┌┬┐┌─┐┬─┐\033[0m
    \033[36m│ ┬│ ││││├┤ ├─┤  │  │ │ │ │├┬┘ │ ├┤ ├┬┘\033[0m
    \033[36m└─┘└─┘┘└┘└─┘┴ ┴  └─┘┴ ┴ └─┘┴└─ ┴ └─┘┴└─\033[0m

====================================================
     \033[35mPlatform\033[0m          : \033[36mzonaairdrop\033[0m
     \033[35mTelegram Channel\033[0m  : \033[36m@ZonaAirdr0p\033[0m
     \033[35mTelegram Group\033[0m    : \033[36m@ZonaAirdropGroup\033[0m
     \033[35mDescription\033[0m      : \033[36mPlatform Airdrop Terpercaya\033[0m
====================================================
    """
        print(logo)

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    # ... [REST OF THE ORIGINAL CLASS METHODS REMAIN UNCHANGED ...]
    # (All other methods from your original file should be kept exactly as they were)

if __name__ == "__main__":
    try:
        bot = Gotchipus()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Gotchipus - BOT{Style.RESET_ALL}"                              
        )