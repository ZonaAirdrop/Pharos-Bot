from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from eth_account.messages import encode_defunct
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime, timezone
import asyncio
import random
import json
import os
import pytz
from colorama import *

wib = pytz.timezone('Asia/Jakarta')

class AquaFluxBot:
    def __init__(self) -> None:
        self.HEADERS = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6,te;q=0.5",
            "Origin": "https://playground.aquaflux.pro",
            "Referer": "https://playground.aquaflux.pro/",
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
        self.BASE_API = "https://api.aquaflux.pro"
        self.RPC_URL = "https://api.zan.top/node/v1/pharos/testnet/54b49326c9f44b6e8730dc5dd4348421"
        self.AQUAFLUX_CONTRACT = "0xCc8cF44E196CaB28DBA2d514dc7353af0eFb370E"
        self.CHAIN_ID = 688688
        
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.operation_count = 0
        self.min_delay = 0
        self.max_delay = 0
        self.jwt_tokens = {}  # Store JWT tokens for each address

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
        print(Fore.GREEN + Style.BRIGHT + "    ⚡ AquaFlux RWAIFI Bot  ⚡")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.YELLOW + Style.BRIGHT + "    🧠 Project    : AquaFlux - RWAIFI Automation")
        print(Fore.YELLOW + Style.BRIGHT + "    🧑‍💻 Author     : YetiDAO")
        print(Fore.YELLOW + Style.BRIGHT + "    🌐 Status     : Running & Monitoring...")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.MAGENTA + Style.BRIGHT + "    🧬 Powered by Cryptodai3 × YetiDAO | Buddy v1.9 🚀")
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

    async def perform_aquaflux_signin(self, account: str, address: str, use_proxy: bool):
        """Sign in to AquaFlux using wallet-login API endpoint"""
        try:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy_url, proxy_auth = self.build_proxy_config(proxy)
            
            request_kwargs = {"timeout": ClientTimeout(total=30), "auto_decompress": False}
            if connector:
                request_kwargs["connector"] = connector
            if proxy_url and proxy_auth:
                request_kwargs["proxy"] = proxy_url
                request_kwargs["proxy_auth"] = proxy_auth

            async with ClientSession(**request_kwargs) as session:
                # Create signature for wallet login
                timestamp = int(datetime.now().timestamp() * 1000)  # Milliseconds
                message = f"Sign in to AquaFlux with timestamp: {timestamp}"
                
                # Sign the message using the private key
                account_obj = Account.from_key(account)
                message_hash = encode_defunct(text=message)
                signed_message = account_obj.sign_message(message_hash)
                signature = "0x" + signed_message.signature.hex()
                
                # Prepare wallet login payload
                login_payload = {
                    "address": address,
                    "message": message,
                    "signature": signature
                }
                
                headers = self.HEADERS.copy()
                
                self.log(f"{Fore.YELLOW + Style.BRIGHT}🔐 Performing wallet login authentication{Style.RESET_ALL}")
                self.log(f"{Fore.CYAN + Style.BRIGHT}📝 Message: {message}{Style.RESET_ALL}")
                self.log(f"{Fore.CYAN + Style.BRIGHT}🔑 Signature: {signature[:50]}...{Style.RESET_ALL}")
               
                
                # Make wallet login request
                login_url = f"{self.BASE_API}/api/v1/users/wallet-login"
                
                async with session.post(login_url, json=login_payload, headers=headers) as response:
                    try:
                        # Read raw response first
                        response_bytes = await response.read()
                        response_text = None
                        
                        # Handle different response encodings manually since aiohttp may not decompress zstd
                        content_encoding = response.headers.get('content-encoding', '').lower()
                        self.log(f"{Fore.CYAN + Style.BRIGHT}🔍 Content-Encoding: {content_encoding or 'none'}{Style.RESET_ALL}")
                        
                        if content_encoding == 'zstd':
                            try:
                                import zstandard as zstd
                                dctx = zstd.ZstdDecompressor()
                                decompressed_bytes = dctx.decompress(response_bytes)
                                response_text = decompressed_bytes.decode('utf-8')
                                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ zstd decompression successful{Style.RESET_ALL}")
                            except ImportError:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ zstandard library not available for zstd decompression{Style.RESET_ALL}")
                                response_text = response_bytes.decode('utf-8', errors='replace')
                            except Exception as e:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ zstd decompression failed: {str(e)}{Style.RESET_ALL}")
                                response_text = response_bytes.decode('utf-8', errors='replace')
                        elif content_encoding == 'gzip':
                            try:
                                import gzip
                                response_text = gzip.decompress(response_bytes).decode('utf-8')
                                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ gzip decompression successful{Style.RESET_ALL}")
                            except Exception as e:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ gzip decompression failed: {str(e)}{Style.RESET_ALL}")
                                response_text = response_bytes.decode('utf-8', errors='replace')
                        elif content_encoding == 'br':
                            try:
                                import brotli
                                response_text = brotli.decompress(response_bytes).decode('utf-8')
                                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ brotli decompression successful{Style.RESET_ALL}")
                            except ImportError:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ brotli library not available{Style.RESET_ALL}")
                                response_text = response_bytes.decode('utf-8', errors='replace')
                            except Exception as e:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ brotli decompression failed: {str(e)}{Style.RESET_ALL}")
                                response_text = response_bytes.decode('utf-8', errors='replace')
                        else:
                            # No compression or unsupported compression
                            try:
                                response_text = response_bytes.decode('utf-8')
                                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ No compression - direct decode successful{Style.RESET_ALL}")
                            except UnicodeDecodeError:
                                response_text = response_bytes.decode('latin-1', errors='ignore')
                                self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ Fallback to latin-1 decode{Style.RESET_ALL}")
                        
                        self.log(f"{Fore.CYAN + Style.BRIGHT}🔍 Response Status: {response.status}{Style.RESET_ALL}")
                        self.log(f"{Fore.CYAN + Style.BRIGHT}🔍 Content-Type: {response.headers.get('content-type', 'unknown')}{Style.RESET_ALL}")
                        
                        if response.status == 200:
                            try:
                                # Try to parse the response text as JSON
                                response_data = json.loads(response_text)
                                
                                if response_data.get("status") == "success" and "data" in response_data:
                                    data = response_data["data"]
                                    access_token = data.get("accessToken")
                                    refresh_token = data.get("refreshToken")
                                    user_info = data.get("user", {})
                                    
                                    if access_token:
                                        # Store the new tokens for this address
                                        self.jwt_tokens[address] = {
                                            "access_token": access_token,
                                            "refresh_token": refresh_token,
                                            "user_id": user_info.get("id"),
                                            "wallet_address": user_info.get("walletAddress"),
                                            "timestamp": timestamp
                                        }
                                        
                                        self.log(f"{Fore.GREEN + Style.BRIGHT}✅ AquaFlux wallet login successful{Style.RESET_ALL}")
                                        self.log(f"{Fore.CYAN + Style.BRIGHT}👤 User ID: {user_info.get('id', 'Unknown')}{Style.RESET_ALL}")
                                        self.log(f"{Fore.CYAN + Style.BRIGHT}📋 Wallet: {address}{Style.RESET_ALL}")
                                        self.log(f"{Fore.CYAN + Style.BRIGHT}🔑 New access token obtained{Style.RESET_ALL}")
                                        
                                        return True
                                    else:
                                        self.log(f"{Fore.RED + Style.BRIGHT}❌ No access token in response{Style.RESET_ALL}")
                                        return False
                                else:
                                    self.log(f"{Fore.RED + Style.BRIGHT}❌ Invalid response format{Style.RESET_ALL}")
                                    self.log(f"{Fore.RED + Style.BRIGHT}Response: {str(response_data)[:200]}...{Style.RESET_ALL}")
                                    return False
                                    
                            except Exception as json_error:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ JSON parsing error: {str(json_error)}{Style.RESET_ALL}")
                                self.log(f"{Fore.RED + Style.BRIGHT}Response: {response_text[:200]}...{Style.RESET_ALL}")
                                return False
                        else:
                            self.log(f"{Fore.RED + Style.BRIGHT}❌ Wallet login failed - Status: {response.status}{Style.RESET_ALL}")
                            self.log(f"{Fore.RED + Style.BRIGHT}Response: {response_text[:200]}...{Style.RESET_ALL}")
                            return False
                            
                    except Exception as response_error:
                        self.log(f"{Fore.RED + Style.BRIGHT}❌ Response processing error: {str(response_error)}{Style.RESET_ALL}")
                        return False
                        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error during AquaFlux wallet login: {str(e)}{Style.RESET_ALL}")
            return False

    async def check_token_holding(self, address: str, use_proxy: bool):
        """Check if the user holds the required token for NFT minting"""
        try:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy_url, proxy_auth = self.build_proxy_config(proxy)
            
            request_kwargs = {"timeout": ClientTimeout(total=30), "auto_decompress": False}
            if connector:
                request_kwargs["connector"] = connector
            if proxy_url and proxy_auth:
                request_kwargs["proxy"] = proxy_url
                request_kwargs["proxy_auth"] = proxy_auth

            async with ClientSession(**request_kwargs) as session:
                # Get the stored JWT token for this address
                token_data = self.jwt_tokens.get(address)
                if not token_data:
                    self.log(f"{Fore.RED + Style.BRIGHT}❌ No JWT token found for token holding check{Style.RESET_ALL}")
                    return False
                
                access_token = token_data.get("access_token")
                if not access_token:
                    self.log(f"{Fore.RED + Style.BRIGHT}❌ No access token in stored data{Style.RESET_ALL}")
                    return False
                
                # Update headers with the dynamic access token
                headers = self.HEADERS.copy()
                headers["Authorization"] = f"Bearer {access_token}"
                
                self.log(f"{Fore.YELLOW + Style.BRIGHT}🔍 Checking token holding status...{Style.RESET_ALL}")
                
                # Check token holding API endpoint
                api_url = f"{self.BASE_API}/api/v1/users/check-token-holding"
                
                async with session.post(api_url, headers=headers) as response:
                    try:
                        # Read raw response first
                        response_bytes = await response.read()
                        response_text = None
                        
                        # Handle different response encodings manually
                        content_encoding = response.headers.get('content-encoding', '').lower()
                        
                        if content_encoding == 'zstd':
                            try:
                                import zstandard as zstd
                                dctx = zstd.ZstdDecompressor()
                                decompressed_bytes = dctx.decompress(response_bytes)
                                response_text = decompressed_bytes.decode('utf-8')
                            except ImportError:
                                response_text = response_bytes.decode('utf-8', errors='replace')
                            except Exception as e:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ zstd decompression failed: {str(e)}{Style.RESET_ALL}")
                                response_text = response_bytes.decode('utf-8', errors='replace')
                        elif content_encoding == 'gzip':
                            try:
                                import gzip
                                response_text = gzip.decompress(response_bytes).decode('utf-8')
                            except Exception as e:
                                response_text = response_bytes.decode('utf-8', errors='replace')
                        elif content_encoding == 'br':
                            try:
                                import brotli
                                response_text = brotli.decompress(response_bytes).decode('utf-8')
                            except ImportError:
                                response_text = response_bytes.decode('utf-8', errors='replace')
                            except Exception as e:
                                response_text = response_bytes.decode('utf-8', errors='replace')
                        else:
                            try:
                                response_text = response_bytes.decode('utf-8')
                            except UnicodeDecodeError:
                                response_text = response_bytes.decode('latin-1', errors='ignore')
                        
                        if response.status == 200:
                            try:
                                # Try to parse the response text as JSON
                                response_data = json.loads(response_text)
                                
                                if response_data.get("status") == "success" and "data" in response_data:
                                    data = response_data["data"]
                                    is_holding = data.get("isHoldingToken", False)
                                    
                                    if is_holding:
                                        self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Account holds required token for NFT minting{Style.RESET_ALL}")
                                        return True
                                    else:
                                        self.log(f"{Fore.RED + Style.BRIGHT}❌ Account does not hold required token{Style.RESET_ALL}")
                                        return False
                                else:
                                    self.log(f"{Fore.RED + Style.BRIGHT}❌ Invalid token holding response format{Style.RESET_ALL}")
                                    self.log(f"{Fore.RED + Style.BRIGHT}Response: {str(response_data)[:200]}...{Style.RESET_ALL}")
                                    return False
                                    
                            except Exception as json_error:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ JSON parsing error in token holding check: {str(json_error)}{Style.RESET_ALL}")
                                self.log(f"{Fore.RED + Style.BRIGHT}Response: {response_text[:200]}...{Style.RESET_ALL}")
                                return False
                        else:
                            self.log(f"{Fore.RED + Style.BRIGHT}❌ Token holding check failed - Status: {response.status}{Style.RESET_ALL}")
                            self.log(f"{Fore.RED + Style.BRIGHT}Response: {response_text[:200]}...{Style.RESET_ALL}")
                            return False
                            
                    except Exception as response_error:
                        self.log(f"{Fore.RED + Style.BRIGHT}❌ Response processing error in token holding check: {str(response_error)}{Style.RESET_ALL}")
                        return False
                        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error checking token holding: {str(e)}{Style.RESET_ALL}")
            return False

    async def check_twitter_binding_status(self, address: str, use_proxy: bool):
        """Check if the user has connected their Twitter account"""
        try:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy_url, proxy_auth = self.build_proxy_config(proxy)
            
            request_kwargs = {"timeout": ClientTimeout(total=30), "auto_decompress": False}
            if connector:
                request_kwargs["connector"] = connector
            if proxy_url and proxy_auth:
                request_kwargs["proxy"] = proxy_url
                request_kwargs["proxy_auth"] = proxy_auth

            async with ClientSession(**request_kwargs) as session:
                # Get the stored JWT token for this address
                token_data = self.jwt_tokens.get(address)
                if not token_data:
                    self.log(f"{Fore.RED + Style.BRIGHT}❌ No JWT token found for Twitter binding check{Style.RESET_ALL}")
                    return False
                
                access_token = token_data.get("access_token")
                if not access_token:
                    self.log(f"{Fore.RED + Style.BRIGHT}❌ No access token in stored data{Style.RESET_ALL}")
                    return False
                
                # Update headers with the dynamic access token
                headers = self.HEADERS.copy()
                headers["Authorization"] = f"Bearer {access_token}"
                
                self.log(f"{Fore.YELLOW + Style.BRIGHT}🔍 Checking Twitter binding status...{Style.RESET_ALL}")
                
                # Check Twitter binding status API endpoint
                api_url = f"{self.BASE_API}/api/v1/users/twitter/binding-status"
                
                async with session.get(api_url, headers=headers) as response:
                    try:
                        # Read raw response first
                        response_bytes = await response.read()
                        response_text = None
                        
                        # Handle different response encodings manually
                        content_encoding = response.headers.get('content-encoding', '').lower()
                        
                        if content_encoding == 'zstd':
                            try:
                                import zstandard as zstd
                                dctx = zstd.ZstdDecompressor()
                                decompressed_bytes = dctx.decompress(response_bytes)
                                response_text = decompressed_bytes.decode('utf-8')
                            except ImportError:
                                response_text = response_bytes.decode('utf-8', errors='replace')
                            except Exception as e:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ zstd decompression failed: {str(e)}{Style.RESET_ALL}")
                                response_text = response_bytes.decode('utf-8', errors='replace')
                        elif content_encoding == 'gzip':
                            try:
                                import gzip
                                response_text = gzip.decompress(response_bytes).decode('utf-8')
                            except Exception as e:
                                response_text = response_bytes.decode('utf-8', errors='replace')
                        elif content_encoding == 'br':
                            try:
                                import brotli
                                response_text = brotli.decompress(response_bytes).decode('utf-8')
                            except ImportError:
                                response_text = response_bytes.decode('utf-8', errors='replace')
                            except Exception as e:
                                response_text = response_bytes.decode('utf-8', errors='replace')
                        else:
                            try:
                                response_text = response_bytes.decode('utf-8')
                            except UnicodeDecodeError:
                                response_text = response_bytes.decode('latin-1', errors='ignore')
                        
                        if response.status == 200:
                            try:
                                # Try to parse the response text as JSON
                                response_data = json.loads(response_text)
                                
                                if response_data.get("status") == "success" and "data" in response_data:
                                    data = response_data["data"]
                                    is_bound = data.get("bound", False)
                                    twitter_info = data.get("twitterInfo", {})
                                    
                                    if is_bound:
                                        username = twitter_info.get("username", "Unknown")
                                        twitter_id = twitter_info.get("id", "Unknown")
                                        self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Twitter account is connected{Style.RESET_ALL}")
                                        self.log(f"{Fore.CYAN + Style.BRIGHT}🐦 Twitter: @{username} (ID: {twitter_id}){Style.RESET_ALL}")
                                        return True
                                    else:
                                        self.log(f"{Fore.RED + Style.BRIGHT}❌ Twitter account is not connected{Style.RESET_ALL}")
                                        return False
                                else:
                                    self.log(f"{Fore.RED + Style.BRIGHT}❌ Invalid Twitter binding status response format{Style.RESET_ALL}")
                                    self.log(f"{Fore.RED + Style.BRIGHT}Response: {str(response_data)[:200]}...{Style.RESET_ALL}")
                                    return False
                                    
                            except Exception as json_error:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ JSON parsing error in Twitter binding check: {str(json_error)}{Style.RESET_ALL}")
                                self.log(f"{Fore.RED + Style.BRIGHT}Response: {response_text[:200]}...{Style.RESET_ALL}")
                                return False
                        else:
                            self.log(f"{Fore.RED + Style.BRIGHT}❌ Twitter binding check failed - Status: {response.status}{Style.RESET_ALL}")
                            self.log(f"{Fore.RED + Style.BRIGHT}Response: {response_text[:200]}...{Style.RESET_ALL}")
                            return False
                            
                    except Exception as response_error:
                        self.log(f"{Fore.RED + Style.BRIGHT}❌ Response processing error in Twitter binding check: {str(response_error)}{Style.RESET_ALL}")
                        return False
                        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error checking Twitter binding status: {str(e)}{Style.RESET_ALL}")
            return False

    async def get_signature_from_api(self, address: str, nft_type: int, use_proxy: bool):
        """Get signature from AquaFlux API using dynamic JWT token"""
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
                # Get the stored JWT token for this address
                token_data = self.jwt_tokens.get(address)
                if not token_data:
                    self.log(f"{Fore.RED + Style.BRIGHT}❌ No JWT token found for address{Style.RESET_ALL}")
                    return None, None
                
                access_token = token_data.get("access_token")
                if not access_token:
                    self.log(f"{Fore.RED + Style.BRIGHT}❌ No access token in stored data{Style.RESET_ALL}")
                    return None, None
                
                # Prepare request payload exactly as shown in the working example
                payload = {
                    "walletAddress": address,
                    "requestedNftType": nft_type
                }
                
                # Update headers with the dynamic access token
                headers = self.HEADERS.copy()
                headers["Authorization"] = f"Bearer {access_token}"
                
                self.log(f"{Fore.YELLOW + Style.BRIGHT}� Using dynamic access token for signature request{Style.RESET_ALL}")
                
                # Try the exact API endpoint from your working example
                api_url = f"{self.BASE_API}/api/v1/users/get-signature"
                
                self.log(f"{Fore.YELLOW + Style.BRIGHT}🔍 Requesting signature from: {api_url.split('/')[-1]}...{Style.RESET_ALL}")
                
                async with session.post(api_url, json=payload, headers=headers) as response:
                    try:
                        response_text = await response.text()
                        
                        if response.status == 200:
                            try:
                                response_data = await response.json()
                                
                                if response_data.get("status") == "success" and "data" in response_data:
                                    data = response_data["data"]
                                    signature = data.get("signature")
                                    expires_at = data.get("expiresAt")
                                    nft_type_response = data.get("nftType")
                                    
                                    if signature and signature.startswith("0x"):
                                        self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Signature obtained successfully{Style.RESET_ALL}")
                                        self.log(f"{Fore.CYAN + Style.BRIGHT}🔑 Signature: {signature[:50]}...{Style.RESET_ALL}")
                                        self.log(f"{Fore.CYAN + Style.BRIGHT}⏰ Expires at: {expires_at}{Style.RESET_ALL}")
                                        self.log(f"{Fore.CYAN + Style.BRIGHT}🎭 NFT Type: {nft_type_response}{Style.RESET_ALL}")
                                        return signature, expires_at
                                    else:
                                        self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ No valid signature found in response{Style.RESET_ALL}")
                                        self.log(f"{Fore.CYAN + Style.BRIGHT}Response: {str(response_data)[:200]}...{Style.RESET_ALL}")
                                        return None, None
                                else:
                                    self.log(f"{Fore.RED + Style.BRIGHT}❌ Invalid response format{Style.RESET_ALL}")
                                    self.log(f"{Fore.RED + Style.BRIGHT}Response: {str(response_data)[:200]}...{Style.RESET_ALL}")
                                    return None, None
                                    
                            except Exception as json_error:
                                self.log(f"{Fore.RED + Style.BRIGHT}❌ JSON parsing error: {str(json_error)}{Style.RESET_ALL}")
                                self.log(f"{Fore.RED + Style.BRIGHT}Response: {response_text[:200]}...{Style.RESET_ALL}")
                                return None, None
                                
                        elif response.status == 401:
                            self.log(f"{Fore.RED + Style.BRIGHT}❌ Authentication failed (401) - Token may be expired{Style.RESET_ALL}")
                            self.log(f"{Fore.RED + Style.BRIGHT}Response: {response_text[:200]}...{Style.RESET_ALL}")
                            return None, None
                        else:
                            self.log(f"{Fore.RED + Style.BRIGHT}❌ API request failed - Status: {response.status}{Style.RESET_ALL}")
                            self.log(f"{Fore.RED + Style.BRIGHT}Response: {response_text[:200]}...{Style.RESET_ALL}")
                            return None, None
                            
                    except Exception as response_error:
                        self.log(f"{Fore.RED + Style.BRIGHT}❌ Response processing error: {str(response_error)}{Style.RESET_ALL}")
                        return None, None
                        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error getting signature: {str(e)}{Style.RESET_ALL}")
            return None, None

    async def send_raw_transaction_with_retries(self, account, web3, tx, retries=5):
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

    async def perform_transaction_1(self, account: str, address: str, use_proxy: bool):
        """First transaction: 0x48c54b9d"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to connect to Web3{Style.RESET_ALL}")
                return None, None
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔄 Transaction 1: First signing operation{Style.RESET_ALL}")
            
            # Get nonce
            current_nonce = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_transaction_count, address)
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Using nonce: {current_nonce}{Style.RESET_ALL}")
            
            # Transaction data exactly as provided
            transaction_data = "0x48c54b9d"
            
            # Get current gas price from network
            try:
                gas_price = await asyncio.get_event_loop().run_in_executor(None, lambda: web3.eth.gas_price)
            except:
                gas_price = web3.to_wei(1.2, 'gwei')
            
            # Build transaction
            tx = {
                'chainId': self.CHAIN_ID,
                'gas': 0x388c8,  # From your example
                'gasPrice': gas_price,
                'nonce': current_nonce,
                'to': web3.to_checksum_address(self.AQUAFLUX_CONTRACT),
                'value': 0,  # No ETH value
                'data': transaction_data
            }

            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Gas Price: {web3.from_wei(gas_price, 'gwei')} gwei{Style.RESET_ALL}")

            # Send transaction
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}📝 Transaction 1 sent: {tx_hash}{Style.RESET_ALL}")
            
            # Wait for receipt
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            
            if receipt and receipt.status == 1:
                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Transaction 1 confirmed in block {receipt.blockNumber}{Style.RESET_ALL}")
                return tx_hash, receipt.blockNumber
            else:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Transaction 1 failed - Status: {receipt.status if receipt else 'No receipt'}{Style.RESET_ALL}")
                return None, None
            
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error performing transaction 1: {str(e)}{Style.RESET_ALL}")
            return None, None

    async def perform_transaction_2(self, account: str, address: str, use_proxy: bool):
        """Second transaction: 0x7905642a - signing transaction (not ETH transfer)"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to connect to Web3{Style.RESET_ALL}")
                return None, None
            
            # This is a parameter for signing, not an ETH amount to transfer
            amount_parameter = 0x056bc75e2d63100000
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔄 Transaction 2: Signing transaction with parameter{Style.RESET_ALL}")
            
            # Get nonce
            current_nonce = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_transaction_count, address)
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Using nonce: {current_nonce}{Style.RESET_ALL}")
            
            # Transaction data: function selector + parameter (not ETH amount)
            function_selector = "7905642a"
            param_hex = format(amount_parameter, '064x')  # 64 chars (32 bytes)
            transaction_data = "0x" + function_selector + param_hex
            
            # Get current gas price from network
            try:
                gas_price = await asyncio.get_event_loop().run_in_executor(None, lambda: web3.eth.gas_price)
            except:
                gas_price = web3.to_wei(1.2, 'gwei')
            
            # Build transaction
            tx = {
                'chainId': self.CHAIN_ID,
                'gas': 0x30527,  # From your example
                'gasPrice': gas_price,
                'nonce': current_nonce,
                'to': web3.to_checksum_address(self.AQUAFLUX_CONTRACT),
                'value': 0,  # No ETH value
                'data': transaction_data
            }

            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Gas Price: {web3.from_wei(gas_price, 'gwei')} gwei{Style.RESET_ALL}")

            # Send transaction
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}📝 Transaction 2 sent: {tx_hash}{Style.RESET_ALL}")
            
            # Wait for receipt
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            
            if receipt and receipt.status == 1:
                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Transaction 2 confirmed in block {receipt.blockNumber}{Style.RESET_ALL}")
                return tx_hash, receipt.blockNumber
            else:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Transaction 2 failed - Status: {receipt.status if receipt else 'No receipt'}{Style.RESET_ALL}")
                return None, None
            
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error performing transaction 2: {str(e)}{Style.RESET_ALL}")
            return None, None

    async def perform_transaction_3(self, account: str, address: str, use_proxy: bool):
        """Third transaction: 0x75e7e053 - NFT claiming with signature"""
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to connect to Web3{Style.RESET_ALL}")
                return None, None
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔄 Transaction 3: NFT claiming operation{Style.RESET_ALL}")
            
            # Check token holding first
            is_holding_token = await self.check_token_holding(address, use_proxy)
            if not is_holding_token:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Account does not hold required token for NFT minting{Style.RESET_ALL}")
                return None, None
            
            # Check Twitter binding status to determine NFT type
            is_twitter_bound = await self.check_twitter_binding_status(address, use_proxy)
            
            # Determine NFT type based on Twitter binding status
            if is_twitter_bound:
                nft_type = 1  # Premium NFT
                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Twitter connected - proceeding with PREMIUM NFT (type 1){Style.RESET_ALL}")
            else:
                nft_type = 0  # Normal NFT
                self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ Twitter not connected - proceeding with NORMAL NFT (type 0){Style.RESET_ALL}")
            
            # Get signature from API with the determined NFT type
            signature, expires_at = await self.get_signature_from_api(address, nft_type, use_proxy)
            
            if not signature:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Failed to get signature from API{Style.RESET_ALL}")
                return None, None
            
            if not expires_at:
                expires_at = int(datetime.now().timestamp()) + 3600  # 1 hour from now
            
            # Get nonce
            current_nonce = await asyncio.get_event_loop().run_in_executor(None, web3.eth.get_transaction_count, address)
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Using nonce: {current_nonce}{Style.RESET_ALL}")
            
            # Build transaction data based on the contract function signature
            # Function: claimNFT(uint256 nftType, uint256 expiresAt, bytes signature)
            function_selector = "75e7e053"
            
            # Parameters
            nft_type_param = format(nft_type, '064x')  # Dynamic NFT type (0 or 1)
            expires_at_param = format(expires_at, '064x')  # Expires at timestamp
            signature_offset = "0000000000000000000000000000000000000000000000000000000000000060"  # Offset to signature data (96 bytes)
            
            # Clean signature (remove 0x prefix if present)
            clean_signature = signature.replace("0x", "")
            
            # Signature length (65 bytes = 0x41)
            signature_length = "0000000000000000000000000000000000000000000000000000000000000041"
            
            # Pad signature to ensure it's exactly 65 bytes (130 hex chars)
            # The signature should be exactly 65 bytes: 32 bytes r + 32 bytes s + 1 byte v
            if len(clean_signature) == 130:  # 65 bytes * 2 hex chars
                signature_padded = clean_signature
            elif len(clean_signature) == 128:  # Missing recovery byte, add 1b
                signature_padded = clean_signature + "1b"
            else:
                # Pad or truncate to 130 characters (65 bytes)
                signature_padded = clean_signature[:130].ljust(130, '0')
            
            # Add padding to make signature data align to 32-byte boundaries
            signature_data = signature_padded.ljust(192, '0')  # Pad to 96 bytes (3 * 32 bytes)
            
            transaction_data = "0x" + function_selector + nft_type_param + expires_at_param + signature_offset + signature_length + signature_data
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 NFT Type: {nft_type} ({'PREMIUM' if nft_type == 1 else 'NORMAL'}){Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}⏰ Expires At: {expires_at} ({datetime.fromtimestamp(expires_at)}){Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔑 Signature Length: {len(clean_signature)} chars ({len(clean_signature)//2} bytes){Style.RESET_ALL}")
            
            # Get current gas price from network
            try:
                gas_price = await asyncio.get_event_loop().run_in_executor(None, lambda: web3.eth.gas_price)
            except:
                gas_price = web3.to_wei(1, 'gwei')
            
            # Build transaction
            tx = {
                'chainId': self.CHAIN_ID,
                'gas': 0x67131,  # From your example
                'gasPrice': gas_price,
                'nonce': current_nonce,
                'to': web3.to_checksum_address(self.AQUAFLUX_CONTRACT),
                'value': 0,  # No ETH value
                'data': transaction_data
            }

            self.log(f"{Fore.CYAN + Style.BRIGHT}🔧 Gas Price: {web3.from_wei(gas_price, 'gwei')} gwei{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}🔑 Using signature: {signature[:50]}...{Style.RESET_ALL}")

            # Send transaction
            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}📝 Transaction 3 sent: {tx_hash}{Style.RESET_ALL}")
            
            # Wait for receipt
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            
            if receipt and receipt.status == 1:
                self.log(f"{Fore.GREEN + Style.BRIGHT}✅ Transaction 3 confirmed in block {receipt.blockNumber}{Style.RESET_ALL}")
                return tx_hash, receipt.blockNumber
            else:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Transaction 3 failed - Status: {receipt.status if receipt else 'No receipt'}{Style.RESET_ALL}")
                
                # Additional debugging information
                if receipt:
                    try:
                        # Try to get more details about the failure
                        self.log(f"{Fore.YELLOW + Style.BRIGHT}🔍 Gas Used: {receipt.gasUsed}/{tx['gas']}{Style.RESET_ALL}")
                        self.log(f"{Fore.YELLOW + Style.BRIGHT}🔍 Block Number: {receipt.blockNumber}{Style.RESET_ALL}")
                        self.log(f"{Fore.YELLOW + Style.BRIGHT}🔍 Transaction Hash: {tx_hash}{Style.RESET_ALL}")
                        
                        # Log first part of transaction data for debugging
                        self.log(f"{Fore.YELLOW + Style.BRIGHT}🔍 Transaction data preview: {transaction_data[:100]}...{Style.RESET_ALL}")
                    except Exception as debug_error:
                        self.log(f"{Fore.YELLOW + Style.BRIGHT}⚠️ Debug info error: {str(debug_error)}{Style.RESET_ALL}")
                
                return None, None
            
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}❌ Error performing transaction 3: {str(e)}{Style.RESET_ALL}")
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

    def print_operation_question(self):
        while True:
            try:
                print(f"\n{Fore.GREEN + Style.BRIGHT}🚀 AquaFlux Operation Configuration:{Style.RESET_ALL}")
                self.operation_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How many complete operations per account? {Style.RESET_ALL}"))
                if self.operation_count > 0:
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
                print(f"{Fore.WHITE + Style.BRIGHT}1.{Style.RESET_ALL} AquaFlux RWAIFI Operations")
                
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
            self.print_operation_question()
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

    async def process_option_1(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}AquaFlux RWAIFI Operations{Style.RESET_ALL}"
        )
        
        success_count = 0
        for i in range(self.operation_count):
            self.log(
                f"{Fore.GREEN+Style.BRIGHT}🚀 Operation {i+1}/{self.operation_count}{Style.RESET_ALL}"
            )
            
            # Step 1: Sign in to AquaFlux
            signin_success = await self.perform_aquaflux_signin(account, address, use_proxy)
            if not signin_success:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Sign-in failed, skipping this operation{Style.RESET_ALL}")
                continue
            
            # Small delay between operations
            await asyncio.sleep(2)
            
            # Step 2: Transaction 1
            tx1_hash, tx1_block = await self.perform_transaction_1(account, address, use_proxy)
            if not tx1_hash:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Transaction 1 failed, skipping remaining operations{Style.RESET_ALL}")
                continue
            
            # Small delay between transactions
            await asyncio.sleep(2)
            
            # Step 3: Transaction 2
            tx2_hash, tx2_block = await self.perform_transaction_2(account, address, use_proxy)
            if not tx2_hash:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Transaction 2 failed, skipping transaction 3{Style.RESET_ALL}")
                continue
            
            # Small delay between transactions
            await asyncio.sleep(2)
            
            # Step 4: Transaction 3
            tx3_hash, tx3_block = await self.perform_transaction_3(account, address, use_proxy)
            if tx3_hash:
                success_count += 1
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}✅ Complete Operation Success{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | "
                    f"Tx1: {tx1_hash[:10]}... | "
                    f"Tx2: {tx2_hash[:10]}... | "
                    f"Tx3: {tx3_hash[:10]}...{Style.RESET_ALL}"
                )
            else:
                self.log(f"{Fore.RED + Style.BRIGHT}❌ Transaction 3 failed{Style.RESET_ALL}")
            
            if i < self.operation_count - 1:
                await self.print_timer()
        
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}📊 Operation Summary: {success_count}/{self.operation_count} successful{Style.RESET_ALL}"
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
        aquaflux = AquaFluxBot()
        asyncio.run(aquaflux.main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED + Style.BRIGHT}❌ Process interrupted by user{Style.RESET_ALL}")
