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
        
        # Supported swap pairs - restricted to 4 pairs only
        self.SUPPORTED_SWAP_PAIRS = [
            {"from": "PHRS", "to": "USDC"},
            {"from": "PHRS", "to": "USDT"},
            {"from": "USDC", "to": "PHRS"},
            {"from": "USDT", "to": "PHRS"}
        ]
        
        # Supported liquidity pairs - restricted to 2 pairs only  
        self.SUPPORTED_LP_PAIRS = [
            {"token0": "PHRS", "token1": "USDC"},
            {"token0": "PHRS", "token1": "USDT"}
        ]

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
                'from': address,
                'gas': 100000,
                'gasPrice': web3.to_wei('20', 'gwei'),
                'nonce': web3.eth.get_transaction_count(address),
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key=privkey)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            self.log(f"📝 Approval transaction sent: {tx_hash.hex()}")
            
            # Verify the transaction
            verified = await self.tx_verifier.verify_transaction(tx_hash.hex())
            if verified:
                self.log(f"✅ Token approval successful")
                return True
            else:
                self.log(f"❌ Token approval failed")
                return False
        else:
            self.log(f"✅ Token already approved")
            return True

    def get_token_address(self, token_symbol):
        """Get token contract address by symbol"""
        if token_symbol == "PHRS":
            return "0x0000000000000000000000000000000000000000"  # Native token
        elif token_symbol == "WPHRS":
            return self.WPHRS_CONTRACT_ADDRESS
        elif token_symbol == "USDC":
            return self.USDC_CONTRACT_ADDRESS
        elif token_symbol == "USDT":
            return self.USDT_CONTRACT_ADDRESS
        else:
            return None

    def display_swap_pairs(self):
        """Display available swap pairs"""
        print(f"{Fore.CYAN}🔄 Available Swap Pairs:")
        for i, pair in enumerate(self.SUPPORTED_SWAP_PAIRS, 1):
            print(f"{Fore.YELLOW}   {i}. {pair['from']} → {pair['to']}")
        print()

    def select_swap_pair(self):
        """Let user select a swap pair"""
        self.display_swap_pairs()
        
        while True:
            try:
                choice = input(f"{Fore.GREEN}Select swap pair (1-{len(self.SUPPORTED_SWAP_PAIRS)}): ").strip()
                if choice:
                    choice = int(choice) - 1
                    if 0 <= choice < len(self.SUPPORTED_SWAP_PAIRS):
                        return self.SUPPORTED_SWAP_PAIRS[choice]
                    else:
                        print(f"{Fore.RED}Invalid choice. Please select 1-{len(self.SUPPORTED_SWAP_PAIRS)}")
                else:
                    print(f"{Fore.RED}Please enter a valid number")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number")

    async def swap_tokens(self, privkey, address, from_token, to_token, amount):
        """Swap tokens using Universal Router with restricted pairs"""
        try:
            web3 = await self.get_web3()
            
            # Validate swap pair
            pair_valid = False
            for pair in self.SUPPORTED_SWAP_PAIRS:
                if pair['from'] == from_token and pair['to'] == to_token:
                    pair_valid = True
                    break
            
            if not pair_valid:
                self.log(f"❌ Swap pair {from_token} → {to_token} not supported")
                return False
            
            self.log(f"🔄 Swapping {amount} {from_token} → {to_token}...")
            
            # Get token addresses
            from_token_addr = self.get_token_address(from_token)
            to_token_addr = self.get_token_address(to_token)
            
            if from_token_addr is None or to_token_addr is None:
                self.log(f"❌ Invalid token addresses")
                return False
            
            # For native PHRS, we need to use WPHRS in the swap
            if from_token == "PHRS":
                from_token_addr = self.WPHRS_CONTRACT_ADDRESS
            if to_token == "PHRS":
                to_token_addr = self.WPHRS_CONTRACT_ADDRESS
            
            # Approve tokens if needed (except for native PHRS)
            if from_token != "PHRS":
                approved = await self.approving_token(privkey, address, self.SWAP_ROUTER_ADDRESS, from_token_addr, amount)
                if not approved:
                    return False
            
            # Build swap transaction
            contract = web3.eth.contract(address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), abi=self.SWAP_CONTRACT_ABI)
            
            # Universal Router commands and inputs
            commands = b"\x00"  # V3_SWAP_EXACT_IN
            deadline = int(time.time()) + 1800  # 30 minutes from now
            
            # Encode swap parameters
            from_token_addr = web3.to_checksum_address(from_token_addr)
            to_token_addr = web3.to_checksum_address(to_token_addr)
            recipient = address
            
            # Convert amount to wei
            if from_token == "PHRS":
                amount_wei = web3.to_wei(amount, 'ether')
            else:
                from_contract = web3.eth.contract(address=from_token_addr, abi=self.ERC20_CONTRACT_ABI)
                decimals = from_contract.functions.decimals().call()
                amount_wei = int(amount * (10 ** decimals))
            
            # Build swap input data
            swap_data = encode(
                ['address', 'uint256', 'uint256', 'bytes', 'bool'],
                [recipient, amount_wei, 0, b'', True]
            )
            
            inputs = [swap_data]
            
            # Prepare transaction
            tx_value = amount_wei if from_token == "PHRS" else 0
            
            tx = contract.functions.execute(commands, inputs, deadline).build_transaction({
                'from': address,
                'value': tx_value,
                'gas': 500000,
                'gasPrice': web3.to_wei('20', 'gwei'),
                'nonce': web3.eth.get_transaction_count(address),
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key=privkey)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            self.log(f"📝 Swap transaction sent: {tx_hash.hex()}")
            
            # Verify the transaction
            verified = await self.tx_verifier.verify_transaction(tx_hash.hex())
            if verified:
                self.log(f"✅ Swap successful: {amount} {from_token} → {to_token}")
                self.swap_count += 1
                return True
            else:
                self.log(f"❌ Swap failed")
                return False
                
        except Exception as e:
            self.log(f"❌ Swap error: {str(e)}")
            return False

    async def wrap_phrs(self, privkey, address, amount):
        """Wrap PHRS to WPHRS"""
        try:
            web3 = await self.get_web3()
            
            self.log(f"🔄 Wrapping {amount} PHRS to WPHRS...")
            
            contract = web3.eth.contract(address=web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS), abi=self.ERC20_CONTRACT_ABI)
            amount_wei = web3.to_wei(amount, 'ether')
            
            tx = contract.functions.deposit().build_transaction({
                'from': address,
                'value': amount_wei,
                'gas': 100000,
                'gasPrice': web3.to_wei('20', 'gwei'),
                'nonce': web3.eth.get_transaction_count(address),
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key=privkey)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            self.log(f"📝 Wrap transaction sent: {tx_hash.hex()}")
            
            # Verify the transaction
            verified = await self.tx_verifier.verify_transaction(tx_hash.hex())
            if verified:
                self.log(f"✅ Wrap successful: {amount} PHRS → WPHRS")
                return True
            else:
                self.log(f"❌ Wrap failed")
                return False
                
        except Exception as e:
            self.log(f"❌ Wrap error: {str(e)}")
            return False

    async def unwrap_phrs(self, privkey, address, amount):
        """Unwrap WPHRS to PHRS"""
        try:
            web3 = await self.get_web3()
            
            self.log(f"🔄 Unwrapping {amount} WPHRS to PHRS...")
            
            contract = web3.eth.contract(address=web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS), abi=self.ERC20_CONTRACT_ABI)
            amount_wei = web3.to_wei(amount, 'ether')
            
            tx = contract.functions.withdraw(amount_wei).build_transaction({
                'from': address,
                'gas': 100000,
                'gasPrice': web3.to_wei('20', 'gwei'),
                'nonce': web3.eth.get_transaction_count(address),
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key=privkey)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            self.log(f"📝 Unwrap transaction sent: {tx_hash.hex()}")
            
            # Verify the transaction
            verified = await self.tx_verifier.verify_transaction(tx_hash.hex())
            if verified:
                self.log(f"✅ Unwrap successful: {amount} WPHRS → PHRS")
                self.unwrap_count += 1
                return True
            else:
                self.log(f"❌ Unwrap failed")
                return False
                
        except Exception as e:
            self.log(f"❌ Unwrap error: {str(e)}")
            return False

    def display_add_lp_pairs(self):
        """Display available liquidity pairs - restricted to PHRS/USDC and PHRS/USDT"""
        print(f"{Fore.CYAN}💧 Available Liquidity Pairs:")
        for i, pair in enumerate(self.SUPPORTED_LP_PAIRS, 1):
            print(f"{Fore.YELLOW}   {i}. {pair['token0']}/{pair['token1']}")
        print()

    def select_lp_pair(self):
        """Let user select a liquidity pair"""
        self.display_add_lp_pairs()
        
        while True:
            try:
                choice = input(f"{Fore.GREEN}Select liquidity pair (1-{len(self.SUPPORTED_LP_PAIRS)}): ").strip()
                if choice:
                    choice = int(choice) - 1
                    if 0 <= choice < len(self.SUPPORTED_LP_PAIRS):
                        return self.SUPPORTED_LP_PAIRS[choice]
                    else:
                        print(f"{Fore.RED}Invalid choice. Please select 1-{len(self.SUPPORTED_LP_PAIRS)}")
                else:
                    print(f"{Fore.RED}Please enter a valid number")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number")
        
        while True:
            try:
                choice = input(f"{Fore.GREEN}Select liquidity pair (1-2): ").strip()
                if choice == "1":
                    return {"token0": "PHRS", "token1": "USDC"}
                elif choice == "2":
                    return {"token0": "PHRS", "token1": "USDT"}
                else:
                    print(f"{Fore.RED}Invalid choice. Please select 1 or 2")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number")

    async def add_liquidity(self, privkey, address, token0, token1, amount0, amount1):
        """Add liquidity to pool - restricted to PHRS/USDC and PHRS/USDT"""
        try:
            web3 = await self.get_web3()
            
            # Validate liquidity pair
            valid_pairs = [
                {"token0": "PHRS", "token1": "USDC"},
                {"token0": "PHRS", "token1": "USDT"}
            ]
            
            pair_valid = False
            for pair in valid_pairs:
                if (pair['token0'] == token0 and pair['token1'] == token1) or \
                   (pair['token0'] == token1 and pair['token1'] == token0):
                    pair_valid = True
                    break
            
            if not pair_valid:
                self.log(f"❌ Liquidity pair {token0}/{token1} not supported")
                return False
            
            self.log(f"💧 Adding liquidity: {amount0} {token0} + {amount1} {token1}...")
            
            # Get token addresses
            token0_addr = self.get_token_address(token0)
            token1_addr = self.get_token_address(token1)
            
            if token0_addr is None or token1_addr is None:
                self.log(f"❌ Invalid token addresses")
                return False
            
            # For native PHRS, we need to use WPHRS in the LP
            if token0 == "PHRS":
                token0_addr = self.WPHRS_CONTRACT_ADDRESS
            if token1 == "PHRS":
                token1_addr = self.WPHRS_CONTRACT_ADDRESS
            
            # Approve tokens if needed
            if token0 != "PHRS":
                approved = await self.approving_token(privkey, address, self.POSITION_MANAGER_ADDRESS, token0_addr, amount0)
                if not approved:
                    return False
            
            if token1 != "PHRS":
                approved = await self.approving_token(privkey, address, self.POSITION_MANAGER_ADDRESS, token1_addr, amount1)
                if not approved:
                    return False
            
            # Build add liquidity transaction
            contract = web3.eth.contract(address=web3.to_checksum_address(self.POSITION_MANAGER_ADDRESS), abi=self.ADD_LP_CONTRACT_ABI)
            
            # Convert amounts to wei
            if token0 == "PHRS":
                amount0_wei = web3.to_wei(amount0, 'ether')
            else:
                token0_contract = web3.eth.contract(address=token0_addr, abi=self.ERC20_CONTRACT_ABI)
                decimals0 = token0_contract.functions.decimals().call()
                amount0_wei = int(amount0 * (10 ** decimals0))
            
            if token1 == "PHRS":
                amount1_wei = web3.to_wei(amount1, 'ether')
            else:
                token1_contract = web3.eth.contract(address=token1_addr, abi=self.ERC20_CONTRACT_ABI)
                decimals1 = token1_contract.functions.decimals().call()
                amount1_wei = int(amount1 * (10 ** decimals1))
            
            # Build multicall data for adding liquidity
            multicall_data = []
            
            # Calculate tx value (only if one of the tokens is native PHRS)
            tx_value = 0
            if token0 == "PHRS":
                tx_value = amount0_wei
            elif token1 == "PHRS":
                tx_value = amount1_wei
            
            tx = contract.functions.multicall(multicall_data).build_transaction({
                'from': address,
                'value': tx_value,
                'gas': 800000,
                'gasPrice': web3.to_wei('20', 'gwei'),
                'nonce': web3.eth.get_transaction_count(address),
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, private_key=privkey)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            self.log(f"📝 Add liquidity transaction sent: {tx_hash.hex()}")
            
            # Verify the transaction
            verified = await self.tx_verifier.verify_transaction(tx_hash.hex())
            if verified:
                self.log(f"✅ Add liquidity successful: {amount0} {token0} + {amount1} {token1}")
                self.add_lp_count += 1
                return True
            else:
                self.log(f"❌ Add liquidity failed")
                return False
                
        except Exception as e:
            self.log(f"❌ Add liquidity error: {str(e)}")
            return False

    def configure_operations(self):
        """Configure operations for batch mode"""
        print(f"{Fore.CYAN}🔧 Configure Operations")
        
        # Configure swaps
        swap_input = input(f"{Fore.YELLOW}Number of swaps to perform [0]: ").strip()
        self.total_swaps = int(swap_input) if swap_input else 0
        
        # Configure unwraps
        unwrap_input = input(f"{Fore.YELLOW}Number of unwraps to perform [0]: ").strip()
        self.total_unwraps = int(unwrap_input) if unwrap_input else 0
        
        # Configure add liquidity
        add_lp_input = input(f"{Fore.YELLOW}Number of add liquidity operations [0]: ").strip()
        self.total_add_lps = int(add_lp_input) if add_lp_input else 0
        
        # Configure auto mode
        auto_input = input(f"{Fore.YELLOW}Enable auto mode? (y/n) [n]: ").strip().lower()
        self.auto_mode = auto_input in ['y', 'yes']
        
        self.log(f"✅ Operations configured - Swaps: {self.total_swaps}, Unwraps: {self.total_unwraps}, Add LP: {self.total_add_lps}, Auto: {self.auto_mode}")

    async def execute_operations(self, privkey, address):
        """Execute configured operations"""
        try:
            operations_completed = 0
            
            # Execute swaps
            for i in range(self.total_swaps):
                if self.swap_count >= self.total_swaps:
                    break
                    
                self.log(f"🔄 Executing swap {self.swap_count + 1}/{self.total_swaps}")
                
                # Select random swap pair
                pair = random.choice(self.SUPPORTED_SWAP_PAIRS)
                
                # Random amount between 0.001 and 0.01
                amount = round(random.uniform(0.001, 0.01), 6)
                
                success = await self.swap_tokens(privkey, address, pair['from'], pair['to'], amount)
                if success:
                    operations_completed += 1
                
                if i < self.total_swaps - 1:
                    await self.wait_random_delay()
            
            # Execute unwraps
            for i in range(self.total_unwraps):
                if self.unwrap_count >= self.total_unwraps:
                    break
                    
                self.log(f"🔄 Executing unwrap {self.unwrap_count + 1}/{self.total_unwraps}")
                
                # Random amount between 0.001 and 0.01
                amount = round(random.uniform(0.001, 0.01), 6)
                
                success = await self.unwrap_phrs(privkey, address, amount)
                if success:
                    operations_completed += 1
                
                if i < self.total_unwraps - 1:
                    await self.wait_random_delay()
            
            # Execute add liquidity
            for i in range(self.total_add_lps):
                if self.add_lp_count >= self.total_add_lps:
                    break
                    
                self.log(f"🔄 Executing add liquidity {self.add_lp_count + 1}/{self.total_add_lps}")
                
                # Select random LP pair from supported pairs
                lp_pairs = [
                    {"token0": "PHRS", "token1": "USDC"},
                    {"token0": "PHRS", "token1": "USDT"}
                ]
                pair = random.choice(lp_pairs)
                
                # Random amounts
                amount0 = round(random.uniform(0.001, 0.01), 6)
                amount1 = round(random.uniform(0.001, 0.01), 6)
                
                success = await self.add_liquidity(privkey, address, pair['token0'], pair['token1'], amount0, amount1)
                if success:
                    operations_completed += 1
                
                if i < self.total_add_lps - 1:
                    await self.wait_random_delay()
            
            self.log(f"🎉 Operations completed: {operations_completed}")
            
        except Exception as e:
            self.log(f"❌ Error executing operations: {str(e)}")

    def display_menu(self):
        """Display main menu"""
        print(f"{Fore.CYAN}🎮 Main Menu:")
        print(f"{Fore.YELLOW}   1. Check Balances")
        print(f"{Fore.YELLOW}   2. Swap Tokens")
        print(f"{Fore.YELLOW}   3. Wrap PHRS")
        print(f"{Fore.YELLOW}   4. Unwrap WPHRS")
        print(f"{Fore.YELLOW}   5. Add Liquidity")
        print(f"{Fore.YELLOW}   6. Configure Delays")
        print(f"{Fore.YELLOW}   7. Configure Operations")
        print(f"{Fore.YELLOW}   8. Execute Operations")
        print(f"{Fore.YELLOW}   9. Exit")
        print()

    async def run_interactive_mode(self, privkey, address):
        """Run interactive mode"""
        while True:
            self.display_menu()
            
            try:
                choice = input(f"{Fore.GREEN}Select option (1-9): ").strip()
                
                if choice == "1":
                    await self.display_balances(address)
                    
                elif choice == "2":
                    pair = self.select_swap_pair()
                    amount = float(input(f"{Fore.YELLOW}Enter amount to swap: ").strip())
                    await self.swap_tokens(privkey, address, pair['from'], pair['to'], amount)
                    
                elif choice == "3":
                    amount = float(input(f"{Fore.YELLOW}Enter amount of PHRS to wrap: ").strip())
                    await self.wrap_phrs(privkey, address, amount)
                    
                elif choice == "4":
                    amount = float(input(f"{Fore.YELLOW}Enter amount of WPHRS to unwrap: ").strip())
                    await self.unwrap_phrs(privkey, address, amount)
                    
                elif choice == "5":
                    pair = self.select_lp_pair()
                    amount0 = float(input(f"{Fore.YELLOW}Enter amount of {pair['token0']}: ").strip())
                    amount1 = float(input(f"{Fore.YELLOW}Enter amount of {pair['token1']}: ").strip())
                    await self.add_liquidity(privkey, address, pair['token0'], pair['token1'], amount0, amount1)
                    
                elif choice == "6":
                    self.configure_delays()
                    
                elif choice == "7":
                    self.configure_operations()
                    
                elif choice == "8":
                    await self.execute_operations(privkey, address)
                    
                elif choice == "9":
                    print(f"{Fore.GREEN}👋 Goodbye!")
                    break
                    
                else:
                    print(f"{Fore.RED}Invalid choice. Please select 1-9")
                    
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number")
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}Operation cancelled by user")
                break
            except Exception as e:
                self.log(f"❌ Error: {str(e)}")

    async def main(self):
        """Main function"""
        try:
            self.welcome()
            
            # Load private keys
            print(f"{Fore.CYAN}📋 Loading private keys...")
            
            if not os.path.exists("accounts.txt"):
                print(f"{Fore.RED}❌ accounts.txt not found!")
                print(f"{Fore.YELLOW}📝 Please create accounts.txt with your private keys (one per line)")
                return
            
            with open("accounts.txt", "r") as f:
                private_keys = [line.strip() for line in f.readlines() if line.strip()]
            
            if not private_keys:
                print(f"{Fore.RED}❌ No private keys found in accounts.txt")
                return
            
            self.log(f"✅ Loaded {len(private_keys)} private keys")
            
            # Process each account
            for i, privkey in enumerate(private_keys):
                try:
                    address = self.generate_address(privkey)
                    if not address:
                        continue
                    
                    self.log(f"🔄 Processing account {i+1}/{len(private_keys)}: {self.mask_account(address)}")
                    
                    # Display initial balances
                    await self.display_balances(address)
                    
                    # Run interactive mode for first account, batch mode for others
                    if i == 0:
                        self.log(f"🎮 Running interactive mode for account 1...")
                        await self.run_interactive_mode(privkey, address)
                    else:
                        if self.auto_mode and (self.total_swaps > 0 or self.total_unwraps > 0 or self.total_add_lps > 0):
                            self.log(f"🤖 Running auto mode for account {i+1}...")
                            await self.execute_operations(privkey, address)
                        else:
                            self.log(f"⏭️ Skipping account {i+1} (auto mode disabled or no operations configured)")
                    
                    # Wait between accounts
                    if i < len(private_keys) - 1:
                        await self.wait_random_delay()
                        
                except Exception as e:
                    self.log(f"❌ Error processing account {i+1}: {str(e)}")
                    continue
            
            # Final summary
            print(f"\n{Fore.GREEN}📊 Final Summary:")
            print(f"{Fore.YELLOW}   Total swaps completed: {self.swap_count}")
            print(f"{Fore.YELLOW}   Total unwraps completed: {self.unwrap_count}")
            print(f"{Fore.YELLOW}   Total add LP completed: {self.add_lp_count}")
            print(f"\n{Fore.GREEN}🛑 Shutdown completed successfully")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}🛑 Bot stopped by user")
        except Exception as e:
            self.log(f"❌ Critical error: {str(e)}")
        finally:
            print(f"\n{Fore.CYAN}👋 Thank you for using Pharos Testnet Bot!")

if __name__ == "__main__":
    bot = PharosTestnet()
    asyncio.run(bot.main())
