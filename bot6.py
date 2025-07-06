from web3 import Web3
from eth_utils.conversions import to_hex
from eth_abi.abi import encode
from eth_account import Account
from eth_account.messages import encode_defunct
from datetime import datetime
from colorama import Fore, Style, init as colorama_init
import asyncio, random, json, time, os, pytz
from utils import TransactionVerifier

colorama_init(autoreset=True)
wib = pytz.timezone('Asia/Jakarta')

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

    def generate_address(self, privkey: str):
        try:
            return Account.from_key(privkey).address
        except Exception:
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
                tx_hash_hex = web3.to_hex(tx_hash)
                
                # Verify transaction
                if await self.tx_verifier.verify_transaction(tx_hash_hex):
                    self.log(f"✅ {action} successful! TxHash: {tx_hash_hex}")
                    return tx_hash_hex
                else:
                    self.log(f"❌ {action} failed in explorer verification")
                    
            except Exception as e:
                if attempt < retries - 1:
                    self.log(f"❌ {action} failed: {e} | Retrying in 15s...")
                    await asyncio.sleep(15)
                else:
                    self.log(f"❌ {action} failed permanently: {e}")
                    return "FAILED"
        
        return "FAILED"

    async def perform_swap(self, privkey, address, from_token, to_token, amount, retries=3):
        """Perform swap with correct method signature 0x3593564c"""
        web3 = await self.get_web3()
        
        for attempt in range(retries):
            try:
                self.log(f"🔄 Swapping {float(amount):.6f} tokens...")
                
                # Approve token spending
                if not await self.approving_token(privkey, address, self.SWAP_ROUTER_ADDRESS, from_token, amount):
                    continue
                
                token_contract = web3.eth.contract(address=web3.to_checksum_address(from_token), abi=self.ERC20_CONTRACT_ABI)
                decimals = token_contract.functions.decimals().call()
                amount_wei = int(float(amount) * (10 ** decimals))
                
                deadline = int(time.time()) + 600
                
                # Build V3 exactInputSingle swap parameters
                swap_params = encode(
                    ["address", "address", "uint24", "address", "uint256", "uint256", "uint160"],
                    [
                        web3.to_checksum_address(from_token),
                        web3.to_checksum_address(to_token),
                        500,  # fee tier (0.05%)
                        web3.to_checksum_address(address),  # recipient
                        amount_wei,  # amountIn
                        0,  # amountOutMinimum
                        0   # sqrtPriceLimitX96 (no limit)
                    ]
                )
                
                # V3_SWAP_EXACT_IN command
                commands = b'\x00'
                inputs = [swap_params]
                
                # Create transaction using execute function (0x3593564c)
                swap_contract = web3.eth.contract(
                    address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), 
                    abi=self.SWAP_CONTRACT_ABI
                )
                
                tx = swap_contract.functions.execute(commands, inputs, deadline).build_transaction({
                    "from": address,
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "gas": 400000,
                    "maxFeePerGas": web3.to_wei(3, "gwei"),
                    "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
                    "chainId": web3.eth.chain_id
                })
                
                signed = web3.eth.account.sign_transaction(tx, privkey)
                tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
                tx_hash_hex = web3.to_hex(tx_hash)
                
                # Verify transaction
                if await self.tx_verifier.verify_transaction(tx_hash_hex):
                    self.log(f"✅ Swap successful! TxHash: {tx_hash_hex}")
                    return tx_hash_hex
                else:
                    self.log(f"❌ Swap failed in explorer verification")
                    
            except Exception as e:
                if attempt < retries - 1:
                    self.log(f"❌ Swap failed: {e} | Retrying in 15s...")
                    await asyncio.sleep(15)
                else:
                    self.log(f"❌ Swap failed permanently: {e}")
                    return "FAILED"
        
        return "FAILED"

    async def perform_add_liquidity(self, privkey, address, token0, token1, amount0, amount1, retries=3):
        """Add liquidity with correct method signature 0xac9650d8"""
        web3 = await self.get_web3()
        
        for attempt in range(retries):
            try:
                self.log(f"🔄 Adding liquidity {float(amount0):.6f}/{float(amount1):.6f}...")
                
                # Approve both tokens
                if not await self.approving_token(privkey, address, self.POSITION_MANAGER_ADDRESS, token0, amount0):
                    continue
                if not await self.approving_token(privkey, address, self.POSITION_MANAGER_ADDRESS, token1, amount1):
                    continue
                
                token0_contract = web3.eth.contract(address=web3.to_checksum_address(token0), abi=self.ERC20_CONTRACT_ABI)
                token1_contract = web3.eth.contract(address=web3.to_checksum_address(token1), abi=self.ERC20_CONTRACT_ABI)
                
                amount0_desired = int(float(amount0) * (10 ** token0_contract.functions.decimals().call()))
                amount1_desired = int(float(amount1) * (10 ** token1_contract.functions.decimals().call()))
                
                deadline = int(time.time()) + 600
                
                # Build mint parameters tuple
                mint_params = (
                    web3.to_checksum_address(token0),    # token0
                    web3.to_checksum_address(token1),    # token1
                    500,                                 # fee (0.05%)
                    -887270,                            # tickLower (full range)
                    887270,                             # tickUpper (full range)
                    amount0_desired,                    # amount0Desired
                    amount1_desired,                    # amount1Desired
                    int(amount0_desired * 0.95),        # amount0Min (5% slippage)
                    int(amount1_desired * 0.95),        # amount1Min (5% slippage)
                    web3.to_checksum_address(address),  # recipient
                    deadline                            # deadline
                )
                
                # Encode mint function call data
                mint_data = encode(
                    ["(address,address,uint24,int24,int24,uint256,uint256,uint256,uint256,address,uint256)"],
                    [mint_params]
                )
                
                # Prepare multicall data with mint function selector (0x88316456)
                mint_selector = b'\x88\x31\x64\x56'
                multicall_data = [mint_selector + mint_data]
                
                # Use multicall function (0xac9650d8) - no deadline parameter
                lp_contract = web3.eth.contract(
                    address=web3.to_checksum_address(self.POSITION_MANAGER_ADDRESS), 
                    abi=self.ADD_LP_CONTRACT_ABI
                )
                
                tx = lp_contract.functions.multicall(multicall_data).build_transaction({
                    "from": address,
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "gas": 500000,
                    "maxFeePerGas": web3.to_wei(3, "gwei"),
                    "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
                    "chainId": web3.eth.chain_id
                })
                
                signed = web3.eth.account.sign_transaction(tx, privkey)
                tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
                tx_hash_hex = web3.to_hex(tx_hash)
                
                # Verify transaction
                if await self.tx_verifier.verify_transaction(tx_hash_hex):
                    self.log(f"✅ Add liquidity successful! TxHash: {tx_hash_hex}")
                    return tx_hash_hex
                else:
                    self.log(f"❌ Add liquidity failed in explorer verification")
                    
            except Exception as e:
                if attempt < retries - 1:
                    self.log(f"❌ Add liquidity failed: {e} | Retrying in 15s...")
                    await asyncio.sleep(15)
                else:
                    self.log(f"❌ Add liquidity failed permanently: {e}")
                    return "FAILED"
        
        return "FAILED"

    async def start(self):
        """Main bot execution with enhanced UI"""
        self.welcome()
        
        # Configure delays
        self.configure_delays()
        
        # Load private keys
        file_paths = [f'bot{i}.py' for i in range(1, 7)]
        account_list = []
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    content = file.read()
                    if 'PRIVATE_KEY' in content:
                        start = content.find("'") + 1
                        end = content.find("'", start)
                        if start > 0 and end > start:
                            privkey = content[start:end]
                            address = self.generate_address(privkey)
                            if address:
                                account_list.append((privkey, address))
                                self.log(f"✅ Loaded account: {self.mask_account(address)}")
        
        if not account_list:
            self.log("❌ No accounts found! Please ensure bot1.py to bot6.py contain valid private keys.")
            return
        
        self.log(f"🚀 Starting bot operations with {len(account_list)} accounts...")
        
        while True:
            try:
                for i, (privkey, address) in enumerate(account_list):
                    self.log(f"🔄 Processing account {i+1}/{len(account_list)}: {self.mask_account(address)}")
                    
                    # Display current balances
                    await self.display_balances(address)
                    
                    # Random operations based on balances
                    phrs_balance = await self.get_token_balance(address, "PHRS")
                    wphrs_balance = await self.get_token_balance(address, self.WPHRS_CONTRACT_ADDRESS)
                    usdc_balance = await self.get_token_balance(address, self.USDC_CONTRACT_ADDRESS)
                    
                    # Convert to float to ensure proper calculations
                    phrs_balance = float(phrs_balance)
                    wphrs_balance = float(wphrs_balance)
                    usdc_balance = float(usdc_balance)
                    
                    operation = random.choice([1, 2, 3, 4])
                    
                    if operation == 1 and phrs_balance > 0.01:
                        # Wrap PHRS
                        wrap_amount = min(phrs_balance * 0.1, 0.5)
                        await self.perform_wrapped(privkey, address, wrap_amount, wrap=True)
                    
                    elif operation == 2 and wphrs_balance > 0.01:
                        # Unwrap WPHRS
                        unwrap_amount = min(wphrs_balance * 0.1, 0.5)
                        await self.perform_wrapped(privkey, address, unwrap_amount, wrap=False)
                    
                    elif operation == 3 and wphrs_balance > 0.01:
                        # Swap WPHRS to USDC
                        swap_amount = min(wphrs_balance * 0.1, 0.3)
                        await self.perform_swap(privkey, address, self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, swap_amount)
                    
                    elif operation == 4 and usdc_balance > 0.01:
                        # Swap USDC to WPHRS
                        swap_amount = min(usdc_balance * 0.1, 1.0)
                        await self.perform_swap(privkey, address, self.USDC_CONTRACT_ADDRESS, self.WPHRS_CONTRACT_ADDRESS, swap_amount)
                    
                    # Random liquidity provision (less frequent)
                    if random.random() < 0.3 and wphrs_balance > 0.02 and usdc_balance > 0.02:
                        lp_amount0 = min(wphrs_balance * 0.05, 0.1)
                        lp_amount1 = min(usdc_balance * 0.05, 0.5)
                        await self.perform_add_liquidity(privkey, address, self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, lp_amount0, lp_amount1)
                    
                    # Wait between accounts
                    await self.wait_random_delay()
                
                # Longer delay between cycles
                cycle_delay = random.randint(30, 60)
                self.log(f"🔄 Cycle completed. Waiting {cycle_delay} seconds before next cycle...")
                await asyncio.sleep(cycle_delay)
                
            except KeyboardInterrupt:
                self.log("👋 Bot stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Unexpected error: {e}")
                await asyncio.sleep(30)

if __name__ == "__main__":
    bot = PharosTestnet()
    asyncio.run(bot.start())
