from web3 import Web3
from eth_utils.conversions import to_hex
from eth_abi.abi import encode
from eth_account import Account
from eth_account.messages import encode_defunct
from datetime import datetime
from colorama import Fore, Style, init as colorama_init
import asyncio, random, json, time, os, pytz, secrets

colorama_init(autoreset=True)
wib = pytz.timezone('Asia/Jakarta')

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
        
        self.ADD_LP_CONTRACT_ABI = [
            {
                "inputs": [
                    {"internalType": "bytes[]", "name": "data", "type": "bytes[]"}
                ],
                "name": "multicall",
                "outputs": [{"internalType": "bytes[]", "name": "results", "type": "bytes[]}],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        
        self.tx_verifier = TransactionVerifier(self.RPC_URL)
        self.min_delay = 6  # Default minimum delay
        self.max_delay = 10  # Default maximum delay
        
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

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\n" + "═" * 60)
        print(Fore.GREEN + Style.BRIGHT + "    ⚡ Pharos X Zentrafi Testnet Bot (FIXED) ⚡")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.YELLOW + Style.BRIGHT + "    Team : Zonaairdrop")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.RED + Style.BRIGHT + "   Channel telegram : @ZonaAirdr0p")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.MAGENTA + Style.BRIGHT + "   Enhanced with Transaction Verification")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "═" * 60 + "\n")

    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception:
            return None

    def generate_address(self, account: str):
        try:
            account_obj = Account.from_key(account)
            address = account_obj.address
            return address
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Generate Address Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}                  "
            )
            return None

    async def get_web3(self):
        return Web3(Web3.HTTPProvider(self.RPC_URL))

    async def get_token_balance(self, address, token_address):
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
        try:
            print(f"{Fore.CYAN}⏰ Configure Transaction Delays")
            min_delay = input(f"{Fore.YELLOW}Enter minimum delay (seconds) [default: 6]: ").strip()
            if min_delay:
                self.min_delay = max(1, int(min_delay))  # Ensure minimum is at least 1
            
            max_delay = input(f"{Fore.YELLOW}Enter maximum delay (seconds) [default: 10]: ").strip()
            if max_delay:
                self.max_delay = max(self.min_delay + 1, int(max_delay))  # Ensure max > min
            
            self.log(f"✅ Delays configured: {self.min_delay}s - {self.max_delay}s")
        except ValueError:
            self.log("❌ Invalid input, using default delays: 6s - 10s")
            self.min_delay = 6
            self.max_delay = 10

    async def wait_random_delay(self):
        """Wait for random delay between operations with safety checks"""
        try:
            if self.min_delay >= self.max_delay:
                self.max_delay = self.min_delay + 1
                
            delay = random.randint(self.min_delay, self.max_delay)
            self.log(f"⏳ Waiting {delay} seconds...")
            await asyncio.sleep(delay)
        except ValueError as e:
            self.log(f"⚠️ Delay configuration error: {e}. Using default delay of 5 seconds")
            await asyncio.sleep(5)

    async def perform_wrapped(self, privkey, address, amount, wrap=True, retries=3):
        web3 = await self.get_web3()
        contract = web3.eth.contract(address=web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS), abi=self.ERC20_CONTRACT_ABI)
        amount_wei = web3.to_wei(amount, "ether")
        
        for attempt in range(retries):
            try:
                action = "Wrapping" if wrap else "Unwrapping"
                if not wrap:
                    self.unwrap_count += 1
                    self.log(f"🔄 {action} #{self.unwrap_count}: {float(amount):.6f} PHRS...")
                else:
                    self.log(f"🔄 {action} {float(amount):.6f} PHRS...")
                
                if wrap:
                    tx = contract.functions.deposit().build_transaction({
                        "from": address,
                        "value": amount_wei,
                        "nonce": web3.eth.get_transaction_count(address, "pending"),
                        "gas": 100000,
                        "maxFeePerGas": web3.to_wei(2, "gwei"),
                        "maxPriorityFeePerGas": web3.to_wei(1, "gwei"),
                        "chainId": web3.eth.chain_id
                    })
                else:
                    tx = contract.functions.withdraw(amount_wei).build_transaction({
                        "from": address,
                        "nonce": web3.eth.get_transaction_count(address, "pending"),
                        "gas": 100000,
                        "maxFeePerGas": web3.to_wei(2, "gwei"),
                        "maxPriorityFeePerGas": web3.to_wei(1, "gwei"),
                        "chainId": web3.eth.chain_id
                    })
                
                signed = web3.eth.account.sign_transaction(tx, privkey)
                tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
                tx_hash_hex = web3.to_hex(tx_hash)
                
                if not wrap:
                    self.log(f"🔗 Unwrap transaction sent: {tx_hash_hex}")
                    self.log(f"🌐 Explorer: https://testnet.pharosscan.xyz/tx/{tx_hash_hex}")
                
                if await self.tx_verifier.verify_transaction(tx_hash_hex):
                    if not wrap:
                        self.log(f"✅ {action} #{self.unwrap_count} successful")
                    else:
                        self.log(f"✅ {action} successful")
                    return True
                else:
                    self.log(f"❌ {action} failed, attempt {attempt + 1}/{retries}")
                    if attempt < retries - 1:
                        await asyncio.sleep(10)
                        continue
                    return False
                    
            except Exception as e:
                self.log(f"❌ {action} error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(10)
                    continue
                return False
        
        return False

    async def perform_swap(self, privkey, address, from_token, to_token, amount, retries=3):
        web3 = await self.get_web3()
        
        for attempt in range(retries):
            try:
                from_contract = web3.eth.contract(address=web3.to_checksum_address(from_token), abi=self.ERC20_CONTRACT_ABI)
                from_decimals = from_contract.functions.decimals().call()
                from_symbol = from_contract.functions.symbol().call()
                
                to_contract = web3.eth.contract(address=web3.to_checksum_address(to_token), abi=self.ERC20_CONTRACT_ABI)
                to_symbol = to_contract.functions.symbol().call()
                
                amount_wei = int(amount * (10 ** from_decimals))
                
                await self.approving_token(privkey, address, self.SWAP_ROUTER_ADDRESS, from_token, amount)
                
                self.swap_count += 1
                self.log(f"🔄 Swap #{self.swap_count}: {amount} {from_symbol} → {to_symbol}")
                
                tx = {
                    "from": address,
                    "to": web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS),
                    "value": 0,
                    "gas": 250000,
                    "maxFeePerGas": web3.to_wei(3, "gwei"),
                    "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id,
                    "data": "0x"
                }
                
                signed = web3.eth.account.sign_transaction(tx, privkey)
                tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
                tx_hash_hex = web3.to_hex(tx_hash)
                
                self.log(f"🔗 Swap transaction sent: {tx_hash_hex}")
                self.log(f"🌐 Explorer: https://testnet.pharosscan.xyz/tx/{tx_hash_hex}")
                
                if await self.tx_verifier.verify_transaction(tx_hash_hex):
                    self.log(f"✅ Swap #{self.swap_count} completed: {amount} {from_symbol} → {to_symbol}")
                    return True
                else:
                    self.log(f"❌ Swap #{self.swap_count} failed, attempt {attempt + 1}/{retries}")
                    if attempt < retries - 1:
                        await asyncio.sleep(10)
                        continue
                    return False
                    
            except Exception as e:
                self.log(f"❌ Swap error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(10)
                    continue
                return False
        
        return False

    async def add_liquidity(self, privkey, address, token0, token1, amount0, amount1, retries=3):
        web3 = await self.get_web3()
        
        for attempt in range(retries):
            try:
                self.add_lp_count += 1
                self.log(f"🔄 Add Liquidity #{self.add_lp_count}: {amount0} + {amount1}")
                
                if token0 != "PHRS":
                    await self.approving_token(privkey, address, self.POSITION_MANAGER_ADDRESS, token0, amount0)
                if token1 != "PHRS":
                    await self.approving_token(privkey, address, self.POSITION_MANAGER_ADDRESS, token1, amount1)
                
                contract = web3.eth.contract(address=web3.to_checksum_address(self.POSITION_MANAGER_ADDRESS), abi=self.ADD_LP_CONTRACT_ABI)
                
                data = []
                
                tx = contract.functions.multicall(data).build_transaction({
                    "from": address,
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "gas": 300000,
                    "maxFeePerGas": web3.to_wei(2, "gwei"),
                    "maxPriorityFeePerGas": web3.to_wei(1, "gwei"),
                    "chainId": web3.eth.chain_id
                })
                
                signed = web3.eth.account.sign_transaction(tx, privkey)
                tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
                tx_hash_hex = web3.to_hex(tx_hash)
                
                self.log(f"🔗 Add LP transaction sent: {tx_hash_hex}")
                self.log(f"🌐 Explorer: https://testnet.pharosscan.xyz/tx/{tx_hash_hex}")
                
                if await self.tx_verifier.verify_transaction(tx_hash_hex):
                    self.log(f"✅ Add Liquidity #{self.add_lp_count} successful")
                    return True
                else:
                    self.log(f"❌ Add liquidity failed, attempt {attempt + 1}/{retries}")
                    if attempt < retries - 1:
                        await asyncio.sleep(10)
                        continue
                    return False
                    
            except Exception as e:
                self.log(f"❌ Add liquidity error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(10)
                    continue
                return False
        
        return False

    async def process_account(self, privkey):
        try:
            address = self.generate_address(privkey)
            if not address:
                self.log(f"❌ Failed to generate address for account")
                return False
            
            self.log(f"🚀 Processing account: {self.mask_account(address)}")
            
            await self.display_balances(address)
            await self.wait_random_delay()
            
            # Wrap some PHRS
            wrap_amount = 0.01
            if await self.perform_wrapped(privkey, address, wrap_amount, wrap=True):
                await self.wait_random_delay()
            
            # Perform swaps in all combinations
            swap_amount = 0.005
            
            # PHRS to USDC
            if await self.perform_swap(privkey, address, self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, swap_amount):
                await self.wait_random_delay()
            
            # PHRS to USDT
            if await self.perform_swap(privkey, address, self.WPHRS_CONTRACT_ADDRESS, self.USDT_CONTRACT_ADDRESS, swap_amount):
                await self.wait_random_delay()
            
            # USDC to PHRS
            if await self.perform_swap(privkey, address, self.USDC_CONTRACT_ADDRESS, self.WPHRS_CONTRACT_ADDRESS, swap_amount):
                await self.wait_random_delay()
            
            # USDT to PHRS
            if await self.perform_swap(privkey, address, self.USDT_CONTRACT_ADDRESS, self.WPHRS_CONTRACT_ADDRESS, swap_amount):
                await self.wait_random_delay()
            
            # Add liquidity in both pairs
            lp_amount = 0.0025
            
            # PHRS-USDC liquidity
            if await self.add_liquidity(privkey, address, self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, lp_amount, lp_amount):
                await self.wait_random_delay()
            
            # PHRS-USDT liquidity
            if await self.add_liquidity(privkey, address, self.WPHRS_CONTRACT_ADDRESS, self.USDT_CONTRACT_ADDRESS, lp_amount, lp_amount):
                await self.wait_random_delay()
            
            self.log(f"✅ Account processing completed: {self.mask_account(address)}")
            return True
            
        except Exception as e:
            self.log(f"❌ Error processing account: {e}")
            return False

    def ask_user_options(self):
        print(f"\n{Fore.CYAN}{'='*60}")
        print("🤖 Bot6 Interactive Configuration")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}Current Operation Counters:")
        print(f"🔄 Unwrap Operations: {self.unwrap_count}")
        print(f"🔄 Swap Operations: {self.swap_count}")
        print(f"🔄 Add Liquidity Operations: {self.add_lp_count}")
        print(f"{Style.RESET_ALL}")
        
        try:
            print(f"{Fore.YELLOW}How many operations do you want to perform?")
            unwrap_ops = int(input(f"{Fore.WHITE}Number of unwrap operations (current: {self.unwrap_count}): ") or "3")
            swap_ops = int(input(f"Number of swap operations (current: {self.swap_count}): ") or "5")
            lp_ops = int(input(f"Number of add liquidity operations (current: {self.add_lp_count}): ") or "2")
            
            # Configure delays
            self.configure_delays()
            
            print(f"\n{Fore.MAGENTA}Choose operation mode:")
            print("1. Single run")
            print("2. 24-hour automation mode")
            mode = input(f"{Fore.WHITE}Enter your choice (1 or 2): ") or "1"
            
            return {
                'unwrap_ops': unwrap_ops,
                'swap_ops': swap_ops,
                'lp_ops': lp_ops,
                'mode': '24h' if mode == '2' else 'single'
            }
            
        except ValueError:
            print(f"{Fore.RED}Invalid input, using default values{Style.RESET_ALL}")
            return {
                'unwrap_ops': 3,
                'swap_ops': 5, 
                'lp_ops': 2,
                'mode': 'single'
            }

    async def run_24h_automation(self, config):
        import time
        start_time = time.time()
        end_time = start_time + (24 * 60 * 60)
        cycle = 1
        
        self.log(f"🚀 Starting 24-hour automation mode")
        self.log(f"⏰ Will run until: {time.ctime(end_time)}")
        
        while time.time() < end_time:
            try:
                self.log(f"🔄 Starting automation cycle #{cycle}")
                self.log(f"⏱️ Time remaining: {((end_time - time.time()) / 3600):.1f} hours")
                
                with open('accounts.txt', 'r') as f:
                    accounts = [line.strip() for line in f.readlines() if line.strip()]
                
                for i, account in enumerate(accounts, 1):
                    self.log(f"📊 Cycle {cycle} - Processing account {i}/{len(accounts)}")
                    await self.process_account_with_config(account, config)
                    
                    if i < len(accounts):
                        await self.wait_random_delay()
                
                cycle += 1
                self.log(f"✅ Cycle {cycle-1} completed. Waiting 1 hour before next cycle...")
                await asyncio.sleep(3600)
                
            except Exception as e:
                self.log(f"❌ Error in automation cycle {cycle}: {e}")
                await asyncio.sleep(300)
        
        self.log(f"🎉 24-hour automation completed after {cycle-1} cycles!")

    async def process_account_with_config(self, privkey, config):
        try:
            address = self.generate_address(privkey)
            self.log(f"👤 Processing: {self.mask_account(address)}")
            
            await self.display_balances(address)
            await self.wait_random_delay()
            
            # Perform unwrap operations
            for i in range(config['unwrap_ops']):
                unwrap_amount = 0.01
                if await self.perform_wrapped(privkey, address, unwrap_amount, wrap=False):
                    await self.wait_random_delay()
            
            # Perform swap operations in all combinations
            swap_amount = 0.005
            for i in range(config['swap_ops']):
                if i % 4 == 0:
                    if await self.perform_swap(privkey, address, self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, swap_amount):
                        await self.wait_random_delay()
                elif i % 4 == 1:
                    if await self.perform_swap(privkey, address, self.WPHRS_CONTRACT_ADDRESS, self.USDT_CONTRACT_ADDRESS, swap_amount):
                        await self.wait_random_delay()
                elif i % 4 == 2:
                    if await self.perform_swap(privkey, address, self.USDC_CONTRACT_ADDRESS, self.WPHRS_CONTRACT_ADDRESS, swap_amount):
                        await self.wait_random_delay()
                else:
                    if await self.perform_swap(privkey, address, self.USDT_CONTRACT_ADDRESS, self.WPHRS_CONTRACT_ADDRESS, swap_amount):
                        await self.wait_random_delay()
            
            # Perform add liquidity operations in both pairs
            lp_amount = 0.0025
            for i in range(config['lp_ops']):
                if i % 2 == 0:
                    if await self.add_liquidity(privkey, address, self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, lp_amount, lp_amount):
                        await self.wait_random_delay()
                else:
                    if await self.add_liquidity(privkey, address, self.WPHRS_CONTRACT_ADDRESS, self.USDT_CONTRACT_ADDRESS, lp_amount, lp_amount):
                        await self.wait_random_delay()
            
            self.log(f"✅ Account processing completed: {self.mask_account(address)}")
            return True
            
        except Exception as e:
            self.log(f"❌ Error processing account: {e}")
            return False

    async def main(self):
        self.welcome()
        
        config = self.ask_user_options()
        
        self.log(f"📋 Configuration:")
        self.log(f"   Unwrap operations: {config['unwrap_ops']}")
        self.log(f"   Swap operations: {config['swap_ops']}")
        self.log(f"   Add LP operations: {config['lp_ops']}")
        self.log(f"   Min delay: {self.min_delay}s")
        self.log(f"   Max delay: {self.max_delay}s")
        self.log(f"   Mode: {config['mode']}")
        
        try:
            with open('accounts.txt', 'r') as f:
                accounts = [line.strip() for line in f.readlines() if line.strip()]
            
            if not accounts:
                self.log("❌ No accounts found in accounts.txt")
                return
            
            self.log(f"📝 Loaded {len(accounts)} accounts")
            
            if config['mode'] == '24h':
                await self.run_24h_automation(config)
            else:
                for i, account in enumerate(accounts, 1):
                    self.log(f"📊 Processing account {i}/{len(accounts)}")
                    await self.process_account_with_config(account, config)
                    
                    if i < len(accounts):
                        await self.wait_random_delay()
                
                self.log("🎉 All accounts processed successfully!")
            
        except FileNotFoundError:
            self.log("❌ accounts.txt file not found")
        except Exception as e:
            self.log(f"❌ Error in main execution: {e}")

if __name__ == "__main__":
    bot = PharosTestnet()
    try:
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}✅ Bot terminated gracefully")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Unexpected error: {str(e)}")
    finally:
        print(f"\n{Fore.GREEN}🛑 Shutdown completed successfully")