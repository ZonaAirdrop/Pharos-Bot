from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_utils import to_hex
from eth_account import Account
from eth_account.messages import encode_defunct
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, random, json, time, re, os

init(autoreset=True)

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
        timestamp_str = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BRIGHT_BLACK}[{timestamp_str}]{Colors.RESET}{symbol}{color}{msg}{Colors.RESET}")

    @staticmethod
    def info(msg): Logger.log("INFO", "[✓]", msg, Colors.GREEN)
    @staticmethod
    def warn(msg): Logger.log("WARN", "[✓]", msg, Colors.YELLOW)
    @staticmethod
    def error(msg): Logger.log("ERR", "[✓]", msg, Colors.RED)
    @staticmethod
    def success(msg): Logger.log("OK", "[✓]", msg, Colors.GREEN)
    @staticmethod
    def loading(msg): Logger.log("LOAD", "[✓]", msg, Colors.CYAN)
    @staticmethod
    def step(msg): Logger.log("STEP", "[✓]", msg, Colors.WHITE)
    @staticmethod
    def action(msg): Logger.log("ACTION", "[✓]", msg, Colors.CYAN)
    @staticmethod
    def actionSuccess(msg): Logger.log("ACTION", "[✓]", msg, Colors.GREEN)

async def display_welcome_screen():
    now = datetime.now()
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}")
    print("╔══════════════════════════════════════╗")
    print("║         AquaFlux   B O T            ║")
    print("║                                      ║")
    print(f"║       {Colors.YELLOW}{now.strftime('%H:%M:%S %d.%m.%Y')}{Colors.BRIGHT_GREEN}         ║")
    print(f"║                                      ║")
    print(f"║    Pharos TESTNET AUTOMATION        ║")
    print(f"║                                      ║")
    print(f"║  {Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}  |  t.me/ZonaAirdr0p    ║")
    print("╚══════════════════════════════════════╝")
    print(f"{Colors.RESET}")

