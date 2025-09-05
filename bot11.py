from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from eth_utils import to_hex, to_bytes
import requests
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, random, json, os
import dotenv
from dotenv import load_dotenv

init(autoreset=True)
load_dotenv()

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
    print("  ║          Pharos Spout B O T            ║")
    print("  ║                                      ║")
    print(f"  ║     {Colors.YELLOW}{now.strftime('%H:%M:%S %d.%m.%Y')}{Colors.BRIGHT_GREEN}           ║")
    print("  ║                                      ║")
    print("  ║     Bot TESTNET AUTOMATION         ║")
    print(f"  ║   {Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}  |  t.me/ZonaAirdr0p   ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    await asyncio.sleep(1)

class Spout:
    def __init__(self) -> None:
        self.BASE_API = "https://www.spout.finance/api"
        self.RPC_URL = "https://testnet.dplabs-internal.com/"
        self.ZERO_CONTRACT_ADDRESS ="0x0000000000000000000000000000000000000000"
        self.USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
        self.SLQD_CONTRACT_ADDRESS = "0x54b753555853ce22f66Ac8CB8e324EB607C4e4eE"
        self.GATEWAY_ROUTER_ADDRESS = "0x126F0c11F3e5EafE37AB143D4AA688429ef7DCB3"
        self.FACTORY_ROUTER_ADDRESS = "0x18cB5F2774a80121d1067007933285B32516226a"
        self.ISSUER_ROUTER_ADDRESS = "0xA5C77b623BEB3bC0071fA568de99e15Ccc06C7cb"
        self.ORDERS_ROUTER_ADDRESS = "0x81b33972f8bdf14fD7968aC99CAc59BcaB7f4E9A"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]}
        ]''')
        self.SPOUT_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "getIdentity",
                "stateMutability": "view",
                "inputs": [
                    { "internalType": "address", "name": "_wallet", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "address", "name": "", "type": "address" }
                ]
            },
            {
                "type": "function",
                "name": "getClaimIdsByTopic",
                "stateMutability": "view",
                "inputs": [
                    { "internalType": "uint256", "name": "_topic", "type": "uint256" }
                ],
                "outputs": [
                    { "internalType": "bytes32[]", "name": "claimIds", "type": "bytes32[]" }
                ]
            },
            {
                "type": "function",
                "name": "deployIdentityForWallet",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "address", "name": "identityOwner", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "address", "name": "", "type": "address" }
                ]
            },
            {
                "type": "function",
                "name": "addClaim",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "_topic", "type": "uint256" },
                    { "internalType": "uint256", "name": "_scheme", "type": "uint256" },
                    { "internalType": "address", "name": "_issuer", "type": "address" },
                    { "internalType": "bytes", "name": "_signature", "type": "bytes" },
                    { "internalType": "bytes", "name": "_data", "type": "bytes" },
                    { "internalType": "string", "name": "_uri", "type": "string" }
                ],
                "outputs": [
                    { "internalType": "bytes32", "name": "claimRequestId", "type": "bytes32" }
                ]
            },
            {
                "type": "function",
                "name": "buyAsset",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "adfsFeedId", "type": "uint256" },
                    { "internalType": "string", "name": "ticker", "type": "string" },
                    { "internalType": "address", "name": "token", "type": "address" },
                    { "internalType": "uint256", "name": "usdcAmount", "type": "uint256" }
                ],
                "outputs": []
            },
            {
                "type": "function",
                "name": "sellAsset",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "adfsFeedId", "type": "uint256" },
                    { "internalType": "string", "name": "ticker", "type": "string" },
                    { "internalType": "address", "name": "token", "type": "address" },
                    { "internalType": "uint256", "name": "tokenAmount", "type": "uint256" }
                ],
                "outputs": []
            }
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        self.identity_address = {}
        self.trade_count = 0
        self.usdc_amount = 0
        self.slqd_amount = 0
        self.min_delay = 0
        self.max_delay = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {message}", flush=True)

    async def welcome(self):
        await display_welcome_screen()

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                logger.error(f"File {filename} Not Found.")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                logger.error("No Proxies Found.")
                return

            logger.info(f"Proxies Total: {len(self.proxies)}")
        
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
            logger.error(f" {str(e)} ")
            return None
        
    async def get_identity_address(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            factory_address = web3.to_checksum_address(self.FACTORY_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=factory_address, abi=self.SPOUT_CONTRACT_ABI)
            identity_address = token_contract.functions.getIdentity(address).call()

            return identity_address
        except Exception as e:
            logger.error(f" {str(e)} ")
            return None
        
    async def get_claim_ids(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            identity_address = web3.to_checksum_address(self.identity_address[address])
            token_contract = web3.eth.contract(address=identity_address, abi=self.SPOUT_CONTRACT_ABI)
            claim_ids = token_contract.functions.getClaimIdsByTopic(1).call()

            return claim_ids
        except Exception as e:
            logger.error(f" {str(e)} ")
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
                logger.warn(f" [Attempt {attempt + 1}] Send TX Error: {str(e)} ")
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
                logger.warn(f" [Attempt {attempt + 1}] Wait for Receipt Error: {str(e)} ")
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
    
    async def perform_deploy_identity(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.GATEWAY_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.SPOUT_CONTRACT_ABI)

            deploy_data = token_contract.functions.deployIdentityForWallet(address)

            identity_address = deploy_data.call({"from": address})
            estimated_gas = deploy_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            deploy_tx = deploy_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, deploy_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            self.used_nonce[address] += 1

            return tx_hash, identity_address
        except Exception as e:
            logger.error(f" {str(e)} ")
            return None, None
    
    async def perform_add_claim(self, account: str, address: str, signature: bytes, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.identity_address[address])
            token_contract = web3.eth.contract(address=contract_address, abi=self.SPOUT_CONTRACT_ABI)

            data = to_bytes(hexstr="0x6fdd523c9e64db4a7a67716a6b20d5da5ce39e3ee59b2ca281248b18087e860")

            add_claim_data = token_contract.functions.addClaim(1, 1, self.ISSUER_ROUTER_ADDRESS, signature, data, "")

            claim_id = add_claim_data.call({"from": address})
            estimated_gas = add_claim_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            add_claim_tx = add_claim_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, add_claim_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            self.used_nonce[address] += 1

            return tx_hash, to_hex(claim_id)
        except Exception as e:
            logger.error(f" {str(e)} ")
            return None, None
        
    async def approving_token(self, account: str, address: str, router_address: str, asset_address: str, amount: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            
            spender = web3.to_checksum_address(router_address)
            asset = web3.to_checksum_address(asset_address)
            token_contract = web3.eth.contract(address=asset, abi=self.ERC20_CONTRACT_ABI)

            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount:
                approve_data = token_contract.functions.approve(spender, amount)
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

                self.used_nonce[address] += 1

                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                
                logger.success(" Success ")
                logger.info(f" Tx Hash: {tx_hash} ")
                logger.info(f" Explorer: {explorer} ")
                await asyncio.sleep(5)

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
    
    async def perform_buy_asset(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            amount_to_wei = int(self.usdc_amount * (10**6))

            await self.approving_token(account, address, self.ORDERS_ROUTER_ADDRESS, self.USDC_CONTRACT_ADDRESS, amount_to_wei, use_proxy)

            contract_address = web3.to_checksum_address(self.ORDERS_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.SPOUT_CONTRACT_ABI)

            buy_data = token_contract.functions.buyAsset(2000002, "LQD", self.SLQD_CONTRACT_ADDRESS, amount_to_wei)

            estimated_gas = buy_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            buy_tx = buy_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, buy_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            self.used_nonce[address] += 1

            return tx_hash
        except Exception as e:
            logger.error(f" {str(e)} ")
            return None
        
    async def print_timer(self):
        delay = random.randint(self.min_delay, self.max_delay)
        for remaining in range(delay, 0, -1):
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {Colors.CYAN}[⟳] Wait For {remaining} Seconds For Next Tx...{Colors.RESET}", end="\r", flush=True)
            await asyncio.sleep(1)
        print(" " * 80, end="\r", flush=True)

    def print_buy_asset_question(self):
        while True:
            try:
                trade_count = int(input(f"{Colors.YELLOW}Enter Trade Count -> {Colors.RESET}").strip())
                if trade_count > 0:
                    self.trade_count = trade_count
                    break
                else:
                    print(f"{Colors.RED}Trade Count must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.{Colors.RESET}")
         
    def print_usdc_question(self):
        while True:
            try:
                usdc_amount = float(input(f"{Colors.YELLOW}Enter USDC Amount -> {Colors.RESET}").strip())
                if usdc_amount > 0:
                    self.usdc_amount = usdc_amount
                    break
                else:
                    print(f"{Colors.RED}Amount must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.{Colors.RESET}")

    def print_delay_question(self):
        while True:
            try:
                min_delay = int(input(f"{Colors.YELLOW}Min Delay Each Tx -> {Colors.RESET}").strip())
                if min_delay >= 0:
                    self.min_delay = min_delay
                    break
                else:
                    print(f"{Colors.RED}Min Delay must be >= 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a number.{Colors.RESET}")

        while True:
            try:
                max_delay = int(input(f"{Colors.YELLOW}Max Delay Each Tx -> {Colors.RESET}").strip())
                if max_delay >= min_delay:
                    self.max_delay = max_delay
                    break
                else:
                    print(f"{Colors.RED}Max Delay must be >= Min Delay.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a number.{Colors.RESET}")

    def print_question(self):
        self.print_buy_asset_question()
        self.print_usdc_question()
        self.print_delay_question()

        while True:
            try:
                print(f"{Colors.WHITE}1. Run With Proxy{Colors.RESET}")
                print(f"{Colors.WHITE}2. Run Without Proxy{Colors.RESET}")
                proxy_choice = int(input(f"{Colors.BLUE}Choose [1/2] -> {Colors.RESET}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Colors.GREEN}Run {proxy_type} Proxy Selected.{Colors.RESET}")
                    break
                else:
                    print(f"{Colors.RED}Please enter either 1 or 2.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a number (1 or 2).{Colors.RESET}")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Colors.BLUE}Rotate Invalid Proxy? [y/n] -> {Colors.RESET}").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Colors.RED}Invalid input. Enter 'y' or 'n'.{Colors.RESET}")

        return proxy_choice, rotate_proxy
    
    async def check_connection(self, proxy_url=None):
        url = "https://api.ipify.org?format=json"
        try:
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            response = await asyncio.to_thread(requests.get, url=url, proxies=proxies, timeout=30)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f" Connection Not 200 OK - {str(e)} ")
            return None
        
    async def kyc_signature(self, address: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/kyc-signature"
        data = json.dumps({
            "userAddress":address,
            "onchainIDAddress":self.identity_address[address],
            "claimData":"KYC passed",
            "topic":1,
            "countryCode":91
        })
        headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Origin": "https://www.spout.finance",
            "Referer": "https://www.spout.finance/app/profile?tab=kyc",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": FakeUserAgent().random
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxies=proxies, timeout=60)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries:
                    await asyncio.sleep(5)
                    continue
                logger.error(f" Fetch Signature Data Failed - {str(e)} ")
                return None
        
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            logger.info(f"Proxy: {proxy} ")

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    await asyncio.sleep(1)
                    continue

                return False
            
            return True
    
    async def process_perform_deploy_identity(self, account: str, address: str, use_proxy: bool):
        tx_hash, identity_address = await self.perform_deploy_identity(account, address, use_proxy)
        if tx_hash and identity_address:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            logger.success(" Success ")
            logger.info(f" Tx Hash: {tx_hash} ")
            logger.info(f" Explorer: {explorer} ")
            return identity_address
        
        else:
            logger.error(" Perform On-Chain Failed ")
            return False
    
    async def process_perform_add_claim(self, account: str, address: str, signature: bytes, use_proxy: bool):
        tx_hash, claim_id = await self.perform_add_claim(account, address, signature, use_proxy)
        if tx_hash and claim_id:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            logger.success(" Success ")
            logger.info(f" Tx Hash: {tx_hash} ")
            logger.info(f" Explorer: {explorer} ")
            return claim_id
        
        else:
            logger.error(" Perform On-Chain Failed ")
            return False
    
    async def process_perform_buy_asset(self, account: str, address: str, use_proxy: bool):
        tx_hash = await self.perform_buy_asset(account, address, use_proxy)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            logger.success(" Success ")
            logger.info(f" Tx Hash: {tx_hash} ")
            logger.info(f" Explorer: {explorer} ")
        else:
            logger.error(" Perform On-Chain Failed ")
    
    async def process_complete_kyc(self, account: str, address: str, use_proxy):
        logger.step("KYC Process")

        logger.action("Create Onchain Id")

        identity_address = await self.get_identity_address(address, use_proxy)
        if identity_address is None: return False

        if identity_address == self.ZERO_CONTRACT_ADDRESS:

            identity_address = await self.process_perform_deploy_identity(account, address, use_proxy)
            if not identity_address: return False

        else:
            logger.warn(" Already Created ")

        logger.info(f"Identity: {identity_address} ")

        self.identity_address[address] = identity_address

        logger.action("Verification With Signature")

        claim_ids = await self.get_claim_ids(address, use_proxy)
        if claim_ids is None: return False

        if len(claim_ids) == 0:
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None

            sign = await self.kyc_signature(address, proxy_url)
            if not sign: return False

            r = int(sign["signature"]["r"], 16)
            s = int(sign["signature"]["s"], 16)
            v = sign["signature"]["v"]

            signature = to_bytes(r) + to_bytes(s) + to_bytes(v)

            claim_id = await self.process_perform_add_claim(account, address, signature, use_proxy)
            if not claim_id: return False

        else:
            claim_id = to_hex(claim_ids[0])
            logger.warn(" Already Verified ")

        logger.info(f"Claim Id: {claim_id} ")

        return True
    
    async def process_trade_buy_asset(self, account: str, address: str, use_proxy: bool):
        logger.action("Buy Asset")

        for i in range(self.trade_count):
            logger.step(f"Buy {i+1} Of {self.trade_count}")

            logger.info(" Pair: USDC to SLQD ")
            logger.info(f" Amount: {self.usdc_amount} ")

            balance = await self.get_token_balance(address, self.USDC_CONTRACT_ADDRESS, use_proxy)

            logger.info(f" Balance: {balance} USDC ")

            if balance is None:
                logger.error(" Fetch USDC Token Balance Failed ")
                continue

            if balance < self.usdc_amount:
                logger.warn(" Insufficient USDC Token Balance ")
                return

            await self.process_perform_buy_asset(account, address, use_proxy)
            await self.print_timer()

    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            
            try:
                web3 = await self.get_web3_with_check(address, use_proxy)
            except Exception as e:
                logger.error(f" Web3 Not Connected - {str(e)} ")
                return
            
            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")
            
            is_verifed = await self.process_complete_kyc(account, address, use_proxy)
            if is_verifed:
                await self.process_trade_buy_asset(account, address, use_proxy)

    async def main(self):
        try:
            await self.welcome()
            
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = True if proxy_choice == 1 else False

                self.clear_terminal()
                await self.welcome()
                logger.info(f"Account's Total: {len(accounts)}")

                if use_proxy:
                    await self.load_proxies()
                
                for account in accounts:
                    if account:
                        address = self.generate_address(account)

                        logger.step(f"Processing Account: {self.mask_account(address)}")

                        if not address:
                            logger.error(" Invalid Private Key or Library Version Not Supported ")
                            continue

                        await self.process_accounts(account, address, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                logger.info("All accounts have been processed. Waiting for 24 hours before restarting...")
                await asyncio.sleep(24 * 60 * 60)

        except FileNotFoundError:
            logger.error("File 'accounts.txt' Not Found.")
            return
        except Exception as e:
            logger.error(f"Error: {e}")
            raise e

if __name__ == "__main__":
    try:
        bot = Spout()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {Colors.RED}[ EXIT ] Spout Finance - BOT{Colors.RESET}")
