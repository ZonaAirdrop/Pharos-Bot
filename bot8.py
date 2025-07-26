from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
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

class AutoStakingBot:
    def __init__(self) -> None:
        self.HEADERS = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6,te;q=0.5",
            "Origin": "https://autostaking.pro",
            "Referer": "https://autostaking.pro/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Content-Type": "application/json",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "priority": "u=1, i",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }
        self.BASE_API = "https://api.autostaking.pro"
        
        # Blockchain configuration
        self.RPC_URL = "https://api.zan.top/node/v1/pharos/testnet/54b49326c9f44b6e8730dc5dd4348421"
        self.CHAIN_ID = 688688
        self.FAUCET_CONTRACT = "0xF1CF5D79bE4682D50f7A60A047eACa9bD351fF8e"
        self.TOKEN_CONTRACT = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
        self.APPROVAL_SPENDER = "0x11cd3700b310339003641fdce57c1f9bd21ae015"
        self.APPROVAL_AMOUNT = "0x000000000000000000000000000000000000000000000000000000003b9f537a"
        
        # Contract ABI for smart contract calls
        self.CONTRACT_ABI = [
            {
                "inputs": [{"internalType": "address", "name": "owner", "type": "address"}, 
                          {"internalType": "address", "name": "spender", "type": "address"}],
                "name": "allowance",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
                "name": "canClaimFaucet",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
                "name": "getNextFaucetClaimTime",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.login_count = 0
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
        print(Fore.GREEN + Style.BRIGHT + "    ⚡ AutoStaking Platform Bot  ⚡")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.YELLOW + Style.BRIGHT + "    🧠 Project    : AutoStaking - Smart Operations Bot")
        print(Fore.YELLOW + Style.BRIGHT + "    🧑‍💻 Author     : YetiDAO")
        print(Fore.YELLOW + Style.BRIGHT + "    🌐 Status     : Running & Monitoring...")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.WHITE + Style.BRIGHT + "    🔐 Login → 🚰 Faucet → ✅ Approval → 🔄 Multicall")
        print(Fore.GREEN + Style.BRIGHT + "    🧠 Smart Checks: Cooldown & Allowance")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.MAGENTA + Style.BRIGHT + "    🧬 Powered by Cryptodai3 × YetiDAO | Buddy v3.0 🚀")
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
        
    def generate_nonce(self):
        """Generate a random nonce similar to the format used by AutoStaking"""
        import random
        import string
        # Generate 20 character nonce to match working example (k98v1ycgu9dr29zfry1v)
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
    
    def create_siwe_message(self, address: str, nonce: str):
        """Create SIWE (Sign-In with Ethereum) message"""
        from datetime import timezone
        # Use the exact timestamp format from your working example: 2025-07-25T12:09:58.295Z
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        message = f"""autostaking.pro wants you to sign in with your Ethereum account:
{address}

Welcome to AutoStaking! Sign in to authenticate your wallet.

URI: https://autostaking.pro
Version: 1
Chain ID: 1
Nonce: {nonce}
Issued At: {timestamp}"""
        
        return message, timestamp
    
    def sign_message(self, private_key: str, message: str):
        """Sign the SIWE message with the private key"""
        try:
            # Create message hash
            message_hash = encode_defunct(text=message)
            
            # Sign the message
            signed_message = Account.sign_message(message_hash, private_key=private_key)
            
            # Return signature with 0x prefix to match working example
            return "0x" + signed_message.signature.hex()
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Error signing message: {str(e)}{Style.RESET_ALL}")
            return None

    async def check_allowance(self, web3, address: str):
        """Check current token allowance for the spender"""
        try:
            contract = web3.eth.contract(
                address=web3.to_checksum_address(self.TOKEN_CONTRACT),
                abi=self.CONTRACT_ABI
            )
            
            allowance = await asyncio.get_event_loop().run_in_executor(
                None,
                contract.functions.allowance(
                    web3.to_checksum_address(address),
                    web3.to_checksum_address(self.APPROVAL_SPENDER)
                ).call
            )
            
            required_amount = int(self.APPROVAL_AMOUNT, 16)
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔍 Current Allowance: {allowance} | Required: {required_amount}{Style.RESET_ALL}")
            
            return allowance >= required_amount
            
        except Exception as e:
            self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ Error checking allowance: {str(e)}{Style.RESET_ALL}")
            return False

    async def check_faucet_eligibility(self, web3, address: str):
        """Check if user can claim faucet and when next claim is available"""
        try:
            contract = web3.eth.contract(
                address=web3.to_checksum_address(self.FAUCET_CONTRACT),
                abi=self.CONTRACT_ABI
            )
            
            # Check if user can claim faucet now
            can_claim = await asyncio.get_event_loop().run_in_executor(
                None,
                contract.functions.canClaimFaucet(web3.to_checksum_address(address)).call
            )
            
            if not can_claim:
                # Get next claim time
                next_claim_time = await asyncio.get_event_loop().run_in_executor(
                    None,
                    contract.functions.getNextFaucetClaimTime(web3.to_checksum_address(address)).call
                )
                
                current_time = int(datetime.now().timestamp())
                wait_time = next_claim_time - current_time
                
                if wait_time > 0:
                    hours = wait_time // 3600
                    minutes = (wait_time % 3600) // 60
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}⏳ Faucet cooldown: {hours}h {minutes}m remaining{Style.RESET_ALL}")
                
            return can_claim
            
        except Exception as e:
            self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ Error checking faucet eligibility: {str(e)}{Style.RESET_ALL}")
            return True  # Assume can claim if check fails

    async def get_web3_with_check(self, address: str, use_proxy: bool, retries=3):
        """Get Web3 connection with validation"""
        for attempt in range(retries):
            try:
                # Create Web3 instance with simple HTTP provider
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL))
                
                # Test connection
                is_connected = await asyncio.get_event_loop().run_in_executor(None, web3.is_connected)
                if is_connected:
                    latest_block = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_block, 'latest')
                    if latest_block:
                        self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Web3 connected - Block: {latest_block.number}{Style.RESET_ALL}")
                        return web3
                    
            except Exception as e:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}Web3 connection attempt {attempt + 1} failed: {str(e)}{Style.RESET_ALL}")
                
                if attempt < retries - 1:
                    await asyncio.sleep(2)
        
        return None

    async def send_raw_transaction_with_retries(self, account, web3, tx, retries=3):
        """Send raw transaction with retry logic"""
        for attempt in range(retries):
            try:
                signed_tx = web3.eth.account.sign_transaction(tx, private_key=account)
                raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
                tx_hash = await asyncio.get_event_loop().run_in_executor(None, web3.eth.send_raw_transaction, raw_tx)
                return web3.to_hex(tx_hash)
            except Exception as e:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}Transaction attempt {attempt + 1} failed: {str(e)}{Style.RESET_ALL}")
                if attempt < retries - 1:
                    await asyncio.sleep(2)
        raise Exception("Transaction failed after maximum retries")

    async def wait_for_receipt_with_retries(self, web3, tx_hash, retries=5):
        """Wait for transaction receipt with retry logic"""
        for attempt in range(retries):
            try:
                receipt = await asyncio.get_event_loop().run_in_executor(None, web3.eth.wait_for_transaction_receipt, tx_hash)
                return receipt
            except Exception as e:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}Receipt attempt {attempt + 1} failed: {str(e)}{Style.RESET_ALL}")
                if attempt < retries - 1:
                    await asyncio.sleep(5)
        raise Exception("Transaction receipt not found after maximum retries")

    async def claim_faucet(self, account: str, address: str, use_proxy: bool):
        """Claim faucet tokens"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to connect to Web3{Style.RESET_ALL}")
                return False
            
            # Check if user can claim faucet
            can_claim = await self.check_faucet_eligibility(web3, address)
            if not can_claim:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}⏳ Faucet claim not available yet (cooldown active){Style.RESET_ALL}")
                return True  # Return True to continue with approval (user might want to approve anyway)
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🚰 Claiming faucet tokens...{Style.RESET_ALL}")
            
            # Get nonce
            current_nonce = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_transaction_count, address)
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Using nonce: {current_nonce}{Style.RESET_ALL}")
            
            # Transaction data from your example
            transaction_data = "0x4fe15335"
            
            # Get current gas price from network
            try:
                gas_price = await asyncio.get_event_loop().run_in_executor(None, lambda: web3.eth.gas_price)
            except:
                gas_price = web3.to_wei(1.2, 'gwei')  # Fallback gas price
            
            # Build transaction exactly as in your example
            tx = {
                'chainId': self.CHAIN_ID,
                'data': transaction_data,
                'from': address,
                'gas': 0x21db8,  # From your example
                'gasPrice': gas_price,
                'nonce': current_nonce,
                'to': web3.to_checksum_address(self.FAUCET_CONTRACT)
            }

            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Gas Price: {web3.from_wei(gas_price, 'gwei')} gwei{Style.RESET_ALL}")

            # Send transaction
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}📝 Faucet claim sent: {tx_hash}{Style.RESET_ALL}")
            
            # Wait for receipt
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            
            if receipt and receipt.status == 1:
                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Faucet claim confirmed in block {receipt.blockNumber}{Style.RESET_ALL}")
                return True
            else:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Faucet claim failed - Status: {receipt.status if receipt else 'No receipt'}{Style.RESET_ALL}")
                return False
            
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error claiming faucet: {str(e)}{Style.RESET_ALL}")
            return False

    async def approve_token(self, account: str, address: str, use_proxy: bool):
        """Approve token spending"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to connect to Web3{Style.RESET_ALL}")
                return False
            
            # Check current allowance first
            has_sufficient_allowance = await self.check_allowance(web3, address)
            if has_sufficient_allowance:
                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Sufficient allowance already exists - skipping approval{Style.RESET_ALL}")
                return True
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}✅ Approving token spending...{Style.RESET_ALL}")
            
            # Get nonce
            current_nonce = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_transaction_count, address)
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Using nonce: {current_nonce}{Style.RESET_ALL}")
            
            # Transaction data from your example (approve function with spender and amount)
            transaction_data = f"0x095ea7b3{self.APPROVAL_SPENDER[2:].lower().zfill(64)}{self.APPROVAL_AMOUNT[2:]}"
            
            # Get current gas price from network
            try:
                gas_price = await asyncio.get_event_loop().run_in_executor(None, lambda: web3.eth.gas_price)
            except:
                gas_price = web3.to_wei(1.2, 'gwei')  # Fallback gas price
            
            # Build transaction exactly as in your example
            tx = {
                'chainId': self.CHAIN_ID,
                'data': transaction_data,
                'from': address,
                'gas': 0xbf3f,  # From your example
                'gasPrice': gas_price,
                'nonce': current_nonce,
                'to': web3.to_checksum_address(self.TOKEN_CONTRACT),
                'value': 0  # No ETH value for approval
            }

            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Gas Price: {web3.from_wei(gas_price, 'gwei')} gwei{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}🎯 Approving spender: {self.APPROVAL_SPENDER}{Style.RESET_ALL}")

            # Send transaction
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}📝 Token approval sent: {tx_hash}{Style.RESET_ALL}")
            
            # Wait for receipt
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            
            if receipt and receipt.status == 1:
                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Token approval confirmed in block {receipt.blockNumber}{Style.RESET_ALL}")
                return True
            else:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Token approval failed - Status: {receipt.status if receipt else 'No receipt'}{Style.RESET_ALL}")
                return False
            
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error approving token: {str(e)}{Style.RESET_ALL}")
            return False

    async def get_multicall_transaction_data(self, jwt_token: str, address: str, use_proxy: bool):
        """Get multicall transaction data from AutoStaking API"""
        try:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy_url, proxy_auth = self.build_proxy_config(proxy)
            
            request_kwargs = {"timeout": ClientTimeout(total=30)}
            if connector:
                request_kwargs["connector"] = connector
            if proxy_url and proxy_auth:
                request_kwargs["proxy"] = proxy_url
                request_kwargs["proxy_auth"] = proxy_auth

            async with ClientSession(**request_kwargs) as session:
                # Update headers with authorization
                headers = self.HEADERS.copy()
                headers["authorization"] = jwt_token
                current_timestamp = int(datetime.now().timestamp())
                headers["Cookie"] = f"_ga=GA1.1.943571911.{current_timestamp}; _ga_ZRD7GRM6F8=GS2.1.s{current_timestamp}$o6$g1$t{current_timestamp}$j60$l0$h0"
                
                # Sample payload with multiple deposits to trigger multicall
                payload = {
                    "user": address, 
                    "changes": [
                        {
                            "type": "deposit",
                            "id": "deposit-1",
                            "token": {
                                "name": "USDC",
                                "address": "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED",
                                "decimals": 6,
                                "chainId": 688688,
                                "price": 1,
                                "amount": "1000000"
                            },
                            "product": {
                                "provider": "MockVault",
                                "chainId": 688688,
                                "address": "0xC6858c1C7047cEc35355Feb2a5Eb7bd1E051dDDf",
                                "depositAsset": {
                                    "address": "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED",
                                    "symbol": "USDC",
                                    "name": "USDC",
                                    "decimals": 6,
                                    "chain": {"id": 688688}
                                },
                                "asset": {
                                    "address": "0xC6858c1C7047cEc35355Feb2a5Eb7bd1E051dDDf",
                                    "symbol": "mvUSDC",
                                    "decimals": 6,
                                    "name": "USDC Vault Shares",
                                    "chain": {"id": 688688}
                                },
                                "name": "USDC Vault",
                                "tvl": 25960387.547369,
                                "fee": 0,
                                "dailyApy": 0.08
                            },
                            "costs": {
                                "gasFee": 0.0075,
                                "platformFee": 0
                            }
                        }
                    ],
                    "prevTransactionResults": {
                        f"688688-0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED": {
                            "progress": 0.5,
                            "type": "tx",
                            "ids": ["approval-1"],
                            "from": address.lower(),
                            "to": "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED",
                            "data": f"0x095ea7b300000000000000000000000011cd3700b310339003641fdce57c1f9bd21ae015{self.APPROVAL_AMOUNT[2:]}",
                            "value": "0x0",
                            "result": "0x" + "0" * 64  # Mock transaction hash
                        }
                    }
                }
                
                # Call the API to generate multicall transaction
                api_url = f"{self.BASE_API}/investment/generate-change-transactions"
                
                self.log(f"{Fore.CYAN + Style.BRIGHT}🔄 Calling AutoStaking API for multicall data...{Style.RESET_ALL}")
                
                async with session.post(api_url, json=payload, headers=headers) as response:
                    response_text = await response.text()
                    
                    self.log(f"{Fore.CYAN + Style.BRIGHT}🔍 API Response Status: {response.status}{Style.RESET_ALL}")
                    
                    if response.status == 201:
                        try:
                            response_data = json.loads(response_text)
                            
                            if response_data.get("code") == 0 and "data" in response_data:
                                # Look for multicall transaction data
                                for key, tx_data in response_data["data"].items():
                                    if tx_data.get("progress") == 1 and tx_data.get("to") == "0x11cD3700B310339003641Fdce57c1f9BD21aE015":
                                        self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Got multicall transaction data from API{Style.RESET_ALL}")
                                        return tx_data.get("data"), tx_data.get("to")
                                
                                self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ No multicall transaction found in API response{Style.RESET_ALL}")
                                return None, None
                            else:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ Invalid API response format{Style.RESET_ALL}")
                                return None, None
                                
                        except json.JSONDecodeError:
                            self.log(f"{Fore.RED + Style.BRIGHT}❌ Invalid JSON response from API{Style.RESET_ALL}")
                            return None, None
                    else:
                        self.log(f"{Fore.RED + Style.BRIGHT}❌ API call failed - Status: {response.status}{Style.RESET_ALL}")
                        self.log(f"{Fore.RED + Style.BRIGHT}Response: {response_text[:300]}...{Style.RESET_ALL}")
                        return None, None
                        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error calling AutoStaking API: {str(e)}{Style.RESET_ALL}")
            return None, None

    async def perform_multicall(self, account: str, address: str, use_proxy: bool, jwt_token: str = None):
        """Perform multicall transaction using API-generated data or fallback to exact working transaction"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to connect to Web3{Style.RESET_ALL}")
                return False
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔄 Performing multicall transaction...{Style.RESET_ALL}")
            
            # Get nonce
            current_nonce = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_transaction_count, address)
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Using nonce: {current_nonce}{Style.RESET_ALL}")
            
            transaction_data = None
            target_contract = None
            
            # Try to get multicall data from API if JWT token is provided
            if jwt_token:
                api_data, api_contract = await self.get_multicall_transaction_data(jwt_token, address, use_proxy)
                if api_data and api_contract:
                    transaction_data = api_data
                    target_contract = api_contract
                    self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Using API-generated multicall data{Style.RESET_ALL}")
            
            # Fallback to your exact working transaction if API fails
            if not transaction_data:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ Using fallback transaction data{Style.RESET_ALL}")
                # Your EXACT working transaction data - only replacing the sender address dynamically
                exact_transaction_data = "0xac9650d80000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000064f9984acd000000000000000000000000c6858c1c7047cec35355feb2a5eb7bd1e051dddf000000000000000000000000000000000000000000000000000000003b9f5379"
                
                # Replace the hardcoded address with dynamic sender address
                dynamic_address_part = f"00000000000000000000000{address[2:].lower()}"
                final_padding = "00000000000000000000000000000000000000000000000000000000"
                
                # Complete transaction data with dynamic address
                transaction_data = f"{exact_transaction_data}{dynamic_address_part}{final_padding}"
                target_contract = "0x11cD3700B310339003641Fdce57c1f9BD21aE015"
            
            # Use your EXACT working transaction parameters
            tx = {
                'chainId': 688688,  # Your exact chainId
                'data': transaction_data,
                'from': address,  # Dynamic sender address
                'gas': 0x44e5b,  # Your exact gas
                'gasPrice': 0x47868c00,  # Your exact gasPrice (1.2 gwei)
                'nonce': current_nonce,  # Dynamic nonce
                'to': web3.to_checksum_address(target_contract),  # Target contract
                'value': 0x0  # Your exact value
            }
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Transaction Data: {transaction_data[:100]}...{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Chain ID: {tx['chainId']}{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Gas: {hex(tx['gas'])}{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Gas Price: {hex(tx['gasPrice'])} (1.2 gwei){Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}🎯 To Contract: {target_contract}{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Function: 0xac9650d8 (multicall){Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔄 Dynamic Sender: {address}{Style.RESET_ALL}")

            # Send transaction
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}📝 Multicall transaction sent: {tx_hash}{Style.RESET_ALL}")
            
            # Wait for receipt
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            
            if receipt and receipt.status == 1:
                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Multicall transaction confirmed in block {receipt.blockNumber}{Style.RESET_ALL}")
                return True
            else:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Multicall transaction failed - Status: {receipt.status if receipt else 'No receipt'}{Style.RESET_ALL}")
                return False
            
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error performing multicall: {str(e)}{Style.RESET_ALL}")
            return False

    async def perform_login(self, account: str, address: str, use_proxy: bool):
        try:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy_url, proxy_auth = self.build_proxy_config(proxy)
            
            request_kwargs = {"timeout": ClientTimeout(total=30)}
            if connector:
                request_kwargs["connector"] = connector
            if proxy_url and proxy_auth:
                request_kwargs["proxy"] = proxy_url
                request_kwargs["proxy_auth"] = proxy_auth

            async with ClientSession(**request_kwargs) as session:
                # Generate nonce and create SIWE message
                nonce = self.generate_nonce()
                message, timestamp = self.create_siwe_message(address, nonce)
                
                self.log(f"{Fore.CYAN + Style.BRIGHT}🔐 Creating SIWE message with nonce: {nonce}{Style.RESET_ALL}")
                
                # Sign the message
                signature = self.sign_message(account, message)
                if not signature:
                    return False, None
                
                self.log(f"{Fore.CYAN + Style.BRIGHT}✍️ Message signed successfully{Style.RESET_ALL}")
                
                # Prepare login payload exactly as shown in your working example
                login_payload = {
                    "address": address,
                    "message": message,
                    "signature": signature
                }
                
                # Update headers for this session - add cookies like in your working example
                headers = self.HEADERS.copy()
                current_timestamp = int(datetime.now().timestamp())
                headers["Cookie"] = f"_ga=GA1.1.943571911.{current_timestamp}; _ga_ZRD7GRM6F8=GS2.1.s{current_timestamp}$o4$g1$t{current_timestamp}$j58$l0$h0"
                
                # Perform login request
                login_url = f"{self.BASE_API}/user/login"
                
                self.log(f"{Fore.YELLOW + Style.BRIGHT}🚀 Attempting login to AutoStaking...{Style.RESET_ALL}")
                
                # Debug: Log the exact payload being sent
                self.log(f"{Fore.YELLOW + Style.BRIGHT}🔍 Login URL: {login_url}{Style.RESET_ALL}")
                self.log(f"{Fore.YELLOW + Style.BRIGHT}🔍 Payload: {login_payload}{Style.RESET_ALL}")
                
                async with session.post(login_url, json=login_payload, headers=headers) as response:
                    response_text = await response.text()
                    
                    self.log(f"{Fore.CYAN + Style.BRIGHT}🔍 Response Status: {response.status}{Style.RESET_ALL}")
                    self.log(f"{Fore.CYAN + Style.BRIGHT}🔍 Response: {response_text[:300]}...{Style.RESET_ALL}")
                    
                    if response.status == 201:
                        try:
                            response_data = json.loads(response_text)
                            
                            if response_data.get("code") == 0 and "data" in response_data:
                                jwt_token = response_data["data"].get("jwt")
                                user_address = response_data["data"].get("address")
                                
                                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Login successful!{Style.RESET_ALL}")
                                self.log(f"{Fore.CYAN + Style.BRIGHT}📋 Address: {user_address}{Style.RESET_ALL}")
                                self.log(f"{Fore.CYAN + Style.BRIGHT}🔑 JWT Token: {jwt_token[:50]}...{Style.RESET_ALL}")
                                
                                return True, jwt_token
                            else:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ Invalid response format{Style.RESET_ALL}")
                                return False, None
                                
                        except json.JSONDecodeError:
                            self.log(f"{Fore.RED + Style.BRIGHT}❌ Invalid JSON response{Style.RESET_ALL}")
                            return False, None
                    else:
                        self.log(f"{Fore.RED + Style.BRIGHT}❌ Login failed - Status: {response.status}{Style.RESET_ALL}")
                        return False, None
                        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error during login: {str(e)}{Style.RESET_ALL}")
            return False, None
        
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

    def print_login_question(self):
        while True:
            try:
                print(f"\n{Fore.GREEN + Style.BRIGHT}🔐 AutoStaking Operations Configuration:{Style.RESET_ALL}")
                print(f"{Fore.CYAN + Style.BRIGHT}Each operation includes: Login → Faucet Claim → Token Approval → Multicall{Style.RESET_ALL}")
                self.login_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How many complete operations per account? {Style.RESET_ALL}"))
                if self.login_count > 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}❌ Please enter a valid number{Style.RESET_ALL}")

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
                print(f"{Fore.WHITE + Style.BRIGHT}1.{Style.RESET_ALL} AutoStaking Complete Operations (Login + Faucet + Approval + Multicall)")
                
                choose = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter your choice (1): {Style.RESET_ALL}"))
                if choose == 1:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}❌ Please enter 1{Style.RESET_ALL}")
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
            self.print_login_question()
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
        
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
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
    
    async def process_perform_login(self, account: str, address: str, use_proxy: bool):
        # Step 1: Login
        login_success, jwt_token = await self.perform_login(account, address, use_proxy)
        if not login_success:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ AutoStaking Login Failed{Style.RESET_ALL}")
            return False
        
        self.log(f"{Fore.GREEN + Style.BRIGHT}✅ AutoStaking Login Success{Style.RESET_ALL}")
        
        # Small delay between operations
        await asyncio.sleep(2)
        
        # Step 2: Claim Faucet (will check eligibility first)
        faucet_success = await self.claim_faucet(account, address, use_proxy)
        # Note: faucet_success can be True even if skipped due to cooldown
        
        # Small delay between transactions
        await asyncio.sleep(2)
        
        # Step 3: Approve Token (will check allowance first)
        approval_success = await self.approve_token(account, address, use_proxy)
        if not approval_success:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Token approval failed{Style.RESET_ALL}")
            return False
        
        # Small delay between transactions
        await asyncio.sleep(2)
        
        # Step 4: Perform Multicall Transaction with JWT token
        multicall_success = await self.perform_multicall(account, address, use_proxy, jwt_token)
        if not multicall_success:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Multicall transaction failed{Style.RESET_ALL}")
            return False
        
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}✅ Complete AutoStaking Operations Success{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | "
            f"Address: {address[:10]}...{address[-6:]}{Style.RESET_ALL}"
        )
        return True

    async def process_option_1(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}AutoStaking Complete Operations{Style.RESET_ALL}"
        )
        
        success_count = 0
        for i in range(self.login_count):
            self.log(
                f"{Fore.GREEN+Style.BRIGHT}🚀 Operation {i+1}/{self.login_count} (Login + Faucet + Approval + Multicall){Style.RESET_ALL}"
            )
            
            success = await self.process_perform_login(account, address, use_proxy)
            if success:
                success_count += 1
            
            if i < self.login_count - 1:
                await self.print_timer()
        
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}📊 Operations Summary: {success_count}/{self.login_count} successful{Style.RESET_ALL}"
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
        autostaking = AutoStakingBot()
        asyncio.run(autostaking.main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED + Style.BRIGHT}❌ Process interrupted by user{Style.RESET_ALL}")