class AquaFlux:
    def __init__(self) -> None:
        self.HEADERS = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://playground.aquaflux.pro",
            "Referer": "https://playground.aquaflux.pro/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api.aquaflux.pro/api/v1"
        self.RPC_URL = "https://testnet.dplabs-internal.com/"
        self.AQUAFLUX_NFT_ADDRESS = "0xCc8cF44E196CaB28DBA2d514dc7353af0eFb370E"
        self.AQUAFLUX_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "claimTokens",
                "stateMutability": "nonpayable",
                "inputs": [],
                "outputs": []
            },
            {
                "type": "function",
                "name": "combineCS",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "amount", "type": "uint256" }
                ],
                "outputs": []
            },
            {
                "type": "function",
                "name": "combinePC",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "amount", "type": "uint256" }
                ],
                "outputs": []
            },
            {
                "type": "function",
                "name": "combinePS",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "amount", "type": "uint256" }
                ],
                "outputs": []
            },
            {
                "type": "function",
                "name": "hasClaimedStandardNFT",
                "stateMutability": "view",
                "inputs": [
                    { "internalType": "address", "name": "owner", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "bool", "name": "", "type": "bool" }
                ]
            },
            {
                "type": "function",
                "name": "hasClaimedPremiumNFT",
                "stateMutability": "view",
                "inputs": [
                    { "internalType": "address", "name": "owner", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "bool", "name": "", "type": "bool" }
                ]
            },
            {
                "type": "function",
                "name": "mint",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "enum AquafluxNFT.NFTType", "name": "nftType", "type": "uint8" },
                    { "internalType": "uint256", "name": "expiresAt", "type": "uint256" },
                    { "internalType": "bytes", "name": "signature", "type": "bytes" }
                ],
                "outputs": []
            }
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.used_nonce = {}
        self.mint_count = 0
        self.min_delay = 0
        self.max_delay = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Colors.BRIGHT_BLACK}[{datetime.now().strftime('%H:%M:%S')}]{Colors.RESET}"
            f"{Fore.GREEN + Style.BRIGHT}[✓]{Style.RESET_ALL}"
            f"{message}",
            flush=True
        )

    def log_status(self, message, symbol="[✓]", color=Colors.GREEN):
        print(
            f"{Colors.BRIGHT_BLACK}[{datetime.now().strftime('%H:%M:%S')}]{Colors.RESET}"
            f"{color}{symbol}{Style.RESET_ALL}"
            f"{message}",
            flush=True
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                if not os.path.exists(filename):
                    self.log_status(f"{Fore.RED}File {filename} Not Found.", color=Colors.RED)
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]

            if not self.proxies and use_proxy_choice == 1:
                self.log_status(f"{Fore.RED}No Proxies Found.", color=Colors.RED)
                return

            if use_proxy_choice == 1:
                self.log_status(
                    f"{Fore.GREEN}Proxies Total: {Fore.WHITE}{len(self.proxies)}{Style.RESET_ALL}", color=Colors.GREEN
                )

        except Exception as e:
            self.log_status(f"{Fore.RED}Failed To Load Proxies: {e}{Style.RESET_ALL}", color=Colors.RED)
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

    def generate_payload(self, account: str, address: str):
        try:
            timestamp = int(time.time()) * 1000
            message = f"Sign in to AquaFlux with timestamp: {timestamp}"
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)

            payload = {
                "address":address,
                "message":message,
                "signature":signature
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
                if attempt == retries - 1:
                    self.log_status(
                        f"{Fore.YELLOW}Send TX Error: {str(e)}{Style.RESET_ALL}", color=Colors.YELLOW
                    )
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
                if attempt == retries - 1:
                    self.log_status(
                        f"{Fore.YELLOW}Wait for Receipt Error: {str(e)}{Style.RESET_ALL}", color=Colors.YELLOW
                    )
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")

    async def check_nft_status(self, address: str, option: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.AQUAFLUX_NFT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.AQUAFLUX_CONTRACT_ABI)

            if option == "Standard NFT":
                nft_status = token_contract.functions.hasClaimedStandardNFT(web3.to_checksum_address(address)).call()
            else:
                nft_status = token_contract.functions.hasClaimedPremiumNFT(web3.to_checksum_address(address)).call()

            return nft_status
        except Exception as e:
            self.log_status(
                f"{Fore.RED}{str(e)}{Style.RESET_ALL}", color=Colors.RED
            )
            return None

    async def perform_claim_tokens(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.AQUAFLUX_NFT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.AQUAFLUX_CONTRACT_ABI)

            claim_data = token_contract.functions.claimTokens()
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
            self.log_status(
                f"{Fore.RED}{str(e)}{Style.RESET_ALL}", color=Colors.RED
            )
            return None, None

    async def perform_combine_tokens(self, account: str, address: str, combine_option: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.AQUAFLUX_NFT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.AQUAFLUX_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(100, "ether")

            if combine_option == "Combine CS":
                combine_data = token_contract.functions.combineCS(amount_to_wei)

            elif combine_option == "Combine PC":
                combine_data = token_contract.functions.combinePC(amount_to_wei)

            elif combine_option == "Combine PS":
                combine_data = token_contract.functions.combinePS(amount_to_wei)

            estimated_gas = combine_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            combine_tx = combine_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, combine_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            self.log_status(
                f"{Fore.RED}{str(e)}{Style.RESET_ALL}", color=Colors.RED
            )
            return None, None

    async def perform_mint_nft(self, account: str, address: str, nft_option: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.AQUAFLUX_NFT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.AQUAFLUX_CONTRACT_ABI)

            nft_type = 0 if nft_option == "Standard NFT" else 1

            data = await self.get_signature(address, nft_type, use_proxy)
            if not data:
                raise Exception("Failed to GET Siganture")

            expiress_at = data["data"]["expiresAt"]
            signature = data["data"]["signature"]

            mint_data = token_contract.functions.mint(nft_type, expiress_at, signature)
            estimated_gas = mint_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            mint_tx = mint_data.build_transaction({
                "from": web3.to_checksum_address(address),
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

            return tx_hash, block_number
        except Exception as e:
            self.log_status(
                f"{Fore.RED}{str(e)}{Style.RESET_ALL}", color=Colors.RED
            )
            return None, None

    async def print_timer(self):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            print(
                f"{Colors.BRIGHT_BLACK}[{datetime.now().strftime('%H:%M:%S')}]{Colors.RESET}"
                f"{Fore.BLUE + Style.BRIGHT}[✓]{Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Fore.WHITE + Style.BRIGHT} {remaining} {Fore.BLUE + Style.BRIGHT}Seconds For Next Tx...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)
        print(" " * 100, end="\r")

    def print_question(self):
        while True:
            try:
                mint_count = int(input(f"{Colors.GREEN + Style.BRIGHT}Enter Total Mint NFT : {Colors.RESET}").strip())
                if mint_count > 0:
                    self.mint_count = mint_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter positive number.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                min_delay = int(input(f"{Colors.GREEN + Style.BRIGHT}Min Delay Each Tx : {Colors.RESET}").strip())
                if min_delay >= 0:
                    self.min_delay = min_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                max_delay = int(input(f"{Colors.GREEN + Style.BRIGHT}Max Delay Each Tx : {Colors.RESET}").strip())
                if max_delay >= min_delay:
                    self.max_delay = max_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= Min Delay.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                print(f"{Colors.WHITE + Style.BRIGHT}1. Run With Private Proxy{Colors.RESET}")
                print(f"{Colors.WHITE + Style.BRIGHT}2. Run Without Proxy{Colors.RESET}")
                choose = int(input(f"{Colors.WHITE + Style.BRIGHT}Choose [1/2] : {Colors.RESET}").strip())

                if choose in [1, 2]:
                    proxy_type = (
                        "With Private Proxy" if choose == 1 else
                        "Without Proxy"
                    )
                    print(f"{Colors.GREEN + Style.BRIGHT}Run {proxy_type} Selected.{Colors.RESET}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        rotate = False
        if choose == 1:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Colors.RESET}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate

    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=10)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            self.log_status(
                f"{Fore.RED}Connection Not 200 OK - {str(e)}{Style.RESET_ALL}", color=Colors.RED
            )
            return None

    async def wallet_login(self, account: str, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/users/wallet-login"
        data = json.dumps(self.generate_payload(account, address))
        headers = {
            **self.HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
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
                self.log_status(
                    f"{Fore.RED}Login Failed - {str(e)}{Style.RESET_ALL}", color=Colors.RED
                )
                return None

    async def check_token_holdings(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/users/check-token-holding"
        headers = {
            **self.HEADERS,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": "0"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    await asyncio.sleep(5)
                    continue
                self.log_status(f"{Fore.RED}Check Token Holdings Failed - {str(e)}{Style.RESET_ALL}", color=Colors.RED)
                return None

    async def check_binding_status(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/users/twitter/binding-status"
        headers = {
            **self.HEADERS,
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    await asyncio.sleep(5)
                    continue
                self.log_status(f"{Fore.RED}Check Binding Status Failed - {str(e)}{Style.RESET_ALL}", color=Colors.RED)
                return None

    async def get_signature(self, address: str, nft_type: int, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/users/get-signature"
        data = json.dumps({"walletAddress":address, "requestedNftType":nft_type})
        headers = {
            **self.HEADERS,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        if response.status == 403:
                            result = await response.json()
                            err_msg = result.get("message", "Unknown Error")
                            self.log_status(f"{Fore.RED}Get Signature Failed: {err_msg}{Style.RESET_ALL}", color=Colors.RED)
                            return None

                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    await asyncio.sleep(5)
                    continue
                self.log_status(f"{Fore.RED}Get Signature Failed - {str(e)}{Style.RESET_ALL}", color=Colors.RED)
                return None

    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        if not use_proxy:
            self.log_status(f"{Colors.GREEN}Proxy: None{Colors.RESET}", color=Colors.GREEN)
            return True

        while True:
            proxy = self.get_next_proxy_for_account(address)
            self.log_status(
                f"{Colors.GREEN}Proxy: {Colors.WHITE}{proxy}{Colors.RESET}", color=Colors.GREEN
            )

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    continue
                return False
            return True

    async def process_wallet_login(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
       is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
       if is_valid:
            login = await self.wallet_login(account, address, use_proxy)
            if login:
                self.access_tokens[address] = login["data"]["accessToken"]
                self.log_status(f"{Colors.GREEN}Status: Login Success{Colors.RESET}", color=Colors.GREEN)
                return True
            return False

    async def process_perform_claim_tokens(self, account: str, address: str, use_proxy: bool):
        self.log_status(f"{Colors.GREEN}Claiming Tokens...{Colors.RESET}", color=Colors.GREEN)

        tx_hash, block_number = await self.perform_claim_tokens(account, address, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log_status(f"{Colors.GREEN}Status: Success{Colors.RESET}", color=Colors.GREEN)
            self.log_status(f"{Colors.GREEN}Tx Hash: {tx_hash}{Colors.RESET}", symbol="[↪️]", color=Colors.GREEN)
            self.log_status(f"{Colors.GREEN}Explorer: {explorer}{Colors.RESET}", symbol="[✅]", color=Colors.GREEN)
            return True

        else:
            self.log_status(f"{Fore.RED}Status: Perform On-Chain Failed{Style.RESET_ALL}", color=Colors.RED)
        return False

    async def process_perform_combine_tokens(self, account: str, address: str, use_proxy: bool):
        self.log_status(f"{Colors.GREEN}Combining Tokens...{Colors.RESET}", color=Colors.GREEN)

        holdings = await self.check_token_holdings(address, use_proxy)
        if holdings:
            is_holdings = holdings.get("data", {}).get("isHoldingToken")

            if is_holdings == False:
                combine_option = random.choice(["Combine CS", "Combine PC", "Combine PS"])

                tx_hash, block_number = await self.perform_combine_tokens(account, address, combine_option, use_proxy)
                if tx_hash and block_number:
                    explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

                    self.log_status(f"{Colors.GREEN}Status: Success{Colors.RESET}", color=Colors.GREEN)
                    self.log_status(f"{Colors.GREEN}Tx Hash: {tx_hash}{Colors.RESET}", symbol="[↪️]", color=Colors.GREEN)
                    self.log_status(f"{Colors.GREEN}Explorer: {explorer}{Colors.RESET}", symbol="[✅]", color=Colors.GREEN)

                    await asyncio.sleep(10)

                    holdings = await self.check_token_holdings(address, use_proxy)
                    if holdings:
                        is_holdings = holdings.get("data", {}).get("isHoldingToken")
                        if is_holdings == True: return True

                    self.log_status(f"{Fore.YELLOW}Status: Refresh Holding Status Failed{Style.RESET_ALL}", color=Colors.YELLOW)
                    return False
                else:
                    self.log_status(f"{Fore.RED}Status: Perform On-Chain Failed{Style.RESET_ALL}", color=Colors.RED)
                    return False
            else:
                self.log_status(f"{Colors.GREEN}Status: Already Combined{Colors.RESET}", color=Colors.GREEN)
                return True
        return False

    async def process_perform_mint_nft(self, account: str, address: str, nft_option: str, use_proxy: bool):
        self.log_status(f"{Colors.GREEN}Attempting to Mint NFT...{Colors.RESET}", color=Colors.GREEN)

        tx_hash, block_number = await self.perform_mint_nft(account, address, nft_option, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log_status(f"{Colors.GREEN}Status: Mint {nft_option} Success{Colors.RESET}", color=Colors.GREEN)
            self.log_status(f"{Colors.GREEN}Tx Hash: {tx_hash}{Colors.RESET}", symbol="[↪️]", color=Colors.GREEN)
            self.log_status(f"{Colors.GREEN}Explorer: {explorer}{Colors.RESET}", symbol="[✅]", color=Colors.GREEN)
        else:
            self.log_status(f"{Fore.RED}Status: Perform On-Chain Failed{Style.RESET_ALL}", color=Colors.RED)

    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool, account_index: int):
        print(f"\n{Colors.GREEN}[✓]Account {account_index} {self.mask_account(address)}{Colors.RESET}")

        logined = await self.process_wallet_login(account, address, use_proxy, rotate_proxy)
        if logined:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log_status(f"{Fore.RED}Status: Web3 Not Connected{Style.RESET_ALL}", color=Colors.RED)
                return

            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")

            for i in range(self.mint_count):
                self.log_status(
                    f"{Colors.GREEN}Mint {Colors.WHITE}{i+1}{Colors.RESET}"
                    f"{Colors.GREEN} Of {Colors.WHITE}{self.mint_count}{Colors.RESET}", color=Colors.GREEN
                )

                for nft_option in ["Standard NFT", "Premium NFT"]:
                    self.log_status(f"{Colors.GREEN}{nft_option}{Colors.RESET}", color=Colors.GREEN)

                    if nft_option == "Premium NFT":
                        binding = await self.check_binding_status(address, use_proxy)
                        if not binding: continue

                        is_bound = binding.get("data", {}).get("bound")
                        if is_bound == False:
                            self.log_status(f"{Fore.YELLOW}Status: Not Eligible, Bind Your Twitter First{Style.RESET_ALL}", color=Colors.YELLOW)
                            continue

                        has_claimed = await self.check_nft_status(address, nft_option, use_proxy)
                        if has_claimed:
                            self.log_status(f"{Fore.YELLOW}Status: {nft_option} Already Minted{Style.RESET_ALL}", color=Colors.YELLOW)
                            continue

                    is_claimed = await self.process_perform_claim_tokens(account, address, use_proxy)
                    if not is_claimed: continue

                    await self.print_timer()

                    is_combined = await self.process_perform_combine_tokens(account, address, use_proxy)
                    if not is_combined: continue

                    await self.print_timer()

                    await self.process_perform_mint_nft(account, address, nft_option, use_proxy)

                    await self.print_timer()

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            await display_welcome_screen()

            use_proxy_choice, rotate_proxy = self.print_question()

            use_proxy = (use_proxy_choice == 1)

            self.log_status(f"{Colors.GREEN}Account's Total: {len(accounts)}{Colors.RESET}", color=Colors.GREEN)

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            for i, account in enumerate(accounts):
                if account:
                    address = self.generate_address(account)

                    if not address:
                        self.log_status(f"{Fore.RED}Status: Invalid Private Key or Library Version Not Supported{Style.RESET_ALL}", color=Colors.RED)
                        continue

                    await self.process_accounts(account, address, use_proxy, rotate_proxy, i + 1)
                    await asyncio.sleep(3)

            print(f"{Colors.BRIGHT_BLACK}[{datetime.now().strftime('%H:%M:%S')}]{Colors.RESET}"
                  f"{Fore.CYAN+Style.BRIGHT}[✓]{Style.RESET_ALL}"
                  f"{Fore.CYAN+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}")
            
            seconds = 24 * 60 * 60
            while seconds > 0:
                formatted_time = self.format_seconds(seconds)
                print(
                    f"\r{Colors.BRIGHT_BLACK}[{datetime.now().strftime('%H:%M:%S')}]{Colors.RESET}"
                    f"{Fore.CYAN+Style.BRIGHT}[✓]{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}Wait for {Fore.WHITE+Style.BRIGHT}{formatted_time}{Style.RESET_ALL}",
                    end=""
                )
                await asyncio.sleep(1)
                seconds -= 1
            print() # Move to next line after countdown finishes

        except FileNotFoundError:
            self.log_status(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}", color=Colors.RED)
            return
        except Exception as e:
            self.log_status(f"{Fore.RED}Error: {e}{Style.RESET_ALL}", color=Colors.RED)
            raise e

if __name__ == "__main__":
    try:
        bot = AquaFlux()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"\n{Colors.BRIGHT_BLACK}[{datetime.now().strftime('%H:%M:%S')}]{Colors.RESET}"
            f"{Fore.RED + Style.BRIGHT}[EXIT]{Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}AquaFlux NFT - BOT{Style.RESET_ALL}"
        )
