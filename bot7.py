from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from eth_utils import to_hex
from eth_abi.abi import encode
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
import asyncio
import random
import secrets
import json
import time
import os
import pytz
from colorama import *

wib = pytz.timezone('Asia/Jakarta')

class ZenithSwap:
    def __init__(self) -> None:
        self.HEADERS = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://zenith.swap.org",
            "Referer": "https://zenith.swap.org/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api.zenith.org"
        self.RPC_URL = "https://api.zan.top/node/v1/pharos/testnet/54b49326c9f44b6e8730dc5dd4348421"
        
        # Contract Addresses
        self.ZENITH_SWAP_ADDRESS = "0x1A4DE519154Ae51200b0Ad7c90F7faC75547888a"
        self.WPHRS_CONTRACT_ADDRESS = "0x76aaaDA469D23216bE5f7C596fA25F282Ff9b364"
        self.USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
        self.USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
        self.SWAP_ROUTER_ADDRESS = "0x1A4DE519154Ae51200b0Ad7c90F7faC75547888a"
        self.POSITION_MANAGER_ADDRESS = "0xF8a1D4FF0f9b9Af7CE58E1fc1833688F3BFd6115"
        
        self.CHAIN_ID = 688688
        
        # Enhanced ERC20 ABI
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"deposit","stateMutability":"payable","inputs":[],"outputs":[]},
            {"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"wad","type":"uint256"}],"outputs":[]}
        ]''')
        
        # Swap Contract ABI
        self.SWAP_CONTRACT_ABI = [
            {
                "inputs": [
                    { "internalType": "uint256", "name": "deadline", "type": "uint256" },
                    { "internalType": "bytes[]", "name": "data", "type": "bytes[]" }
                ],
                "name": "multicall",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        
        # Add Liquidity Contract ABI
        self.ADD_LP_CONTRACT_ABI = [
            {
                "inputs": [
                    {
                        "components": [
                            { "internalType": "address", "name": "token0", "type": "address" },
                            { "internalType": "address", "name": "token1", "type": "address" },
                            { "internalType": "uint24", "name": "fee", "type": "uint24" },
                            { "internalType": "int24", "name": "tickLower", "type": "int24" },
                            { "internalType": "int24", "name": "tickUpper", "type": "int24" },
                            { "internalType": "uint256", "name": "amount0Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount0Min", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Min", "type": "uint256" },
                            { "internalType": "address", "name": "recipient", "type": "address" },
                            { "internalType": "uint256", "name": "deadline", "type": "uint256" },
                        ],
                        "internalType": "struct INonfungiblePositionManager.MintParams",
                        "name": "params",
                        "type": "tuple",
                    },
                ],
                "name": "mint",
                "outputs": [
                    { "internalType": "uint256", "name": "tokenId", "type": "uint256" },
                    { "internalType": "uint128", "name": "liquidity", "type": "uint128" },
                    { "internalType": "uint256", "name": "amount0", "type": "uint256" },
                    { "internalType": "uint256", "name": "amount1", "type": "uint256" },
                ],
                "stateMutability": "payable",
                "type": "function",
            },
        ]
        
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        
        # Original swap parameters
        self.usdt_swap_count = 0
        self.usdt_swap_amount = 0
        self.usdc_swap_count = 0
        self.usdc_swap_amount = 0
        
        # New enhanced parameters
        self.add_lp_count = 0
        self.swap_count = 0
        self.wphrs_amount = 0
        self.usdc_amount = 0
        self.usdt_amount = 0
        self.wrap_option = None
        self.wrap_amount = 0
        
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
        print(Fore.YELLOW + Style.BRIGHT + "    🧠 Project    : Zenith Swap - Automation Bot")
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

    async def perform_usdt_swap(self, account: str, address: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to connect to Web3{Style.RESET_ALL}")
                return None, None
            
            # Convert amount to wei (assuming 18 decimals for calculation)
            amount_wei = web3.to_wei(amount, 'ether')
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}💱 USDT Swap Details: Amount: {amount} tokens{Style.RESET_ALL}")
            
            # Get nonce
            nonce_key = f"{address}_usdt_swap"
            if nonce_key in self.used_nonce:
                nonce = self.used_nonce[nonce_key] + 1
            else:
                nonce = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_transaction_count, address)
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Using nonce: {nonce}{Style.RESET_ALL}")
            
            # Build exact USDT swap transaction data based on your provided structure
            # Function: multicall(uint256 deadline, bytes[] data)
            # MethodID: 0x5ae401dc
            
            function_selector = "5ae401dc"
            
            # Use current timestamp + 1 hour as deadline (like your working example)
            deadline = int(datetime.now().timestamp()) + 3600
            deadline_hex = format(deadline, '064x')  # 64 chars (32 bytes)
            
            # Dynamic parts - receiver address and amount
            receiver_hex = address[2:].lower()  # Remove 0x prefix - should be 40 chars
            amount_hex = format(int(amount_wei), 'x')  # Convert to hex string
            
            # Build exact USDT transaction structure from your example
            transaction_data = (
                "0x" + function_selector +
                deadline_hex +
                "0000000000000000000000000000000000000000000000000000000000000040" +
                "0000000000000000000000000000000000000000000000000000000000000001" +
                "0000000000000000000000000000000000000000000000000000000000000020" +
                "00000000000000000000000000000000000000000000000000000000000000e4" +
                "04e45aaf00000000000000000000000076aaada469d23216be5f7c596fa25f28" +
                "2ff9b364000000000000000000000000d4071393f8716661958f766df660033b" +
                "3d35fd2900000000000000000000000000000000000000000000000000000000" +
                "000001f4000000000000000000000000" + receiver_hex +
                "00000000000000000000000000000000000000000000000000000" + amount_hex +
                "00000000000000000000000000000000000000000000000000000000" +
                "00001b9b00000000000000000000000000000000000000000000000000000000" +
                "0000000000000000000000000000000000000000000000000000000000000000"
            )
            
            # Debug: Log the transaction data
            
           
        
            
            # Get current gas price from network
            try:
                gas_price = await asyncio.get_event_loop().run_in_executor(None, lambda: web3.eth.gas_price)
            except:
                # Fallback to manual gas price
                gas_price = web3.to_wei(1.2, 'gwei')
            
            # Build transaction - CRITICAL: Use amount_wei as value since this is a payable function
            tx = {
                'chainId': self.CHAIN_ID,
                'gas': 350000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'to': web3.to_checksum_address(self.ZENITH_SWAP_ADDRESS),
                'value': int(amount_wei),  # Send PHRS value for the swap
                'data': transaction_data
            }

            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Gas Price: {web3.from_wei(gas_price, 'gwei')} gwei, Value: {web3.from_wei(amount_wei, 'ether')} PHRS{Style.RESET_ALL}")

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
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error performing USDT swap: {str(e)}{Style.RESET_ALL}")
            return None, None

    async def perform_usdc_swap(self, account: str, address: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to connect to Web3{Style.RESET_ALL}")
                return None, None
            
            # Convert amount to wei (assuming 18 decimals for calculation)
            amount_wei = web3.to_wei(amount, 'ether')
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}💱 USDC Swap Details: Amount: {amount} tokens{Style.RESET_ALL}")
            
            # Get nonce
            nonce_key = f"{address}_usdc_swap"
            if nonce_key in self.used_nonce:
                nonce = self.used_nonce[nonce_key] + 1
            else:
                nonce = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_transaction_count, address)
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Using nonce: {nonce}{Style.RESET_ALL}")
            
            # Build exact USDC swap transaction data from your provided structure
            function_selector = "5ae401dc"
            
            # Use current timestamp + 1 hour as deadline 
            deadline = int(datetime.now().timestamp()) + 3600
            deadline_hex = format(deadline, '064x')  # 64 chars (32 bytes)
            
            # Dynamic parts - receiver address and amount
            receiver_hex = address[2:].lower()  # Remove 0x prefix
            amount_hex = format(int(amount_wei), 'x')  # Convert to hex
            
            # Build exact USDC transaction structure from your example
            transaction_data = (
                "0x" + function_selector +
                deadline_hex +
                "0000000000000000000000000000000000000000000000000000000000000040" +
                "0000000000000000000000000000000000000000000000000000000000000001" +
                "0000000000000000000000000000000000000000000000000000000000000020" +
                "00000000000000000000000000000000000000000000000000000000000000e4" +
                "04e45aaf00000000000000000000000076aaada469d23216be5f7c596fa25f28" +
                "2ff9b36400000000000000000000000072df0bcd7276f2dfbac900d1ce63c272" +
                "c4bccced00000000000000000000000000000000000000000000000000000000" +
                "000001f4000000000000000000000000" + receiver_hex +
                "00000000000000000000000000000000000000000000000000000" + amount_hex +
                "00000000000000000000000000000000000000000000000000000000" +
                "00005c9800000000000000000000000000000000000000000000000000000000" +
                "0000000000000000000000000000000000000000000000000000000000000000"
            )
            
            # Debug: Log the transaction data
           
            
          
          
            
            # Get current gas price from network
            try:
                gas_price = await asyncio.get_event_loop().run_in_executor(None, lambda: web3.eth.gas_price)
            except:
                # Fallback to manual gas price
                gas_price = web3.to_wei(1.2, 'gwei')
            
            # Build transaction - CRITICAL: Use amount_wei as value since this is a payable function
            tx = {
                'chainId': self.CHAIN_ID,
                'gas': 350000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'to': web3.to_checksum_address(self.ZENITH_SWAP_ADDRESS),
                'value': int(amount_wei),  # Send PHRS value for the swap
                'data': transaction_data
            }
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Gas Price: {web3.from_wei(gas_price, 'gwei')} gwei, Value: {web3.from_wei(amount_wei, 'ether')} PHRS{Style.RESET_ALL}")
            
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
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error performing USDC swap: {str(e)}{Style.RESET_ALL}")
            return None, None

    # Enhanced Methods from Reference Code
    async def get_token_balance(self, address: str, contract_address: str, use_proxy: bool):
        """Get token balance for any ERC20 token or native PHRS"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                return 0

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
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error getting token balance: {str(e)}{Style.RESET_ALL}")
            return 0

    async def approving_token(self, account: str, address: str, spender_address: str, contract_address: str, amount: float, use_proxy: bool):
        """Approve token spending"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                return False
            
            spender = web3.to_checksum_address(spender_address)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()

            amount_to_wei = int(amount * (10 ** decimals))

            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount_to_wei:
                approve_data = token_contract.functions.approve(spender, 2**256 - 1)
                estimated_gas = approve_data.estimate_gas({"from": address})

                gas_price = web3.eth.gas_price

                approve_tx = approve_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "gasPrice": gas_price,
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id,
                })

                signed_tx = web3.eth.account.sign_transaction(approve_tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction)
                tx_hash = web3.to_hex(raw_tx)
                receipt = await asyncio.get_event_loop().run_in_executor(None, web3.eth.wait_for_transaction_receipt, tx_hash)
                
                if receipt.status == 1:
                    self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Token approval successful{Style.RESET_ALL}")
                    await asyncio.sleep(5)
                    return True
                else:
                    self.log(f"{Fore.RED + Style.BRIGHT}❌ Token approval failed{Style.RESET_ALL}")
                    return False
            
            return True
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error approving token: {str(e)}{Style.RESET_ALL}")
            return False

    async def perform_wrapped(self, account: str, address: str, use_proxy: bool):
        """Wrap PHRS to WPHRS"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                return None, None

            contract_address = web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(self.wrap_amount, "ether")
            wrap_data = token_contract.functions.deposit()
            estimated_gas = wrap_data.estimate_gas({"from": address, "value": amount_to_wei})

            gas_price = web3.eth.gas_price

            wrap_tx = wrap_data.build_transaction({
                "from": address,
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "gasPrice": gas_price,
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(wrap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.get_event_loop().run_in_executor(None, web3.eth.wait_for_transaction_receipt, tx_hash)
            
            if receipt and receipt.status == 1:
                return tx_hash, receipt.blockNumber
            else:
                return None, None

        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error wrapping PHRS: {str(e)}{Style.RESET_ALL}")
            return None, None

    async def perform_unwrapped(self, account: str, address: str, use_proxy: bool):
        """Unwrap WPHRS to PHRS"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                return None, None

            contract_address = web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(self.wrap_amount, "ether")
            unwrap_data = token_contract.functions.withdraw(amount_to_wei)
            estimated_gas = unwrap_data.estimate_gas({"from": address})

            gas_price = web3.eth.gas_price

            unwrap_tx = unwrap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "gasPrice": gas_price,
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(unwrap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.get_event_loop().run_in_executor(None, web3.eth.wait_for_transaction_receipt, tx_hash)
            
            if receipt and receipt.status == 1:
                return tx_hash, receipt.blockNumber
            else:
                return None, None

        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error unwrapping WPHRS: {str(e)}{Style.RESET_ALL}")
            return None, None

    def generate_swap_option(self):
        """Generate random swap option"""
        swap_option = random.choice([
            "WPHRStoUSDC", "WPHRStoUSDT", "USDCtoWPHRS",
            "USDTtoWPHRS", "USDCtoUSDT", "USDTtoUSDC"
        ])

        from_token = (
            self.USDC_CONTRACT_ADDRESS if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
            self.USDT_CONTRACT_ADDRESS if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
            self.WPHRS_CONTRACT_ADDRESS
        )

        to_token = (
            self.USDC_CONTRACT_ADDRESS if swap_option in ["WPHRStoUSDC", "USDTtoUSDC"] else
            self.USDT_CONTRACT_ADDRESS if swap_option in ["WPHRStoUSDT", "USDCtoUSDT"] else
            self.WPHRS_CONTRACT_ADDRESS
        )

        from_ticker = (
            "USDC" if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
            "USDT" if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
            "WPHRS"
        )

        to_ticker = (
            "USDC" if swap_option in ["WPHRStoUSDC", "USDTtoUSDC"] else
            "USDT" if swap_option in ["WPHRStoUSDT", "USDCtoUSDT"] else
            "WPHRS"
        )

        swap_amount = (
            self.usdc_amount if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
            self.usdt_amount if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
            self.wphrs_amount
        )

        return from_token, to_token, from_ticker, to_ticker, swap_amount

    def generate_add_lp_option(self):
        """Generate random add liquidity option"""
        add_lp_option = random.choice(["USDCnWPHRS", "USDCnUSDT", "WPHRSnUSDT"])

        if add_lp_option == "USDCnWPHRS":
            token0 = self.USDC_CONTRACT_ADDRESS
            token1 = self.WPHRS_CONTRACT_ADDRESS
            amount0 = 0.45
            amount1 = 0.001
            ticker0 = "USDC"
            ticker1 = "WPHRS"
        elif add_lp_option == "USDCnUSDT":
            token0 = self.USDC_CONTRACT_ADDRESS
            token1 = self.USDT_CONTRACT_ADDRESS
            amount0 = 1
            amount1 = 1
            ticker0 = "USDC"
            ticker1 = "USDT"
        else:
            token0 = self.WPHRS_CONTRACT_ADDRESS
            token1 = self.USDT_CONTRACT_ADDRESS
            amount0 = 0.001
            amount1 = 0.45
            ticker0 = "WPHRS"
            ticker1 = "USDT"

        return add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1

    async def generate_multicall_data(self, address: str, from_token: str, to_token: str, swap_amount: float, use_proxy: bool):
        """Generate multicall data for enhanced swaps"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                return None

            token_contract = web3.eth.contract(address=web3.to_checksum_address(from_token), abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()
            amount_to_wei = int(swap_amount * (10 ** decimals))
            
            encoded_data = encode(
                ["address", "address", "uint256", "address", "uint256", "uint256", "uint256"],
                [
                    web3.to_checksum_address(from_token),
                    web3.to_checksum_address(to_token),
                    500,
                    web3.to_checksum_address(address),
                    amount_to_wei,
                    0,
                    0
                ]
            )

            multicall_data = [b'\x04\xe4\x5a\xaf' + encoded_data]
            return multicall_data
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error generating multicall data: {str(e)}{Style.RESET_ALL}")
            return None

    async def perform_enhanced_swap(self, account: str, address: str, from_token: str, to_token: str, swap_amount: float, use_proxy: bool):
        """Perform enhanced swap using reference code pattern"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                return None, None

            # Approve token first
            if not await self.approving_token(account, address, self.SWAP_ROUTER_ADDRESS, from_token, swap_amount, use_proxy):
                return None, None

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), abi=self.SWAP_CONTRACT_ABI)

            deadline = int(time.time()) + 300
            multicall_data = await self.generate_multicall_data(address, from_token, to_token, swap_amount, use_proxy)
            
            if not multicall_data:
                return None, None

            swap_data = token_contract.functions.multicall(deadline, multicall_data)
            estimated_gas = swap_data.estimate_gas({"from": address})
            gas_price = web3.eth.gas_price

            swap_tx = swap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "gasPrice": gas_price,
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(swap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.get_event_loop().run_in_executor(None, web3.eth.wait_for_transaction_receipt, tx_hash)
            
            if receipt and receipt.status == 1:
                return tx_hash, receipt.blockNumber
            else:
                return None, None

        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error performing enhanced swap: {str(e)}{Style.RESET_ALL}")
            return None, None

    async def perform_add_liquidity(self, account: str, address: str, add_lp_option: str, token0: str, token1: str, amount0: float, amount1: float, use_proxy: bool):
        """Add liquidity to pools"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                return None, None

            # Approve tokens
            if add_lp_option == "USDCnWPHRS":
                await self.approving_token(account, address, self.POSITION_MANAGER_ADDRESS, token0, amount0, use_proxy)
            elif add_lp_option == "WPHRSnUSDT":
                await self.approving_token(account, address, self.POSITION_MANAGER_ADDRESS, token1, amount1, use_proxy)
            else:
                await self.approving_token(account, address, self.POSITION_MANAGER_ADDRESS, token0, amount0, use_proxy)
                await self.approving_token(account, address, self.POSITION_MANAGER_ADDRESS, token1, amount1, use_proxy)
            
            token0_contract = web3.eth.contract(address=web3.to_checksum_address(token0), abi=self.ERC20_CONTRACT_ABI)
            token0_decimals = token0_contract.functions.decimals().call()
            amount0_desired = int(amount0 * (10 ** token0_decimals))

            token1_contract = web3.eth.contract(address=web3.to_checksum_address(token1), abi=self.ERC20_CONTRACT_ABI)
            token1_decimals = token1_contract.functions.decimals().call()
            amount1_desired = int(amount1 * (10 ** token1_decimals))

            mint_params = {
                "token0": web3.to_checksum_address(token0),
                "token1": web3.to_checksum_address(token1),
                "fee": 500,
                "tickLower": -887270,
                "tickUpper": 887270,
                "amount0Desired": amount0_desired,
                "amount1Desired": amount1_desired,
                "amount0Min": 0,
                "amount1Min": 0,
                "recipient": web3.to_checksum_address(address),
                "deadline": int(time.time()) + 600
            }

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.POSITION_MANAGER_ADDRESS), abi=self.ADD_LP_CONTRACT_ABI)

            lp_data = token_contract.functions.mint(mint_params)
            estimated_gas = lp_data.estimate_gas({"from": address})
            gas_price = web3.eth.gas_price

            lp_tx = lp_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "gasPrice": gas_price,
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(lp_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.get_event_loop().run_in_executor(None, web3.eth.wait_for_transaction_receipt, tx_hash)
            
            if receipt and receipt.status == 1:
                return tx_hash, receipt.blockNumber
            else:
                return None, None

        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error adding liquidity: {str(e)}{Style.RESET_ALL}")
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

    def print_usdt_swap_question(self):
        while True:
            try:
                print(f"\n{Fore.GREEN + Style.BRIGHT}💱 USDT Swap Configuration:{Style.RESET_ALL}")
                self.usdt_swap_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How many USDT swaps per account? {Style.RESET_ALL}"))
                if self.usdt_swap_count > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

        # Fixed amount - no user input needed
        self.usdt_swap_amount = 0.00001
        print(f"{Fore.GREEN + Style.BRIGHT}💰 USDT swap amount set to: {self.usdt_swap_amount} PHRS{Style.RESET_ALL}")

    def print_usdc_swap_question(self):
        while True:
            try:
                print(f"\n{Fore.BLUE + Style.BRIGHT}💱 USDC Swap Configuration:{Style.RESET_ALL}")
                self.usdc_swap_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How many USDC swaps per account? {Style.RESET_ALL}"))
                if self.usdc_swap_count > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

        # Fixed amount - no user input needed
        self.usdc_swap_amount = 0.00001
        print(f"{Fore.GREEN + Style.BRIGHT}💰 USDC swap amount set to: {self.usdc_swap_amount} PHRS{Style.RESET_ALL}")

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
        
    def print_enhanced_swap_question(self):
        while True:
            try:
                print(f"\n{Fore.GREEN + Style.BRIGHT}🔄 Enhanced Multi-Token Swap Configuration:{Style.RESET_ALL}")
                self.swap_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How many swaps per account? {Style.RESET_ALL}"))
                if self.swap_count > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

        while True:
            try:
                self.wphrs_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}WPHRS swap amount (e.g., 0.001): {Style.RESET_ALL}"))
                if self.wphrs_amount > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

        while True:
            try:
                self.usdc_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}USDC swap amount (e.g., 0.5): {Style.RESET_ALL}"))
                if self.usdc_amount > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

        while True:
            try:
                self.usdt_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}USDT swap amount (e.g., 0.5): {Style.RESET_ALL}"))
                if self.usdt_amount > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

    def print_add_liquidity_question(self):
        while True:
            try:
                print(f"\n{Fore.BLUE + Style.BRIGHT}💧 Add Liquidity Configuration:{Style.RESET_ALL}")
                self.add_lp_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How many liquidity additions per account? {Style.RESET_ALL}"))
                if self.add_lp_count > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN + Style.BRIGHT}💰 Liquidity amounts will be automatically set based on random pool selection{Style.RESET_ALL}")

    def print_wrap_question(self):
        while True:
            try:
                print(f"\n{Fore.MAGENTA + Style.BRIGHT}🔄 Wrap/Unwrap Configuration:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1.{Style.RESET_ALL} Wrap PHRS to WPHRS")
                print(f"{Fore.WHITE + Style.BRIGHT}2.{Style.RESET_ALL} Unwrap WPHRS to PHRS")
                
                self.wrap_option = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter your choice (1-2): {Style.RESET_ALL}"))
                if self.wrap_option in [1, 2]:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter 1 or 2{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

        while True:
            try:
                self.wrap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter amount to wrap/unwrap (e.g., 0.001): {Style.RESET_ALL}"))
                if self.wrap_amount > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")
        
    def print_question(self):
        while True:
            try:
                print(f"\n{Fore.CYAN + Style.BRIGHT}🚀 Choose Operation:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1.{Style.RESET_ALL} USDT Swap (Original)")
                print(f"{Fore.WHITE + Style.BRIGHT}2.{Style.RESET_ALL} USDC Swap (Original)")
                print(f"{Fore.WHITE + Style.BRIGHT}3.{Style.RESET_ALL} Enhanced Multi-Token Swap")
                print(f"{Fore.WHITE + Style.BRIGHT}4.{Style.RESET_ALL} Add Liquidity Pool")
                print(f"{Fore.WHITE + Style.BRIGHT}5.{Style.RESET_ALL} Wrap/Unwrap PHRS")
                print(f"{Fore.WHITE + Style.BRIGHT}6.{Style.RESET_ALL} Check Balance")
                
                choose = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter your choice (1-6): {Style.RESET_ALL}"))
                if choose in [1, 2, 3, 4, 5, 6]:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter 1-6{Style.RESET_ALL}")
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
            self.print_usdt_swap_question()
            self.print_delay_question()
        elif choose == 2:
            self.print_usdc_swap_question()
            self.print_delay_question()
        elif choose == 3:
            self.print_enhanced_swap_question()
            self.print_delay_question()
        elif choose == 4:
            self.print_add_liquidity_question()
            self.print_delay_question()
        elif choose == 5:
            self.print_wrap_question()

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
    
    async def process_perform_usdt_swap(self, account: str, address: str, amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_usdt_swap(account, address, amount, use_proxy)
        if tx_hash and block_number:
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}✅ USDT Swap Success{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | "
                f"Hash: {tx_hash[:10]}...{tx_hash[-6:]} | "
                f"Block: {block_number} | "
                f"Amount: {amount} USDT{Style.RESET_ALL}"
            )
            return True
        else:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ USDT Swap Failed{Style.RESET_ALL}")
            return False

    async def process_perform_usdc_swap(self, account: str, address: str, amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_usdc_swap(account, address, amount, use_proxy)
        if tx_hash and block_number:
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}✅ USDC Swap Success{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | "
                f"Hash: {tx_hash[:10]}...{tx_hash[-6:]} | "
                f"Block: {block_number} | "
                f"Amount: {amount} USDC{Style.RESET_ALL}"
            )
            return True
        else:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ USDC Swap Failed{Style.RESET_ALL}")
            return False

    async def process_option_1(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}USDT Swap Operations{Style.RESET_ALL}"
        )
        
        success_count = 0
        for i in range(self.usdt_swap_count):
            self.log(
                f"{Fore.GREEN+Style.BRIGHT}💱 USDT Swap {i+1}/{self.usdt_swap_count}{Style.RESET_ALL}"
            )
            
            balance = await self.get_phrs_balance(address, use_proxy)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Balance:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance:.6f} PHRS {Style.RESET_ALL}"
            )
            
            success = await self.process_perform_usdt_swap(account, address, self.usdt_swap_amount, use_proxy)
            if success:
                success_count += 1
            
            if i < self.usdt_swap_count - 1:
                await self.print_timer()
        
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}📊 USDT Swap Summary: {success_count}/{self.usdt_swap_count} successful{Style.RESET_ALL}"
        )

    async def process_option_2(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.BLUE+Style.BRIGHT}USDC Swap Operations{Style.RESET_ALL}"
        )
        
        success_count = 0
        for i in range(self.usdc_swap_count):
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}💱 USDC Swap {i+1}/{self.usdc_swap_count}{Style.RESET_ALL}"
            )
            
            balance = await self.get_phrs_balance(address, use_proxy)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Balance:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance:.6f} PHRS {Style.RESET_ALL}"
            )
            
            success = await self.process_perform_usdc_swap(account, address, self.usdc_swap_amount, use_proxy)
            if success:
                success_count += 1
            
            if i < self.usdc_swap_count - 1:
                await self.print_timer()
        
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}📊 USDC Swap Summary: {success_count}/{self.usdc_swap_count} successful{Style.RESET_ALL}"
        )

    async def process_option_3(self, account: str, address: str, use_proxy: bool):
        """Enhanced Multi-Token Swap"""
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Enhanced Multi-Token Swap Operations{Style.RESET_ALL}"
        )
        
        success_count = 0
        for i in range(self.swap_count):
            self.log(
                f"{Fore.GREEN+Style.BRIGHT}🔄 Enhanced Swap {i+1}/{self.swap_count}{Style.RESET_ALL}"
            )
            
            # Generate random swap option
            from_token, to_token, from_ticker, to_ticker, swap_amount = self.generate_swap_option()
            
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Swap:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {swap_amount} {from_ticker} → {to_ticker} {Style.RESET_ALL}"
            )
            
            balance = await self.get_token_balance(address, from_token if from_token != self.WPHRS_CONTRACT_ADDRESS else "PHRS", use_proxy)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Balance:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance:.6f} {from_ticker} {Style.RESET_ALL}"
            )
            
            if balance >= swap_amount:
                tx_hash, block_number = await self.perform_enhanced_swap(account, address, from_token, to_token, swap_amount, use_proxy)
                if tx_hash and block_number:
                    self.log(
                        f"{Fore.GREEN + Style.BRIGHT}✅ Enhanced Swap Success{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | "
                        f"Hash: {tx_hash[:10]}...{tx_hash[-6:]} | "
                        f"Block: {block_number}{Style.RESET_ALL}"
                    )
                    success_count += 1
                else:
                    self.log(f"{Fore.RED + Style.BRIGHT}❌ Enhanced Swap Failed{Style.RESET_ALL}")
            else:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ Insufficient {from_ticker} balance{Style.RESET_ALL}")
            
            if i < self.swap_count - 1:
                await self.print_timer()
        
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}📊 Enhanced Swap Summary: {success_count}/{self.swap_count} successful{Style.RESET_ALL}"
        )

    async def process_option_4(self, account: str, address: str, use_proxy: bool):
        """Add Liquidity Pool"""
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.BLUE+Style.BRIGHT}Add Liquidity Pool Operations{Style.RESET_ALL}"
        )
        
        success_count = 0
        for i in range(self.add_lp_count):
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}💧 Add Liquidity {i+1}/{self.add_lp_count}{Style.RESET_ALL}"
            )
            
            # Generate random liquidity option
            add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1 = self.generate_add_lp_option()
            
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Pool:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {amount0} {ticker0} + {amount1} {ticker1} {Style.RESET_ALL}"
            )
            
            balance0 = await self.get_token_balance(address, token0 if token0 != self.WPHRS_CONTRACT_ADDRESS else "PHRS", use_proxy)
            balance1 = await self.get_token_balance(address, token1 if token1 != self.WPHRS_CONTRACT_ADDRESS else "PHRS", use_proxy)
            
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Balances:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance0:.6f} {ticker0} | {balance1:.6f} {ticker1} {Style.RESET_ALL}"
            )
            
            if balance0 >= amount0 and balance1 >= amount1:
                tx_hash, block_number = await self.perform_add_liquidity(account, address, add_lp_option, token0, token1, amount0, amount1, use_proxy)
                if tx_hash and block_number:
                    self.log(
                        f"{Fore.GREEN + Style.BRIGHT}✅ Add Liquidity Success{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | "
                        f"Hash: {tx_hash[:10]}...{tx_hash[-6:]} | "
                        f"Block: {block_number}{Style.RESET_ALL}"
                    )
                    success_count += 1
                else:
                    self.log(f"{Fore.RED + Style.BRIGHT}❌ Add Liquidity Failed{Style.RESET_ALL}")
            else:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ Insufficient token balances{Style.RESET_ALL}")
            
            if i < self.add_lp_count - 1:
                await self.print_timer()
        
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}📊 Add Liquidity Summary: {success_count}/{self.add_lp_count} successful{Style.RESET_ALL}"
        )

    async def process_option_5(self, account: str, address: str, use_proxy: bool):
        """Wrap/Unwrap PHRS"""
        operation = "Wrap" if self.wrap_option == 1 else "Unwrap"
        from_token = "PHRS" if self.wrap_option == 1 else "WPHRS"
        to_token = "WPHRS" if self.wrap_option == 1 else "PHRS"
        
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.MAGENTA+Style.BRIGHT}{operation} {from_token} to {to_token} Operation{Style.RESET_ALL}"
        )
        
        balance = await self.get_token_balance(address, "PHRS" if self.wrap_option == 1 else self.WPHRS_CONTRACT_ADDRESS, use_proxy)
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Balance:{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {balance:.6f} {from_token} {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Amount:{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {self.wrap_amount} {from_token} {Style.RESET_ALL}"
        )
        
        if balance >= self.wrap_amount:
            if self.wrap_option == 1:
                tx_hash, block_number = await self.perform_wrapped(account, address, use_proxy)
            else:
                tx_hash, block_number = await self.perform_unwrapped(account, address, use_proxy)
            
            if tx_hash and block_number:
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}✅ {operation} Success{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | "
                    f"Hash: {tx_hash[:10]}...{tx_hash[-6:]} | "
                    f"Block: {block_number}{Style.RESET_ALL}"
                )
            else:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ {operation} Failed{Style.RESET_ALL}")
        else:
            self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ Insufficient {from_token} balance{Style.RESET_ALL}")

    async def process_option_6(self, account: str, address: str, use_proxy: bool):
        """Check Balance"""
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Balance Check{Style.RESET_ALL}"
        )
        
        # Check PHRS balance
        phrs_balance = await self.get_phrs_balance(address, use_proxy)
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}💰 PHRS Balance:{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {phrs_balance:.6f} PHRS {Style.RESET_ALL}"
        )
        
        # Check WPHRS balance
        wphrs_balance = await self.get_token_balance(address, self.WPHRS_CONTRACT_ADDRESS, use_proxy)
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}💰 WPHRS Balance:{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {wphrs_balance:.6f} WPHRS {Style.RESET_ALL}"
        )
        
        # Check USDC balance
        usdc_balance = await self.get_token_balance(address, self.USDC_CONTRACT_ADDRESS, use_proxy)
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}💰 USDC Balance:{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {usdc_balance:.6f} USDC {Style.RESET_ALL}"
        )
        
        # Check USDT balance
        usdt_balance = await self.get_token_balance(address, self.USDT_CONTRACT_ADDRESS, use_proxy)
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}💰 USDT Balance:{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {usdt_balance:.6f} USDT {Style.RESET_ALL}"
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
        elif option == 4:
            await self.process_option_4(account, address, use_proxy)
        elif option == 5:
            await self.process_option_5(account, address, use_proxy)
        elif option == 6:
            await self.process_option_6(account, address, use_proxy)

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
        zenith = ZenithSwap()
        asyncio.run(zenith.main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED + Style.BRIGHT}❌ Process interrupted by user{Style.RESET_ALL}")
