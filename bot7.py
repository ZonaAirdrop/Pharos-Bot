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

from colorama import init, Fore, Style
from datetime import datetime
import asyncio

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
    BRIGHT_YELLOW = Fore.LIGHTYELLOW_EX
    BRIGHT_RED = Fore.LIGHTRED_EX
    BRIGHT_CYAN = Fore.LIGHTCYAN_EX
    BRIGHT_MAGENTA = Fore.LIGHTMAGENTA_EX
    BRIGHT_WHITE = Fore.LIGHTWHITE_EX
    BRIGHT_BLACK = Fore.LIGHTBLACK_EX

class CustomLogger:
    @staticmethod
    def log(label, symbol, msg, color):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {color}[{symbol}] {msg}{Colors.RESET}")

    @staticmethod
    def info(msg): CustomLogger.log("INFO", "✓", msg, Colors.GREEN)
    @staticmethod
    def warn(msg): CustomLogger.log("WARN", "!", msg, Colors.YELLOW)
    @staticmethod
    def error(msg): CustomLogger.log("ERR", "✗", msg, Colors.RED)
    @staticmethod
    def success(msg): CustomLogger.log("OK", "+", msg, Colors.GREEN)
    @staticmethod
    def loading(msg): CustomLogger.log("LOAD", "⟳", msg, Colors.CYAN)
    @staticmethod
    def step(msg): CustomLogger.log("STEP", "➤", msg, Colors.WHITE)
    @staticmethod
    def commit_action(msg): CustomLogger.log("COMMIT", "↪️", msg, Colors.CYAN)
    @staticmethod
    def register_success(msg): CustomLogger.log("REGISTER", "✅", msg, Colors.BRIGHT_GREEN)

logger = CustomLogger()

CONFIG = {
    'RPC_URL': "https://testnet.dplabs-internal.com",
    'CONTROLLER_ADDRESS': "0x51be1ef20a1fd5179419738fc71d95a8b6f8a175",
    'DURATION': 31536000,
    'RESOLVER': "0x9a43dcA1C3BB268546b98eb2AB1401bFc5b58505",
    'DATA': [],
    'REVERSE_RECORD': True,
    'OWNER_CONTROLLED_FUSES': 0,
    'CHAIN_ID': 688688
}

CONTROLLER_ABI = [
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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_file_lines(filename: str) -> List[str]:
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"File '{filename}' not found.")
        return []

def random_name(length: int = 9) -> str:
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


def test_proxy(proxy: str) -> Tuple[str, bool]:
    try:
        response = requests.get('https://api.ipify.org', proxies={'http': proxy, 'https': proxy}, timeout=5)
        return proxy, response.status_code == 200
    except (requests.RequestException, HTTPError) as e:
        logger.warn(f"Proxy {proxy} failed to test: {e}") 
        return proxy, False

def create_web3_instance(proxy: str = None) -> Web3:
    if proxy:
        session = requests.Session()
        session.proxies = {'http': proxy, 'https': proxy}
        return Web3(HTTPProvider(CONFIG['RPC_URL'], session=session))
    return Web3(HTTPProvider(CONFIG['RPC_URL']))

def validate_private_key(private_key: str) -> bool:
    if private_key.startswith('0x'):
        private_key = private_key[2:]
    if len(private_key) != 64 or not all(c in string.hexdigits for c in private_key):
        return False
    return True

success_count = 0
failed_count = 0
total_tasks = 0
current_tasks_processed = 0
processed_lock = threading.Lock() 

