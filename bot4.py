from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from eth_abi.abi import encode
from eth_utils import keccak, to_hex
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, time, json, re, os, pytz
from dotenv import load_dotenv

wib = pytz.timezone('Asia/Jakarta')

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
        timestamp = datetime.now().astimezone(wib).strftime('%H:%M:%S')
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
    def tx_sent(msg): Logger.log("TX", "↪️", msg, Colors.CYAN)
    @staticmethod
    def tx_success(msg): Logger.log("TX", "✅", msg, Colors.GREEN)

logger = Logger()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

async def display_welcome_screen():
    clear_console()
    now = datetime.now().astimezone(wib)
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}")
    print("  ╔══════════════════════════════════════╗")
    print("  ║            Gotchipus  B O T         ║")
    print("  ║                                     ║")
    print(f"  ║     {Colors.YELLOW}{now.strftime('%H:%M:%S %d.%m.%Y')}{Colors.BRIGHT_GREEN}              ║")
    print("  ║                                     ║")
    print("  ║     Pharos TESTNET AUTOMATION       ║")
    print(f"  ║   {Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}  |  t.me/ZonaAirdr0p   ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    await asyncio.sleep(1)

class Gotchipus:
    def __init__(self) -> None:
        init(autoreset=True)
        load_dotenv()
        self.HEADERS = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://gotchipus.com",
            "Referer": "https://gotchipus.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://gotchipus.com"
        self.RPC_URL = "https://testnet.dplabs-internal.com"
        self.GOTCHIPUS_CONTRACT_ADDRESS = "0x0000000038f050528452D6Da1E7AACFA7B3Ec0a8"
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
                "inputs": [],
                "name": "claimWearable",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        logger.info(message)

    def welcome(self):
        asyncio.run(display_welcome_screen())

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, proxy_mode: int):
        filename = "proxy.txt"
        try:
            if proxy_mode == 1:
                if not os.path.exists(filename):
                    logger.error(f"File {filename} Not Found.")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]

            if not self.proxies and proxy_mode == 1:
                logger.error("No Proxies Found.")
                return

            if proxy_mode == 1:
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
            return mask_account
        
    def build_struct_data(self, account: str, address: str):
        try:
            domain_typehash = keccak(text="EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)")
            name_hash = keccak(text="Gotchipus")
            version_hash = keccak(text="v0.1.0")

            domain_separator = keccak(encode(
                ['bytes32', 'bytes32', 'bytes32', 'uint256', 'address'],
                [domain_typehash, name_hash, version_hash, 688688, self.GOTCHIPUS_CONTRACT_ADDRESS]
            ))

            checkin_typehash = keccak(text="CheckIn(string intent,address user,uint256 timestamp)")
            intent_hash = keccak(text="Daily Check-In for Gotchipus")

            timestamp = int(time.time())

            struct_hash = keccak(encode(
                ['bytes32', 'bytes32', 'address', 'uint256'],
                [checkin_typehash, intent_hash, address, timestamp]
            ))

            digest = keccak(b"\x19\x01" + domain_separator + struct_hash)

            acct = Account.from_key(account)
            signed = acct.unsafe_sign_hash(digest)
            signature = to_hex(signed.signature)

            payload = {
                "address": address,
                "signature": signature,
                "timestamp": timestamp,
            }

            return payload
        except Exception as e:
            raise Exception(f"Build Struct Data Failed: {str(e)}")
        
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
                logger.error(f"Failed to Connect to RPC: {e}")
                return None
        
    async def get_token_balance(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3: return None
            balance = web3.eth.get_balance(address)
            token_balance = balance / (10 ** 18)

            return token_balance
        except Exception as e:
            logger.error(f"Message: {e}")
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

    async def process_perform_mint_nft(self, account: str, address: str, use_proxy: bool):
        try:
            logger.tx_sent("Attempting to Mint NFT...")
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3: return None, None

            contract_address = web3.to_checksum_address(self.GOTCHIPUS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.MINT_CONTRACT_ABI)

            mint_data = token_contract.functions.freeMint()
            estimated_gas = mint_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(0, "gwei")
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

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1
            
            explorer_url = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            logger.tx_success(f"NFT Mint Transaction Sent! Explorer: {explorer_url}")
            return tx_hash, block_number
        except Exception as e:
            logger.error(f"Message: {e}")
            return None, None
        
    async def process_perform_claim_wearable(self, account: str, address: str, use_proxy: bool):
        try:
            logger.tx_sent("Attempting to Claim Wearable...")
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3: return None, None

            contract_address = web3.to_checksum_address(self.GOTCHIPUS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.MINT_CONTRACT_ABI)

            mint_data = token_contract.functions.claimWearable()
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

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1
            
            explorer_url = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            logger.tx_success(f"Wearable Claim Transaction Sent! Explorer: {explorer_url}")
            return tx_hash, block_number
        except Exception as e:
            logger.error(f"Message: {e}")
            return None, None
        
    def print_question(self):
        while True:
            try:
                print(f"{Colors.GREEN + Colors.BOLD}Select Option:{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}1. Claim Daily Check-In{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}2. Mint Gotchipus NFT{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}3. Claim Wearable{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}4. Run All Features{Colors.RESET}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3/4] -> {Colors.RESET}").strip())

                if option in [1, 2, 3, 4]:
                    option_type = (
                        "Claim Daily Check-In" if option == 1 else 
                        "Mint Gotchipus NFT" if option == 2 else 
                        "Claim Wearable" if option == 3 else 
                        "Run All Features"
                    )
                    print(f"{Colors.GREEN + Colors.BOLD}{option_type} Selected.{Colors.RESET}")
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Please enter either 1, 2, 3, or 4.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a number (1, 2, 3, or 4).{Colors.RESET}")

        while True:
            try:
                print(f"{Colors.WHITE + Colors.BOLD}1. Run With Private Proxy{Colors.RESET}")
                print(f"{Colors.WHITE + Colors.BOLD}2. Run Without Proxy{Colors.RESET}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Colors.RESET}").strip())

                if choose in [1, 2]:
                    proxy_type = (
                        "With Private" if choose == 1 else 
                        "Without"
                    )
                    print(f"{Colors.GREEN + Colors.BOLD}Run {proxy_type} Proxy Selected.{Colors.RESET}")
                    break
                else:
                    print(f"{Colors.RED + Colors.BOLD}Please enter either 1 or 2.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED + Colors.BOLD}Invalid input. Enter a number (1 or 2).{Colors.RESET}")

        rotate = False
        if choose == 1:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Colors.RESET}").strip()

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
            logger.warn(f"Connection Not 200 OK - {e}")
            return None
        
    async def task_info(self, address: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/tasks/info"
        data = json.dumps({"address":address})
        headers = {
            **self.HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
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
                logger.warn(f"Fetch Last Check-In Failed - {e}")
                return None
            
    async def verify_tasks(self, account: str, address: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/tasks/verify"
        data = json.dumps(self.build_struct_data(account, address))
        headers = {
            **self.HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
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
                logger.error(f"Verify Failed - {e}")
                return None
            
    async def claim_checkin(self, address: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/tasks/checkin"
        data = json.dumps({"address":address, "event":"check_in"})
        headers = {
            **self.HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
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
                logger.warn(f"Not Claimed - {e}")
                return None
    
    async def process_option_1(self, account: str, address: str, use_proxy: bool):
        logger.step("Checking-In...")

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None
        
        tasks = await self.task_info(address, proxy)
        if tasks and tasks.get("code") == 0:
            xp_point = tasks.get("data", {}).get("xp", 0)
            level = tasks.get("data", {}).get("level", 0)
            last_checkin = tasks.get("data", {}).get("latest_check_in_at", None)

            logger.info(f"Points: {xp_point} XP")
            logger.info(f"Level: {level}")

            if last_checkin is None:
                verified = await self.verify_tasks(account, address, proxy)
                if verified and verified.get("code") == 0:
                    logger.success("Verify Success")

                    claim = await self.claim_checkin(address, proxy)
                    if claim and claim.get("code") == 0:
                        logger.success("Claimed Successfully")
                    elif claim and claim.get("code") == 1:
                        err_msg = claim.get("message", "Unknown Error")
                        logger.warn(f"Not Claimed - {err_msg}")

                elif verified and verified.get("code") == 1:
                    err_msg = verified.get("message", "Unknown Error")
                    logger.error(f"Verify Failed - {err_msg}")
            
            else:
                next_checkin = last_checkin + 86400
                if int(time.time()) < next_checkin:
                    formatted_time = datetime.fromtimestamp(next_checkin).astimezone(wib).strftime('%x %X %Z')
                    logger.warn(f"Not Time to Claim - Next Claim at {formatted_time}")
                    return
                
                verified = await self.verify_tasks(account, address, proxy)
                if verified and verified.get("code") == 0:
                    logger.success("Verify Success")

                    claim = await self.claim_checkin(address, proxy)
                    if claim and claim.get("code") == 0:
                        logger.success("Claimed Successfully")
                    elif claim and claim.get("code") == 1:
                        err_msg = claim.get("message", "Unknown Error")
                        logger.warn(f"Not Claimed - {err_msg}")

                elif verified and verified.get("code") == 1:
                    err_msg = verified.get("message", "Unknown Error")
                    logger.error(f"Verify Failed - {err_msg}")

        elif tasks and tasks.get("code") == 1:
            err_msg = tasks.get("message", "Unknown Error")
            logger.error(f"Fetch Last Check-In Failed - {err_msg}")

    async def process_option_2(self, account: str, address: str, use_proxy: bool):
        logger.step("Minting NFT...")
        balance = await self.get_token_balance(address, use_proxy)
        fees = 0.000355

        logger.info(f"Balance: {balance} PHRS")
        logger.info(f"Mint Fee: {fees} PHRS")

        if not balance or balance <=  fees:
            logger.warn("Insufficient PHRS Token Balance")
            return
        
        await self.process_perform_mint_nft(account, address, use_proxy)

    async def process_option_3(self, account: str, address: str, use_proxy: bool):
        logger.step("Claiming Wearable...")
        balance = await self.get_token_balance(address, use_proxy)
        fees = 0.0007
        logger.info(f"Balance: {balance} PHRS")
        logger.info(f"Mint Fee: {fees} PHRS")

        if not balance or balance <=  fees:
            logger.warn("Insufficient PHRS Token Balance")
            return
        
        await self.process_perform_claim_wearable(account, address, use_proxy)

    async def process_check_connection(self, address: int, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            if not use_proxy:
                break 
            logger.info(f"Proxy: {proxy}")

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    continue

                return False
            
            return True

    async def process_accounts(self, account: str, address: str, option: int, use_proxy: bool, rotate_proxy: bool):
        if use_proxy:
            is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
            if not is_valid:
                logger.error("Failed to establish proxy connection.")
                return

        web3 = await self.get_web3_with_check(address, use_proxy)
        if not web3:
            logger.error("Web3 Not Connected")
            return
        
        self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")
        
        if option == 1:
            logger.info("Option: Claim Daily Check-In")
            await self.process_option_1(account, address, use_proxy)
        elif option == 2:
            logger.info("Option: Mint Gotchipus NFT")
            await self.process_option_2(account, address, use_proxy)
        elif option == 3:
            logger.info("Option: Claim Wearable")
            await self.process_option_3(account, address, use_proxy)
        else:
            logger.info("Option: Run All Features")
            
            await self.process_option_1(account, address, use_proxy)
            await asyncio.sleep(5)

            await self.process_option_2(account, address, use_proxy)
            await asyncio.sleep(5)

            await self.process_option_3(account, address, use_proxy)

    async def main(self):
        while True:
            try:
                with open('accounts.txt', 'r') as file:
                    accounts = [line.strip() for line in file if line.strip()]
                
                if not accounts:
                    logger.error("No accounts found in 'accounts.txt'. Please add private keys.")
                    await asyncio.sleep(10)
                    continue

                option, choose, rotate_proxy = self.print_question()

                self.clear_terminal()
                await display_welcome_screen()

                logger.info(f"Account's Total: {len(accounts)}")

                use_proxy = False
                if choose == 1:
                    use_proxy = True
                    await self.load_proxies(1)
                
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        logger.info(f"Processing account: {self.mask_account(address)}")

                        if not address:
                            logger.error("Invalid Private Key or Library Version Not Supported")
                            continue

                        await self.process_accounts(account, address, option, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Colors.CYAN+Colors.BOLD}[ Wait for{Colors.RESET}"
                        f"{Colors.WHITE+Colors.BOLD} {formatted_time} {Colors.RESET}"
                        f"{Colors.CYAN+Colors.BOLD}... ]{Colors.RESET}"
                        f"{Colors.WHITE+Colors.BOLD} | {Colors.RESET}"
                        f"{Fore.BLUE+Style.BRIGHT}All Tasks Completed.{Colors.RESET}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

            except FileNotFoundError:
                logger.error("File 'accounts.txt' Not Found. Please create it and add private keys.")
                await asyncio.sleep(10)
                continue

            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                await asyncio.sleep(10)
                continue

if __name__ == "__main__":
    try:
        bot = Gotchipus()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Colors.CYAN + Colors.BOLD}[ {datetime.now().astimezone(wib).strftime('%H:%M:%S %d.%m.%Y')} ]{Colors.RESET}"
            f"{Colors.WHITE + Colors.BOLD} | {Colors.RESET}"
            f"{Colors.RED + Colors.BOLD}[ EXIT ] Gotchipus - BOT{Colors.RESET}                                       "                              
        )
