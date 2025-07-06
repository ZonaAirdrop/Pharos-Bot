from web3 import Web3
from eth_utils.conversions import to_hex
from eth_abi.abi import encode
from eth_account import Account
from eth_account.messages import encode_defunct
from datetime import datetime, timedelta
from colorama import Fore, Style, init as colorama_init
import asyncio, random, json, time, os, pytz, secrets, signal, sys

colorama_init(autoreset=True)
wib = pytz.timezone('Asia/Jakarta')

# Global flag for graceful shutdown
shutdown_requested = False

class TransactionVerifier:
    def __init__(self, rpc_url):
        self.rpc_url = rpc_url
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    async def verify_transaction(self, tx_hash, max_wait_time=120, check_interval=5):
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                receipt = self.web3.eth.get_transaction_receipt(tx_hash)
                
                if receipt:
                    if receipt.status == 1:
                        print(f"{Fore.GREEN}✅ Transaction verified: {tx_hash}")
                        return True
                    else:
                        print(f"{Fore.RED}❌ Transaction failed: {tx_hash}")
                        return False
                
            except Exception as e:
                if "not found" not in str(e).lower():
                    print(f"{Fore.YELLOW}⚠️ Error checking transaction: {e}")
            
            await asyncio.sleep(check_interval)
        
        print(f"{Fore.RED}❌ Transaction verification timeout: {tx_hash}")
        return False

