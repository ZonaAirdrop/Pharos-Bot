from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, random, json, re, os, pytz
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
    BRIGHT_GREEN = Fore.LIGHTGREEN_EX
    BRIGHT_MAGENTA = Fore.LIGHTMAGENTA_EX
    BRIGHT_WHITE = Fore.LIGHTWHITE_EX
    BRIGHT_BLACK = Fore.LIGHTBLACK_EX
    BLUE = Fore.BLUE

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
    print("  ║           Brokex  B O T            ║")
    print("  ║                                      ║")
    print(f"  ║      {Colors.YELLOW}{now.strftime('%H:%M:%S %d.%m.%Y')}{Colors.BRIGHT_GREEN}          ║")
    print("  ║                                      ║")
    print("  ║      PHAROS TESTNET AUTOMATION        ║")
    print(f"  ║   {Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}  |  t.me/ZonaAirdr0p   ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    await asyncio.sleep(1)


wib = pytz.timezone('Asia/Jakarta')

class Brokex:
    def __init__(self) -> None:
        self.HEADERS = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://app.brokex.trade",
            "Referer": "https://app.brokex.trade/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://proofcrypto-production.up.railway.app"
        self.RPC_URL = "https://api.zan.top/node/v1/pharos/testnet/54b49326c9f44b6e8730dc5dd4348421"
        self.USDT_CONTRACT_ADDRESS = "0x78ac5e2d8a78a8b8e6d10c7b7274b03c10c91cef"
        self.CLAIM_ROUTER_ADDRESS = "0x50576285BD33261DEe1aD99BF766CD8249520a58"
        self.TRADE_ROUTER_ADDRESS = "0xDe897635870b3Dd2e097C09f1cd08841DBc3976a"
        self.POOL_ROUTER_ADDRESS = "0x9A88d07850723267DB386C681646217Af7e220d7"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"hasClaimed","stateMutability":"view","inputs":[{"internalType":"address","name":"","type":"address"}],"outputs":[{"internalType":"bool","name":"","type":"bool"}]},
            {"type":"function","name":"claim","stateMutability":"nonpayable","inputs":[],"outputs":[]}
        ]''')
        self.BROKEX_CONTRACT_ABI = [
            {
                "name": "openPosition",
                "type": "function",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "idx", "type": "uint256" },
                    { "internalType": "bytes",   "name": "proof", "type": "bytes" },
                    { "internalType": "bool",    "name": "isLong", "type": "bool" },
                    { "internalType": "uint256", "name": "lev", "type": "uint256" },
                    { "internalType": "uint256", "name": "size", "type": "uint256" },
                    { "internalType": "uint256", "name": "sl", "type": "uint256" },
                    { "internalType": "uint256", "name": "tp", "type": "uint256" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ]
            },
            {
                "name": "depositLiquidity",
                "type": "function",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "usdtAmount", "type": "uint256" }
                ],
                "outputs": []
            },
            {
                "name": "balanceOf",
                "type": "function",
                "stateMutability": "view",
                "inputs": [
                    { "internalType": "address", "name": "account", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ],
            },
            {
                "name": "withdrawLiquidity",
                "type": "function",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "lpAmount", "type":"uint256" }
                ],
                "outputs": []
            }
        ]
        self.pairs = [
            { "name": "BTC_USDT", "desimal": 0 },
            { "name": "ETH_USDT", "desimal": 1 },
            { "name": "SOL_USDT", "desimal": 10 },
            { "name": "XRP_USDT", "desimal": 14 },
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        self.trade_count = 0
        self.trade_amount = 0
        self.deposit_lp_count = 0
        self.deposit_lp_amount = 0
        self.withdraw_lp_count = 0
        self.withdraw_lp_amount = 0
        self.lp_option = 0
        self.min_delay = 0
        self.max_delay = 0

    def log(self, message):
        logger.info(message)

    def clear_terminal(self):
        clear_console()

    def welcome(self):
        # This will be replaced by display_welcome_screen
        pass

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1: # Now corresponds to private proxy
                if not os.path.exists(filename):
                    self.log(f"{Colors.RED + Colors.BOLD}File {filename} Not Found.{Colors.RESET}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]

            if not self.proxies and use_proxy_choice == 1: # Only for private proxy option
                self.log(f"{Colors.RED + Colors.BOLD}No Proxies Found.{Colors.RESET}")
                return

            if self.proxies:
                self.log(
                    f"{Colors.GREEN + Colors.BOLD}Proxies Total  : {Colors.RESET}"
                    f"{Colors.WHITE + Colors.BOLD}{len(self.proxies)}{Colors.RESET}"
                )

        except Exception as e:
            self.log(f"{Colors.RED + Colors.BOLD}Failed To Load Proxies: {e}{Colors.RESET}")
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

            if contract_address == "PHRS":
                balance = web3.eth.get_balance(address)
                decimals = 18
            else:
                token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
                balance = token_contract.functions.balanceOf(address).call()
                decimals = token_contract.functions.decimals().call()

            token_balance = balance / (10 ** decimals)

            return token_balance
        except Exception as e:
            logger.error(f"Message: {str(e)}")
            return None

    async def get_lp_balance(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.POOL_ROUTER_ADDRESS), abi=self.BROKEX_CONTRACT_ABI)
            balance = token_contract.functions.balanceOf(address).call()

            lp_balance = balance / (10 ** 18)

            return lp_balance
        except Exception as e:
            logger.error(f"Message: {str(e)}")
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
                pass
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
                pass
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")

    async def check_faucet_status(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.CLAIM_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)
            claim_data = token_contract.functions.hasClaimed(web3.to_checksum_address(address)).call()

            return claim_data
        except Exception as e:
            logger.error(f"Message: {str(e)}")
            return None

    async def perform_claim_faucet(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.CLAIM_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            claim_data = token_contract.functions.claim()
            estimated_gas = claim_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            claim_tx = claim_data.build_transaction({
                "from": address,
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
            logger.error(f"Message: {str(e)}")
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

                logger.success(f"Approve: Success")
                logger.info(f"Block: {block_number}")
                logger.action(f"Tx Hash: {tx_hash}")
                logger.actionSuccess(f"Explorer: {explorer}")
                await asyncio.sleep(5)

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")

    async def perform_trade(self, account: str, address: str, pair: int, is_long: bool, use_proxy: bool, lev=1, sl=0, tp=0):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            asset_address = web3.to_checksum_address(self.USDT_CONTRACT_ADDRESS)
            asset_contract = web3.eth.contract(address=web3.to_checksum_address(asset_address), abi=self.ERC20_CONTRACT_ABI)
            decimals = asset_contract.functions.decimals().call()

            trade_amount = int(self.trade_amount * (10 ** decimals))

            await self.approving_token(account, address, self.TRADE_ROUTER_ADDRESS, asset_address, trade_amount, use_proxy)

            proof = await self.get_proof(address, pair, use_proxy)
            if not proof:
                raise Exception("Failed to Fetch Proof")

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.TRADE_ROUTER_ADDRESS), abi=self.BROKEX_CONTRACT_ABI)

            position_data = token_contract.functions.openPosition(pair, proof['proof'], is_long, lev, trade_amount, sl, tp)
            estimated_gas = position_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            position_tx = position_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, position_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            logger.error(f"Message: {str(e)}")
            return None, None

    async def perform_deposit_lp(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            asset_address = web3.to_checksum_address(self.USDT_CONTRACT_ADDRESS)
            asset_contract = web3.eth.contract(address=web3.to_checksum_address(asset_address), abi=self.ERC20_CONTRACT_ABI)
            decimals = asset_contract.functions.decimals().call()

            deposit_lp_amount = int(self.deposit_lp_amount * (10 ** decimals))

            await self.approving_token(account, address, self.POOL_ROUTER_ADDRESS, asset_address, deposit_lp_amount, use_proxy)

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.POOL_ROUTER_ADDRESS), abi=self.BROKEX_CONTRACT_ABI)

            lp_data = token_contract.functions.depositLiquidity(deposit_lp_amount)
            estimated_gas = lp_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            lp_tx = lp_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, lp_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            logger.error(f"Message: {str(e)}")
            return None, None

    async def perform_withdraw_lp(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            withdraw_lp_amount = int(self.withdraw_lp_amount * (10 ** 18))

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.POOL_ROUTER_ADDRESS), abi=self.BROKEX_CONTRACT_ABI)

            lp_data = token_contract.functions.withdrawLiquidity(withdraw_lp_amount)
            estimated_gas = lp_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            lp_tx = lp_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, lp_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            logger.error(f"Message: {str(e)}")
            return None, None

    async def print_timer(self):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            print(
                f"{Colors.BRIGHT_BLACK}[ {datetime.now().astimezone(wib).strftime('%H:%M:%S')} ]{Colors.RESET} {Colors.CYAN}[⟳] "
                f"{Colors.BLUE + Colors.BOLD}Wait For {remaining} Seconds For Next Tx...{Colors.RESET}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

    def print_trade_question(self):
        while True:
            try:
                trade_count = int(input(f"{Colors.YELLOW + Colors.BOLD}Trade Count For Each Wallet -> {Colors.RESET}").strip())
                if trade_count > 0:
                    self.trade_count = trade_count
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Trade Count must be > 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a number.{Colors.RESET}")

        while True:
            try:
                trade_amount = float(input(f"{Colors.YELLOW + Colors.BOLD}Enter Trade Amount [Min 10] -> {Colors.RESET}").strip())
                if trade_amount >= 10:
                    self.trade_amount = trade_amount
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Trade Amount must be >= 10.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a float or decimal number.{Colors.RESET}")

    def print_lp_option_question(self):
        while True:
            try:
                print(f"{Colors.GREEN + Colors.BOLD}Choose LP Option:{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}1. Deposit Liquidity{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}2. Withdraw Liquidity{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}3. Skipped{Colors.RESET}")
                option = int(input(f"{Colors.BLUE + Colors.BOLD}Choose [1/2/3] -> {Colors.RESET}").strip())

                if option in [1, 2, 3]:
                    option_type = (
                        "Deposit Liquidity" if option == 1 else
                        "Withdraw Liquidity" if option == 2 else
                        "Skipped"
                    )
                    logger.success(f"{option_type} Selected.")

                    if option == 1:
                        self.print_deposit_lp_question()

                    elif option == 2:
                        self.print_withdraw_lp_question()

                    self.lp_option = option
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Please enter either 1, 2, or 3.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a number (1, 2, or 3).{Colors.RESET}")

    def print_deposit_lp_question(self):
        while True:
            try:
                deposit_lp_count = int(input(f"{Colors.YELLOW + Colors.BOLD}Deposit Liquidity Count For Each Wallet -> {Colors.RESET}").strip())
                if deposit_lp_count > 0:
                    self.deposit_lp_count = deposit_lp_count
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Deposit Liquidity Count must be > 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a number.{Colors.RESET}")

        while True:
            try:
                deposit_lp_amount = float(input(f"{Colors.YELLOW + Colors.BOLD}Enter Deposit Liquidity Amount -> {Colors.RESET}").strip())
                if deposit_lp_amount > 0:
                    self.deposit_lp_amount = deposit_lp_amount
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Deposit Liquidity Amount must be > 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a float or decimal number.{Colors.RESET}")

    def print_withdraw_lp_question(self):
        while True:
            try:
                withdraw_lp_count = int(input(f"{Colors.YELLOW + Colors.BOLD}Withdraw Liquidity Count For Each Wallet -> {Colors.RESET}").strip())
                if withdraw_lp_count > 0:
                    self.withdraw_lp_count = withdraw_lp_count
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Withdraw Liquidity Count must be > 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a number.{Colors.RESET}")

        while True:
            try:
                withdraw_lp_amount = float(input(f"{Colors.YELLOW + Colors.BOLD}Enter Withdraw Liquidity Amount -> {Colors.RESET}").strip())
                if withdraw_lp_amount > 0:
                    self.withdraw_lp_amount = withdraw_lp_amount
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Withdraw Liquidity Amount must be > 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a float or decimal number.{Colors.RESET}")

    def print_delay_question(self):
        while True:
            try:
                min_delay = int(input(f"{Colors.YELLOW + Colors.BOLD}Min Delay For Each Tx -> {Colors.RESET}").strip())
                if min_delay >= 0:
                    self.min_delay = min_delay
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Min Delay must be >= 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a number.{Colors.RESET}")

        while True:
            try:
                max_delay = int(input(f"{Colors.YELLOW + Colors.BOLD}Max Delay For Each Tx -> {Colors.RESET}").strip())
                if max_delay >= min_delay:
                    self.max_delay = max_delay
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Max Delay must be >= Min Delay.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a number.{Colors.RESET}")

    def print_question(self):
        while True:
            try:
                print(f"{Colors.GREEN + Colors.BOLD}Select Option:{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}1. Claim Faucet{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}2. Random Trade{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}3. Deposit Liquidity{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}4. Withdraw Liquidity{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}5. Run All Features{Colors.RESET}")
                option = int(input(f"{Colors.BLUE + Colors.BOLD}Choose [1/2/3/4/5] -> {Colors.RESET}").strip())

                if option in [1, 2, 3, 4, 5]:
                    option_type = (
                        "Claim Faucet" if option == 1 else
                        "Random Trade" if option == 2 else
                        "Deposit Liquidity" if option == 3 else
                        "Withdraw Liquidity" if option == 4 else
                        "Run All Features"
                    )
                    logger.success(f"{option_type} Selected.")
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Please enter either 1, 2, 3, 4, or 5.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a number (1, 2, 3, 4, or 5).{Colors.RESET}")

        if option == 2:
            self.print_trade_question()
            self.print_delay_question()

        elif option == 3:
            self.print_deposit_lp_question()
            self.print_delay_question()

        elif option == 4:
            self.print_withdraw_lp_question()
            self.print_delay_question()

        elif option == 5:
            self.print_trade_question()
            self.print_lp_option_question()
            self.print_delay_question()

        while True:
            try:
                print(f"{Colors.WHITE + Colors.BOLD}1. Run With Private Proxy{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}2. Run Without Proxy{Colors.RESET}")
                choose = int(input(f"{Colors.BLUE + Colors.BOLD}Choose [1/2] -> {Colors.RESET}").strip())

                if choose in [1, 2]:
                    proxy_type = (
                        "With Private" if choose == 1 else
                        "Without"
                    )
                    logger.success(f"Run {proxy_type} Proxy Selected.")
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Please enter either 1 or 2.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a number (1 or 2).{Colors.RESET}")

        rotate = False
        if choose == 1: # Only ask for rotation if private proxy is selected
            while True:
                rotate = input(f"{Colors.BLUE + Colors.BOLD}Rotate Invalid Proxy? [y/n] -> {Colors.RESET}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter 'y' or 'n'.{Colors.RESET}")

        return option, choose, rotate

    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=10)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            logger.error(f"Status: Connection Not 200 OK - {str(e)}")
            return None

    async def get_proof(self, address: str, pair: int, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/proof?pairs={pair}"
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=self.HEADERS, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    await asyncio.sleep(5)
                    continue
                return None

    async def process_check_connection(self, address: int, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            logger.info(f"Proxy: {proxy}")

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    continue

                return False

            return True

    async def process_perform_claim_faucet(self, account: str, address: str, use_proxy: bool):
        has_claimed = await self.check_faucet_status(address, use_proxy)
        if not has_claimed:
            tx_hash, block_number = await self.perform_claim_faucet(account, address, use_proxy)
            if tx_hash and block_number:
                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

                logger.actionSuccess(f"USDT Faucet Claimed Successfully")
                logger.info(f"Block: {block_number}")
                logger.action(f"Tx Hash: {tx_hash}")
                logger.actionSuccess(f"Explorer: {explorer}")
            else:
                logger.error(f"Perform On-Chain Failed")
        else:
            logger.warn(f"Already Claimed")

    async def process_perform_trade(self, account: str, address: str, pair: int, is_long: bool, use_proxy: bool):
        tx_hash, block_number = await self.perform_trade(account, address, pair, is_long, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            logger.actionSuccess(f"Trade Success")
            logger.info(f"Block: {block_number}")
            logger.action(f"Tx Hash: {tx_hash}")
            logger.actionSuccess(f"Explorer: {explorer}")
        else:
            logger.error(f"Perform On-Chain Failed")

    async def process_perform_deposit_lp(self, account: str, address: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_deposit_lp(account, address, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            logger.actionSuccess(f"Deposit Liquidity Success")
            logger.info(f"Block: {block_number}")
            logger.action(f"Tx Hash: {tx_hash}")
            logger.actionSuccess(f"Explorer: {explorer}")
        else:
            logger.error(f"Perform On-Chain Failed")

    async def process_perform_withdraw_lp(self, account: str, address: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_withdraw_lp(account, address, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            logger.actionSuccess(f"Withdraw Liquidity Success")
            logger.info(f"Block: {block_number}")
            logger.action(f"Tx Hash: {tx_hash}")
            logger.actionSuccess(f"Explorer: {explorer}")
        else:
            logger.error(f"Perform On-Chain Failed")

    async def process_option_1(self, account: str, address: str, use_proxy):
        logger.step(f"Faucet")

        await self.process_perform_claim_faucet(account, address, use_proxy)

    async def process_option_2(self, account: str, address: str, use_proxy: bool):
        for i in range(self.trade_count):
            logger.step(f"Trade {i+1} Of {self.trade_count}")

            pairs = random.choice(self.pairs)
            is_long = random.choice([True, False])
            name = pairs["name"]
            pair = pairs["desimal"]
            action = "Long" if is_long == True else "Short"

            balance = await self.get_token_balance(address, self.USDT_CONTRACT_ADDRESS, use_proxy)

            logger.info(f"Balance: {balance} USDT")
            logger.info(f"Amount: {self.trade_amount} USDT")
            logger.info(f"Pair: {action} - {name}")

            if not balance or balance <= self.trade_amount:
                logger.warn(f"Insufficient USDT Token Balance")
                return

            await self.process_perform_trade(account, address, pair, is_long, use_proxy)
            await self.print_timer()

    async def process_option_3(self, account: str, address: str, use_proxy: bool):
        for i in range(self.deposit_lp_count):
            logger.step(f"Deposit LP {i+1} Of {self.deposit_lp_count}")

            balance = await self.get_token_balance(address, self.USDT_CONTRACT_ADDRESS, use_proxy)

            logger.info(f"Balance: {balance} USDT")
            logger.info(f"Amount: {self.deposit_lp_amount} USDT")

            if not balance or balance <= self.deposit_lp_amount:
                logger.warn(f"Insufficient USDT Token Balance")
                return

            await self.process_perform_deposit_lp(account, address, use_proxy)
            await self.print_timer()

    async def process_option_4(self, account: str, address: str, use_proxy: bool):
        for i in range(self.withdraw_lp_count):
            logger.step(f"Withdraw LP {i+1} Of {self.withdraw_lp_count}")

            balance = await self.get_lp_balance(address, use_proxy)

            logger.info(f"LP Held: {balance}")
            logger.info(f"Amount: {self.withdraw_lp_amount}")

            if not balance or balance <= self.withdraw_lp_amount:
                logger.warn(f"Insufficient LP Tokens Held")
                return

            await self.process_perform_withdraw_lp(account, address, use_proxy)
            await self.print_timer()

    async def process_accounts(self, account: str, address: str, option: int, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                logger.error(f"Status: Web3 Not Connected")
                return

            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")

        if option == 1:
            logger.step(f"Option: Claim Faucet")

            await self.process_option_1(account, address, use_proxy)

        elif option == 2:
            logger.step(f"Option: Random Trade")

            await self.process_option_2(account, address, use_proxy)

        elif option == 3:
            logger.step(f"Option: Deposit Liquidity")

            await self.process_option_3(account, address, use_proxy)

        elif option == 4:
            logger.step(f"Option: Withdraw Liquidity")

            await self.process_option_4(account, address, use_proxy)

        else:
            logger.step(f"Option: Run All Features")

            await self.process_option_1(account, address, use_proxy)
            await asyncio.sleep(5)

            await self.process_option_2(account, address, use_proxy)
            await asyncio.sleep(5)

            if self.lp_option == 1:
                await self.process_option_3(account, address, use_proxy)

            elif self.lp_option == 2:
                await self.process_option_4(account, address, use_proxy)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            option, use_proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = False
                if use_proxy_choice == 1: # Now corresponds to private proxy
                    use_proxy = True

                await display_welcome_screen() # Call the new welcome screen
                logger.info(f"Account's Total: {len(accounts)}")

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)

                for account in accounts:
                    if account:
                        address = self.generate_address(account)

                        print(f"{Colors.CYAN + Colors.BOLD}[ {Colors.WHITE + Colors.BOLD}{self.mask_account(address)} {Colors.CYAN + Colors.BOLD}]{Colors.RESET}")


                        if not address:
                            logger.error(f"Status: Invalid Private Key or Library Version Not Supported")
                            continue

                        await self.process_accounts(account, address, option, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)
                
                # Modified countdown logic
                seconds = 24 * 60 * 60 # Start with 24 hours
                start_time_str = datetime.now(wib).strftime('%H:%M:%S')

                print(f"{Colors.BRIGHT_BLACK}[{start_time_str}]{Colors.RESET} {Colors.GREEN}[✓] 23:59:59 All Task Completeed 🗿", end="\r", flush=True)
                await asyncio.sleep(1) # Initial display for one second

                seconds -= 1 # Decrement for the actual countdown

                while seconds >= 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Colors.BRIGHT_BLACK}[ {datetime.now().astimezone(wib).strftime('%H:%M:%S')} ]{Colors.RESET} "
                        f"{Colors.CYAN}[⟳] Task Completeed Next cycle in: {formatted_time}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            logger.error(f"File 'accounts.txt' Not Found.")
            return
        except Exception as e:
            logger.error(f"Error: {e}")
            raise e

if __name__ == "__main__":
    try:
        bot = Brokex()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        logger.error("[ EXIT ] Brokex Protocol - BOT")
