import os
import random
import string
import asyncio
from datetime import datetime
from colorama import Fore, Style, init
from fake_useragent import FakeUserAgent
from web3 import Web3

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
    BRIGHT_GREEN = Fore.LIGHTGREEN_EX
    BRIGHT_MAGENTA = Fore.LIGHTMAGENTA_EX
    BRIGHT_WHITE = Fore.LIGHTWHITE_EX
    BRIGHT_BLACK = Fore.LIGHTBLACK_EX

class Logger:
    @staticmethod
    def log(label, symbol, msg, color):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {color}[{symbol}] {msg}{Colors.RESET}")

    @staticmethod
    def info(msg): Logger.log("INFO", "✓", msg, Colors.GREEN)
    @staticmethod
    def warn(msg): Logger.log("WARN", "!", msg, Colors.YELLOW)
    @staticmethod
    def error(msg): Logger.log("ERR", "✗", msg, Colors.RED)
    @staticmethod
    def success(msg): Logger.log("OK", "+", msg, Colors.GREEN)
    @staticmethod
    def loading(msg): Logger.log("LOAD", "⟳", msg, Colors.CYAN)
    @staticmethod
    def step(msg): Logger.log("STEP", "➤", msg, Colors.WHITE)
    @staticmethod
    def action(msg): Logger.log("ACTION", "↪️", msg, Colors.CYAN)
    @staticmethod
    def actionSuccess(msg): Logger.log("ACTION", "✅", msg, Colors.GREEN)

logger = Logger()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