def register_domain_single_task(private_key: str, index: int, reg_index: int, proxy: str = None) -> None:
    global success_count, failed_count, current_tasks_processed

    MAX_RETRY = 5
    retry = 0
    
    if not validate_private_key(private_key):
        logger.error(f"[Wallet #{index+1} | Attempt {reg_index}] Invalid private key, skipping registration.")
        with processed_lock:
            failed_count += 1
            current_tasks_processed += 1
        return

    w3 = create_web3_instance(proxy)
    
    try:
        account = Account.from_key(private_key)
        owner_address = account.address
        controller_address = w3.to_checksum_address(CONFIG['CONTROLLER_ADDRESS'])
        resolver_address = w3.to_checksum_address(CONFIG['RESOLVER'])
    except ValueError as e:
        logger.error(f"[Wallet #{index+1} | Attempt {reg_index}] Invalid contract or resolver address in configuration: {e}")
        with processed_lock:
            failed_count += 1
            current_tasks_processed += 1
        return

    domain_registered = False
    name = random_name()

    wallet_log_prefix = f"Wallet #{index+1} ({owner_address[:6]}...{owner_address[-4:]}) | Attempt {reg_index} | {name}.phrs"

    try:
        balance_wei = w3.eth.get_balance(owner_address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        logger.info(f"[{wallet_log_prefix}] Current Balance: {balance_eth:.4f} ETH")
    except Exception as e:
        logger.warn(f"[{wallet_log_prefix}] Could not fetch balance: {e}")


    while retry < MAX_RETRY:
        try:
            controller = w3.eth.contract(address=controller_address, abi=CONTROLLER_ABI)
            
            secret = HexBytes(os.urandom(32))
            
            logger.step(f"Starting registration for {wallet_log_prefix}...")

            logger.commit_action(f"COMMIT {wallet_log_prefix} - Creating commitment...")
            commitment = controller.functions.makeCommitment(
                name,
                owner_address,
                CONFIG['DURATION'],
                secret,
                resolver_address,
                CONFIG['DATA'],
                CONFIG['REVERSE_RECORD'],
                CONFIG['OWNER_CONTROLLED_FUSES']
            ).call()
            
            logger.commit_action(f"COMMIT {wallet_log_prefix} - Sending transaction...")
            tx_commit = controller.functions.commit(commitment).build_transaction({
                'from': owner_address,
                'nonce': w3.eth.get_transaction_count(owner_address),
                'gas': 200000,
                'gasPrice': w3.eth.gas_price,
                'chainId': CONFIG['CHAIN_ID']
            })
            
            signed_tx_commit = account.sign_transaction(tx_commit)
            
            try:
                tx_hash_commit = w3.eth.send_raw_transaction(signed_tx_commit.raw_transaction)
            except AttributeError as e:
                logger.error(f"[CRITICAL] Failed to access raw_transaction for {wallet_log_prefix}: {e}")
                raise
            except ValueError as e: 
                 if "nonce" in str(e).lower() or "transaction already in pool" in str(e).lower():
                     logger.warn(f"Nonce error or transaction already in pool for {wallet_log_prefix}, retrying with new nonce.")
                     tx_commit['nonce'] = w3.eth.get_transaction_count(owner_address) 
                     signed_tx_commit = account.sign_transaction(tx_commit) 
                     tx_hash_commit = w3.eth.send_raw_transaction(signed_tx_commit.raw_transaction) 
                 else:
                     raise 

            receipt_commit = w3.eth.wait_for_transaction_receipt(tx_hash_commit)
            
            if receipt_commit.status == 1:
                logger.info(f"COMMIT {wallet_log_prefix} - Successful! TX Hash: {tx_hash_commit.hex()}")
            else:
                logger.error(f"COMMIT {wallet_log_prefix} - Failed. TX Hash: {tx_hash_commit.hex()}")
                raise Exception("Commitment transaction failed.")

            logger.loading(f"WAITING 60 seconds for {wallet_log_prefix}...")
            time.sleep(60)

            logger.step(f"REGISTER {wallet_log_prefix} - Calculating rent price...")
            price = controller.functions.rentPrice(name, CONFIG['DURATION']).call()
            value = price[0] + price[1]
            logger.info(f"REGISTER {wallet_log_prefix} - Rent price: {w3.from_wei(value, 'ether')} ETH.")

            logger.step(f"REGISTER {wallet_log_prefix} - Sending transaction...")
            tx_register = controller.functions.register(
                name,
                owner_address,
                CONFIG['DURATION'],
                secret,
                resolver_address,
                CONFIG['DATA'],
                CONFIG['REVERSE_RECORD'],
                CONFIG['OWNER_CONTROLLED_FUSES']
            ).build_transaction({
                'from': owner_address,
                'nonce': w3.eth.get_transaction_count(owner_address),
                'gas': 300000,
                'gasPrice': w3.eth.gas_price,
                'value': value,
                'chainId': CONFIG['CHAIN_ID']
            })
            
            signed_tx_register = account.sign_transaction(tx_register)

            try:
                tx_hash_register = w3.eth.send_raw_transaction(signed_tx_register.raw_transaction)
            except AttributeError as e:
                logger.error(f"[CRITICAL] Failed to access raw_transaction for {wallet_log_prefix}: {e}")
                raise 
            except ValueError as e: 
                 if "nonce" in str(e).lower() or "transaction already in pool" in str(e).lower():
                     logger.warn(f"Nonce error or transaction already in pool for {wallet_log_prefix}, retrying with new nonce.")
                     tx_register['nonce'] = w3.eth.get_transaction_count(owner_address) 
                     signed_tx_register = account.sign_transaction(tx_register) 
                     tx_hash_register = w3.eth.send_raw_transaction(signed_tx_register.raw_transaction) 
                 else:
                     raise 
            
            receipt_register = w3.eth.wait_for_transaction_receipt(tx_hash_register)
            
            if receipt_register.status == 1:
                logger.register_success(f"REGISTER {wallet_log_prefix} - SUCCESS! Domain {name}.phrs Registered! TX Hash: {tx_hash_register.hex()}")
                domain_registered = True
                break
            else:
                logger.error(f"REGISTER {wallet_log_prefix} - FAILED. TX Hash: {tx_hash_register.hex()}")
                raise Exception("Registration transaction failed.")

        except Exception as err:
            retry += 1
            msg = str(err)[:150] + '...' if len(str(err)) > 150 else str(err)
            logger.warn(f"Error processing {wallet_log_prefix}: {msg} - retrying ({retry}/{MAX_RETRY}) in 60 seconds...")
            time.sleep(60)
                
    with processed_lock:
        if domain_registered:
            success_count += 1
        else:
            failed_count += 1
        current_tasks_processed += 1
    
    print_progress()

def print_progress():
    clear_screen()
    current_time_str = datetime.now().strftime("%H:%M:%S %d.%m.%y")
    
    print(f"""
{Colors.BRIGHT_GREEN}{Colors.BOLD}
[ WARDEN BOT ]
{current_time_str}

Automated Protocol Utility
by {Colors.BRIGHT_WHITE}@ZonaAirdrop{Colors.BRIGHT_GREEN}

Total Tasks: {total_tasks}
Success: {success_count}
Failed: {failed_count}
Processed: {current_tasks_processed}/{total_tasks}
{Colors.RESET}
""")

async def display_welcome_screen():
    clear_screen()
    now = datetime.now()
    box_width = 40
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}")
    print("  ╔" + "═" * (box_width - 2) + "╗")
    print(f"  ║{' ' * ((box_width - 2 - len('P H A R O S  B O T')) // 2)}P H A R O S  B O T{' ' * ((box_width - 2 - len('P H A R O S  B O T')) // 2 + (1 if (box_width - 2 - len('P H A R O S  B O T')) % 2 != 0 else 0))}║")
    print("  ║" + " " * (box_width - 2) + "║")
    
    time_str = now.strftime('%H:%M:%S %d.%m.%Y')
    print(f"  ║{' ' * ((box_width - 2 - len(time_str)) // 2)}{Colors.YELLOW}{time_str}{Colors.BRIGHT_GREEN}{' ' * ((box_width - 2 - len(time_str)) // 2 + (1 if (box_width - 2 - len(time_str)) % 2 != 0 else 0))}║")
    print("  ║" + " " * (box_width - 2) + "║")

    monad_str = "PHAROS TESTNET AUTOMATION"
    print(f"  ║{' ' * ((box_width - 2 - len(monad_str)) // 2)}{monad_str}{' ' * ((box_width - 2 - len(monad_str)) % 2 != 0)}║") # Adjusted for correct spacing
    
    dev_str = "ZonaAirdrop | t.me/ZonaAirdr0p"
    print(f"  ║{' ' * ((box_width - 2 - len(dev_str) + len(Colors.BRIGHT_WHITE) + len(Colors.BRIGHT_GREEN) + len(Colors.RESET)) // 2)}{Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}   |  t.me/ZonaAirdr0p{' ' * ((box_width - 2 - len(dev_str) + len(Colors.BRIGHT_WHITE) + len(Colors.BRIGHT_GREEN) + len(Colors.RESET)) // 2 + (1 if (box_width - 2 - len(dev_str) + len(Colors.BRIGHT_WHITE) + len(Colors.BRIGHT_GREEN) + len(Colors.RESET)) % 2 != 0 else 0))}║")
    print("  ╚" + "═" * (box_width - 2) + "╝")
    print(f"{Colors.RESET}")