class PharosTestnet:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://testnet.pharosnetwork.xyz",
            "Referer": "https://testnet.pharosnetwork.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0"
        }
        self.BASE_API = "https://api.pharosnetwork.xyz"
        self.RPC_URL = "https://testnet.dplabs-internal.com"
        self.WPHRS_CONTRACT_ADDRESS = "0x76aaaDA469D23216bE5f7C596fA25F282Ff9b364"
        self.USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
        self.USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
        self.SWAP_ROUTER_ADDRESS = "0xbc3813206c3cb99347c96a18a757ed39386d12b8"
        self.POSITION_MANAGER_ADDRESS = "0x7ec504ae0771ec2aa1900f117e609868d0650043"
        
        # Trading pairs configuration
        self.SWAP_PAIRS = {
            "WPHRS_TO_USDC": {
                "token_in": self.WPHRS_CONTRACT_ADDRESS,
                "token_out": self.USDC_CONTRACT_ADDRESS,
                "name": "WPHRS → USDC"
            },
            "WPHRS_TO_USDT": {
                "token_in": self.WPHRS_CONTRACT_ADDRESS,
                "token_out": self.USDT_CONTRACT_ADDRESS,
                "name": "WPHRS → USDT"
            },
            "USDC_TO_WPHRS": {
                "token_in": self.USDC_CONTRACT_ADDRESS,
                "token_out": self.WPHRS_CONTRACT_ADDRESS,
                "name": "USDC → WPHRS"
            },
            "USDT_TO_WPHRS": {
                "token_in": self.USDT_CONTRACT_ADDRESS,
                "token_out": self.WPHRS_CONTRACT_ADDRESS,
                "name": "USDT → WPHRS"
            }
        }
        
        self.LP_PAIRS = {
            "WPHRS_USDC": {
                "token0": self.WPHRS_CONTRACT_ADDRESS,
                "token1": self.USDC_CONTRACT_ADDRESS,
                "name": "WPHRS/USDC"
            },
            "WPHRS_USDT": {
                "token0": self.WPHRS_CONTRACT_ADDRESS,
                "token1": self.USDT_CONTRACT_ADDRESS,
                "name": "WPHRS/USDT"
            }
        }
        
        # Updated ERC20 ABI with complete function signatures
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"account","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"symbol","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"string"}]},
            {"type":"function","name":"name","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"string"}]},
            {"type":"function","name":"deposit","stateMutability":"payable","inputs":[],"outputs":[]},
            {"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"wad","type":"uint256"}],"outputs":[]}
        ]''')
        
        # Swap Router ABI
        self.SWAP_CONTRACT_ABI = [
            {
                "inputs": [
                    {"internalType": "bytes", "name": "commands", "type": "bytes"},
                    {"internalType": "bytes[]", "name": "inputs", "type": "bytes[]"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "execute",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        
        # Position Manager ABI
        self.ADD_LP_CONTRACT_ABI = [
            {
                "inputs": [
                    {"internalType": "bytes[]", "name": "data", "type": "bytes[]"}
                ],
                "name": "multicall",
                "outputs": [{"internalType": "bytes[]", "name": "results", "type": "bytes[]"}],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        
        self.tx_verifier = TransactionVerifier(self.RPC_URL)
        self.min_delay = 5
        self.max_delay = 10
        
        # Operation counters
        self.swap_count = 0
        self.unwrap_count = 0
        self.add_lp_count = 0
        
        # User configurations
        self.total_swaps = 0
        self.total_unwraps = 0 
        self.total_add_lps = 0
        self.auto_mode = False
        self.last_run_time = 0
        
        # Timer configuration
        self.start_time = None
        self.total_runtime = 24 * 3600  # 24 hours in seconds

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            global shutdown_requested
            shutdown_requested = True
            print(f"\n{Fore.YELLOW}📢 Graceful shutdown requested. Finishing current operations...")
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\n" + "═" * 60)
        print(Fore.GREEN + Style.BRIGHT + "    ⚡ Pharos X Zentrafi Testnet Bot (ENHANCED) ⚡")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.YELLOW + Style.BRIGHT + "    Team : Zonaairdrop")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.RED + Style.BRIGHT + "   Channel telegram : @ZonaAirdr0p")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.MAGENTA + Style.BRIGHT + "   Enhanced with Multi-Pair Swap & Timer")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "═" * 60 + "\n")

    def display_countdown(self):
        """Display countdown timer in HH:MM:SS format"""
        if self.start_time is None:
            return "00:00:00"
        
        elapsed = time.time() - self.start_time
        remaining = max(0, self.total_runtime - elapsed)
        
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def display_countdown_live(self):
        """Display live countdown timer with digital clock style"""
        if self.start_time is None:
            self.start_time = time.time()
        
        elapsed = time.time() - self.start_time
        remaining = max(0, self.total_runtime - elapsed)
        
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        
        # Digital clock style display
        countdown_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        print(f"\r{Fore.CYAN}⏰ Countdown Timer: {Fore.YELLOW}{countdown_str} {Fore.CYAN}remaining", end="", flush=True)
        
        return remaining > 0

    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception:
            return None

    def generate_address(self, account: str):
        """Generate address directly from private key"""
        try:
            account_obj = Account.from_key(account)
            address = account_obj.address
            return address
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Generate Address Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None

    def generate_random_receiver(self):
        """Generate random receiver address"""
        try:
            private_key_bytes = secrets.token_bytes(32)
            private_key_hex = to_hex(private_key_bytes)
            account = Account.from_key(private_key_hex)
            receiver = account.address
            return receiver
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Generate Random Receiver Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None

    def generate_signature(self, account: str):
        """Generate signature using private key"""
        try:
            encoded_message = encode_defunct(text="pharos")
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)
            return signature
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Generate Signature Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None

    async def get_web3(self):
        return Web3(Web3.HTTPProvider(self.RPC_URL))

    async def get_token_balance(self, address, token_address):
        """Get token balance for display"""
        try:
            web3 = await self.get_web3()
            if token_address == "PHRS":
                balance_wei = web3.eth.get_balance(address)
                return web3.from_wei(balance_wei, 'ether')
            else:
                contract = web3.eth.contract(address=web3.to_checksum_address(token_address), abi=self.ERC20_CONTRACT_ABI)
                balance = contract.functions.balanceOf(address).call()
                decimals = contract.functions.decimals().call()
                return balance / (10 ** decimals)
        except Exception as e:
            self.log(f"Error getting balance for {token_address}: {e}")
            return 0

    async def display_balances(self, address):
        """Display all token balances"""
        self.log(f"🔍 Checking balances for {self.mask_account(address)}...")
        
        phrs_balance = await self.get_token_balance(address, "PHRS")
        wphrs_balance = await self.get_token_balance(address, self.WPHRS_CONTRACT_ADDRESS)
        usdc_balance = await self.get_token_balance(address, self.USDC_CONTRACT_ADDRESS)
        usdt_balance = await self.get_token_balance(address, self.USDT_CONTRACT_ADDRESS)
        
        print(f"{Fore.GREEN}💰 Token Balances:")
        print(f"{Fore.YELLOW}   PHRS: {phrs_balance:.6f}")
        print(f"{Fore.YELLOW}   WPHRS: {wphrs_balance:.6f}")
        print(f"{Fore.YELLOW}   USDC: {usdc_balance:.6f}")
        print(f"{Fore.YELLOW}   USDT: {usdt_balance:.6f}")
        print()

    def configure_delays(self):
        """Configure min and max delays with validation"""
        try:
            print(f"{Fore.CYAN}⏰ Configure Transaction Delays")
            min_delay = input(f"{Fore.YELLOW}Enter minimum delay (seconds) [default: 5]: ").strip()
            if min_delay:
                self.min_delay = int(min_delay)
            
            max_delay = input(f"{Fore.YELLOW}Enter maximum delay (seconds) [default: 10]: ").strip()
            if max_delay:
                self.max_delay = int(max_delay)
            
            # Validate delays
            if self.min_delay > self.max_delay:
                self.log(f"❌ {Fore.RED}PERINGATAN: Max delay ({self.max_delay}s) harus lebih tinggi dari min delay ({self.min_delay}s)!")
                self.log(f"🔧 Setting max delay to {self.min_delay + 5}s")
                self.max_delay = self.min_delay + 5
            
            self.log(f"✅ Delays configured: {self.min_delay}s - {self.max_delay}s")
        except ValueError:
            self.log("❌ Invalid input, using default delays: 5s - 10s")
            self.min_delay = 5
            self.max_delay = 10

    def configure_operation_counts(self):
        """Configure random operation counts"""
        try:
            print(f"{Fore.CYAN}🎲 Configure Random Operation Counts")
            
            # Swap configuration
            swap_count = input(f"{Fore.YELLOW}How many times to swap (random)? [default: 5]: ").strip()
            if swap_count:
                self.total_swaps = int(swap_count)
            else:
                self.total_swaps = 5
            
            # Unwrap configuration
            unwrap_count = input(f"{Fore.YELLOW}How many times to unwrap (random)? [default: 3]: ").strip()
            if unwrap_count:
                self.total_unwraps = int(unwrap_count)
            else:
                self.total_unwraps = 3
            
            # Add liquidity configuration
            lp_count = input(f"{Fore.YELLOW}How many times to add liquidity (random)? [default: 2]: ").strip()
            if lp_count:
                self.total_add_lps = int(lp_count)
            else:
                self.total_add_lps = 2
            
            self.log(f"✅ Operation counts configured:")
            self.log(f"   📊 Swaps: {self.total_swaps}")
            self.log(f"   🔄 Unwraps: {self.total_unwraps}")
            self.log(f"   💧 Add LP: {self.total_add_lps}")
            
        except ValueError:
            self.log("❌ Invalid input, using default counts: Swaps=5, Unwraps=3, LP=2")
            self.total_swaps = 5
            self.total_unwraps = 3
            self.total_add_lps = 2

    async def wait_random_delay(self):
        """Wait for random delay between operations"""
        global shutdown_requested
        delay = random.randint(self.min_delay, self.max_delay)
        self.log(f"⏳ Waiting {delay} seconds...")
        
        for _ in range(delay):
            if shutdown_requested:
                break
            await asyncio.sleep(1)

    async def approving_token(self, privkey, address, spender, contract_addr, amount):
        """Approve token spending with verification"""
        try:
            web3 = await self.get_web3()
            spender = web3.to_checksum_address(spender)
            contract = web3.eth.contract(address=web3.to_checksum_address(contract_addr), abi=self.ERC20_CONTRACT_ABI)
            decimals = contract.functions.decimals().call()
            amount_wei = int(amount * (10 ** decimals))
            allowance = contract.functions.allowance(address, spender).call()
            
            if allowance < amount_wei:
                self.log(f"🔓 Approving token spending...")
                
                tx = contract.functions.approve(spender, 2**256-1).build_transaction({
                    'from': address,
                    'gas': 100000,
                    'gasPrice': web3.to_wei('20', 'gwei'),
                    'nonce': web3.eth.get_transaction_count(address)
                })
                
                signed_tx = web3.eth.account.sign_transaction(tx, private_key=privkey)
                tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_hash_hex = to_hex(tx_hash)
                
                self.log(f"📤 Approval sent: {tx_hash_hex}")
                
                # Verify transaction
                verified = await self.tx_verifier.verify_transaction(tx_hash_hex)
                if verified:
                    self.log(f"✅ Token approval successful")
                    return True
                else:
                    self.log(f"❌ Token approval failed")
                    return False
            else:
                self.log(f"✅ Token already approved")
                return True
                
        except Exception as e:
            self.log(f"❌ Approval error: {str(e)}")
            return False

    async def perform_swap(self, privkey, address, pair_key, amount):
        """Perform token swap with enhanced pair support"""
        try:
            if pair_key not in self.SWAP_PAIRS:
                self.log(f"❌ Invalid swap pair: {pair_key}")
                return False
                
            pair_config = self.SWAP_PAIRS[pair_key]
            token_in = pair_config["token_in"]
            token_out = pair_config["token_out"]
            pair_name = pair_config["name"]
            
            self.log(f"🔄 Performing swap: {pair_name}")
            
            # Check if approval is needed
            if token_in != "PHRS":  # If not native token
                approved = await self.approving_token(privkey, address, self.SWAP_ROUTER_ADDRESS, token_in, amount)
                if not approved:
                    return False
            
            web3 = await self.get_web3()
            
            # Get token decimals
            if token_in == "PHRS":
                decimals_in = 18
            else:
                contract_in = web3.eth.contract(address=web3.to_checksum_address(token_in), abi=self.ERC20_CONTRACT_ABI)
                decimals_in = contract_in.functions.decimals().call()
            
            amount_in = int(amount * (10 ** decimals_in))
            
            # Build swap transaction
            deadline = int(time.time()) + 300  # 5 minutes from now
            
            # Command for exact input swap
            commands = "0x08"  # SWAP_EXACT_IN command
            
            # Encode swap parameters
            swap_params = encode([
                'address',  # recipient
                'uint256',  # amountIn
                'uint256',  # amountOutMinimum
                'bytes',    # path
                'bool'      # payerIsUser
            ], [
                address,
                amount_in,
                0,  # Accept any amount of tokens out
                encode(['address', 'uint24', 'address'], [token_in, 3000, token_out]),  # Path with 0.3% fee
                True
            ])
            
            # Build transaction
            swap_contract = web3.eth.contract(address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), abi=self.SWAP_CONTRACT_ABI)
            
            tx = swap_contract.functions.execute(
                commands,
                [swap_params],
                deadline
            ).build_transaction({
                'from': address,
                'gas': 300000,
                'gasPrice': web3.to_wei('20', 'gwei'),
                'nonce': web3.eth.get_transaction_count(address),
                'value': amount_in if token_in == "PHRS" else 0
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key=privkey)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = to_hex(tx_hash)
            
            self.log(f"📤 Swap transaction sent: {tx_hash_hex}")
            
            # Verify transaction
            verified = await self.tx_verifier.verify_transaction(tx_hash_hex)
            if verified:
                self.log(f"✅ Swap successful: {pair_name}")
                self.swap_count += 1
                return True
            else:
                self.log(f"❌ Swap failed: {pair_name}")
                return False
                
        except Exception as e:
            self.log(f"❌ Swap error: {str(e)}")
            return False

    async def add_liquidity(self, privkey, address, pair_key, amount0, amount1):
        """Add liquidity to specified pairs"""
        try:
            if pair_key not in self.LP_PAIRS:
                self.log(f"❌ Invalid LP pair: {pair_key}")
                return False
                
            pair_config = self.LP_PAIRS[pair_key]
            token0 = pair_config["token0"]
            token1 = pair_config["token1"]
            pair_name = pair_config["name"]
            
            self.log(f"💧 Adding liquidity to: {pair_name}")
            
            # Approve both tokens
            approved0 = await self.approving_token(privkey, address, self.POSITION_MANAGER_ADDRESS, token0, amount0)
            approved1 = await self.approving_token(privkey, address, self.POSITION_MANAGER_ADDRESS, token1, amount1)
            
            if not (approved0 and approved1):
                return False
            
            web3 = await self.get_web3()
            
            # Get token decimals
            contract0 = web3.eth.contract(address=web3.to_checksum_address(token0), abi=self.ERC20_CONTRACT_ABI)
            contract1 = web3.eth.contract(address=web3.to_checksum_address(token1), abi=self.ERC20_CONTRACT_ABI)
            
            decimals0 = contract0.functions.decimals().call()
            decimals1 = contract1.functions.decimals().call()
            
            amount0_wei = int(amount0 * (10 ** decimals0))
            amount1_wei = int(amount1 * (10 ** decimals1))
            
            # Build mint parameters
            mint_params = encode([
                'address',  # token0
                'address',  # token1
                'uint24',   # fee
                'int24',    # tickLower
                'int24',    # tickUpper
                'uint256',  # amount0Desired
                'uint256',  # amount1Desired
                'uint256',  # amount0Min
                'uint256',  # amount1Min
                'address',  # recipient
                'uint256'   # deadline
            ], [
                token0,
                token1,
                3000,  # 0.3% fee
                -887220,  # tickLower
                887220,   # tickUpper
                amount0_wei,
                amount1_wei,
                0,  # amount0Min
                0,  # amount1Min
                address,
                int(time.time()) + 300  # deadline
            ])
            
            # Build multicall transaction
            position_manager = web3.eth.contract(address=web3.to_checksum_address(self.POSITION_MANAGER_ADDRESS), abi=self.ADD_LP_CONTRACT_ABI)
            
            tx = position_manager.functions.multicall([mint_params]).build_transaction({
                'from': address,
                'gas': 500000,
                'gasPrice': web3.to_wei('20', 'gwei'),
                'nonce': web3.eth.get_transaction_count(address)
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key=privkey)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = to_hex(tx_hash)
            
            self.log(f"📤 Add liquidity transaction sent: {tx_hash_hex}")
            
            # Verify transaction
            verified = await self.tx_verifier.verify_transaction(tx_hash_hex)
            if verified:
                self.log(f"✅ Liquidity added successfully: {pair_name}")
                self.add_lp_count += 1
                return True
            else:
                self.log(f"❌ Add liquidity failed: {pair_name}")
                return False
                
        except Exception as e:
            self.log(f"❌ Add liquidity error: {str(e)}")
            return False

    async def unwrap_wphrs(self, privkey, address, amount):
        """Unwrap WPHRS to PHRS"""
        try:
            self.log(f"🔄 Unwrapping WPHRS to PHRS...")
            
            web3 = await self.get_web3()
            wphrs_contract = web3.eth.contract(address=web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS), abi=self.ERC20_CONTRACT_ABI)
            
            decimals = wphrs_contract.functions.decimals().call()
            amount_wei = int(amount * (10 ** decimals))
            
            tx = wphrs_contract.functions.withdraw(amount_wei).build_transaction({
                'from': address,
                'gas': 100000,
                'gasPrice': web3.to_wei('20', 'gwei'),
                'nonce': web3.eth.get_transaction_count(address)
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key=privkey)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = to_hex(tx_hash)
            
            self.log(f"📤 Unwrap transaction sent: {tx_hash_hex}")
            
            # Verify transaction
            verified = await self.tx_verifier.verify_transaction(tx_hash_hex)
            if verified:
                self.log(f"✅ Unwrap successful")
                self.unwrap_count += 1
                return True
            else:
                self.log(f"❌ Unwrap failed")
                return False
                
        except Exception as e:
            self.log(f"❌ Unwrap error: {str(e)}")
            return False

    def show_menu(self):
        """Display main menu"""
        print(f"\n{Fore.CYAN}🎯 Pharos Testnet Bot Menu")
        print(f"{Fore.YELLOW}1. Configure Settings")
        print(f"{Fore.YELLOW}2. Manual Operations")
        print(f"{Fore.YELLOW}3. Start 24H Automation")
        print(f"{Fore.YELLOW}4. Check Balances")
        print(f"{Fore.YELLOW}5. Exit")
        
        if self.start_time:
            countdown = self.display_countdown()
            print(f"\n{Fore.GREEN}⏰ Remaining Time: {countdown}")
        
        print(f"\n{Fore.MAGENTA}📊 Statistics:")
        print(f"{Fore.CYAN}   Swaps: {self.swap_count}")
        print(f"{Fore.CYAN}   Unwraps: {self.unwrap_count}")
        print(f"{Fore.CYAN}   Add LP: {self.add_lp_count}")

    def configure_automation(self):
        """Configure automation parameters"""
        try:
            print(f"\n{Fore.CYAN}⚙️ Configure Automation Settings")
            
            # Configure operation counts
            self.configure_operation_counts()
            
            # Configure delays
            self.configure_delays()
            
            self.log(f"✅ Automation configured:")
            self.log(f"   - Swaps per cycle: {self.total_swaps}")
            self.log(f"   - Unwraps per cycle: {self.total_unwraps}")
            self.log(f"   - Add LP per cycle: {self.total_add_lps}")
            
        except ValueError:
            self.log("❌ Invalid input, using defaults")
            self.total_swaps = 5
            self.total_unwraps = 2
            self.total_add_lps = 1

    async def run_automation_cycle(self, privkey, address):
        """Run one automation cycle"""
        global shutdown_requested
        
        self.log(f"🚀 Starting automation cycle...")
        
        # Available swap pairs
        swap_pairs = list(self.SWAP_PAIRS.keys())
        lp_pairs = list(self.LP_PAIRS.keys())
        
        # Perform swaps
        for i in range(self.total_swaps):
            if shutdown_requested:
                break
                
            pair = random.choice(swap_pairs)
            amount = random.uniform(0.001, 0.005)  # Random amount between 0.001 and 0.005
            
            await self.perform_swap(privkey, address, pair, amount)
            
            if i < self.total_swaps - 1:  # Don't delay after last swap
                await self.wait_random_delay()
        
        # Perform unwraps
        for i in range(self.total_unwraps):
            if shutdown_requested:
                break
                
            amount = random.uniform(0.001, 0.003)
            await self.unwrap_wphrs(privkey, address, amount)
            
            if i < self.total_unwraps - 1:
                await self.wait_random_delay()
        
        # Add liquidity
        for i in range(self.total_add_lps):
            if shutdown_requested:
                break
                
            pair = random.choice(lp_pairs)
            amount0 = random.uniform(0.001, 0.002)
            amount1 = random.uniform(0.001, 0.002)
            
            await self.add_liquidity(privkey, address, pair, amount0, amount1)
            
            if i < self.total_add_lps - 1:
                await self.wait_random_delay()
        
        self.log(f"✅ Automation cycle completed")

    async def run_24h_automation(self, config):
        """Run 24-hour automation with countdown timer"""
        global shutdown_requested
        
        privkey = config.get("privkey")
        address = config.get("address")
        
        if not privkey or not address:
            self.log("❌ Private key or address not configured")
            return
        
        self.start_time = time.time()
        self.log(f"🕐 Starting 24-hour automation...")
        
        cycle_count = 0
        
        while not shutdown_requested:
            # Check if 24 hours have passed
            elapsed = time.time() - self.start_time
            if elapsed >= self.total_runtime:
                self.log(f"⏰ 24-hour automation completed!")
                break
            
            cycle_count += 1
            self.log(f"🔄 Starting cycle {cycle_count}")
            
            # Display current countdown
            countdown = self.display_countdown()
            self.log(f"⏰ Time remaining: {countdown}")
            
            # Run automation cycle
            await self.run_automation_cycle(privkey, address)
            
            if shutdown_requested:
                break
            
            # Wait 1 hour between cycles (3600 seconds)
            self.log(f"✅ Cycle {cycle_count} completed. Waiting 1 hour before next cycle...")
            
            # Wait in smaller increments to check for shutdown
            for _ in range(3600):  # 1 hour = 3600 seconds
                if shutdown_requested:
                    break
                await asyncio.sleep(1)
                
                # Update countdown every 60 seconds
                if _ % 60 == 0:
                    countdown = self.display_countdown()
                    print(f"\r{Fore.GREEN}⏰ Time remaining: {countdown} | Next cycle in: {3600-_}s", end="", flush=True)
            
            print()  # New line after countdown
        
        if shutdown_requested:
            self.log(f"🛑 Automation stopped by user request")
        
        self.log(f"📊 Final Statistics:")
        self.log(f"   - Total cycles: {cycle_count}")
        self.log(f"   - Total swaps: {self.swap_count}")
        self.log(f"   - Total unwraps: {self.unwrap_count}")
        self.log(f"   - Total add LP: {self.add_lp_count}")

    async def manual_operations(self, config):
        """Manual operations menu"""
        privkey = config.get("privkey")
        address = config.get("address")
        
        if not privkey or not address:
            self.log("❌ Private key or address not configured")
            return
        
        while True:
            print(f"\n{Fore.CYAN}🎯 Manual Operations")
            print(f"{Fore.YELLOW}1. Perform Swap")
            print(f"{Fore.YELLOW}2. Add Liquidity")
            print(f"{Fore.YELLOW}3. Unwrap WPHRS")
            print(f"{Fore.YELLOW}4. Back to Main Menu")
            
            choice = input(f"\n{Fore.WHITE}Select option (1-4): ").strip()
            
            if choice == "1":
                await self.manual_swap(privkey, address)
            elif choice == "2":
                await self.manual_add_liquidity(privkey, address)
            elif choice == "3":
                await self.manual_unwrap(privkey, address)
            elif choice == "4":
                break
            else:
                print(f"{Fore.RED}❌ Invalid choice")

    async def manual_swap(self, privkey, address):
        """Manual swap operation"""
        print(f"\n{Fore.CYAN}Available Swap Pairs:")
        for i, (key, config) in enumerate(self.SWAP_PAIRS.items(), 1):
            print(f"{Fore.YELLOW}{i}. {config['name']}")
        
        try:
            choice = int(input(f"\n{Fore.WHITE}Select pair (1-{len(self.SWAP_PAIRS)}): ").strip())
            if 1 <= choice <= len(self.SWAP_PAIRS):
                pair_key = list(self.SWAP_PAIRS.keys())[choice - 1]
                amount = float(input(f"{Fore.WHITE}Enter amount: ").strip())
                
                await self.perform_swap(privkey, address, pair_key, amount)
            else:
                print(f"{Fore.RED}❌ Invalid choice")
        except ValueError:
            print(f"{Fore.RED}❌ Invalid input")

    async def manual_add_liquidity(self, privkey, address):
        """Manual add liquidity operation"""
        print(f"\n{Fore.CYAN}Available LP Pairs:")
        for i, (key, config) in enumerate(self.LP_PAIRS.items(), 1):
            print(f"{Fore.YELLOW}{i}. {config['name']}")
        
        try:
            choice = int(input(f"\n{Fore.WHITE}Select pair (1-{len(self.LP_PAIRS)}): ").strip())
            if 1 <= choice <= len(self.LP_PAIRS):
                pair_key = list(self.LP_PAIRS.keys())[choice - 1]
                amount0 = float(input(f"{Fore.WHITE}Enter amount for token 0: ").strip())
                amount1 = float(input(f"{Fore.WHITE}Enter amount for token 1: ").strip())
                
                await self.add_liquidity(privkey, address, pair_key, amount0, amount1)
            else:
                print(f"{Fore.RED}❌ Invalid choice")
        except ValueError:
            print(f"{Fore.RED}❌ Invalid input")

    async def manual_unwrap(self, privkey, address):
        """Manual unwrap operation"""
        try:
            amount = float(input(f"{Fore.WHITE}Enter WPHRS amount to unwrap: ").strip())
            await self.unwrap_wphrs(privkey, address, amount)
        except ValueError:
            print(f"{Fore.RED}❌ Invalid amount")

    async def main(self):
        """Main application loop"""
        global shutdown_requested
        
        self.setup_signal_handlers()
        self.welcome()
        
        # Configuration storage
        config = {}
        
        while not shutdown_requested:
            self.show_menu()
            
            try:
                choice = input(f"\n{Fore.WHITE}Select option (1-5): ").strip()
                
                if choice == "1":
                    # Configure Settings
                    print(f"\n{Fore.CYAN}⚙️ Configuration")
                    
                    # Get private key
                    privkey = input(f"{Fore.YELLOW}Enter private key: ").strip()
                    if privkey:
                        address = self.generate_address(privkey)
                        if address:
                            config["privkey"] = privkey
                            config["address"] = address
                            self.log(f"✅ Address configured: {self.mask_account(address)}")
                        else:
                            self.log(f"❌ Invalid private key")
                            continue
                    
                    # Configure automation
                    self.configure_automation()
                    
                elif choice == "2":
                    # Manual Operations
                    await self.manual_operations(config)
                    
                elif choice == "3":
                    # Start 24H Automation
                    if not config.get("privkey"):
                        self.log("❌ Please configure settings first")
                        continue
                    
                    await self.run_24h_automation(config)
                    
                elif choice == "4":
                    # Check Balances
                    if not config.get("address"):
                        self.log("❌ Please configure settings first")
                        continue
                    
                    await self.display_balances(config["address"])
                    
                elif choice == "5":
                    # Exit
                    self.log("👋 Goodbye!")
                    break
                    
                else:
                    print(f"{Fore.RED}❌ Invalid choice")
                    
            except KeyboardInterrupt:
                shutdown_requested = True
                break
            except Exception as e:
                self.log(f"❌ Error: {str(e)}")
        
        if shutdown_requested:
            self.log("🛑 Application stopped gracefully")

if __name__ == "__main__":
    bot = PharosTestnet()
    try:
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Application terminated gracefully")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Unexpected error: {str(e)}")
