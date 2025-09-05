from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from datetime import datetime
from colorama import *
import asyncio, random, json, re, os
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
    BLUE = Fore.BLUE  # Ditambahkan
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
    print("  ║            Pharos OpenFi B O T            ║")
    print("  ║                                      ║")
    print(f"  ║     {Colors.YELLOW}{now.strftime('%H:%M:%S %d.%m.%Y')}{Colors.BRIGHT_GREEN}           ║")
    print("  ║                                      ║")
    print("  ║     Bot TESTNET AUTOMATION         ║")
    print(f"  ║   {Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}  |  t.me/ZonaAirdr0p   ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    await asyncio.sleep(1)

class OpenFi:
    def __init__(self) -> None:
        self.RPC_URL = "https://api.zan.top/node/v1/pharos/testnet/42c3418d1faa45babe2af2f1fedf2325"
        self.PHRS_CONTRACT_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        self.WPHRS_CONTRACT_ADDRESS = "0x3019B247381c850ab53Dc0EE53bCe7A07Ea9155f"
        self.USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
        self.USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
        self.WETH_CONTRACT_ADDRESS = "0x4E28826d32F1C398DED160DC16Ac6873357d048f"
        self.WBTC_CONTRACT_ADDRESS = "0x8275c526d1bCEc59a31d673929d3cE8d108fF5c7"
        self.GOLD_CONTRACT_ADDRESS = "0xAaf03Cbb486201099EdD0a52E03Def18cd0c7354"
        self.TSLA_CONTRACT_ADDRESS = "0xA778b48339d3c6b4Bc5a75B37c6Ce210797076b1"
        self.NVIDIA_CONTRACT_ADDRESS = "0xAaF3A7F1676385883593d7Ea7ea4FcCc675EE5d6"
        self.FAUCET_ROUTER_ADDRESS = "0x0E29d74Af0489f4B08fBfc774e25C0D3b5f43285"
        self.WRAPPED_ROUTER_ADDRESS = "0x974828e18bff1E71780f9bE19d0DFf4Fe1f61fCa"
        self.POOL_ROUTER_ADDRESS = "0x11d1ca4012d94846962bca2FBD58e5A27ddcBfC5"
        self.POOL_PROVIDER_ADDRESS = "0x54cb4f6C4c12105B48b11e21d78becC32Ef694EC"
        self.LENDING_POOL_ADDRESS = "0x0000000000000000000000000000000000000000"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]}
        ]''')
        self.OPENFI_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "isMintable",
                "stateMutability": "view",
                "inputs": [
                    { "internalType": "address", "name": "asset", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "bool", "name": "", "type": "bool" }
                ]
            },
            {
                "type": "function",
                "name": "getUserReserveData",
                "stateMutability": "view",
                "inputs": [
                    { "internalType": "address", "name": "asset", "type": "address" },
                    { "internalType": "address", "name": "user", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "currentBTokenBalance", "type": "uint256" },
                    { "internalType": "uint256", "name": "currentStableDebt", "type": "uint256" },
                    { "internalType": "uint256", "name": "currentVariableDebt", "type": "uint256" },
                    { "internalType": "uint256", "name": "principalStableDebt", "type": "uint256" },
                    { "internalType": "uint256", "name": "scaledVariableDebt", "type": "uint256" },
                    { "internalType": "uint256", "name": "stableBorrowRate", "type": "uint256" },
                    { "internalType": "uint256", "name": "liquidityRate", "type": "uint256" },
                    { "internalType": "uint40", "name": "stableRateLastUpdated", "type": "uint40" },
                    { "internalType": "bool", "name": "usageAsCollateralEnabled", "type": "bool" }
                ]
            },
            {
                "type": "function",
                "name": "getReserveConfigurationData",
                "stateMutability": "view",
                "inputs": [
                    { "internalType": "address", "name": "asset", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "decimals", "type": "uint256" },
                    { "internalType": "uint256", "name": "ltv", "type": "uint256" },
                    { "internalType": "uint256", "name": "liquidationThreshold", "type": "uint256" },
                    { "internalType": "uint256", "name": "liquidationBonus", "type": "uint256" },
                    { "internalType": "uint256", "name": "reserveFactor", "type": "uint256" },
                    { "internalType": "bool", "name": "usageAsCollateralEnabled", "type": "bool" },
                    { "internalType": "bool", "name": "borrowingEnabled", "type": "bool" },
                    { "internalType": "bool", "name": "stableBorrowRateEnabled", "type": "bool" },
                    { "internalType": "bool", "name": "isActive", "type": "bool" },
                    { "internalType": "bool", "name": "isFrozen", "type": "bool" }
                ]
            },
            {
                "type": "function",
                "name": "getReserveData",
                "stateMutability": "view",
                "inputs": [
                    { "internalType": "address", "name": "asset", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "unbacked", "type": "uint256" },
                    { "internalType": "uint256", "name": "accruedToTreasuryScaled", "type": "uint256" },
                    { "internalType": "uint256", "name": "totalBToken", "type": "uint256" },
                    { "internalType": "uint256", "name": "totalStableDebt", "type": "uint256" },
                    { "internalType": "uint256", "name": "totalVariableDebt", "type": "uint256" },
                    { "internalType": "uint256", "name": "liquidityRate", "type": "uint256" },
                    { "internalType": "uint256", "name": "variableBorrowRate", "type": "uint256" },
                    { "internalType": "uint256", "name": "stableBorrowRate", "type": "uint256" },
                    { "internalType": "uint256", "name": "averageStableBorrowRate", "type": "uint256" },
                    { "internalType": "uint256", "name": "liquidityIndex", "type": "uint256" },
                    { "internalType": "uint256", "name": "variableBorrowIndex", "type": "uint256" },
                    { "internalType": "uint40", "name": "lastUpdateTimestamp", "type": "uint40" }
                ]
            },
            {
                "type": "function",
                "name": "mint",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "address", "name": "token", "type": "address" },
                    { "internalType": "address", "name": "to", "type": "address" },
                    { "internalType": "uint256", "name": "amount", "type": "uint256" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ]
            },
            {
                "type": "function",
                "name": "depositETH",
                "stateMutability": "payable",
                "inputs": [
                    { "internalType": "address", "name": "", "type": "address" },
                    { "internalType": "address", "name": "onBehalfOf", "type": "address" },
                    { "internalType": "uint16", "name": "referralCode", "type": "uint16" }
                ],
                "outputs": []
            },
            {
                "type": "function",
                "name": "supply",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "address", "name": "asset", "type": "address" },
                    { "internalType": "uint256", "name": "amount", "type": "uint256" },
                    { "internalType": "address", "name": "onBehalfOf", "type": "address" },
                    { "internalType": "uint16", "name": "referralCode", "type": "uint16" }
                ],
                "outputs": []
            },
            {
                "type": "function",
                "name": "borrow",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "address", "name": "asset", "type": "address" },
                    { "internalType": "uint256", "name": "amount", "type": "uint256" },
                    { "internalType": "uint256", "name": "interestRateMode", "type": "uint256" },
                    { "internalType": "uint16", "name": "referralCode", "type": "uint16" },
                    { "internalType": "address", "name": "onBehalfOf", "type": "address" }
                ],
                "outputs": []
            },
            {
                "type": "function",
                "name": "repay",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "address", "name": "asset", "type": "address" },
                    { "internalType": "uint256", "name": "amount", "type": "uint256" },
                    { "internalType": "uint256", "name": "interestRateMode", "type": "uint256" },
                    { "internalType": "address", "name": "onBehalfOf", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ]
            },
            {
                "type": "function",
                "name": "withdraw",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "address", "name": "asset", "type": "address" },
                    { "internalType": "uint256", "name": "amount", "type": "uint256" },
                    { "internalType": "address", "name": "to", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ]
            }
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        self.deposit_count = 0
        self.deposit_amount = 0
        self.supply_count = 0
        self.supply_amount = 0
        self.borrow_count = 0
        self.borrow_amount = 0
        self.repay_count = 0
        self.repay_amount = 0
        self.withdraw_count = 0
        self.withdraw_amount = 0
        self.min_delay = 0
        self.max_delay = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {message}", flush=True)

    def welcome(self):
        now = datetime.now()
        print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}")
        print("  ╔══════════════════════════════════════╗")
        print("  ║           Pharos OpenFi B O T            ║")
        print("  ║                                      ║")
        print(f"  ║     {Colors.YELLOW}{now.strftime('%H:%M:%S %d.%m.%Y')}{Colors.BRIGHT_GREEN}           ║")
        print("  ║                                      ║")
        print("  ║     Bot TESTNET AUTOMATION         ║")
        print(f"  ║   {Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}  |  t.me/ZonaAirdr0p   ║")
        print("  ╚══════════════════════════════════════╝")
        print(f"{Colors.RESET}")

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Colors.RED}File {filename} Not Found.{Colors.RESET}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Colors.RED}No Proxies Found.{Colors.RESET}")
                return

            self.log(
                f"{Colors.GREEN}Proxies Total  : {Colors.WHITE}{len(self.proxies)}{Colors.RESET}"
            )
        
        except Exception as e:
            self.log(f"{Colors.RED}Failed To Load Proxies: {e}{Colors.RESET}")
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
            self.log(
                f"{Colors.CYAN}Status  :{Colors.RED} Generate Address Failed {Colors.MAGENTA}-{Colors.YELLOW} {str(e)}"
            )
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None
        
    def generate_random_option(self):
        assets = [
            ("WPHRS", self.WPHRS_CONTRACT_ADDRESS, 18),
            ("USDC", self.USDC_CONTRACT_ADDRESS, 6),
            ("USDT", self.USDT_CONTRACT_ADDRESS, 6),
            ("WETH", self.WETH_CONTRACT_ADDRESS, 18),
            ("WBTC", self.WBTC_CONTRACT_ADDRESS, 8),
            ("GOLD", self.GOLD_CONTRACT_ADDRESS, 18),
            ("TSLA", self.TSLA_CONTRACT_ADDRESS, 18),
            ("NVIDIA", self.NVIDIA_CONTRACT_ADDRESS, 18)
        ]

        ticker, asset_address, decimals = random.choice(assets)
        return ticker, asset_address, decimals
        
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

            if contract_address == self.PHRS_CONTRACT_ADDRESS:
                balance = web3.eth.get_balance(address)
                decimals = 18
            else:
                token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
                balance = token_contract.functions.balanceOf(address).call()
                decimals = token_contract.functions.decimals().call()

            token_balance = balance / (10 ** decimals)
            return token_balance
        except Exception as e:
            self.log(f"{Colors.CYAN}Message  :{Colors.RED} {str(e)}")
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
                self.log(f"{Colors.CYAN}Message  :{Colors.YELLOW} [Attempt {attempt + 1}] Send TX Error: {str(e)}")
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
                self.log(f"{Colors.CYAN}Message  :{Colors.YELLOW} [Attempt {attempt + 1}] Wait for Receipt Error: {str(e)}")
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
        
    async def check_faucet_status(self, address: str, asset_address, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.FAUCET_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.OPENFI_CONTRACT_ABI)
            is_mintable = token_contract.functions.isMintable(web3.to_checksum_address(asset_address)).call()

            return is_mintable
        except Exception as e:
            self.log(f"{Colors.CYAN}Message  :{Colors.RED} {str(e)}")
            return None
        
    async def get_supplied_balance(self, address: str, asset_address, decimals: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            asset = web3.to_checksum_address(asset_address)

            contract_address = web3.to_checksum_address(self.POOL_PROVIDER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.OPENFI_CONTRACT_ABI)
            user_reserve_data = token_contract.functions.getUserReserveData(asset, address).call()
            
            supplied_balance = user_reserve_data[0] / (10 ** decimals)
            return supplied_balance
        except Exception as e:
            self.log(f"{Colors.CYAN}Message  :{Colors.RED} {str(e)}")
            return None
        
    async def get_borrowed_balance(self, address: str, asset_address, decimals: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            asset = web3.to_checksum_address(asset_address)

            contract_address = web3.to_checksum_address(self.POOL_PROvider_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.OPENFI_CONTRACT_ABI)
            user_reserve_data = token_contract.functions.getUserReserveData(asset, address).call()

            stable_debt     = user_reserve_data[1]
            variable_debt   = user_reserve_data[2]

            total_debt = (stable_debt + variable_debt) / (10 ** decimals)
            return total_debt
        except Exception as e:
            self.log(f"{Colors.CYAN}Message  :{Colors.RED} {str(e)}")
            return None
        
    async def get_available_borrowed_balance(self, address: str, asset_address, decimals: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            asset = web3.to_checksum_address(asset_address)

            contract_address = web3.to_checksum_address(self.POOL_PROVIDER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.OPENFI_CONTRACT_ABI)

            user_reserve_data = token_contract.functions.getUserReserveData(asset, address).call()
            supplied_balance = user_reserve_data[0]
            stable_debt = user_reserve_data[1]
            variable_debt = user_reserve_data[2]

            configuration_data = token_contract.functions.getReserveConfigurationData(asset).call()
            ltv = configuration_data[1] 

            reserve_data = token_contract.functions.getReserveData(asset).call()
            total_token = reserve_data[2]
            total_stable_debt = reserve_data[3]
            total_variable_debt = reserve_data[4]

            available_liquidity = total_token - (total_stable_debt + total_variable_debt)

            total_debt = stable_debt + variable_debt
            max_borrow_from_collateral = (supplied_balance * ltv) // 10000
            available_to_borrow = max_borrow_from_collateral - total_debt
            if available_to_borrow < 0:
                available_to_borrow = 0

            available_to_borrow = min(available_to_borrow, available_liquidity) / (10 ** decimals)
            return available_to_borrow
        except Exception as e:
            self.log(f"{Colors.CYAN}Message  :{Colors.RED} {str(e)}")
            return None
        
    async def mint_faucet(self, account: str, address: str, asset_address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            router_address = web3.to_checksum_address(self.FAUCET_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.OPENFI_CONTRACT_ABI)

            asset_address = web3.to_checksum_address(asset_address)
            asset_contract = web3.eth.contract(address=asset_address, abi=self.ERC20_CONTRACT_ABI)

            decimals = asset_contract.functions.decimals().call()

            amount_to_wei = int(100 * (10 ** decimals))
            mint_data = router_contract.functions.mint(asset_address, address, amount_to_wei)
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
            self.log(f"{Colors.CYAN}Message  :{Colors.RED} {str(e)}")
            return None
        
    async def perform_deposit(self, account: str, address: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            amount_to_wei = web3.to_wei(amount, "ether")

            router_address = web3.to_checksum_address(self.WRAPPED_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.OPENFI_CONTRACT_ABI)

            deposit_data = router_contract.functions.depositETH(self.LENDING_POOL_ADDRESS, address, 0)
            estimated_gas = deposit_data.estimate_gas({"from": address, "value": amount_to_wei})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            deposit_tx = deposit_data.build_transaction({
                "from": address,
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, deposit_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            self.used_nonce[address] += 1
            return tx_hash
        except Exception as e:
            self.log(f"{Colors.CYAN}Message  :{Colors.RED} {str(e)}")
            return None
        
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

                self.used_nonce[address] += 1
                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                
                self.log(f"{Colors.CYAN}Approve  :{Colors.GREEN} Success")
                self.log(f"{Colors.CYAN}Tx Hash  :{Colors.WHITE} {tx_hash}")
                self.log(f"{Colors.CYAN}Explorer :{Colors.WHITE} {explorer}")
                await self.print_timer()

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
        
    async def perform_supply(self, account: str, address: str, asset_address: str, supply_amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            await self.approving_token(account, address, self.POOL_ROUTER_ADDRESS, asset_address, supply_amount, use_proxy)

            router_address = web3.to_checksum_address(self.POOL_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.OPENFI_CONTRACT_ABI)

            token_address = web3.to_checksum_address(asset_address)
            token_contract = web3.eth.contract(address=token_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()

            amount_to_wei = int(supply_amount * (10 ** decimals))
            supply_data = router_contract.functions.supply(token_address, amount_to_wei, address, 0)
            estimated_gas = supply_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            supply_tx = supply_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, supply_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            self.used_nonce[address] += 1
            return tx_hash
        except Exception as e:
            self.log(f"{Colors.CYAN}Message  :{Colors.RED} {str(e)}")
            return None
        
    async def perform_borrow(self, account: str, address: str, asset_address: str, borrow_amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            router_address = web3.to_checksum_address(self.POOL_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.OPENFI_CONTRACT_ABI)

            token_address = web3.to_checksum_address(asset_address)
            token_contract = web3.eth.contract(address=token_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()

            amount_to_wei = int(borrow_amount * (10 ** decimals))
            borrow_data = router_contract.functions.borrow(token_address, amount_to_wei, 2, 0, address)
            estimated_gas = borrow_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            borrow_tx = borrow_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, borrow_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            self.used_nonce[address] += 1
            return tx_hash
        except Exception as e:
            self.log(f"{Colors.CYAN}Message  :{Colors.RED} {str(e)}")
            return None
        
    async def perform_repay(self, account: str, address: str, asset_address: str, repay_amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            await self.approving_token(account, address, self.POOL_ROUTER_ADDRESS, asset_address, repay_amount, use_proxy)

            router_address = web3.to_checksum_address(self.POOL_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.OPENFI_CONTRACT_ABI)

            token_address = web3.to_checksum_address(asset_address)
            token_contract = web3.eth.contract(address=token_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()

            amount_to_wei = int(repay_amount * (10 ** decimals))
            repay_data = router_contract.functions.repay(token_address, amount_to_wei, 2, address)
            estimated_gas = repay_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            repay_tx = repay_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, repay_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            self.used_nonce[address] += 1
            return tx_hash
        except Exception as e:
            self.log(f"{Colors.CYAN}Message  :{Colors.RED} {str(e)}")
            return None
        
    async def perform_withdraw(self, account: str, address: str, asset_address: str, withdraw_amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            router_address = web3.to_checksum_address(self.POOL_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.OPENFI_CONTRACT_ABI)

            token_address = web3.to_checksum_address(asset_address)
            token_contract = web3.eth.contract(address=token_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()

            amount_to_wei = int(withdraw_amount * (10 ** decimals))
            withdraw_data = router_contract.functions.withdraw(token_address, amount_to_wei, address)
            estimated_gas = withdraw_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            withdraw_tx = withdraw_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, withdraw_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            self.used_nonce[address] += 1
            return tx_hash
        except Exception as e:
            self.log(f"{Colors.CYAN}Message  :{Colors.RED} {str(e)}")
            return None
        
    async def print_timer(self):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {Colors.CYAN}Wait For {remaining} Seconds For Next Tx...", end="\r", flush=True)
            await asyncio.sleep(1)
        print()

    def print_deposit_question(self):
         while True:
            try:
                deposit_count = int(input(f"{Colors.YELLOW}Enter Deposit Count -> {Colors.RESET}").strip())
                if deposit_count > 0:
                    self.deposit_count = deposit_count
                    break
                else:
                    print(f"{Colors.RED}Deposit Count must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.{Colors.RESET}")
         
         while True:
            try:
                deposit_amount = float(input(f"{Colors.YELLOW}Enter Deposit Amount [PHRS] -> {Colors.RESET}").strip())
                if deposit_amount > 0:
                    self.deposit_amount = deposit_amount
                    break
                else:
                    print(f"{Colors.RED}Amount must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.{Colors.RESET}")
    
    def print_supply_question(self):
        while True:
            try:
                supply_count = int(input(f"{Colors.YELLOW}Enter Supply Count -> {Colors.RESET}").strip())
                if supply_count > 0:
                    self.supply_count = supply_count
                    break
                else:
                    print(f"{Colors.RED}Supply Count must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.{Colors.RESET}")
         
        while True:
            try:
                supply_amount = float(input(f"{Colors.YELLOW}Enter Supply Amount [ERC20] -> {Colors.RESET}").strip())
                if supply_amount > 0:
                    self.supply_amount = supply_amount
                    break
                else:
                    print(f"{Colors.RED}Amount must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.{Colors.RESET}")
    
    def print_borrow_question(self):
        while True:
            try:
                borrow_count = int(input(f"{Colors.YELLOW}Enter Borrow Count -> {Colors.RESET}").strip())
                if borrow_count > 0:
                    self.borrow_count = borrow_count
                    break
                else:
                    print(f"{Colors.RED}Borrow Count must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.{Colors.RESET}")
         
        while True:
            try:
                borrow_amount = float(input(f"{Colors.YELLOW}Enter Borrow Amount [ERC20] -> {Colors.RESET}").strip())
                if borrow_amount > 0:
                    self.borrow_amount = borrow_amount
                    break
                else:
                    print(f"{Colors.RED}Amount must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.{Colors.RESET}")
    
    def print_repay_question(self):
        while True:
            try:
                repay_count = int(input(f"{Colors.YELLOW}Enter Repay Count -> {Colors.RESET}").strip())
                if repay_count > 0:
                    self.repay_count = repay_count
                    break
                else:
                    print(f"{Colors.RED}Repay Count must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.{Colors.RESET}")
         
        while True:
            try:
                repay_amount = float(input(f"{Colors.YELLOW}Enter Repay Amount [ERC20] -> {Colors.RESET}").strip())
                if repay_amount > 0:
                    self.repay_amount = repay_amount
                    break
                else:
                    print(f"{Colors.RED}Amount must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.{Colors.RESET}")
    
    def print_withdraw_question(self):
        while True:
            try:
                withdraw_count = int(input(f"{Colors.YELLOW}Enter Withdraw Count -> {Colors.RESET}").strip())
                if withdraw_count > 0:
                    self.withdraw_count = withdraw_count
                    break
                else:
                    print(f"{Colors.RED}Withdraw Count must be greater than 0.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a float or decimal number.{Colors.RESET}")
         
        while True:
            try:
                withdraw_amount = float(input(f"{Colors.YELLOW}Enter Withdraw Amount [ERC20] -> {Colors.RESET}").strip())
                if withdraw_amount > 0:
                    self.withdraw_amount = withdraw_amount
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
                    print(f"{Colors.RED}Min Delay must be >= Min Delay.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a number.{Colors.RESET}")
        
    def print_question(self):
        while True:
            try:
                print(f"{Colors.GREEN}Select Option:{Colors.RESET}")
                print(f"{Colors.WHITE}1. Mint Faucets{Colors.RESET}")
                print(f"{Colors.WHITE}2. Deposit PHRS{Colors.RESET}")
                print(f"{Colors.WHITE}3. Supply Assets{Colors.RESET}")
                print(f"{Colors.WHITE}4. Borrow Assets{Colors.RESET}")
                print(f"{Colors.WHITE}5. Repay Assets{Colors.RESET}")
                print(f"{Colors.WHITE}6. Withdraw Assets{Colors.RESET}")
                print(f"{Colors.WHITE}7. Run All Features{Colors.RESET}")
                option = int(input(f"{Colors.BLUE}Choose [1/2/3/4/5/6/7] -> {Colors.RESET}").strip())

                if option in [1, 2, 3, 4, 5, 6, 7]:
                    option_type = (
                        "Mint Faucets" if option == 1 else 
                        "Deposit PHRS" if option == 2 else 
                        "Supply Assets" if option == 3 else
                        "Borrow Assets" if option == 4 else
                        "Repay Assets" if option == 5 else
                        "Withdraw Assets" if option == 6 else
                        "Run All Features"
                    )
                    print(f"{Colors.GREEN}{option_type} Selected.{Colors.RESET}")
                    break
                else:
                    print(f"{Colors.RED}Please enter either 1, 2, 3, 4, 5, 6 or 7.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input. Enter a number (1, 2, 3, 4, 5, 6 or 7).{Colors.RESET}")

        if option == 1:
            self.print_delay_question()

        elif option == 2:
            self.print_deposit_question()
            self.print_delay_question()
            
        elif option == 3:
            self.print_supply_question()
            self.print_delay_question()

        elif option == 4:
            self.print_borrow_question()
            self.print_delay_question()
        
        elif option == 5:
            self.print_repay_question()
            self.print_delay_question()
        
        elif option == 6:
            self.print_withdraw_question()
            self.print_delay_question()
            
        elif option == 7:
            self.print_deposit_question()
            self.print_supply_question()
            self.print_borrow_question()
            self.print_repay_question()
            self.print_withdraw_question()
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

        return option, proxy_choice, rotate_proxy
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            self.log(f"{Colors.CYAN}Status  :{Colors.RED} Connection Not 200 OK {Colors.MAGENTA}-{Colors.YELLOW} {str(e)}")
            return None
        
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(f"{Colors.CYAN}Proxy   :{Colors.WHITE} {proxy}")

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    await asyncio.sleep(1)
                    continue
                return False
            return True
    
    async def process_mint_faucet(self, account: str, address: str, asset_address: str, ticker: str, use_proxy: bool):
        is_mintable = await self.check_faucet_status(address, asset_address, use_proxy)
        if is_mintable:
            tx_hash = await self.mint_faucet(account, address, asset_address, use_proxy)
            if tx_hash:
                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                self.log(f"{Colors.CYAN}Status   :{Colors.GREEN} Mint 100 {ticker} Faucet Success")
                self.log(f"{Colors.CYAN}Tx Hash  :{Colors.WHITE} {tx_hash}")
                self.log(f"{Colors.CYAN}Explorer :{Colors.WHITE} {explorer}")
            else:
                self.log(f"{Colors.CYAN}Status   :{Colors.RED} Perform On-Chain Failed")
        else:
            self.log(f"{Colors.CYAN}Status   :{Colors.YELLOW} Not Able to Mint")

    async def process_perform_deposit(self, account: str, address: str, deposit_amount: float, use_proxy: bool):
        tx_hash = await self.perform_deposit(account, address, deposit_amount, use_proxy)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(f"{Colors.CYAN}Status   :{Colors.GREEN} Deposit {deposit_amount} PHRS Success")
            self.log(f"{Colors.CYAN}Tx Hash  :{Colors.WHITE} {tx_hash}")
            self.log(f"{Colors.CYAN}Explorer :{Colors.WHITE} {explorer}")
        else:
            self.log(f"{Colors.CYAN}Status   :{Colors.RED} Perform On-Chain Failed")

    async def process_perform_supply(self, account: str, address: str, asset_address: str, supply_amount: float, ticker: str, use_proxy: bool):
        tx_hash = await self.perform_supply(account, address, asset_address, supply_amount, use_proxy)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(f"{Colors.CYAN}Status   :{Colors.GREEN} Supply {supply_amount} {ticker} Success")
            self.log(f"{Colors.CYAN}Tx Hash  :{Colors.WHITE} {tx_hash}")
            self.log(f"{Colors.CYAN}Explorer :{Colors.WHITE} {explorer}")
        else:
            self.log(f"{Colors.CYAN}Status   :{Colors.RED} Perform On-Chain Failed")

    async def process_perform_borrow(self, account: str, address: str, asset_address: str, borrow_amount: float, ticker: str, use_proxy: bool):
        tx_hash = await self.perform_borrow(account, address, asset_address, borrow_amount, use_proxy)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(f"{Colors.CYAN}Status   :{Colors.GREEN} Borrow {borrow_amount} {ticker} Success")
            self.log(f"{Colors.CYAN}Tx Hash  :{Colors.WHITE} {tx_hash}")
            self.log(f"{Colors.CYAN}Explorer :{Colors.WHITE} {explorer}")
        else:
            self.log(f"{Colors.CYAN}Status   :{Colors.RED} Perform On-Chain Failed")
            
    async def process_perform_repay(self, account: str, address: str, asset_address: str, repay_amount: float, ticker: str, use_proxy: bool):
        tx_hash = await self.perform_repay(account, address, asset_address, repay_amount, use_proxy)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(f"{Colors.CYAN}Status   :{Colors.GREEN} Repay {repay_amount} {ticker} Success")
            self.log(f"{Colors.CYAN}Tx Hash  :{Colors.WHITE} {tx_hash}")
            self.log(f"{Colors.CYAN}Explorer :{Colors.WHITE} {explorer}")
        else:
            self.log(f"{Colors.CYAN}Status   :{Colors.RED} Perform On-Chain Failed")

    async def process_perform_withdraw(self, account: str, address: str, asset_address: str, withdraw_amount: float, ticker: str, use_proxy: bool):
        tx_hash = await self.perform_withdraw(account, address, asset_address, withdraw_amount, use_proxy)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(f"{Colors.CYAN}Status   :{Colors.GREEN} Withdraw {withdraw_amount} {ticker} Success")
            self.log(f"{Colors.CYAN}Tx Hash  :{Colors.WHITE} {tx_hash}")
            self.log(f"{Colors.CYAN}Explorer :{Colors.WHITE} {explorer}")
        else:
            self.log(f"{Colors.CYAN}Status   :{Colors.RED} Perform On-Chain Failed")

    async def process_option_1(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Colors.MAGENTA}● {Colors.GREEN}Mint")

        for ticker, asset_address in [
                ("GOLD", self.GOLD_CONTRACT_ADDRESS), 
                ("TSLA", self.TSLA_CONTRACT_ADDRESS), 
                ("NVIDIA", self.NVIDIA_CONTRACT_ADDRESS)
            ]:

            self.log(f"{Colors.CYAN}Assets   :{Colors.BLUE} {ticker}")
            await self.process_mint_faucet(account, address, asset_address, ticker, use_proxy)
            await self.print_timer()

    async def process_option_2(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Colors.MAGENTA}● {Colors.GREEN}Deposit")

        for i in range(self.deposit_count):
            self.log(f"{Colors.GREEN}● {Colors.BLUE}Deposit {Colors.WHITE}{i+1} {Colors.MAGENTA}Of {Colors.WHITE}{self.deposit_count}")
            self.log(f"{Colors.CYAN}Assets   :{Colors.BLUE} PHRS")
            self.log(f"{Colors.CYAN}Amount   :{Colors.WHITE} {self.deposit_amount} PHRS")

            balance = await self.get_token_balance(address, self.PHRS_CONTRACT_ADDRESS, use_proxy)
            self.log(f"{Colors.CYAN}Balance  :{Colors.WHITE} {balance} PHRS")

            if not balance or balance <= self.deposit_amount:
                self.log(f"{Colors.CYAN}Status   :{Colors.YELLOW} Insufficient PHRS Token Balance")
                return

            await self.process_perform_deposit(account, address, self.deposit_amount, use_proxy)
            await self.print_timer()

    async def process_option_3(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Colors.MAGENTA}● {Colors.GREEN}Supply")

        for i in range(self.supply_count):
            self.log(f"{Colors.GREEN}● {Colors.BLUE}Supply {Colors.WHITE}{i+1} {Colors.MAGENTA}Of {Colors.WHITE}{self.supply_count}")

            ticker, asset_address, decimals = self.generate_random_option()
            self.log(f"{Colors.CYAN}Assets   :{Colors.BLUE} {ticker}")
            self.log(f"{Colors.CYAN}Amount   :{Colors.WHITE} {self.supply_amount} {ticker}")

            balance = await self.get_token_balance(address, asset_address, use_proxy)
            self.log(f"{Colors.CYAN}Balance  :{Colors.WHITE} {balance} {ticker}")

            if not balance or balance <= self.supply_amount:
                self.log(f"{Colors.CYAN}Status   :{Colors.YELLOW} Insufficient {ticker} Token Balance")
                continue

            await self.process_perform_supply(account, address, asset_address, self.supply_amount, ticker, use_proxy)
            await self.print_timer()

    async def process_option_4(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Colors.MAGENTA}● {Colors.GREEN}Borrow")

        for i in range(self.borrow_count):
            self.log(f"{Colors.GREEN}● {Colors.BLUE}Borrow {Colors.WHITE}{i+1} {Colors.MAGENTA}Of {Colors.WHITE}{self.borrow_count}")

            ticker, asset_address, decimals = self.generate_random_option()
            self.log(f"{Colors.CYAN}Assets   :{Colors.BLUE} {ticker}")
            self.log(f"{Colors.CYAN}Amount   :{Colors.WHITE} {self.borrow_amount} {ticker}")

            available_to_borrow = await self.get_available_borrowed_balance(address, asset_address, decimals, use_proxy)
            self.log(f"{Colors.CYAN}Available:{Colors.WHITE} {available_to_borrow} {ticker}")

            if not available_to_borrow or available_to_borrow < self.borrow_amount:
                self.log(f"{Colors.CYAN}Status   :{Colors.YELLOW} Available {ticker} Borrow Balance Less Than Borrow Amount")
                continue

            await self.process_perform_borrow(account, address, asset_address, self.borrow_amount, ticker, use_proxy)
            await self.print_timer()

    async def process_option_5(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Colors.MAGENTA}● {Colors.GREEN}Repay")

        for i in range(self.repay_count):
            self.log(f"{Colors.GREEN}● {Colors.BLUE}Repay {Colors.WHITE}{i+1} {Colors.MAGENTA}Of {Colors.WHITE}{self.repay_count}")

            ticker, asset_address, decimals = self.generate_random_option()
            self.log(f"{Colors.CYAN}Assets   :{Colors.BLUE} {ticker}")
            self.log(f"{Colors.CYAN}Amount   :{Colors.WHITE} {self.repay_amount} {ticker}")

            borrowed_balance = await self.get_borrowed_balance(address, asset_address, decimals, use_proxy)
            self.log(f"{Colors.CYAN}Borrowed :{Colors.WHITE} {borrowed_balance} {ticker}")

            if not borrowed_balance or borrowed_balance < self.repay_amount:
                self.log(f"{Colors.CYAN}Status   :{Colors.YELLOW} Borrowed {ticker} Token Balance Less Than Repay Amount")
                continue

            balance = await self.get_token_balance(address, asset_address, use_proxy)
            self.log(f"{Colors.CYAN}Balance  :{Colors.WHITE} {balance} {ticker}")

            if not balance or balance <= self.repay_amount:
                self.log(f"{Colors.CYAN}Status   :{Colors.YELLOW} Insufficient {ticker} Token Balance")
                continue

            await self.process_perform_repay(account, address, asset_address, self.repay_amount, ticker, use_proxy)
            await self.print_timer()

    async def process_option_6(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Colors.MAGENTA}● {Colors.GREEN}Withdraw")
        
        for i in range(self.withdraw_count):
            self.log(f"{Colors.GREEN}● {Colors.BLUE}Withdraw {Colors.WHITE}{i+1} {Colors.MAGENTA}Of {Colors.WHITE}{self.withdraw_count}")

            ticker, asset_address, decimals = self.generate_random_option()
            self.log(f"{Colors.CYAN}Assets   :{Colors.BLUE} {ticker}")
            self.log(f"{Colors.CYAN}Amount   :{Colors.WHITE} {self.withdraw_amount} {ticker}")

            supplied_balance = await self.get_supplied_balance(address, asset_address, decimals, use_proxy)
            self.log(f"{Colors.CYAN}Supplied :{Colors.WHITE} {supplied_balance} {ticker}")

            if not supplied_balance or supplied_balance < self.withdraw_amount:
                self.log(f"{Colors.CYAN}Status   :{Colors.YELLOW} Supplied {ticker} Token Balance Less Than Withdraw Amount")
                continue

            await self.process_perform_withdraw(account, address, asset_address, self.withdraw_amount, ticker, use_proxy)
            await self.print_timer()

    async def process_accounts(self, account: str, address: str, option: int, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            
            try:
                web3 = await self.get_web3_with_check(address, use_proxy)
            except Exception as e:
                self.log(f"{Colors.CYAN}Status  :{Colors.RED} Web3 Not Connected {Colors.MAGENTA}-{Colors.YELLOW} {str(e)}")
                return
            
            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")

            if option == 1:
                self.log(f"{Colors.CYAN}Option  :{Colors.BLUE} Mint Faucets")
                await self.process_option_1(account, address, use_proxy)

            elif option == 2:
                self.log(f"{Colors.CYAN}Option  :{Colors.BLUE} Deposit PHRS")
                await self.process_option_2(account, address, use_proxy)

            elif option == 3:
                self.log(f"{Colors.CYAN}Option  :{Colors.BLUE} Supply Assets")
                await self.process_option_3(account, address, use_proxy)

            elif option == 4:
                self.log(f"{Colors.CYAN}Option  :{Colors.BLUE} Borrow Assets")
                await self.process_option_4(account, address, use_proxy)

            elif option == 5:
                self.log(f"{Colors.CYAN}Option  :{Colors.BLUE} Repay Assets")
                await self.process_option_5(account, address, use_proxy)

            elif option == 6:
                self.log(f"{Colors.CYAN}Option  :{Colors.BLUE} Withdraw Assets")
                await self.process_option_6(account, address, use_proxy)

            else:
                self.log(f"{Colors.CYAN}Option  :{Colors.BLUE} Run All Features")
                await self.process_option_1(account, address, use_proxy)
                await self.process_option_2(account, address, use_proxy)
                await self.process_option_3(account, address, use_proxy)
                await self.process_option_4(account, address, use_proxy)
                await self.process_option_5(account, address, use_proxy)
                await self.process_option_6(account, address, use_proxy)

    async def main(self):
        try:
            await display_welcome_screen()
            
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            option, proxy_choice, rotate_proxy = self.print_question()
            use_proxy = True if proxy_choice == 1 else False

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(f"{Colors.GREEN}Account's Total: {Colors.WHITE}{len(accounts)}{Colors.RESET}")

                if use_proxy:
                    await self.load_proxies()
                
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        self.log(f"{Colors.CYAN}Processing account: {self.mask_account(address)}")

                        if not address:
                            self.log(f"{Colors.CYAN}Status  :{Colors.RED} Invalid Private Key or Library Version Not Supported")
                            continue

                        await self.process_accounts(account, address, option, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Colors.CYAN}All accounts processed. Waiting for 24 hours...")
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {Colors.CYAN}Wait for {formatted_time} ...", end="\r")
                    await asyncio.sleep(1)
                    seconds -= 1
                print()

        except FileNotFoundError:
            self.log(f"{Colors.RED}File 'accounts.txt' Not Found.")
            return
        except Exception as e:
            self.log(f"{Colors.RED}Error: {e}")
            raise e

if __name__ == "__main__":
    try:
        bot = OpenFi()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {Colors.RED}[ EXIT ] OpenFi - BOT")
