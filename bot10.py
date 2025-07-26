import threading
import queue
import random
import time
import os
import string
from web3 import Web3, HTTPProvider
from eth_account import Account
from hexbytes import HexBytes
import logging
from typing import List, Tuple
import requests
from concurrent.futures import ThreadPoolExecutor
from urllib3.exceptions import HTTPError
from datetime import datetime
import asyncio
import pytz
from colorama import *

wib = pytz.timezone('Asia/Jakarta')

class PharosENSBot:
    def __init__(self) -> None:
        self.CONFIG = {
            'RPC_URL': "https://testnet.dplabs-internal.com",
            'CONTROLLER_ADDRESS': "0x51be1ef20a1fd5179419738fc71d95a8b6f8a175",
            'DURATION': 31536000,
            'RESOLVER': "0x9a43dcA1C3BB268546b98eb2AB1401bFc5b58505",
            'DATA': [],
            'REVERSE_RECORD': True,
            'OWNER_CONTROLLED_FUSES': 0,
            'CHAIN_ID': 688688
        }
        
        self.CONTROLLER_ABI = [
            {
                "constant": True,
                "inputs": [
                    {"name": "name", "type": "string"},
                    {"name": "owner", "type": "address"},
                    {"name": "duration", "type": "uint256"},
                    {"name": "secret", "type": "bytes32"},
                    {"name": "resolver", "type": "address"},
                    {"name": "data", "type": "bytes[]"},
                    {"name": "reverseRecord", "type": "bool"},
                    {"name": "ownerControlledFuses", "type": "uint16"}
                ],
                "name": "makeCommitment",
                "outputs": [{"name": "", "type": "bytes32"}],
                "stateMutability": "pure",
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [{"name": "commitment", "type": "bytes32"}],
                "name": "commit",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [
                    {"name": "name", "type": "string"},
                    {"name": "duration", "type": "uint256"}
                ],
                "name": "rentPrice",
                "outputs": [
                    {
                        "components": [
                            {"name": "base", "type": "uint256"},
                            {"name": "premium", "type": "uint256"}
                        ],
                        "name": "",
                        "type": "tuple"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "name", "type": "string"},
                    {"name": "owner", "type": "address"},
                    {"name": "duration", "type": "uint256"},
                    {"name": "secret", "type": "bytes32"},
                    {"name": "resolver", "type": "address"},
                    {"name": "data", "type": "bytes[]"},
                    {"name": "reverseRecord", "type": "bool"},
                    {"name": "ownerControlledFuses", "type": "uint16"}
                ],
                "name": "register",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        
        self.success_count = 0
        self.failed_count = 0
        self.total_tasks = 0
        self.current_tasks_processed = 0
        self.processed_lock = threading.Lock()

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
        print(Fore.GREEN + Style.BRIGHT + "    ⚡ Pharos ENS Domain Registration BOT  ⚡")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.YELLOW + Style.BRIGHT + "    🧠 Project    : Pharos ENS Domain Bot")
        print(Fore.YELLOW + Style.BRIGHT + "    🧑‍💻 Author     : YetiDAO")
        print(Fore.YELLOW + Style.BRIGHT + "    🌐 Network    : Pharos Testnet (Chain ID: 688688)")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.WHITE + Style.BRIGHT + "    🔄 Commit → ⏳ Wait → 🎯 Register")
        print(Fore.GREEN + Style.BRIGHT + "    🧠 Full ENS Registration Flow")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.MAGENTA + Style.BRIGHT + "    🧬 Powered by Cryptodai3 × YetiDAO | ENS v1.0 🚀")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "═" * 60 + "\n")

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def mask_account(self, account):
        try:
            if len(account) <= 10:
                return f"{account[:4]}...{account[-2:]}"
            return f"{account[:6]}...{account[-4:]}"
        except:
            return "Unknown"

    def load_file_lines(self, filename: str) -> List[str]:
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.log(f"{Fore.RED}File '{filename}' not found.{Style.RESET_ALL}")
            return []

    def random_name(self, length: int = 9) -> str:
        if length < 3: 
            length = 3 

        chars_letters = string.ascii_lowercase
        chars_letters_digits = string.ascii_lowercase + string.digits
        
        name_list = []

        name_list.append(random.choice(chars_letters))

        for _ in range(length - 1):
            if name_list[-1] == '-':
                name_list.append(random.choice(chars_letters_digits))
            else:
                name_list.append(random.choice(chars_letters_digits + '-' * 1)) 

        if name_list[-1] == '-':
            name_list[-1] = random.choice(chars_letters_digits)

        cleaned_name = []
        for i, char in enumerate(name_list):
            if char == '-' and i > 0 and cleaned_name and cleaned_name[-1] == '-':
                cleaned_name.append(random.choice(chars_letters_digits))
            else:
                cleaned_name.append(char)
                
        while len(cleaned_name) < length:
            if cleaned_name and cleaned_name[-1] == '-':
                cleaned_name.append(random.choice(chars_letters_digits))
            else:
                cleaned_name.append(random.choice(chars_letters_digits + '-'))

        final_result = ''.join(cleaned_name[:length])
        if final_result.startswith('-'):
            final_result = random.choice(chars_letters_digits) + final_result[1:]
        if final_result.endswith('-'):
            final_result = final_result[:-1] + random.choice(chars_letters_digits)
        
        final_result = final_result.replace('--', random.choice(chars_letters_digits) + random.choice(chars_letters_digits))
        
        while len(final_result) < length:
            final_result += random.choice(chars_letters_digits)

        return final_result[:length]

    def test_proxy(self, proxy: str) -> Tuple[str, bool]:
        try:
            response = requests.get('https://api.ipify.org', proxies={'http': proxy, 'https': proxy}, timeout=5)
            return proxy, response.status_code == 200
        except (requests.RequestException, HTTPError) as e:
            self.log(f"{Fore.YELLOW}Proxy {proxy} failed to test: {e}{Style.RESET_ALL}") 
            return proxy, False

    def create_web3_instance(self, proxy: str = None) -> Web3:
        if proxy:
            session = requests.Session()
            session.proxies = {'http': proxy, 'https': proxy}
            return Web3(HTTPProvider(self.CONFIG['RPC_URL'], session=session))
        return Web3(HTTPProvider(self.CONFIG['RPC_URL']))

    def validate_private_key(self, private_key: str) -> bool:
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        if len(private_key) != 64 or not all(c in string.hexdigits for c in private_key):
            return False
        return True

    def register_domain_single_task(self, private_key: str, index: int, reg_index: int, proxy: str = None) -> None:
        MAX_RETRY = 5
        retry = 0
        
        if not self.validate_private_key(private_key):
            self.log(f"{Fore.RED}[Wallet #{index+1} | Attempt {reg_index}] Invalid private key, skipping registration.{Style.RESET_ALL}")
            with self.processed_lock:
                self.failed_count += 1
                self.current_tasks_processed += 1
            return

        w3 = self.create_web3_instance(proxy)
        
        try:
            account = Account.from_key(private_key)
            owner_address = account.address
            controller_address = w3.to_checksum_address(self.CONFIG['CONTROLLER_ADDRESS'])
            resolver_address = w3.to_checksum_address(self.CONFIG['RESOLVER'])
        except ValueError as e:
            self.log(f"{Fore.RED}[Wallet #{index+1} | Attempt {reg_index}] Invalid contract or resolver address in configuration: {e}{Style.RESET_ALL}")
            with self.processed_lock:
                self.failed_count += 1
                self.current_tasks_processed += 1
            return

        domain_registered = False
        name = self.random_name()

        wallet_log_prefix = f"Wallet #{index+1} ({owner_address[:6]}...{owner_address[-4:]}) | Attempt {reg_index} | {name}.phrs"

        try:
            balance_wei = w3.eth.get_balance(owner_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            self.log(f"{Fore.GREEN}[{wallet_log_prefix}] Current Balance: {balance_eth:.4f} ETH{Style.RESET_ALL}")
        except Exception as e:
            self.log(f"{Fore.YELLOW}[{wallet_log_prefix}] Could not fetch balance: {e}{Style.RESET_ALL}")

        while retry < MAX_RETRY:
            try:
                controller = w3.eth.contract(address=controller_address, abi=self.CONTROLLER_ABI)
                
                secret = HexBytes(os.urandom(32))
                
                self.log(f"{Fore.CYAN}Starting registration for {wallet_log_prefix}...{Style.RESET_ALL}")

                self.log(f"{Fore.BLUE}COMMIT {wallet_log_prefix} - Creating commitment...{Style.RESET_ALL}")
                commitment = controller.functions.makeCommitment(
                    name,
                    owner_address,
                    self.CONFIG['DURATION'],
                    secret,
                    resolver_address,
                    self.CONFIG['DATA'],
                    self.CONFIG['REVERSE_RECORD'],
                    self.CONFIG['OWNER_CONTROLLED_FUSES']
                ).call()
                
                self.log(f"{Fore.BLUE}COMMIT {wallet_log_prefix} - Sending transaction...{Style.RESET_ALL}")
                tx_commit = controller.functions.commit(commitment).build_transaction({
                    'from': owner_address,
                    'nonce': w3.eth.get_transaction_count(owner_address),
                    'gas': 200000,
                    'gasPrice': w3.eth.gas_price,
                    'chainId': self.CONFIG['CHAIN_ID']
                })
                
                signed_tx_commit = account.sign_transaction(tx_commit)
                
                try:
                    tx_hash_commit = w3.eth.send_raw_transaction(signed_tx_commit.raw_transaction)
                except AttributeError as e:
                    self.log(f"{Fore.RED}[CRITICAL] Failed to access raw_transaction for {wallet_log_prefix}: {e}{Style.RESET_ALL}")
                    raise
                except ValueError as e: 
                     if "nonce" in str(e).lower() or "transaction already in pool" in str(e).lower():
                         self.log(f"{Fore.YELLOW}Nonce error or transaction already in pool for {wallet_log_prefix}, retrying with new nonce.{Style.RESET_ALL}")
                         tx_commit['nonce'] = w3.eth.get_transaction_count(owner_address) 
                         signed_tx_commit = account.sign_transaction(tx_commit) 
                         tx_hash_commit = w3.eth.send_raw_transaction(signed_tx_commit.raw_transaction) 
                     else:
                         raise 

                receipt_commit = w3.eth.wait_for_transaction_receipt(tx_hash_commit)
                
                if receipt_commit.status == 1:
                    self.log(f"{Fore.GREEN}COMMIT {wallet_log_prefix} - Successful! TX Hash: {tx_hash_commit.hex()}{Style.RESET_ALL}")
                else:
                    self.log(f"{Fore.RED}COMMIT {wallet_log_prefix} - Failed. TX Hash: {tx_hash_commit.hex()}{Style.RESET_ALL}")
                    raise Exception("Commitment transaction failed.")

                self.log(f"{Fore.YELLOW}WAITING 60 seconds for {wallet_log_prefix}...{Style.RESET_ALL}")
                time.sleep(60)

                self.log(f"{Fore.BLUE}REGISTER {wallet_log_prefix} - Calculating rent price...{Style.RESET_ALL}")
                price = controller.functions.rentPrice(name, self.CONFIG['DURATION']).call()
                value = price[0] + price[1]
                self.log(f"{Fore.GREEN}REGISTER {wallet_log_prefix} - Rent price: {w3.from_wei(value, 'ether')} ETH.{Style.RESET_ALL}")

                self.log(f"{Fore.BLUE}REGISTER {wallet_log_prefix} - Sending transaction...{Style.RESET_ALL}")
                tx_register = controller.functions.register(
                    name,
                    owner_address,
                    self.CONFIG['DURATION'],
                    secret,
                    resolver_address,
                    self.CONFIG['DATA'],
                    self.CONFIG['REVERSE_RECORD'],
                    self.CONFIG['OWNER_CONTROLLED_FUSES']
                ).build_transaction({
                    'from': owner_address,
                    'nonce': w3.eth.get_transaction_count(owner_address),
                    'gas': 300000,
                    'gasPrice': w3.eth.gas_price,
                    'value': value,
                    'chainId': self.CONFIG['CHAIN_ID']
                })
                
                signed_tx_register = account.sign_transaction(tx_register)

                try:
                    tx_hash_register = w3.eth.send_raw_transaction(signed_tx_register.raw_transaction)
                except AttributeError as e:
                    self.log(f"{Fore.RED}[CRITICAL] Failed to access raw_transaction for {wallet_log_prefix}: {e}{Style.RESET_ALL}")
                    raise 
                except ValueError as e: 
                     if "nonce" in str(e).lower() or "transaction already in pool" in str(e).lower():
                         self.log(f"{Fore.YELLOW}Nonce error or transaction already in pool for {wallet_log_prefix}, retrying with new nonce.{Style.RESET_ALL}")
                         tx_register['nonce'] = w3.eth.get_transaction_count(owner_address) 
                         signed_tx_register = account.sign_transaction(tx_register) 
                         tx_hash_register = w3.eth.send_raw_transaction(signed_tx_register.raw_transaction) 
                     else:
                         raise 
                
                receipt_register = w3.eth.wait_for_transaction_receipt(tx_hash_register)
                
                if receipt_register.status == 1:
                    self.log(f"{Fore.GREEN}✅ REGISTER {wallet_log_prefix} - SUCCESS! Domain {name}.phrs Registered! TX Hash: {tx_hash_register.hex()}{Style.RESET_ALL}")
                    domain_registered = True
                    break
                else:
                    self.log(f"{Fore.RED}REGISTER {wallet_log_prefix} - FAILED. TX Hash: {tx_hash_register.hex()}{Style.RESET_ALL}")
                    raise Exception("Registration transaction failed.")

            except Exception as err:
                retry += 1
                msg = str(err)[:150] + '...' if len(str(err)) > 150 else str(err)
                self.log(f"{Fore.YELLOW}Error processing {wallet_log_prefix}: {msg} - retrying ({retry}/{MAX_RETRY}) in 60 seconds...{Style.RESET_ALL}")
                time.sleep(60)
                    
        with self.processed_lock:
            if domain_registered:
                self.success_count += 1
            else:
                self.failed_count += 1
            self.current_tasks_processed += 1
        
        self.print_progress()

    def print_progress(self):
        """Display progress statistics"""
        self.clear_terminal()
        self.welcome()
        
        print(f"{Fore.CYAN + Style.BRIGHT}╔══════════════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}                           {Fore.YELLOW + Style.BRIGHT}📊 REGISTRATION PROGRESS 📊{Style.RESET_ALL}                            {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}╠══════════════════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Total Tasks:{Style.RESET_ALL} {Fore.BLUE + Style.BRIGHT}{self.total_tasks:>6}{Style.RESET_ALL}     {Fore.WHITE + Style.BRIGHT}Completed:{Style.RESET_ALL} {Fore.GREEN + Style.BRIGHT}{self.current_tasks_processed:>6}{Style.RESET_ALL}/{Fore.BLUE + Style.BRIGHT}{self.total_tasks}{Style.RESET_ALL}               {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Successful:{Style.RESET_ALL} {Fore.GREEN + Style.BRIGHT}{self.success_count:>6}{Style.RESET_ALL}     {Fore.WHITE + Style.BRIGHT}Failed:{Style.RESET_ALL}    {Fore.RED + Style.BRIGHT}{self.failed_count:>6}{Style.RESET_ALL}                   {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        
        # Progress bar
        progress = (self.current_tasks_processed / self.total_tasks * 100) if self.total_tasks > 0 else 0
        filled = int(progress // 2)
        bar = "█" * filled + "░" * (50 - filled)
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Progress:{Style.RESET_ALL}  [{Fore.GREEN + Style.BRIGHT}{bar}{Style.RESET_ALL}] {progress:>5.1f}%                  {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print()

    def show_menu(self):
        """Display main menu"""
        print()
        print(f"{Fore.CYAN + Style.BRIGHT}╔═══════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}      {Fore.YELLOW + Style.BRIGHT}🚀 PHAROS ENS REGISTRATION BOT 🚀{Style.RESET_ALL}       {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}╠═══════════════════════════════════════╣{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}  {Fore.GREEN + Style.BRIGHT}[1]{Style.RESET_ALL} Run with Private Proxy             {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}  {Fore.RED + Style.BRIGHT}[2]{Style.RESET_ALL} Run without Proxy                {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}  {Fore.MAGENTA + Style.BRIGHT}[0]{Style.RESET_ALL} Exit                              {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}╚═══════════════════════════════════════╝{Style.RESET_ALL}")
        print()

    async def main(self):
        """Main bot execution"""
        self.show_menu()

        while True:
            try:
                choice = input(f"{Fore.YELLOW + Style.BRIGHT}Select option: {Style.RESET_ALL}").strip()
                
                if choice == '0':
                    self.log(f"{Fore.YELLOW}Exiting bot...{Style.RESET_ALL}")
                    return
                elif choice in ['1', '2']:
                    break
                else:
                    self.log(f"{Fore.RED}Invalid option. Please choose 1, 2, or 0.{Style.RESET_ALL}")
            except KeyboardInterrupt:
                self.log(f"{Fore.YELLOW}Bot interrupted by user{Style.RESET_ALL}")
                return

        use_proxy_option = choice
        
        proxy_list = []
        if use_proxy_option == '1':
            raw_proxy_list = self.load_file_lines("proxy.txt")
            if not raw_proxy_list:
                self.log(f"{Fore.YELLOW}No proxies found in 'proxy.txt'. Running without proxy.{Style.RESET_ALL}")
                use_proxy_option = '2'
            else:
                self.log(f"{Fore.GREEN}Testing {len(raw_proxy_list)} proxies...{Style.RESET_ALL}")
                proxy_test_workers = min(len(raw_proxy_list), os.cpu_count() * 2 if os.cpu_count() else 10)
                if proxy_test_workers == 0 and len(raw_proxy_list) > 0:
                     proxy_test_workers = 1 

                if proxy_test_workers > 0:
                    with ThreadPoolExecutor(max_workers=proxy_test_workers) as executor:
                        tested_proxies_results = list(executor.map(self.test_proxy, raw_proxy_list))
                    proxy_list = [p for p, success in tested_proxies_results if success]
                
                if not proxy_list:
                    self.log(f"{Fore.YELLOW}No working proxies found. Running without proxy.{Style.RESET_ALL}")
                    use_proxy_option = '2'
                else:
                    self.log(f"{Fore.GREEN}{len(proxy_list)} working proxies loaded{Style.RESET_ALL}")

        pk_list = self.load_file_lines("accounts.txt")
        
        if not pk_list:
            self.log(f"{Fore.RED}No private keys found in 'accounts.txt'. Please check the file.{Style.RESET_ALL}")
            input("Press Enter to exit...")
            return

        self.log(f"{Fore.GREEN}Loaded {len(pk_list)} accounts{Style.RESET_ALL}")

        try:
            reg_per_key = int(input(f"{Fore.CYAN + Style.BRIGHT}Domains per account: {Style.RESET_ALL}").strip())
            if reg_per_key <= 0:
                raise ValueError
        except (ValueError, KeyboardInterrupt):
            self.log(f"{Fore.RED}Invalid input or interrupted{Style.RESET_ALL}")
            return
        
        try:
            max_concurrency = int(input(f"{Fore.CYAN + Style.BRIGHT}Thread count: {Style.RESET_ALL}").strip())
            if max_concurrency <= 0:
                raise ValueError
        except (ValueError, KeyboardInterrupt):
            self.log(f"{Fore.RED}Invalid input or interrupted{Style.RESET_ALL}")
            return

        self.success_count = 0
        self.failed_count = 0
        self.current_tasks_processed = 0

        tasks_to_process = [(pk, idx, i + 1) for idx, pk in enumerate(pk_list) for i in range(reg_per_key)]
        random.shuffle(tasks_to_process)
        self.total_tasks = len(tasks_to_process)

        self.print_progress()

        self.log(f"{Fore.GREEN}Starting ENS registration: {len(pk_list)} accounts, {self.total_tasks} total domains{Style.RESET_ALL}")
        
        try:
            with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
                futures = []
                for pk, idx, reg_idx in tasks_to_process:
                    chosen_proxy = None
                    if use_proxy_option == '1' and proxy_list:
                        chosen_proxy = random.choice(proxy_list)
                    
                    futures.append(executor.submit(self.register_domain_single_task, pk, idx, reg_idx, chosen_proxy))
                
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        self.log(f"{Fore.RED}Task error: {e}{Style.RESET_ALL}")
        except KeyboardInterrupt:
            self.log(f"{Fore.YELLOW}Bot stopped by user{Style.RESET_ALL}")
        except Exception as e:
            self.log(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")

        self.print_progress()
        self.log(f"{Fore.GREEN}Registration completed!{Style.RESET_ALL}")
        input("Press Enter to exit...")

    async def run(self):
        """Main entry point for the bot"""        
        while True:
            try:
                await self.main()
                break
            except Exception as err:
                self.log(f"{Fore.RED}Fatal error: {str(err)}{Style.RESET_ALL}")
                self.log(f"{Fore.YELLOW}Restarting in 60 seconds...{Style.RESET_ALL}")
                await asyncio.sleep(60)


if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)
    
    # Initialize and run the bot
    bot = PharosENSBot()
    
    # Initial welcome screen
    bot.clear_terminal()
    bot.welcome()
    
    asyncio.run(bot.run())