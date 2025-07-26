from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
import asyncio
import random
import json
import os
import pytz
from colorama import *

wib = pytz.timezone('Asia/Jakarta')

class PrimusLabs:
    def __init__(self) -> None:
        self.HEADERS = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://social.primuslabs.org",
            "Referer": "https://social.primuslabs.org/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api.primuslabs.org"
        self.RPC_URL = "https://api.zan.top/node/v1/pharos/testnet/54b49326c9f44b6e8730dc5dd4348421"
        self.SOCIAL_TRANSFER_ADDRESS = "0xD17512B7EC12880Bd94Eca9d774089fF89805F02"
        self.RED_PACKET_ADDRESS = "0x673D74d95A35B26804475066d9cD1DA3947f4eC3"
        self.CHAIN_ID = 688688
        
        # Social Transfer Contract ABI - updated based on actual transaction
        self.SOCIAL_TRANSFER_ABI = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "param1", "type": "uint256"},
                    {"internalType": "uint256", "name": "param2", "type": "uint256"},
                    {"internalType": "bytes", "name": "param3", "type": "bytes"},
                    {"internalType": "bytes", "name": "param4", "type": "bytes"},
                    {"internalType": "uint256", "name": "param5", "type": "uint256"},
                    {"internalType": "uint256", "name": "param6", "type": "uint256"}
                ],
                "name": "socialTransfer", 
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        
        # ERC20 ABI for balance checking
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]}
        ]''')
        
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        self.transfer_count = 0
        self.transfer_amount = 0
        self.red_packet_count = 0
        self.red_packet_amount = 0
        self.min_delay = 0
        self.max_delay = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\n" + "═" * 60)
        print(Fore.GREEN + Style.BRIGHT + "    ⚡ Pharos Testnet Automation BOT  ⚡")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.YELLOW + Style.BRIGHT + "    🧠 Project    : Primus Labs Social - Automation Bot")
        print(Fore.YELLOW + Style.BRIGHT + "    🧑‍💻 Author     : YetiDAO")
        print(Fore.YELLOW + Style.BRIGHT + "    🌐 Status     : Running & Monitoring...")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.MAGENTA + Style.BRIGHT + "    🧬 Powered by Cryptodai3 × YetiDAO | Buddy v1.7 🚀")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "═" * 60 + "\n")

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}Proxy file not found: {filename}{Style.RESET_ALL}")
                return
            
            with open(filename, 'r') as file:
                proxies = [line.strip() for line in file if line.strip()]
            
            if not proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No proxies found in {filename}{Style.RESET_ALL}")
                return
            
            self.proxies = proxies
            self.log(f"{Fore.GREEN + Style.BRIGHT}Loaded {len(self.proxies)} proxies{Style.RESET_ALL}")
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Error loading proxies: {str(e)}{Style.RESET_ALL}")

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            self.account_proxies[token] = self.rotate_proxy_for_account(token)
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
            parts = proxy.replace("http://", "").replace("https://", "")
            if "@" in parts:
                auth_part, host_part = parts.split("@", 1)
                if ":" in auth_part:
                    username, password = auth_part.split(":", 1)
                    auth = BasicAuth(username, password)
                    return None, f"http://{host_part}", auth
            return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def generate_address(self, account: str):
        try:
            account_obj = Account.from_key(account)
            return account_obj.address
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Error generating address: {str(e)}{Style.RESET_ALL}")
            return None
        
    def mask_account(self, account):
        try:
            if len(account) <= 10:
                return f"{account[:4]}...{account[-2:]}"
            return f"{account[:6]}...{account[-4:]}"
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Error masking account: {str(e)}{Style.RESET_ALL}")
            return "Unknown"
        
    async def get_web3_with_check(self, address: str, use_proxy: bool, retries=3, timeout=60):
        request_kwargs = {}

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if use_proxy and proxy:
            connector, proxy_url, proxy_auth = self.build_proxy_config(proxy)
            if connector:
                request_kwargs["connector"] = connector
            if proxy_url and proxy_auth:
                request_kwargs["proxy"] = proxy_url
                request_kwargs["proxy_auth"] = proxy_auth

        for attempt in range(retries):
            try:
                # Create Web3 instance with simple HTTP provider
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL))
                
                # Test connection
                is_connected = await asyncio.get_event_loop().run_in_executor(None, web3.is_connected)
                if is_connected:
                    latest_block = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_block, 'latest')
                    if latest_block:
                        return web3
                    
            except Exception as e:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}Web3 connection attempt {attempt + 1} failed: {str(e)}{Style.RESET_ALL}")
                
                if attempt < retries - 1:
                    await asyncio.sleep(2)
        
        return None
        
    async def get_phrs_balance(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                return 0
            
            balance_wei = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_balance, address)
            balance_phrs = web3.from_wei(balance_wei, 'ether')
            return float(balance_phrs)
            
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Error getting PHRS balance: {str(e)}{Style.RESET_ALL}")
            return 0
        
    async def send_raw_transaction_with_retries(self, account, web3, tx, retries=5):
        for attempt in range(retries):
            try:
                signed_tx = web3.eth.account.sign_transaction(tx, private_key=account)
                # Use raw_transaction instead of rawTransaction for newer web3.py versions
                raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
                tx_hash = await asyncio.get_event_loop().run_in_executor(None, web3.eth.send_raw_transaction, raw_tx)
                return web3.to_hex(tx_hash)
            except Exception as e:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}Transaction attempt {attempt + 1} failed: {str(e)}{Style.RESET_ALL}")
                if attempt < retries - 1:
                    await asyncio.sleep(2)
        raise Exception("Transaction Hash Not Found After Maximum Retries")

    async def wait_for_receipt_with_retries(self, web3, tx_hash, retries=5):
        for attempt in range(retries):
            try:
                receipt = await asyncio.get_event_loop().run_in_executor(None, web3.eth.wait_for_transaction_receipt, tx_hash)
                return receipt
            except TransactionNotFound:
                if attempt < retries - 1:
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}Receipt not found, retrying... ({attempt + 1}/{retries}){Style.RESET_ALL}")
                    await asyncio.sleep(5)
            except Exception as e:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}Receipt attempt {attempt + 1} failed: {str(e)}{Style.RESET_ALL}")
                if attempt < retries - 1:
                    await asyncio.sleep(5)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")

    def generate_random_social_data(self):
        """Generate random social transfer data"""
        post_id = random.randint(1, 1000)
        comment_id = 0  # Usually 0 for post tips
        
        # Random recipient usernames
        recipients = ["alice", "bob", "charlie", "diana", "eve", "frank", "grace", "henry"]
        recipient = random.choice(recipients).encode('utf-8')
        
        # Random tip messages
        messages = [
            "Great post! 👍",
            "Thanks for sharing!",
            "Amazing content!",
            "Keep it up! 🚀",
            "Love this! ❤️",
            "Awesome work!",
            "So helpful!",
            "Nice! 🔥"
        ]
        message = random.choice(messages).encode('utf-8')
        
        tip_type = 1  # Type 1 for regular tips
        
        return post_id, comment_id, recipient, message, tip_type

    async def perform_social_transfer(self, account: str, address: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to connect to Web3{Style.RESET_ALL}")
                return None, None
            
            # Generate random social data
            post_id, comment_id, recipient, message, tip_type = self.generate_random_social_data()
            
            # Convert amount to wei
            amount_wei = web3.to_wei(amount, 'ether')
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Transfer Details: Post ID: {post_id}, Recipient: {recipient.decode()}, Amount: {amount} PHRS{Style.RESET_ALL}")
            
            # Get nonce
            nonce_key = f"{address}_social_transfer"
            if nonce_key in self.used_nonce:
                nonce = self.used_nonce[nonce_key] + 1
            else:
                nonce = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_transaction_count, address)
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Using nonce: {nonce}{Style.RESET_ALL}")
            
            # Build exact transaction data from your provided structure
            # Only manipulate the amount, keep everything else exactly the same
            function_selector = "8e57fa5d"
            
            # Fixed parameters from your original transaction (everything stays the same except amount)
            param1 = "0000000000000000000000000000000000000000000000000000000000000001"  # Fixed
            param2 = "0000000000000000000000000000000000000000000000000000000000000000"  # Fixed
            param3 = "0000000000000000000000000000000000000000000000000000000000000060"  # Fixed
            param4 = "0000000000000000000000000000000000000000000000000000000000000080"  # Fixed
            param5 = "00000000000000000000000000000000000000000000000000000000000000c0"  # Fixed
            param6 = format(amount_wei, '064x')  # DYNAMIC amount - this changes based on user input
            param7 = "0000000000000000000000000000000000000000000000000000000000000100"  # Fixed
            param8 = "0000000000000000000000000000000000000000000000000000000000000001"  # Fixed
            param9 = "7800000000000000000000000000000000000000000000000000000000000000"  # Fixed
            param10 = "0000000000000000000000000000000000000000000000000000000000000006"  # Fixed
            param11 = "6169716e62680000000000000000000000000000000000000000000000000000"  # Fixed
            param12 = "0000000000000000000000000000000000000000000000000000000000000000"  # Fixed
            
            # Combine all data exactly as in your structure
            transaction_data = "0x" + function_selector + param1 + param2 + param3 + param4 + param5 + param6 + param7 + param8 + param9 + param10 + param11 + param12
            
            # Get current gas price from network
            try:
                gas_price = await asyncio.get_event_loop().run_in_executor(None, lambda: web3.eth.gas_price)
            except:
                # Fallback to manual gas price
                gas_price = web3.to_wei(1.2, 'gwei')
            
            # Build transaction
            tx = {
                'chainId': self.CHAIN_ID,
                'gas': 300000,  # Increase gas limit
                'gasPrice': gas_price,  # Use network gas price
                'nonce': nonce,
                'to': web3.to_checksum_address(self.SOCIAL_TRANSFER_ADDRESS),
                'value': amount_wei,  # The tip amount sent as value
                'data': transaction_data
            }
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Gas Price: {web3.from_wei(gas_price, 'gwei')} gwei, Gas Limit: 300000{Style.RESET_ALL}")
            
            # Send transaction
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
            self.used_nonce[nonce_key] = nonce
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}📝 Transaction sent: {tx_hash}{Style.RESET_ALL}")
            
            # Wait for receipt
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            
            if receipt and receipt.status == 1:
                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Transaction confirmed in block {receipt.blockNumber}{Style.RESET_ALL}")
                return tx_hash, receipt.blockNumber
            else:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Transaction failed - Status: {receipt.status if receipt else 'No receipt'}{Style.RESET_ALL}")
                return None, None
            
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error performing social transfer: {str(e)}{Style.RESET_ALL}")
            return None, None

    async def perform_red_packet_transfer(self, account: str, address: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to connect to Web3{Style.RESET_ALL}")
                return None, None
            
            # Convert amount to wei
            amount_wei = web3.to_wei(amount, 'ether')
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🧧 Red Packet Details: Amount: {amount} PHRS{Style.RESET_ALL}")
            
            # Get nonce
            nonce_key = f"{address}_red_packet"
            if nonce_key in self.used_nonce:
                nonce = self.used_nonce[nonce_key] + 1
            else:
                nonce = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_transaction_count, address)
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Using nonce: {nonce}{Style.RESET_ALL}")
            
            # Build exact red packet transaction data from your provided structure
            # Only manipulate the amount, keep everything else exactly the same
            function_selector = "22a014c9"
            
            # Fixed parameters from your red packet transaction (everything stays the same except amount)
            param1 = "0000000000000000000000000000000000000000000000000000000000000001"  # Fixed
            param2 = "0000000000000000000000000000000000000000000000000000000000000000"  # Fixed
            param3 = "0000000000000000000000000000000000000000000000000000000000000060"  # Fixed
            param4 = "0000000000000000000000000000000000000000000000000000000000000001"  # Fixed
            param5 = "0000000000000000000000000000000000000000000000000000000000000002"  # Fixed
            param6 = format(amount_wei, '064x')  # DYNAMIC amount - this changes based on user input
            param7 = "0000000000000000000000000000000000000000000000000000000000000000"  # Fixed
            param8 = "00000000000000000000000000000000000000000000000000000000000000a0"  # Fixed
            param9 = "0000000000000000000000000000000000000000000000000000000000000080"  # Fixed
            param10 = "0000000000000000000000000000000000000000000000000000000000000000"  # Fixed
            param11 = "0000000000000000000000000000000000000000000000000000000000000040"  # Fixed
            param12 = "0000000000000000000000000000000000000000000000000000000000000006"  # Fixed
            param13 = "6169716e62680000000000000000000000000000000000000000000000000000"  # Fixed
            
            # Combine all data exactly as in your structure
            transaction_data = "0x" + function_selector + param1 + param2 + param3 + param4 + param5 + param6 + param7 + param8 + param9 + param10 + param11 + param12 + param13
            
            # Get current gas price from network
            try:
                gas_price = await asyncio.get_event_loop().run_in_executor(None, lambda: web3.eth.gas_price)
            except:
                # Fallback to manual gas price
                gas_price = web3.to_wei(1.2, 'gwei')
            
            # Build transaction
            tx = {
                'chainId': self.CHAIN_ID,
                'gas': 300000,  # Gas limit
                'gasPrice': gas_price,  # Use network gas price
                'nonce': nonce,
                'to': web3.to_checksum_address(self.RED_PACKET_ADDRESS),
                'value': amount_wei,  # The red packet amount sent as value
                'data': transaction_data
            }
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Gas Price: {web3.from_wei(gas_price, 'gwei')} gwei, Gas Limit: 300000{Style.RESET_ALL}")
            
            # Send transaction
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
            self.used_nonce[nonce_key] = nonce
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}📝 Transaction sent: {tx_hash}{Style.RESET_ALL}")
            
            # Wait for receipt
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            
            if receipt and receipt.status == 1:
                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Transaction confirmed in block {receipt.blockNumber}{Style.RESET_ALL}")
                return tx_hash, receipt.blockNumber
            else:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Transaction failed - Status: {receipt.status if receipt else 'No receipt'}{Style.RESET_ALL}")
                return None, None
            
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error performing red packet transfer: {str(e)}{Style.RESET_ALL}")
            return None, None
        
    async def print_timer(self):
        delay = random.randint(self.min_delay, self.max_delay)
        for remaining in range(delay, 0, -1):
            print(
                f"\r{Fore.CYAN + Style.BRIGHT}⏳ Next operation in: "
                f"{Fore.YELLOW + Style.BRIGHT}{self.format_seconds(remaining)}{Style.RESET_ALL}",
                end="",
                flush=True
            )
            await asyncio.sleep(1)
        print()

    def print_transfer_question(self):
        while True:
            try:
                print(f"\n{Fore.CYAN + Style.BRIGHT}🎯 Social Transfer Configuration:{Style.RESET_ALL}")
                self.transfer_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How many transfers per account? {Style.RESET_ALL}"))
                if self.transfer_count > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

        while True:
            try:
                self.transfer_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Transfer amount (PHRS): {Style.RESET_ALL}"))
                if self.transfer_amount > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive amount{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid amount{Style.RESET_ALL}")

    def print_red_packet_question(self):
        while True:
            try:
                print(f"\n{Fore.RED + Style.BRIGHT}🧧 Red Packet Configuration:{Style.RESET_ALL}")
                self.red_packet_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How many red packets per account? {Style.RESET_ALL}"))
                if self.red_packet_count > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

        while True:
            try:
                self.red_packet_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Red packet amount (PHRS): {Style.RESET_ALL}"))
                if self.red_packet_amount > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive amount{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid amount{Style.RESET_ALL}")

    def print_delay_question(self):
        while True:
            try:
                print(f"\n{Fore.CYAN + Style.BRIGHT}⏱️  Delay Configuration:{Style.RESET_ALL}")
                self.min_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Minimum delay between operations (seconds): {Style.RESET_ALL}"))
                if self.min_delay >= 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a non-negative number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

        while True:
            try:
                self.max_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Maximum delay between operations (seconds): {Style.RESET_ALL}"))
                if self.max_delay >= self.min_delay:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Maximum delay must be >= minimum delay{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")
        
    def print_question(self):
        while True:
            try:
                print(f"\n{Fore.CYAN + Style.BRIGHT}🚀 Choose Operation:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1.{Style.RESET_ALL} Social Transfer")
                print(f"{Fore.WHITE + Style.BRIGHT}2.{Style.RESET_ALL} Red Packet Transfer")
                print(f"{Fore.WHITE + Style.BRIGHT}3.{Style.RESET_ALL} Check Balance")
                
                choose = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter your choice (1-3): {Style.RESET_ALL}"))
                if choose in [1, 2, 3]:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter 1, 2, or 3{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

        while True:
            try:
                print(f"\n{Fore.CYAN + Style.BRIGHT}🌐 Proxy Configuration:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1.{Style.RESET_ALL} Use proxy")
                print(f"{Fore.WHITE + Style.BRIGHT}2.{Style.RESET_ALL} Don't use proxy")
                
                proxy_choice = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter your choice (1-2): {Style.RESET_ALL}"))
                if proxy_choice in [1, 2]:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter 1 or 2{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

        use_proxy = proxy_choice == 1
        rotate_proxy = False
        
        if use_proxy:
            while True:
                try:
                    print(f"\n{Fore.CYAN + Style.BRIGHT}🔄 Proxy Rotation:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE + Style.BRIGHT}1.{Style.RESET_ALL} Rotate proxy for each account")
                    print(f"{Fore.WHITE + Style.BRIGHT}2.{Style.RESET_ALL} Use same proxy for all accounts")
                    
                    rotate_choice = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter your choice (1-2): {Style.RESET_ALL}"))
                    if rotate_choice in [1, 2]:
                        rotate_proxy = rotate_choice == 1
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}❌ Please enter 1 or 2{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")
        
        if choose == 1:
            self.print_transfer_question()
            self.print_delay_question()
        elif choose == 2:
            self.print_red_packet_question()
            self.print_delay_question()

        return choose, use_proxy, rotate_proxy
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            request_kwargs = {"timeout": ClientTimeout(total=10)}
            if connector:
                request_kwargs["connector"] = connector
            if proxy and proxy_auth:
                request_kwargs["proxy"] = proxy
                request_kwargs["proxy_auth"] = proxy_auth

            async with ClientSession(**request_kwargs) as session:
                async with session.get("https://httpbin.org/ip") as response:
                    if response.status == 200:
                        return True
                    return False
        except (Exception, ClientResponseError) as e:
            return False
        
    async def process_check_connection(self, address: int, use_proxy: bool, rotate_proxy: bool):
        if use_proxy:
            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(address)
            else:
                proxy = self.get_next_proxy_for_account(address)
            
            connection_status = await self.check_connection(proxy)
            status_text = f"{Fore.GREEN + Style.BRIGHT}Connected{Style.RESET_ALL}" if connection_status else f"{Fore.RED + Style.BRIGHT}Failed{Style.RESET_ALL}"
            proxy_text = f" | Proxy: {proxy}" if proxy else ""
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}Connection Status: {status_text}{proxy_text}{Style.RESET_ALL}")
        else:
            connection_status = await self.check_connection()
            status_text = f"{Fore.GREEN + Style.BRIGHT}Connected{Style.RESET_ALL}" if connection_status else f"{Fore.RED + Style.BRIGHT}Failed{Style.RESET_ALL}"
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}Direct Connection Status: {status_text}{Style.RESET_ALL}")
    
    async def process_perform_social_transfer(self, account: str, address: str, amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_social_transfer(account, address, amount, use_proxy)
        if tx_hash and block_number:
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}✅ Social Transfer Success{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | "
                f"Hash: {tx_hash[:10]}...{tx_hash[-6:]} | "
                f"Block: {block_number} | "
                f"Amount: {amount} PHRS{Style.RESET_ALL}"
            )
            return True
        else:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Social Transfer Failed{Style.RESET_ALL}")
            return False

    async def process_perform_red_packet_transfer(self, account: str, address: str, amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_red_packet_transfer(account, address, amount, use_proxy)
        if tx_hash and block_number:
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}✅ Red Packet Transfer Success{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | "
                f"Hash: {tx_hash[:10]}...{tx_hash[-6:]} | "
                f"Block: {block_number} | "
                f"Amount: {amount} PHRS{Style.RESET_ALL}"
            )
            return True
        else:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Red Packet Transfer Failed{Style.RESET_ALL}")
            return False

    async def process_option_1(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Social Transfer Operations{Style.RESET_ALL}"
        )
        
        success_count = 0
        for i in range(self.transfer_count):
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}📤 Transfer {i+1}/{self.transfer_count}{Style.RESET_ALL}"
            )
            
            balance = await self.get_phrs_balance(address, use_proxy)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Balance:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance:.6f} PHRS {Style.RESET_ALL}"
            )
            
            if balance < self.transfer_amount:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Insufficient balance for transfer{Style.RESET_ALL}")
                break
            
            success = await self.process_perform_social_transfer(account, address, self.transfer_amount, use_proxy)
            if success:
                success_count += 1
            
            if i < self.transfer_count - 1:
                await self.print_timer()
        
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}📊 Transfer Summary: {success_count}/{self.transfer_count} successful{Style.RESET_ALL}"
        )

    async def process_option_2(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.RED+Style.BRIGHT}Red Packet Operations{Style.RESET_ALL}"
        )
        
        success_count = 0
        for i in range(self.red_packet_count):
            self.log(
                f"{Fore.RED+Style.BRIGHT}🧧 Red Packet {i+1}/{self.red_packet_count}{Style.RESET_ALL}"
            )
            
            balance = await self.get_phrs_balance(address, use_proxy)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Balance:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance:.6f} PHRS {Style.RESET_ALL}"
            )
            
            if balance < self.red_packet_amount:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Insufficient balance for red packet{Style.RESET_ALL}")
                break
            
            success = await self.process_perform_red_packet_transfer(account, address, self.red_packet_amount, use_proxy)
            if success:
                success_count += 1
            
            if i < self.red_packet_count - 1:
                await self.print_timer()
        
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}📊 Red Packet Summary: {success_count}/{self.red_packet_count} successful{Style.RESET_ALL}"
        )

    async def process_option_3(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Balance Check{Style.RESET_ALL}"
        )
        
        balance = await self.get_phrs_balance(address, use_proxy)
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}💰 PHRS Balance:{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {balance:.6f} PHRS {Style.RESET_ALL}"
        )

    async def process_accounts(self, account: str, address: str, option: int, use_proxy: bool, rotate_proxy: bool):
        masked_account = self.mask_account(account)
        short_address = f"{address[:6]}...{address[-4:]}"
        
        self.log(
            f"{Fore.YELLOW + Style.BRIGHT}👤 Account: {masked_account} | Address: {short_address}{Style.RESET_ALL}"
        )
        
        await self.process_check_connection(address, use_proxy, rotate_proxy)
        
        if option == 1:
            await self.process_option_1(account, address, use_proxy)
        elif option == 2:
            await self.process_option_2(account, address, use_proxy)
        elif option == 3:
            await self.process_option_3(account, address, use_proxy)

    async def main(self):
        self.clear_terminal()
        self.welcome()
        
        option, use_proxy, rotate_proxy = self.print_question()
        
        if use_proxy:
            await self.load_proxies(True)
        
        # Load accounts
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ accounts.txt file not found{Style.RESET_ALL}")
            return
        
        if not accounts:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ No accounts found in accounts.txt{Style.RESET_ALL}")
            return
        
        self.log(f"{Fore.GREEN + Style.BRIGHT}📋 Loaded {len(accounts)} accounts{Style.RESET_ALL}")
        
        for i, account in enumerate(accounts):
            try:
                address = self.generate_address(account)
                if not address:
                    continue
                
                self.log(f"\n{Fore.MAGENTA + Style.BRIGHT}{'='*60}{Style.RESET_ALL}")
                self.log(f"{Fore.CYAN + Style.BRIGHT}🚀 Processing Account {i+1}/{len(accounts)}{Style.RESET_ALL}")
                
                await self.process_accounts(account, address, option, use_proxy, rotate_proxy)
                
                if i < len(accounts) - 1:
                    self.log(f"\n{Fore.YELLOW + Style.BRIGHT}⏸️  Moving to next account...{Style.RESET_ALL}")
                    await asyncio.sleep(3)
                    
            except Exception as e:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Error processing account {i+1}: {str(e)}{Style.RESET_ALL}")
                continue
        
        self.log(f"\n{Fore.GREEN + Style.BRIGHT}🎉 All accounts processed successfully!{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        primus = PrimusLabs()
        asyncio.run(primus.main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED + Style.BRIGHT}❌ Process interrupted by user{Style.RESET_ALL}")
