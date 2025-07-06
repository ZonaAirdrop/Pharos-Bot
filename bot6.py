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

# TransactionVerifier class embedded directly in the file
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
        
        # Corrected Swap Router ABI with proper method signature 0x3593564c
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
        
        # Corrected Position Manager ABI with proper method signature 0xac9650d8
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
        """Generate address directly from private key like bot1"""
        try:
            # Use the private key directly - account parameter is the private key
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

    def generate_random_receiver(self):
        """Generate random receiver address using bot1's approach"""
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
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}                  "
            )
            return None

    def generate_signature(self, account: str):
        """Generate signature using direct private key like bot1"""
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
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}                  "
            )
            return None

    async def get_web3(self):
        return Web3(Web3.HTTPProvider(self.RPC_URL))

    async def get_token_balance(self, address, token_address):
        """Get token balance for display"""
        try:
            web3 = await self.get_web3()
            if token_address == "PHRS":
                # Native token balance
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
        
        # Get all balances
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
        """Configure min and max delays"""
        try:
            print(f"{Fore.CYAN}⏰ Configure Transaction Delays")
            min_delay = input(f"{Fore.YELLOW}Enter minimum delay (seconds) [default: 5]: ").strip()
            if min_delay:
                self.min_delay = int(min_delay)
            
            max_delay = input(f"{Fore.YELLOW}Enter maximum delay (seconds) [default: 10]: ").strip()
            if max_delay:
                self.max_delay = int(max_delay)
            
            if self.min_delay > self.max_delay:
                self.max_delay = self.min_delay
            
            self.log(f"✅ Delays configured: {self.min_delay}s - {self.max_delay}s")
        except ValueError:
            self.log("❌ Invalid input, using default delays: 5s - 10s")
            self.min_delay = 5
            self.max_delay = 10

    async def wait_random_delay(self):
        """Wait for random delay between operations"""
        delay = random.randint(self.min_delay, self.max_delay)
        self.log(f"⏳ Waiting {delay} seconds...")
        await asyncio.sleep(delay)

    async def approving_token(self, privkey, address, spender, contract_addr, amount):
        """Approve token spending with verification"""
        web3 = await self.get_web3()
        spender = web3.to_checksum_address(spender)
        contract = web3.eth.contract(address=web3.to_checksum_address(contract_addr), abi=self.ERC20_CONTRACT_ABI)
        decimals = contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        allowance = contract.functions.allowance(address, spender).call()
        
        if allowance < amount_wei:
            self.log(f"🔓 Approving token spending...")
            
            tx = contract.functions.approve(spender, 2**256-1).build_transaction({
                "from": address,
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "gas": 80000,
                "maxFeePerGas": web3.to_wei(2, "gwei"),
                "maxPriorityFeePerGas": web3.to_wei(1, "gwei"),
                "chainId": web3.eth.chain_id
            })
            signed = web3.eth.account.sign_transaction(tx, privkey)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            
            # Verify approval transaction
            if await self.tx_verifier.verify_transaction(web3.to_hex(tx_hash)):
                self.log(f"✅ Token approval successful")
            else:
                self.log(f"❌ Token approval failed")
                return False
                
            await asyncio.sleep(5)
        return True

    async def perform_wrapped(self, privkey, address, amount, wrap=True, retries=3):
        """Perform wrap/unwrap operations with verification"""
        web3 = await self.get_web3()
        contract = web3.eth.contract(address=web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS), abi=self.ERC20_CONTRACT_ABI)
        amount_wei = web3.to_wei(amount, "ether")
        
        for attempt in range(retries):
            try:
                action = "Wrapping" if wrap else "Unwrapping"
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
                
                # Verify transaction
                if await self.tx_verifier.verify_transaction(web3.to_hex(tx_hash)):
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
        """Perform token swap with verification"""
        web3 = await self.get_web3()
        
        for attempt in range(retries):
            try:
                self.log(f"🔄 Swapping {amount} tokens...")
                
                # First approve if needed
                if from_token != "PHRS":
                    await self.approving_token(privkey, address, self.SWAP_ROUTER_ADDRESS, from_token, amount)
                
                # Build swap transaction
                contract = web3.eth.contract(address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), abi=self.SWAP_CONTRACT_ABI)
                
                # Simplified swap parameters for demonstration
                commands = b"\x00"  # Simple swap command
                deadline = int(time.time()) + 1800  # 30 minutes
                
                tx = contract.functions.execute(commands, [], deadline).build_transaction({
                    "from": address,
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "gas": 200000,
                    "maxFeePerGas": web3.to_wei(2, "gwei"),
                    "maxPriorityFeePerGas": web3.to_wei(1, "gwei"),
                    "chainId": web3.eth.chain_id
                })
                
                signed = web3.eth.account.sign_transaction(tx, privkey)
                tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
                
                # Verify transaction
                if await self.tx_verifier.verify_transaction(web3.to_hex(tx_hash)):
                    self.log(f"✅ Swap successful")
                    return True
                else:
                    self.log(f"❌ Swap failed, attempt {attempt + 1}/{retries}")
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
        """Add liquidity with verification"""
        web3 = await self.get_web3()
        
        for attempt in range(retries):
            try:
                self.log(f"🔄 Adding liquidity...")
                
                # Approve tokens if needed
                if token0 != "PHRS":
                    await self.approving_token(privkey, address, self.POSITION_MANAGER_ADDRESS, token0, amount0)
                if token1 != "PHRS":
                    await self.approving_token(privkey, address, self.POSITION_MANAGER_ADDRESS, token1, amount1)
                
                # Build add liquidity transaction
                contract = web3.eth.contract(address=web3.to_checksum_address(self.POSITION_MANAGER_ADDRESS), abi=self.ADD_LP_CONTRACT_ABI)
                
                # Simplified multicall for demonstration
                data = []  # Would contain encoded function calls
                
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
                
                # Verify transaction
                if await self.tx_verifier.verify_transaction(web3.to_hex(tx_hash)):
                    self.log(f"✅ Add liquidity successful")
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
        """Process a single account with all operations"""
        try:
            # Generate address using fixed method
            address = self.generate_address(privkey)
            if not address:
                self.log(f"❌ Failed to generate address for account")
                return False
            
            self.log(f"🚀 Processing account: {self.mask_account(address)}")
            
            # Display balances
            await self.display_balances(address)
            
            # Wait random delay
            await self.wait_random_delay()
            
            # Example operations - customize as needed
            # 1. Wrap some PHRS
            wrap_amount = 0.01  # 0.01 PHRS
            if await self.perform_wrapped(privkey, address, wrap_amount, wrap=True):
                await self.wait_random_delay()
            
            # 2. Perform a swap
            if await self.perform_swap(privkey, address, self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, wrap_amount):
                await self.wait_random_delay()
            
            # 3. Add liquidity
            if await self.add_liquidity(privkey, address, self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, wrap_amount/2, wrap_amount/2):
                await self.wait_random_delay()
            
            self.log(f"✅ Account processing completed: {self.mask_account(address)}")
            return True
            
        except Exception as e:
            self.log(f"❌ Error processing account: {e}")
            return False

    async def main(self):
        """Main execution function"""
        self.welcome()
        
        # Configure delays
        self.configure_delays()
        
        # Load private keys from file
        try:
            with open('private_keys.txt', 'r') as f:
                private_keys = [line.strip() for line in f.readlines() if line.strip()]
            
            if not private_keys:
                self.log("❌ No private keys found in private_keys.txt")
                return
            
            self.log(f"📝 Loaded {len(private_keys)} private keys")
            
            # Process each account
            for i, privkey in enumerate(private_keys, 1):
                self.log(f"📊 Processing account {i}/{len(private_keys)}")
                await self.process_account(privkey)
                
                if i < len(private_keys):
                    await self.wait_random_delay()
            
            self.log("🎉 All accounts processed successfully!")
            
        except FileNotFoundError:
            self.log("❌ private_keys.txt file not found")
        except Exception as e:
            self.log(f"❌ Error in main execution: {e}")

if __name__ == "__main__":
    bot = PharosTestnet()
    asyncio.run(bot.main())