def main():
    global success_count, failed_count, total_tasks, current_tasks_processed

    asyncio.run(display_welcome_screen())

    box_width = 38
    
    print(f"{Colors.BRIGHT_WHITE}")
    print("  ╔" + "═" * (box_width - 2) + "╗")
    print(f"  ║ {Colors.BRIGHT_GREEN}[1] Run with Private Proxy{' ' * (box_width - 2 - len('[1] Run with Private Proxy'))}║")
    print(f"  ║ {Colors.BRIGHT_RED}[2] Run without Proxy{' ' * (box_width - 2 - len('[2] Run without Proxy'))}║")
    print("  ╚" + "═" * (box_width - 2) + "╝")
    print(f"{Colors.RESET}")


    use_proxy_option = input(f"{Colors.BRIGHT_CYAN}Choose an option (1 or 2): {Colors.RESET}").strip()
    
    proxy_list = []
    if use_proxy_option == '1':
        raw_proxy_list = load_file_lines("proxy.txt")
        if not raw_proxy_list:
            logger.warn("No proxies found in 'proxy.txt'. Running without proxy.")
            use_proxy_option = '2'
        else:
            logger.info(f"Testing {len(raw_proxy_list)} proxies found...")
            proxy_test_workers = min(len(raw_proxy_list), os.cpu_count() * 2 if os.cpu_count() else 10)
            if proxy_test_workers == 0 and len(raw_proxy_list) > 0:
                 proxy_test_workers = 1 

            if proxy_test_workers > 0:
                with ThreadPoolExecutor(max_workers=proxy_test_workers) as executor:
                    tested_proxies_results = list(executor.map(test_proxy, raw_proxy_list))
                proxy_list = [p for p, success in tested_proxies_results if success]
            
            if not proxy_list:
                logger.warn("No functional proxies found from 'proxy.txt'. Bot will run without proxy.")
                use_proxy_option = '2'
            else:
                logger.info(f"{len(proxy_list)} functional proxies will be used.")

    pk_list = load_file_lines("accounts.txt")
    
    if not pk_list:
        logger.error("No private keys found in 'accounts.txt'. Ensure the file exists and contains private keys.")
        input("Press Enter to exit...")
        return

    logger.info(f"Total Accounts found: {len(pk_list)}")

    reg_per_key_str = input(f"{Colors.BRIGHT_CYAN}How many domains do you want to generate per account? (e.g., 1): {Colors.RESET}").strip()
    try:
        CONFIG['REG_PER_KEY'] = int(reg_per_key_str)
        if CONFIG['REG_PER_KEY'] <= 0:
            raise ValueError
    except ValueError:
        logger.error("Invalid input. The number of domains must be a positive integer.")
        input("Press Enter to exit...")
        return
    
    max_concurrency_str = input(f"{Colors.BRIGHT_CYAN}Enter max threads/concurrency (e.g., 1 for sequential flow, >1 for parallel across accounts/tasks): {Colors.RESET}").strip()
    try:
        CONFIG['MAX_CONCURRENCY'] = int(max_concurrency_str)
        if CONFIG['MAX_CONCURRENCY'] <= 0:
            raise ValueError
    except ValueError:
        logger.error("Invalid input. The number of threads must be a positive integer.")
        input("Press Enter to exit...")
        return

    success_count = 0
    failed_count = 0
    current_tasks_processed = 0

    tasks_to_process = [(pk, idx, i + 1) for idx, pk in enumerate(pk_list) for i in range(CONFIG['REG_PER_KEY'])]
    random.shuffle(tasks_to_process)
    total_tasks = len(tasks_to_process)

    print_progress()

    logger.info(f"Starting domain registration for {len(pk_list)} accounts, total {total_tasks} registrations.")
    
    try:
        with ThreadPoolExecutor(max_workers=CONFIG['MAX_CONCURRENCY']) as executor:
            futures = []
            for pk, idx, reg_idx in tasks_to_process:
                chosen_proxy = None
                if use_proxy_option == '1' and proxy_list:
                    chosen_proxy = random.choice(proxy_list)
                
                futures.append(executor.submit(register_domain_single_task, pk, idx, reg_idx, chosen_proxy))
            
            # Wait for all futures to complete or for KeyboardInterrupt
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Fatal error in one of the tasks: {e}. Bot may need to be restarted.")
    except KeyboardInterrupt:
        logger.warn("Bot interrupted by user (Ctrl+C). Shutting down gracefully...")
        # No need for manual thread shutdown here, ThreadPoolExecutor handles it
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

    print_progress()
    logger.info("All domain registration tasks completed or bot was interrupted!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.CRITICAL) 
    
    clear_screen()
    logger.info("Domain registration bot started. Ensure 'accounts.txt' and 'proxy.txt' (optional) are available.")
    while True:
        try:
            main()
            break
        except Exception as err:
            logger.error(f"A FATAL unhandled error occurred in the main function: {str(err)}")
            logger.info("Waiting 60 seconds before trying all processes again...")
            time.sleep(60)
