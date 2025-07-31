from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from base64 import b64encode
from colorama import init, Fore, Style
import asyncio, random, time, json, re, os, pytz
from dotenv import load_dotenv

wib = pytz.timezone('Asia/Jakarta')

PUBLIC_KEY_PEM = b"""
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDWPv2qP8+xLABhn3F/U/hp76HP
e8dD7kvPUh70TC14kfvwlLpCTHhYf2/6qulU1aLWpzCz3PJr69qonyqocx8QlThq
5Hik6H/5fmzHsjFvoPeGN5QRwYsVUH07MbP7MNbJH5M2zD5Z1WEp9AHJklITbS1z
h23cf2WfZ0vwDYzZ8QIDAQAB
-----END PUBLIC KEY-----
"""

# === Terminal Color Setup ===
class Colors:
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    WHITE = Fore.WHITE
    BLUE = Fore.BLUE
    BRIGHT_GREEN = Fore.LIGHTGREEN_EX
    BRIGHT_MAGENTA = Fore.LIGHTMAGENTA_EX
    BRIGHT_WHITE = Fore.LIGHTWHITE_EX
    BRIGHT_BLACK = Fore.LIGHTBLACK_EX

class Logger:
    @staticmethod
    def log(label, symbol, msg, color):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {color}[{symbol}] {msg}{Colors.RESET}")

    @staticmethod
    def info(msg): Logger.log("INFO", "✓", msg, Colors.GREEN)
    @staticmethod
    def warn(msg): Logger.log("WARN", "!", msg, Colors.YELLOW)
    @staticmethod
    def error(msg): Logger.log("ERR", "✗", msg, Colors.RED)
    @staticmethod
    def success(msg): Logger.log("OK", "+", msg, Colors.GREEN)
    @staticmethod
    def loading(msg): Logger.log("LOAD", "⟳", msg, Colors.CYAN)
    @staticmethod
    def step(msg): Logger.log("STEP", "➤", msg, Colors.WHITE)
    @staticmethod
    def action(msg): Logger.log("ACTION", "↪️", msg, Colors.CYAN)
    @staticmethod
    def actionSuccess(msg): Logger.log("ACTION", "✅", msg, Colors.GREEN)

logger = Logger()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