async def display_welcome_screen():
    now = datetime.now()
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}")
    print("  ╔══════════════════════════════════════╗")
    print("  ║            P R I M U S L A B           ║")
    print("  ║                                      ║")
    print(f"  ║      {Colors.YELLOW}{now.strftime('%H:%M:%S %d.%m.%Y')}{Colors.BRIGHT_GREEN}            ║")
    print("  ║                                      ║")
    print("  ║      PHAROS TESTNET AUTOMATION       ║")
    print(f"  ║   {Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}  |  t.me/ZonaAirdr0p    ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"{Colors.RESET}")

class SocialTipBot:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://pay.primuslabs.xyz/",
            "Referer": "https://pay.primuslabs.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api.pharosnetwork.xyz"
        self.RPC_URL = "https://testnet.dplabs-internal.com"
        self.Explorer_URL = "https://explorer.dplabs-internal.com/tx/"
        self.Router = "0xd17512b7ec12880bd94eca9d774089ff89805f02"
        self.proxies = []
        self.use_proxy = False
        self.accounts = []
        self.min_delay = 0
        self.max_delay = 0
        
        self.contract_abi = [
            {
                "inputs": [
                    {
                        "components": [
                            {
                                "internalType": "uint32",
                                "name": "tokenType",
                                "type": "uint32"
                            },
                            {
                                "internalType": "address",
                                "name": "tokenAddress",
                                "type": "address"
                            }
                        ],
                        "internalType": "struct TipToken",
                        "name": "token",
                        "type": "tuple"
                    },
                    {
                        "components": [
                            {
                                "internalType": "string",
                                "name": "idSource",
                                "type": "string"
                            },
                            {
                                "internalType": "string",
                                "name": "id",
                                "type": "string"
                            },
                            {
                                "internalType": "uint256",
                                "name": "amount",
                                "type": "uint256"
                            },
                            {
                                "internalType": "uint256[]",
                                "name": "nftIds",
                                "type": "uint256[]"
                            }
                        ],
                        "internalType": "struct TipRecipientInfo",
                        "name": "recipient",
                        "type": "tuple"
                    }
                ],
                "name": "tip",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        
        self.init_web3()
        
        self.load_accounts()
        self.load_proxies()

    def init_web3(self, proxy=None):
        if proxy:
            self.w3 = Web3(Web3.HTTPProvider(self.RPC_URL))
        else:
            self.w3 = Web3(Web3.HTTPProvider(self.RPC_URL))
        
        self.checksum_router_address = self.w3.to_checksum_address(self.Router)
        
        self.contract = self.w3.eth.contract(
            address=self.checksum_router_address,
            abi=self.contract_abi
        )

    def load_accounts(self):
        try:
            with open('accounts.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            account = self.w3.eth.account.from_key(line)
                            self.accounts.append(account)
                        except ValueError:
                            logger.error(f"Invalid private key: {line[:6]}...{line[-4:]}")
            logger.success(f"Loaded {len(self.accounts)} accounts.")
            if not self.accounts:
                logger.error("No valid accounts found in accounts.txt. Please add private keys.")
        except FileNotFoundError:
            logger.error("accounts.txt not found! Please create it and add private keys.")

    def load_proxies(self):
        try:
            with open('proxies.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.proxies.append(line)
            logger.success(f"Loaded {len(self.proxies)} proxies.")
        except FileNotFoundError:
            pass

    def generate_random_username(self, platform='x'):
        prefix = '@'
        length = random.randint(5, 12)
        chars = string.ascii_lowercase + string.digits + '_'
        return prefix + ''.join(random.choice(chars) for _ in range(length))

    async def check_balance(self, account):
        try:
            balance = await asyncio.to_thread(self.w3.eth.get_balance, account.address)
            return {
                'eth': self.w3.from_wei(balance, 'ether'),
                'token': ""
            }
        except Exception as e:
            logger.error(f"Balance check failed for {account.address}: {str(e)}")
            return None

    async def send_tip(self, sender_account, username, amount):
        try:
            tip_token = {
                "tokenType": 1,
                "tokenAddress": "0x0000000000000000000000000000000000000000"
            }
            
            value_in_wei = self.w3.to_wei(amount, 'ether')

            tip_recipient = {
                "idSource": "x",
                "id": username,
                "amount": value_in_wei,
                "nftIds": []
            }
            
            nonce = await asyncio.to_thread(self.w3.eth.get_transaction_count, sender_account.address)

            tx = self.contract.functions.tip(
                tip_token,
                tip_recipient
            ).build_transaction({
                'from': sender_account.address,
                'nonce': nonce,
                'gas': 300000,
                'gasPrice': self.w3.to_wei('50', 'gwei'),
                'value': value_in_wei
            })
            
            signed_tx = sender_account.sign_transaction(tx) 
            raw_transaction = signed_tx.raw_transaction

            logger.action(f"Sending transaction from {sender_account.address[:6]}...{sender_account.address[-4:]}...")
            
            tx_hash = await asyncio.to_thread(self.w3.eth.send_raw_transaction, raw_transaction)
            
            logger.loading(f"Waiting for transaction confirmation... {self.Explorer_URL}{tx_hash.hex()}")
            
            receipt = await asyncio.to_thread(self.w3.eth.wait_for_transaction_receipt, tx_hash)
            
            if receipt.status == 1:
                explorer_link = f"{self.Explorer_URL}{tx_hash.hex()}"
                logger.actionSuccess(f"Sent {amount} token to {username} | TX: {tx_hash.hex()} | Explorer: {explorer_link}")
                return True
            else:
                logger.error(f"Transaction failed for {username}. Receipt status: {receipt.status}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending tip from {sender_account.address[:6]}...{sender_account.address[-4:]} to {username}: {str(e)}")
            return False

    async def show_main_menu(self):
        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}=== PRIMUS BOT MENU ===")
        print(f"{Colors.RESET}")
        print("1. Send Tip")
        print("2. Check Balance")
        print("3. Exit")
        
        choice = input(f"\n{Colors.CYAN}Select option (1-3): {Colors.RESET}")
        return choice

    async def show_proxy_menu(self):
        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}=== PROXY MODE ===")
        print(f"{Colors.RESET}")
        print("1. Run with private proxy")
        print("2. Run without proxy")
        
        choice = input(f"\n{Colors.CYAN}Select option (1-2): {Colors.RESET}")
        return choice

    async def handle_send_tip(self):
        clear_console()
        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}=== SEND TIP ===") # Corrected this line
        print(f"{Colors.RESET}")
        
        if not self.accounts:
            logger.error("No accounts available! Please add private keys to accounts.txt.")
            await asyncio.sleep(2)
            return

        total_transactions = 0
        while True:
            try:
                num_transactions_str = input(f"\n{Colors.CYAN}How many transactions do you want to perform (e.g., 10)? {Colors.RESET}")
                total_transactions = int(num_transactions_str.strip())
                if total_transactions <= 0:
                    raise ValueError
                break
            except ValueError:
                logger.error("Invalid number of transactions! Please enter a positive integer.")
                await asyncio.sleep(1)

        proxy_choice = await self.show_proxy_menu()
        if proxy_choice == '1':
            if not self.proxies:
                logger.warn("You selected private proxy mode, but no proxies were loaded from proxies.txt. Continuing without proxy.") # This line was the one still in Indonesian
                self.use_proxy = False
            else:
                self.use_proxy = True
                logger.info("Private proxy mode enabled.")
        elif proxy_choice == '2':
            self.use_proxy = False
            logger.info("Private proxy mode disabled.")
        else:
            logger.error("Invalid choice! Cancelling.")
            await asyncio.sleep(1)
            return

        amount_range_str = input(f"\n{Colors.CYAN}Enter the amount range to send (e.g., 0.01-0.05): {Colors.RESET}")
        try:
            min_amount_str, max_amount_str = amount_range_str.split('-')
            min_amount = float(min_amount_str.strip())
            max_amount = float(max_amount_str.strip())
            if min_amount <= 0 or max_amount <= 0 or min_amount > max_amount:
                raise ValueError
            logger.info(f"Random amount will be selected between {min_amount:.6f}-{max_amount:.6f}.")
        except ValueError:
            logger.error("Invalid amount range! Please enter 'min-max' format with positive numbers (e.g., 0.01-0.05).")
            await asyncio.sleep(2)
            return

        try:
            min_delay_str = input(f"\n{Colors.CYAN}Enter minimum delay between transactions (seconds): {Colors.RESET}")
            self.min_delay = int(min_delay_str.strip())
            max_delay_str = input(f"{Colors.CYAN}Enter maximum delay between transactions (seconds): {Colors.RESET}")
            self.max_delay = int(max_delay_str.strip())
            if self.min_delay < 0 or self.max_delay < 0 or self.min_delay > self.max_delay:
                raise ValueError
            logger.info(f"Delay between transactions set between {self.min_delay}-{self.max_delay} seconds.")
        except ValueError:
            logger.error("Invalid delay! Please enter positive integers.")
            await asyncio.sleep(2)
            return

        print("\nAvailable Accounts:")
        for i, acc in enumerate(self.accounts, 1):
            print(f"{i}. {acc.address}")
            
        acc_choice = input(f"\n{Colors.CYAN}Select account (1-{len(self.accounts)}) or 'all' for all accounts: {Colors.RESET}")
        
        selected_accounts = []
        if acc_choice.lower() == 'all':
            selected_accounts = self.accounts
            logger.info(f"All {len(selected_accounts)} accounts selected.")
        else:
            try:
                account = self.accounts[int(acc_choice)-1]
                selected_accounts.append(account)
                logger.info(f"Account {account.address} selected.")
            except (ValueError, IndexError):
                logger.error("Invalid choice! Please enter a valid number or 'all'.")
                await asyncio.sleep(2)
                return
        
        if not selected_accounts:
            logger.error("No accounts selected for transactions.")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
            return

        logger.info(f"Starting {total_transactions} transactions...")
        for i in range(total_transactions):
            logger.step(f"Transaction {i+1}/{total_transactions}")
            account = random.choice(selected_accounts)
            amount_to_send = random.uniform(min_amount, max_amount)
            username = self.generate_random_username()
            
            logger.step(f"Attempting to send {amount_to_send:.6f} token (to Router: {self.checksum_router_address}) to @{username} from {account.address}...")
            
            selected_proxy = None
            if self.use_proxy and self.proxies:
                selected_proxy = random.choice(self.proxies)
                logger.info(f"Using proxy: {selected_proxy}")
                logger.warn("Proxy setup for Web3.py RPC calls requires more advanced configuration (e.g., custom transport). The selected proxy is noted but not directly applied to blockchain transactions in this setup.")

            success = await self.send_tip(account, username, amount_to_send)
            if success:
                logger.success("Tip sent successfully!")
            else:
                logger.error("Failed to send tip!")
            
            if i < total_transactions - 1:
                delay = random.randint(self.min_delay, self.max_delay)
                logger.loading(f"Waiting {delay} seconds before next transaction...")
                await asyncio.sleep(delay)
            
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")


    async def check_balances_menu(self):
        clear_console()
        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}=== ACCOUNT BALANCES ===")
        print(f"{Colors.RESET}")
        
        if not self.accounts:
            logger.error("No accounts available!")
            await asyncio.sleep(2)
            return
            
        for account in self.accounts:
            balances = await self.check_balance(account)
            if balances:
                print(f"\n{Colors.CYAN}Account: {account.address}")
                print(f"{Colors.WHITE}ETH Balance: {balances['eth']:.6f}")
                print(f"{Colors.WHITE}Token Balance: {balances['token']}")
            else:
                logger.error(f"Failed to check balance for {account.address}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")

    async def run(self):
        await display_welcome_screen()
        
        while True:
            choice = await self.show_main_menu()
            
            if choice == '1':
                await self.handle_send_tip()
            elif choice == '2':
                await self.check_balances_menu()
            elif choice == '3':
                logger.info("Exiting...")
                break
            else:
                logger.error("Invalid option!")
                await asyncio.sleep(1)

if __name__ == "__main__":
    bot = SocialTipBot()
    asyncio.run(bot.run())
