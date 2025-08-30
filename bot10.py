from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from datetime import datetime
from colorama import *
import asyncio, random, json, re, os
from dotenv import load_dotenv

# Initialize colorama with autoreset
init(autoreset=True)
load_dotenv()

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
    print("  ║              B O T                   ║")
    print("  ║                                      ║")
    print(f"  ║     {Colors.YELLOW}{now.strftime('%H:%M:%S %d.%m.%Y')}{Colors.BRIGHT_GREEN}           ║")
    print("  ║                                      ║")
    print("  ║     Bot TESTNET AUTOMATION           ║")
    print(f"  ║   {Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}  |  t.me/ZonaAirdr0p   ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    await asyncio.sleep(1)

class R2:
    def __init__(self) -> None:
        self.RPC_URL = "https://testnet.dplabs-internal.com/"
        self.USDC_CONTRACT_ADDRESS = "0x8bebfcbe5468f146533c182df3dfbf5ff9be00e2"
        self.R2USD_CONTRACT_ADDRESS = "0x4f5b54d4AF2568cefafA73bB062e5d734b55AA05"
        self.sR2USD_CONTRACT_ADDRESS = "0xF8694d25947A0097CB2cea2Fc07b071Bdf72e1f8"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]}
        ]''')
        self.R2_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "mint",
                "inputs": [
                    { "name": "to", "type": "address", "internalType": "address" },
                    { "name": "value", "type": "uint256", "internalType": "uint256" },
                    {
                        "name": "permit",
                        "type": "tuple",
                        "internalType": "struct R2USD.PermitData",
                        "components": [
                            { "name": "value", "type": "uint256", "internalType": "uint256" },
                            { "name": "deadline", "type": "uint256", "internalType": "uint256" },
                            { "name": "v", "type": "uint8", "internalType": "uint8" },
                            { "name": "r", "type": "bytes32", "internalType": "bytes32" },
                            { "name": "s", "type": "bytes32", "internalType": "bytes32" }
                        ]
                    }
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            },
            {
                "type": "function",
                "name": "burn",
                "inputs": [
                    { "name": "to", "type": "address", "internalType": "address" },
                    { "name": "value", "type": "uint256", "internalType": "uint256" }
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            },
            {
                "type": "function",
                "name": "stake",
                "inputs": [
                    { "name": "r2USDValue", "type": "uint256", "internalType": "uint256" }, 
                    {
                        "name": "permit",
                        "type": "tuple",
                        "internalType": "struct SR2USDTestnet.PermitData",
                        "components": [
                            { "name": "value", "type": "uint256", "internalType": "uint256" }, 
                            { "name": "deadline", "type": "uint256", "internalType": "uint256" }, 
                            { "name": "v", "type": "uint8", "internalType": "uint8" }, 
                            { "name": "r", "type": "bytes32", "internalType": "bytes32" }, 
                            { "name": "s", "type": "bytes32", "internalType": "bytes32" }
                        ]
                    }
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            },
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        self.swap_option = 0
        self.earn_option = 0
        self.swap_count = 0
        self.earn_count = 0
        self.usdc_swap_amount = 0
        self.r2usd_swap_amount = 0
        self.r2usd_earn_amount = 0
        self.min_delay = 0
        self.max_delay = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {message}")

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

            logger.success(f"Proxies Total: {len(self.proxies)}")
        
        except Exception as e:
            logger.error(f"Failed To Load Proxies: {e}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
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
            logger.error(f"Generate Address Failed - {str(e)}")
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None
        
    def generate_swap_option(self):
        buy = {
            "pair": "USDC to R2USD",
            "ticker": "USDC",
            "amount": self.usdc_swap_amount,
            "asset": self.USDC_CONTRACT_ADDRESS,
        }

        sell = {
            "pair": "R2USD to USDC",
            "ticker": "R2USD",
            "amount": self.r2usd_swap_amount,
            "asset": self.R2USD_CONTRACT_ADDRESS,
        }

        if self.swap_option == 1:
            return buy

        elif self.swap_option == 2:
            return sell

        elif self.swap_option == 3:
            return random.choice([buy, sell])
        
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

            token_balance = balance / (10 ** 6)

            return token_balance
        except Exception as e:
            logger.error(f"{str(e)}")
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
                logger.warn(f"[Attempt {attempt + 1}] Send TX Error: {str(e)}")
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
                logger.warn(f"[Attempt {attempt + 1}] Wait for Receipt Error: {str(e)}")
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
        
    async def approving_token(self, account: str, address: str, router_address: str, asset_address: str, required: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            
            spender = web3.to_checksum_address(router_address)
            asset = web3.to_checksum_address(asset_address)
            token_contract = web3.eth.contract(address=asset, abi=self.ERC20_CONTRACT_ABI)

            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < required:
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

                self.used_nonce[address] += 1

                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                
                logger.success("Approve Success")
                logger.info(f"Tx Hash: {tx_hash}")
                logger.info(f"Explorer: {explorer}")
                await self.print_timer()

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
        
    async def perform_mint(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            amount_to_wei = int(self.usdc_swap_amount * (10 ** 6))

            await self.approving_token(
                account, address, self.R2USD_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, amount_to_wei, use_proxy
            )

            permit = (0, 0, 0, b'\x00' * 32, b'\x00' * 32)

            token_address = web3.to_checksum_address(self.R2USD_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=token_address, abi=self.R2_CONTRACT_ABI)

            mint_data = token_contract.functions.mint(address, amount_to_wei, permit)
            estimated_gas = mint_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            mint_tx = mint_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, mint_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            self.used_nonce[address] += 1

            return tx_hash
        except Exception as e:
            logger.error(f"{str(e)}")
            return None
        
    async def perform_burn(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            amount_to_wei = int(self.r2usd_swap_amount * (10 ** 6))

            token_address = web3.to_checksum_address(self.R2USD_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=token_address, abi=self.R2_CONTRACT_ABI)

            burn_data = token_contract.functions.burn(address, amount_to_wei)
            estimated_gas = burn_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            burn_tx = burn_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, burn_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            self.used_nonce[address] += 1

            return tx_hash
        except Exception as e:
            logger.error(f"{str(e)}")
            return None
        
    async def perform_stake(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            amount_to_wei = int(self.r2usd_earn_amount * (10 ** 6))

            await self.approving_token(
                account, address, self.sR2USD_CONTRACT_ADDRESS, self.R2USD_CONTRACT_ADDRESS, amount_to_wei, use_proxy
            )

            permit = (0, 0, 0, b'\x00' * 32, b'\x00' * 32)

            token_address = web3.to_checksum_address(self.sR2USD_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=token_address, abi=self.R2_CONTRACT_ABI)

            stake_data = token_contract.functions.stake(amount_to_wei, permit)
            estimated_gas = stake_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            stake_tx = stake_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, stake_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            self.used_nonce[address] += 1

            return tx_hash
        except Exception as e:
            logger.error(f"{str(e)}")
            return None
        
    async def print_timer(self):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(
                f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} "
                f"{Colors.CYAN}Wait For {remaining} Seconds For Next Tx...",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)
        print(" " * 80, end="\r", flush=True)  # Clear the line

    def print_swap_count(self):
        while True:
            try:
                swap_count = int(input(f"{Colors.YELLOW}Enter Swap Count -> ").strip())
                if swap_count > 0:
                    self.swap_count = swap_count
                    break
                else:
                    print(f"{Colors.RED}Swap Count must be greater than 0.")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.")
    
    def print_earn_count(self):
        while True:
            try:
                earn_count = int(input(f"{Colors.YELLOW}Enter Earn Count -> ").strip())
                if earn_count > 0:
                    self.earn_count = earn_count
                    break
                else:
                    print(f"{Colors.RED}Earn Count must be greater than 0.")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.")

    def print_usdc_swap_amount(self):
        while True:
            try:
                usdc_swap_amount = float(input(f"{Colors.YELLOW}Enter Swap Amount [USDC] -> ").strip())
                if usdc_swap_amount > 0:
                    self.usdc_swap_amount = usdc_swap_amount
                    break
                else:
                    print(f"{Colors.RED}Swap Amount must be greater than 0.")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.")
    
    def print_r2usd_swap_amount(self):
        while True:
            try:
                r2usd_swap_amount = float(input(f"{Colors.YELLOW}Enter Swap Amount [R2USD] -> ").strip())
                if r2usd_swap_amount > 0:
                    self.r2usd_swap_amount = r2usd_swap_amount
                    break
                else:
                    print(f"{Colors.RED}Swap Amount must be greater than 0.")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.")
    
    def print_r2usd_earn_amount(self):
        while True:
            try:
                r2usd_earn_amount = float(input(f"{Colors.YELLOW}Enter Earn Amount [R2USD] -> ").strip())
                if r2usd_earn_amount > 0:
                    self.r2usd_earn_amount = r2usd_earn_amount
                    break
                else:
                    print(f"{Colors.RED}Earn Amount must be greater than 0.")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.")
    
    def print_delay_question(self):
        while True:
            try:
                min_delay = int(input(f"{Colors.YELLOW}Min Delay Each Tx -> ").strip())
                if min_delay >= 0:
                    self.min_delay = min_delay
                    break
                else:
                    print(f"{Colors.RED}Min Delay must be >= 0.")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a number.")

        while True:
            try:
                max_delay = int(input(f"{Colors.YELLOW}Max Delay Each Tx -> ").strip())
                if max_delay >= min_delay:
                    self.max_delay = max_delay
                    break
                else:
                    print(f"{Colors.RED}Min Delay must be >= Min Delay.")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a number.")
        
    def print_swap_question(self):
        while True:
            try:
                print(f"{Colors.GREEN}Select Option:")
                print(f"{Colors.WHITE}1. Buy -> USDC to R2USD")
                print(f"{Colors.WHITE}2. Sell -> R2USD to USDC")
                print(f"{Colors.WHITE}3. Random Swap")
                option = int(input(f"{Colors.CYAN}Choose [1/2/3] -> ").strip())

                if option in [1, 2, 3]:
                    option_type = (
                        "Buy -> USDC to R2USD" if option == 1 else 
                        "Sell -> R2USD to USDC" if option == 2 else 
                        "Random Swap"
                    )
                    print(f"{Colors.GREEN}{option_type} Selected.")
                    self.swap_option = option
                    self.print_swap_count()
                    if self.swap_option in [1, 3]:
                        self.print_usdc_swap_amount()
                    if self.swap_option in [2, 3]:
                        self.print_r2usd_swap_amount()
                    break
                else:
                    print(f"{Colors.RED}Please enter either 1, 2, or 3.")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a number (1, 2, or 3).")
    
    def print_question(self):
        while True:
            try:
                print(f"{Colors.GREEN}Select Option:")
                print(f"{Colors.WHITE}1. R2 Swap")
                print(f"{Colors.WHITE}2. R2 Earn")
                print(f"{Colors.WHITE}3. Run All Features")
                option = int(input(f"{Colors.CYAN}Choose [1/2/3 -> ").strip())

                if option in [1, 2, 3]:
                    option_type = (
                        "R2 Swap" if option == 1 else 
                        "R2 Earn" if option == 2 else 
                        "Run All Features"
                    )
                    print(f"{Colors.GREEN}{option_type} Selected.")
                    break
                else:
                    print(f"{Colors.RED}Please enter either 1, 2, or 3.")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a number (1, 2, or 3).")

        if option == 1:
            self.print_swap_question()
            self.print_delay_question()

        elif option == 2:
            self.print_earn_count()
            self.print_r2usd_earn_amount()
            self.print_delay_question()

        elif option == 3:
            self.print_swap_question()
            self.print_earn_count()
            self.print_r2usd_earn_amount()
            self.print_delay_question()

        while True:
            try:
                print(f"{Colors.WHITE}1. Run With Proxy")
                print(f"{Colors.WHITE}2. Run Without Proxy")
                proxy_choice = int(input(f"{Colors.CYAN}Choose [1/2] -> ").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Colors.GREEN}Run {proxy_type} Proxy Selected.")
                    break
                else:
                    print(f"{Colors.RED}Please enter either 1 or 2.")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a number (1 or 2).")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Colors.CYAN}Rotate Invalid Proxy? [y/n] -> ").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Colors.RED}Invalid input. Enter 'y' or 'n'.")

        return option, proxy_choice, rotate_proxy
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            logger.error(f"Connection Not 200 OK - {str(e)}")
            return None
        
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            logger.info(f"Proxy: {proxy}")

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    await asyncio.sleep(1)
                    continue

                return False
            
            return True
    
    async def process_perform_mint(self, account: str, address: str, use_proxy: bool):
        tx_hash = await self.perform_mint(account, address, use_proxy)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            logger.success("Mint Success")
            logger.info(f"Tx Hash: {tx_hash}")
            logger.info(f"Explorer: {explorer}")
        else:
            logger.error("Perform On-Chain Failed")
    
    async def process_perform_burn(self, account: str, address: str, use_proxy: bool):
        tx_hash = await self.perform_burn(account, address, use_proxy)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            logger.success("Burn Success")
            logger.info(f"Tx Hash: {tx_hash}")
            logger.info(f"Explorer: {explorer}")
        else:
            logger.error("Perform On-Chain Failed")
    
    async def process_perform_stake(self, account: str, address: str, use_proxy: bool):
        tx_hash = await self.perform_stake(account, address, use_proxy)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            logger.success("Stake Success")
            logger.info(f"Tx Hash: {tx_hash}")
            logger.info(f"Explorer: {explorer}")
        else:
            logger.error("Perform On-Chain Failed")

    async def process_option_1(self, account: str, address: str, use_proxy: bool):
        logger.info("R2 Swap")

        for i in range(self.swap_count):
            logger.step(f"Swap {i+1} Of {self.swap_count}")

            option = self.generate_swap_option()
            pair = option["pair"]
            ticker = option["ticker"]
            amount = option["amount"]
            asset = option["asset"]

            logger.info(f"Option: {pair}")
            logger.info(f"Amount: {amount} {ticker}")

            balance = await self.get_token_balance(address, asset, use_proxy)

            logger.info(f"Balance: {balance} {ticker}")

            if balance is None:
                logger.error(f"Fetch {ticker} Token Balance Failed")
                continue
            
            if balance < amount:
                logger.error(f"Insufficient {ticker} Token Balance")
                return

            if pair == "USDC to R2USD":
                await self.process_perform_mint(account, address, use_proxy)

            elif pair == "R2USD to USDC":
                await self.process_perform_burn(account, address, use_proxy)

            await self.print_timer()

    async def process_option_2(self, account: str, address: str, use_proxy: bool):
        logger.info("R2 Earn")

        for i in range(self.earn_count):
            logger.step(f"Earn {i+1} Of {self.earn_count}")

            logger.info("Option: R2USD to sR2USD")
            logger.info(f"Amount: {self.r2usd_earn_amount} R2USD")

            balance = await self.get_token_balance(address, self.R2USD_CONTRACT_ADDRESS, use_proxy)

            logger.info(f"Balance: {balance} R2USD")

            if balance is None:
                logger.error("Fetch R2USD Token Balance Failed")
                continue
            
            if balance < self.r2usd_earn_amount:
                logger.error("Insufficient R2USD Token Balance")
                return

            await self.process_perform_stake(account, address, use_proxy)
            await self.print_timer()

    async def process_accounts(self, account: str, address: str, option: int, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            
            try:
                web3 = await self.get_web3_with_check(address, use_proxy)
            except Exception as e:
                logger.error(f"Web3 Not Connected - {str(e)}")
                return
            
            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")

            if option == 1:
                logger.info("Option: R2 Swap")
                await self.process_option_1(account, address, use_proxy)

            elif option == 2:
                logger.info("Option: R2 Earn")
                await self.process_option_2(account, address, use_proxy)

            elif option == 3:
                logger.info("Option: Run All Features")
                await self.process_option_1(account, address, use_proxy)
                await self.process_option_2(account, address, use_proxy)

    async def main(self):
        try:
            await display_welcome_screen()
            
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            option, proxy_choice, rotate_proxy = self.print_question()

            use_proxy = True if proxy_choice == 1 else False

            while True:
                self.clear_terminal()
                logger.info(f"Account's Total: {len(accounts)}")

                if use_proxy:
                    await self.load_proxies()
                
                for account in accounts:
                    if account:
                        address = self.generate_address(account)

                        logger.info(f"Processing: {self.mask_account(address)}")

                        if not address:
                            logger.error("Invalid Private Key or Library Version Not Supported")
                            continue

                        await self.process_accounts(account, address, option, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(
                        f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} "
                        f"{Colors.CYAN}Next cycle in: {formatted_time}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)
                    seconds -= 1
                print(" " * 80, end="\r", flush=True)  # Clear the line

        except FileNotFoundError:
            logger.error("File 'accounts.txt' Not Found.")
            return
        except Exception as e:
            logger.error(f"Error: {e}")
            raise e

if __name__ == "__main__":
    try:
        bot = R2()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {Colors.RED}[ EXIT ] R2 Pharos - BOT")