async def display_welcome_screen():
    clear_console()
    now = datetime.now()
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}")
    print("  ╔══════════════════════════════════════╗")
    print("  ║         Auto Staking B O T             ║")
    print("  ║                                      ║")
    print(f"  ║       {Colors.YELLOW}{now.strftime('%H:%M:%S %d.%m.%Y')}{Colors.BRIGHT_GREEN}         ║")
    print("  ║                                      ║")
    print("  ║     Pharos TESTNET AUTOMATION         ║")
    print(f"  ║   {Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}  |  t.me/ZonaAirdr0p   ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    await asyncio.sleep(1)

class AutoStaking:
    def __init__(self) -> None:
        self.HEADERS = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://autostaking.pro",
            "Referer": "https://autostaking.pro/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api.autostaking.pro"
        self.RPC_URL = "https://api.zan.top/node/v1/pharos/testnet/d8df54c30b72451894be4a3bd5c21220"
        self.USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
        self.USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
        self.MUSD_CONTRACT_ADDRESS = "0x7F5e05460F927Ee351005534423917976F92495e"
        self.mvMUSD_CONTRACT_ADDRESS = "0xF1CF5D79bE4682D50f7A60A047eACa9bD351fF8e"
        self.STAKING_ROUTER_ADDRESS = "0x11cD3700B310339003641Fdce57c1f9BD21aE015"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"claimFaucet","stateMutability":"nonpayable","inputs":[],"outputs":[{"name":"","type":"uint256"}]}
        ]''')
        self.AUTOSTAKING_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "getNextFaucetClaimTime",
                "stateMutability": "view",
                "inputs": [
                    { "name": "user", "type": "address" }
                ],
                "outputs": [
                    { "name": "", "type": "uint256" }
                ]
            }
        ]
        self.PROMPT = (
            "1. Mandatory Requirement: The product's TVL must be higher than one million USD.\n"
            "2. Balance Preference: Prioritize products that have a good balance of high current APY and high TVL.\n"
            "3. Portfolio Allocation: Select the 3 products with the best combined ranking in terms of current APY and TVL among those with TVL > 1,000,000 USD. "
            "To determine the combined ranking, rank all eligible products by current APY (highest to lowest) and by TVL (highest to lowest), "
            "then sum the two ranks for each product. Choose the 3 products with the smallest sum of ranks. Allocate the investment equally among these 3 products, "
            "with each receiving approximately 33.3% of the investment."
        )
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.auth_tokens = {}
        self.used_nonce = {}
        self.staking_count = 0
        self.usdc_amount = 0
        self.usdt_amount = 0
        self.musd_amount = 0
        self.min_delay = 0
        self.max_delay = 0

    async def welcome(self):
        await display_welcome_screen()

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/http.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    logger.error(f"File {filename} Not Found.")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                logger.error(f"No Proxies Found.")
                return

            logger.info(
                f"Proxies Total  : {len(self.proxies)}"
            )
        
        except Exception as e:
            logger.error(f"Failed To Load Proxies: {e}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None
        
    def generate_auth_token(self, address: str):
        try:
            public_key = serialization.load_pem_public_key(PUBLIC_KEY_PEM)

            ciphertext = public_key.encrypt(
                address.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            token_base64 = b64encode(ciphertext).decode('utf-8')

            return token_base64
        except Exception as e:
            logger.error(f"Error generating auth token: {e}") 
            return None
        
    def generate_recommendation_payload(self, address: str):
        try:
            usdc_assets = int(self.usdc_amount * (10 ** 6))
            usdt_assets = int(self.usdt_amount * (10 ** 6))
            musd_assets = int(self.musd_amount * (10 ** 6))

            payload = {
                "user":address,
                "profile":self.PROMPT,
                "userPositions":[],
                "userAssets":[
                    {
                        "chain":{"id":688688},
                        "name":"USDC",
                        "symbol":"USDC",
                        "decimals":6,
                        "address":"0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED",
                        "assets":str(usdc_assets),
                        "price":1,
                        "assetsUsd":self.usdc_amount
                    },
                    {
                        "chain":{"id":688688},
                        "name":"USDT",
                        "symbol":"USDT",
                        "decimals":6,
                        "address":"0xD4071393f8716661958F766DF660033b3d35fD29",
                        "assets":str(usdt_assets),
                        "price":1,
                        "assetsUsd":self.usdt_amount
                    },
                    {
                        "chain":{"id":688688},
                        "name":"MockUSD",
                        "symbol":"MockUSD",
                        "decimals":6,
                        "address":"0x7F5e05460F927Ee351005534423917976F92495e",
                        "assets":str(musd_assets),
                        "price":1,
                        "assetsUsd":self.musd_amount
                    }
                ],
                "chainIds":[688688],
                "tokens":["USDC","USDT","MockUSD"],
                "protocols":["MockVault"],
                "env":"pharos"
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
        
    def generate_transactions_payload(self, address: str, change_tx: list):
        try:
            payload = {
                "user":address,
                "changes":change_tx,
                "prevTransactionResults":{}
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
        
    async def get_web3_with_check(self, address: str, use_proxy: bool, retries=3, timeout=60):
        request_kwargs = {"timeout": timeout}

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if use_proxy and proxy:
            request_kwargs["proxies"] = {"http": proxy, "https": proxy}

        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs=request_kwargs))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                raise Exception(f"Failed to Connect to RPC: {str(e)}")
            
    async def get_token_balance(self, address: str, contract_address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
            balance = token_contract.functions.balanceOf(address).call()
            decimals = token_contract.functions.decimals().call()

            token_balance = balance / (10 ** decimals)

            return token_balance
        except Exception as e:
            logger.error(f" {str(e)}")
            return None
        
    async def send_raw_transaction_with_retries(self, account, web3, tx, retries=5):
        for attempt in range(retries):
            try:
                signed_tx = web3.eth.account.sign_transaction(tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                return tx_hash
            except TransactionNotFound:
                pass
            except Exception as e:
                logger.warn(f" [Attempt {attempt + 1}] Send TX Error: {str(e)}")
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Hash Not Found After Maximum Retries")

    async def wait_for_receipt_with_retries(self, web3, tx_hash, retries=5):
        for attempt in range(retries):
            try:
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                return receipt
            except TransactionNotFound:
                pass
            except Exception as e:
                logger.warn(f" [Attempt {attempt + 1}] Wait for Receipt Error: {str(e)}")
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
    
    async def get_next_faucet_claim_time(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.mvMUSD_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.AUTOSTAKING_CONTRACT_ABI)

            next_faucet_claim_time = token_contract.functions.getNextFaucetClaimTime(web3.to_checksum_address(address)).call()

            return next_faucet_claim_time
        except Exception as e:
            logger.error(f" {str(e)}")
            return None
        
    async def perform_claim_faucet(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.mvMUSD_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            claim_data = token_contract.functions.claimFaucet()
            estimated_gas = claim_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            claim_tx = claim_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, claim_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            logger.error(f" {str(e)}")
            return None, None
        
    async def approving_token(self, account: str, address: str, router_address: str, asset_address: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            
            spender = web3.to_checksum_address(router_address)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(asset_address), abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()
            
            amount_to_wei = int(amount * (10 ** decimals))

            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount_to_wei:
                approve_data = token_contract.functions.approve(spender, 2**256 - 1)
                estimated_gas = approve_data.estimate_gas({"from": address})

                max_priority_fee = web3.to_wei(1, "gwei")
                max_fee = max_priority_fee

                approve_tx = approve_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": self.used_nonce[address],
                    "chainId": web3.eth.chain_id,
                })

                tx_hash = await self.send_raw_transaction_with_retries(account, web3, approve_tx)
                receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

                block_number = receipt.blockNumber
                self.used_nonce[address] += 1

                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                
                logger.success(f"Approve : Success")
                logger.action(f" Tx Hash : {tx_hash}")
                logger.actionSuccess(f" Explorer: {explorer}")
                await asyncio.sleep(5)

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
        
    async def perform_staking(self, account: str, address: str, change_tx: list, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            await self.approving_token(account, address, self.STAKING_ROUTER_ADDRESS, self.USDC_CONTRACT_ADDRESS, self.usdc_amount, use_proxy)
            await self.approving_token(account, address, self.STAKING_ROUTER_ADDRESS, self.USDT_CONTRACT_ADDRESS, self.usdt_amount, use_proxy)
            await self.approving_token(account, address, self.STAKING_ROUTER_ADDRESS, self.MUSD_CONTRACT_ADDRESS, self.musd_amount, use_proxy)

            transactions = await self.generate_change_transactions(address, change_tx, use_proxy)
            if not transactions:
                raise Exception("Generate Transaction Calldata Failed")
            
            calldata = transactions["data"]["688688"]["data"]

            estimated_gas = web3.eth.estimate_gas({
                "from": web3.to_checksum_address(address),
                "to": web3.to_checksum_address(self.STAKING_ROUTER_ADDRESS),
                "data": calldata,
            })

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            tx = {
                "from": web3.to_checksum_address(address),
                "to": web3.to_checksum_address(self.STAKING_ROUTER_ADDRESS),
                "data": calldata,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            }

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            logger.error(f" {str(e)}")
            return None, None
        
    async def print_timer(self):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            # Formatted the timestamp to match the desired output [16:27:25]
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(
                f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} "
                f"{Colors.BLUE}{Colors.BOLD}Wait For {Colors.RESET}"
                f"{Colors.WHITE}{Colors.BOLD}{remaining} {Colors.RESET}"
                f"{Colors.BLUE}{Colors.BOLD}Seconds For Next Tx...{Colors.RESET}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)
        print(" " * 100, end="\r") # Clear the line after countdown
        

    def print_question(self):
        while True:
            try:
                staking_count = int(input(f"{Colors.YELLOW}{Colors.BOLD}Enter Staking Count For Each Wallets -> {Colors.RESET}").strip())
                if staking_count > 0:
                    self.staking_count = staking_count
                    break
                else:
                    print(f"{Colors.RED}{Colors.BOLD}Please enter positive number.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}{Colors.BOLD}Invalid input. Enter a number.{Colors.RESET}")

        while True:
            try:
                usdc_amount = float(input(f"{Colors.YELLOW}{Colors.BOLD}Enter USDC Amount -> {Colors.RESET}").strip())
                if usdc_amount > 0:
                    self.usdc_amount = usdc_amount
                    break
                else:
                    print(f"{Colors.RED}{Colors.BOLD}Amount must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}{Colors.BOLD}Invalid input. Enter a float or decimal number.{Colors.RESET}")

        while True:
            try:
                usdt_amount = float(input(f"{Colors.YELLOW}{Colors.BOLD}Enter USDT Amount -> {Colors.RESET}").strip())
                if usdt_amount > 0:
                    self.usdt_amount = usdt_amount
                    break
                else:
                    print(f"{Colors.RED}{Colors.BOLD}Amount must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}{Colors.BOLD}Invalid input. Enter a float or decimal number.{Colors.RESET}")

        while True:
            try:
                musd_amount = float(input(f"{Colors.YELLOW}{Colors.BOLD}Enter MockUSD Amount -> {Colors.RESET}").strip())
                if musd_amount > 0:
                    self.musd_amount = musd_amount
                    break
                else:
                    print(f"{Colors.RED}{Colors.BOLD}Amount must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}{Colors.BOLD}Invalid input. Enter a float or decimal number.{Colors.RESET}")

        while True:
            try:
                min_delay = int(input(f"{Colors.GREEN}{Colors.BOLD}Min Delay Each Tx -> {Colors.RESET}").strip())
                if min_delay >= 0:
                    self.min_delay = min_delay
                    break
                else:
                    print(f"{Colors.RED}{Colors.BOLD}Min Delay must be >= 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}{Colors.BOLD}Invalid input. Enter a number.{Colors.RESET}")

        while True:
            try:
                max_delay = int(input(f"{Colors.GREEN}{Colors.BOLD}Max Delay Each Tx -> {Colors.RESET}").strip())
                if max_delay >= min_delay:
                    self.max_delay = max_delay
                    break
                else:
                    print(f"{Colors.RED}{Colors.BOLD}Min Delay must be >= Min Delay.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}{Colors.BOLD}Invalid input. Enter a number.{Colors.RESET}")

        while True:
            try:
                # Reordered options
                print(f"{Colors.WHITE}{Colors.BOLD}1. Run With Private Proxy{Colors.RESET}")
                print(f"{Colors.WHITE}{Colors.BOLD}2. Run Without Proxy{Colors.RESET}")
                print(f"{Colors.WHITE}{Colors.BOLD}3. Run With Free Proxyscrape Proxy{Colors.RESET}")
                choose = int(input(f"{Colors.BOLD}{Colors.BOLD}Choose [1/2/3] -> {Colors.RESET}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Private" if choose == 1 else 
                        "Without" if choose == 2 else 
                        "With Free Proxyscrape"
                    )
                    print(f"{Colors.GREEN}{Colors.BOLD}Run {proxy_type} Proxy Selected.{Colors.RESET}")
                    break
                else:
                    print(f"{Colors.RED}{Colors.BOLD}Please enter either 1, 2 or 3.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}{Colors.BOLD}Invalid input. Enter a number (1, 2 or 3).{Colors.RESET}")

        rotate = False
        # Proxy rotation only applicable for proxy options (1 and 3 in the new order)
        if choose in [1, 3]:
            while True:
                rotate = input(f"{Colors.BLUE}{Colors.BOLD}Rotate Invalid Proxy? [y/n] -> {Colors.RESET}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Colors.RED}{Colors.BOLD}Invalid input. Enter 'y' or 'n'.{Colors.RESET}")

        return choose, rotate
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=10)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            logger.error(
                f"Status  : Connection Not 200 OK - {str(e)}"
            )
            return None
            
    async def financial_portfolio_recommendation(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/investment/financial-portfolio-recommendation"
        data = json.dumps(self.generate_recommendation_payload(address))
        headers = {
            **self.HEADERS,
            "Authorization": self.auth_tokens[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def generate_change_transactions(self, address: str, change_tx: list, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/investment/generate-change-transactions"
        data = json.dumps(self.generate_transactions_payload(address, change_tx))
        headers = {
            **self.HEADERS,
            "Authorization": self.auth_tokens[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    await asyncio.sleep(5)
                    continue
                return None
        
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            logger.info(f"Proxy   : {proxy}")

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    continue

                return False
            
            return True
    
    async def process_perform_claim_faucet(self, account: str, address: str, use_proxy: bool):
        next_faucet_claim_time = await self.get_next_faucet_claim_time(address, use_proxy)
        if next_faucet_claim_time is not None:
            if int(time.time()) >= next_faucet_claim_time:
                tx_hash, block_number = await self.perform_claim_faucet(account, address, use_proxy)
                if tx_hash and block_number:
                    explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

                    logger.success(f" Status : Success")
                    logger.action(f" Tx Hash : {tx_hash}")
                    logger.actionSuccess(f" Explorer: {explorer}")
                
                else:
                    logger.error(f" Status : Perform On-Chain Failed")
            else:
                formatted_next_claim = datetime.fromtimestamp(next_faucet_claim_time).astimezone(wib).strftime("%x %X %Z")
                logger.warn(f" Status : Already Claimed - Next Claim at {formatted_next_claim}")

    async def process_perform_staking(self, account: str, address: str, use_proxy: bool):
        portfolio = await self.financial_portfolio_recommendation(address, use_proxy)
        if portfolio:
            change_tx = portfolio["data"]["changes"]

            tx_hash, block_number = await self.perform_staking(account, address, change_tx, use_proxy)
            if tx_hash and block_number:
                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

                logger.success(f" Status : Success")
                logger.action(f" Tx Hash : {tx_hash}")
                logger.actionSuccess(f" Explorer: {explorer}")
            
            else:
                logger.error(f" Status : Perform On-Chain Failed")
        else:
            logger.error(f" Status : GET Financial Portfolio Recommendation Failed")

    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                logger.error(f"Status  : Web3 Not Connected")
                return
            
            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")

            logger.step(f"Faucet :")

            await self.process_perform_claim_faucet(account, address, use_proxy)

            logger.step(f"Staking :")

            for i in range(self.staking_count):
                logger.action(
                    f" Stake {i+1} Of {self.staking_count}"
                )

                logger.info(f" Balance :")

                usdc_balance = await self.get_token_balance(address, self.USDC_CONTRACT_ADDRESS, use_proxy)
                logger.info(f" 1. {usdc_balance} USDC")
                usdt_balance = await self.get_token_balance(address, self.USDT_CONTRACT_ADDRESS, use_proxy)
                logger.info(f" 2. {usdt_balance} USDT")
                musd_balance = await self.get_token_balance(address, self.MUSD_CONTRACT_ADDRESS, use_proxy)
                logger.info(f" 3. {musd_balance} MockUSD")

                logger.info(f" Amount  :")
                logger.info(f" 1. {self.usdc_amount} USDC")
                logger.info(f" 2. {self.usdt_amount} USDT")
                logger.info(f" 3. {self.musd_amount} MockUSD")

                # The original logic had a bug here, checking usdt_balance and musd_balance against self.usdc_amount.
                # Assuming it should be against their respective amounts. Corrected below.
                if usdc_balance is None or usdc_balance < self.usdc_amount:
                    logger.warn(f" Status : Insufficient USDC Token Balance")
                    break

                if usdt_balance is None or usdt_balance < self.usdt_amount:
                    logger.warn(f" Status : Insufficient USDT Token Balance")
                    break

                if musd_balance is None or musd_balance < self.musd_amount:
                    logger.warn(f" Status : Insufficient MockUSD Token Balance")
                    break

                await self.process_perform_staking(account, address, use_proxy)
                # Only print timer if it's not the last stake
                if i < self.staking_count - 1:
                    await self.print_timer()
            
    async def main(self):
        try:
            with open("accounts.txt", "r") as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            await self.welcome()

            use_proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = False
                # Adjusted based on new ordering of proxy choices:
                # 1: Private Proxy, 2: No Proxy, 3: Free Proxyscrape
                if use_proxy_choice == 1 or use_proxy_choice == 3:
                    use_proxy = True

                clear_console()
                await self.welcome()
                logger.info(
                    f"Account's Total: {len(accounts)}"
                )

                if use_proxy:
                    # If free proxyscrape (choice 3) or private proxy (choice 1)
                    await self.load_proxies(use_proxy_choice)
                
                for account in accounts:
                    if account:
                        address = self.generate_address(account)

                        logger.step(f"[{self.mask_account(address)}]")

                        if not address:
                            logger.error(
                                f"Status : Invalid Private Key or Library Version Not Supported"
                            )
                            continue

                        self.auth_tokens[address] = self.generate_auth_token(address)
                        if not self.auth_tokens[address]:
                            logger.error(
                                f"Status  : Cryptography Library Version Not Supported"
                            )
                            continue

                        await self.process_accounts(account, address, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                # Removed the line with `========================================================================`
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    # Update on the same line, remove the extra text that was asked to be removed
                    print(
                        f"[ Wait for {formatted_time} ... ] | All Accounts Have Been Processed.",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1
                print(" " * 100, end="\r") # Clear the line after countdown

        except FileNotFoundError:
            logger.error(f"File 'accounts.txt' Not Found.")
            return
        except Exception as e:
            logger.error(f"Error: {e}")
            raise e

if __name__ == "__main__":
    init(autoreset=True)
    load_dotenv()
    try:
        bot = AutoStaking()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        logger.error("[ EXIT ] AutoStaking - BOT")
