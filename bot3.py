import requests
import time
import random
import websocket
import json
import pytz
from datetime import datetime
from web3 import Web3
from eth_account import Account
from colorama import Fore, Style, init
from functools import wraps
from supabase import create_client
import os
import asyncio
from dotenv import load_dotenv

init(autoreset=True)
load_dotenv()

# === Terminal Color Setup ===
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
    def action(msg): Logger.log("ACTION", "✓", msg, Colors.CYAN) # Changed emoji to checkmark
    @staticmethod
    def actionSuccess(msg): Logger.log("ACTION", "✓", msg, Colors.GREEN) # Changed emoji to checkmark

logger = Logger()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

async def display_welcome_screen():
    clear_console()
    now = datetime.now()
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}")
    print("  ╔══════════════════════════════════════╗")
    print("  ║           Brokex   B O T            ║")
    print("  ║                                      ║")
    print(f"  ║     {Colors.YELLOW}{now.strftime('%H:%M:%S %d.%m.%Y')}{Colors.BRIGHT_GREEN}           ║")
    print("  ║                                      ║")
    print("  ║     Pharos TESTNET AUTOMATION         ║")
    print(f"  ║   {Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}   |   t.me/ZonaAirdr0p   ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    await asyncio.sleep(1)

class BrokexBot:
    def __init__(self, private_key=None):
        self.private_key = private_key
        self.account = Account.from_key(private_key) if private_key else None
        self.wallet_address = self.account.address if self.account else None
        self.RPC_URL = "https://testnet.dplabs-internal.com"
        self.CHAIN_ID = 688688
        self.MAX_RETRIES = 5
        self.RETRY_BASE_DELAY = 2
        self.USDT_ADDRESS = Web3.to_checksum_address("0x78ac5e2d8a78a8b8e6d10c7b7274b03c10c91cef")
        self.BROKEX_ADDRESS = Web3.to_checksum_address("0xde897635870b3dd2e097c09f1cd08841dbc3976a")
        self.LIQUIDITY_CONTRACT_ADDRESS = Web3.to_checksum_address("0x9a88d07850723267db386c681646217af7e220d7")
        self.ROUTER_CONTRACT = Web3.to_checksum_address("0x50576285bd33261dee1ad99bf766cd8249520a58")
        self.ORACLE_PROOF_URL = "https://proofcrypto-production.up.railway.app/proof?pairs={}"
        self.USDT_DECIMALS = 6
        self.MIN_USDT_BALANCE = 10
        self.MAX_UINT256 = 2**256 - 1
        self.GAS_LIMIT = 300000
        self.GAS_PRICE = Web3.to_wei(5, 'gwei')
        self.WEBSOCKET_URL = "wss://wss-production-9302.up.railway.app"
        self.SUPABASE_URL = "https://yaikidiqvtxiqtrawvgf.supabase.co"
        self.SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhaWtpZGlxdnR4aXF0cmF3dmdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3MDI3MzcsImV4cCI6MjA1OTI3ODczN30.z2gZvFpA5HMIODCpjXJFNX0amE3V5MqAgJSrIr7jS1Y"
        self.STALE_ORDER_DEVIATION_PCT = 15
        self.nonce_cache = {}
        self.asset_data = {}
        self.USDT_ABI = json.loads('[{"constant":true,"inputs":[{"name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"}]')
        self.BROKEX_ABI = json.loads('[{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getUserOpenIds","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"id","type":"uint256"}],"name":"getOpenById","outputs":[{"components":[{"internalType":"address","name":"trader","type":"address"},{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"uint256","name":"assetIndex","type":"uint256"},{"internalType":"bool","name":"isLong","type":"bool"},{"internalType":"uint256","name":"leverage","type":"uint256"},{"internalType":"uint256","name":"openPrice","type":"uint256"},{"internalType":"uint256","name":"sizeUsd","type":"uint256"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"uint256","name":"stopLossPrice","type":"uint256"},{"internalType":"uint256","name":"takeProfitPrice","type":"uint256"},{"internalType":"uint256","name":"liquidationPrice","type":"uint256"}],"internalType":"struct IBrokexStorage.Open","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"assetIndex","type":"uint256"},{"internalType":"bool","name":"isLong","type":"bool"},{"internalType":"uint256","name":"leverage","type":"uint256"},{"internalType":"uint256","name":"orderPrice","type":"uint256"},{"internalType":"uint256","name":"sizeUsd","type":"uint256"},{"internalType":"uint256","name":"stopLoss","type":"uint256"},{"internalType":"uint256","name":"takeProfit","type":"uint256"}],"name":"placeOrder","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getUserOrderIds","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"id","type":"uint256"}],"name":"getOrderById","outputs":[{"components":[{"internalType":"address","name":"trader","type":"address"},{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"uint256","name":"assetIndex","type":"uint256"},{"internalType":"bool","name":"isLong","type":"bool"},{"internalType":"uint256","name":"leverage","type":"uint256"},{"internalType":"uint256","name":"orderPrice","type":"uint256"},{"internalType":"uint256","name":"sizeUsd","type":"uint256"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"uint256","name":"stopLoss","type":"uint256"},{"internalType":"uint256","name":"takeProfit","type":"uint256"},{"internalType":"uint256","name":"limitBucketId","type":"uint256"}],"internalType":"struct IBrokexStorage.Order","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"assetIndex","type":"uint256"},{"internalType":"bytes","name":"proof","type":"bytes"},{"internalType":"bool","name":"isLong","type":"bool"},{"internalType":"uint256","name":"leverage","type":"uint256"},{"internalType":"uint256","name":"sizeUsd","type":"uint256"},{"internalType":"uint256","name":"stopLoss","type":"uint256"},{"internalType":"uint256","name":"takeProfit","type":"uint256"}],"name":"openPosition","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"openId","type":"uint256"},{"internalType":"bytes","name":"proof","type":"bytes"}],"name":"closePosition","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"orderId","type":"uint256"}],"name":"cancelOrder","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
        self.LIQUIDITY_ABI = json.loads('[{"inputs":[{"internalType":"uint256","name":"usdtAmount","type":"uint256"}],"name":"depositLiquidity","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"lpAmount","type":"uint256"}],"name":"withdrawLiquidity","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getLpPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')
        self.CLAIM_ABI = json.loads('[{"name":"claim","type":"function","stateMutability":"nonpayable","inputs":[],"outputs":[]}]')
        self.supabase = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_banner(self):
        # The banner is removed as per the request
        pass

    @staticmethod
    def with_retry(max_retries, base_delay):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(1, max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        logger.warn(f"[Retry {attempt}/{max_retries}] Error: {e}")
                        if attempt == max_retries:
                            raise
                        sleep_time = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                        logger.warn(f"Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
            return wrapper
        return decorator

    @with_retry(max_retries=5, base_delay=2)
    def connect_web3(self):
        web3 = Web3(Web3.HTTPProvider(self.RPC_URL))
        if not web3.is_connected():
            raise Exception("Failed to connect to RPC")
        return web3

    @with_retry(max_retries=5, base_delay=2)
    def wait_tx_receipt_and_status(self, web3, tx_hash):
        logger.loading(f"Waiting tx receipt: 0x{tx_hash.hex()} ...")
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        if receipt.status == 1:
            logger.success("TX success")
            return True
        else:
            logger.error("TX failed")
            return False

    @with_retry(max_retries=5, base_delay=2)
    def get_nonce(self, web3, wallet):
        nonce = web3.eth.get_transaction_count(wallet, 'pending')
        self.nonce_cache[wallet] = max(self.nonce_cache.get(wallet, nonce), nonce)
        return self.nonce_cache[wallet]

    @with_retry(max_retries=5, base_delay=2)
    def send_raw_tx(self, web3, signed_tx):
        return web3.eth.send_raw_transaction(signed_tx.raw_transaction)

    @with_retry(max_retries=5, base_delay=2)
    def update_asset_data_from_websocket(self):
        logger.loading("Connecting to WebSocket to update asset data...")
        try:
            ws = websocket.create_connection(self.WEBSOCKET_URL, timeout=15)
            message = ws.recv()
            ws.close()
            payload = json.loads(message)
            temp_data = {}
            for obj in payload.values():
                if obj.get('instruments'):
                    instrument = obj['instruments'][0]
                    asset_id = obj.get('id')
                    price = instrument.get('currentPrice')
                    name = obj.get('name') or instrument.get('tradingPair')
                    if asset_id is not None and price is not None and name:
                        if '/' in name: name = name.upper()
                        temp_data[str(asset_id)] = {"name": name, "price": float(price)}
            if not temp_data:
                raise Exception("Asset data from WebSocket is empty.")
            self.asset_data = temp_data
            logger.success(f"Data for {len(self.asset_data)} assets successfully updated.")
            return True
        except Exception as e:
            logger.error(f"Failed to retrieve data from WebSocket: {e}")
            raise e

    @with_retry(max_retries=5, base_delay=2)
    def get_usdt_balance(self, web3):
        usdt_contract = web3.eth.contract(address=self.USDT_ADDRESS, abi=self.USDT_ABI)
        balance = usdt_contract.functions.balanceOf(self.wallet_address).call()
        return balance / 10**self.USDT_DECIMALS

    @with_retry(max_retries=5, base_delay=2)
    def approve_usdt(self, web3, spender_address):
        usdt_contract = web3.eth.contract(address=self.USDT_ADDRESS, abi=self.USDT_ABI)
        logger.step(f"Approving maximum USDT for spender {spender_address}...")
        nonce = self.get_nonce(web3, self.wallet_address)
        tx = usdt_contract.functions.approve(spender_address, self.MAX_UINT256).build_transaction({
            "chainId": self.CHAIN_ID, "gas": 300000, "gasPrice": self.GAS_PRICE, "nonce": nonce,
        })
        signed_tx = web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.send_raw_tx(web3, signed_tx)
        return self.wait_tx_receipt_and_status(web3, tx_hash)

    @with_retry(max_retries=5, base_delay=2)
    def claim_usdt(self, web3):
        logger.step("Attempting to claim USDT...")
        router_contract = web3.eth.contract(address=self.ROUTER_CONTRACT, abi=self.CLAIM_ABI)
        balance = self.get_usdt_balance(web3)
        if balance >= 1000:
            logger.success(f"Skip claim - USDT balance is sufficient ({balance:.2f}).")
            return True
        nonce = self.get_nonce(web3, self.wallet_address)
        tx = router_contract.functions.claim().build_transaction({
            'from': self.wallet_address, 'nonce': nonce, 'chainId': self.CHAIN_ID, 'gas': self.GAS_LIMIT, 'gasPrice': self.GAS_PRICE,
        })
        signed_tx = web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.send_raw_tx(web3, signed_tx)
        return self.wait_tx_receipt_and_status(web3, tx_hash)

    @with_retry(max_retries=5, base_delay=2)
    def add_liquidity(self, web3):
        usdt_amount_to_add = round(random.uniform(10.1, 15.5), 2)
        logger.step(f"Attempting to add liquidity of {usdt_amount_to_add:.2f} USDT...")
        balance = self.get_usdt_balance(web3)
        if balance < usdt_amount_to_add:
            logger.warn(f"USDT balance ({balance:.2f}) is insufficient. Attempting to claim...")
            if not self.claim_usdt(web3):
                logger.error("Failed to claim USDT. Skipping add liquidity action.")
                return False
            balance = self.get_usdt_balance(web3)
            if balance < usdt_amount_to_add:
                logger.error(f"USDT balance ({balance:.2f}) is still insufficient after claim.")
                return False
        usdt_contract = web3.eth.contract(address=self.USDT_ADDRESS, abi=self.USDT_ABI)
        allowance = usdt_contract.functions.allowance(self.wallet_address, self.LIQUIDITY_CONTRACT_ADDRESS).call()
        if allowance < usdt_amount_to_add * 10**self.USDT_DECIMALS:
            if not self.approve_usdt(web3, self.LIQUIDITY_CONTRACT_ADDRESS):
                return False
            time.sleep(10)
        nonce = self.get_nonce(web3, self.wallet_address)
        tx = web3.eth.contract(address=self.LIQUIDITY_CONTRACT_ADDRESS, abi=self.LIQUIDITY_ABI).functions.depositLiquidity(int(usdt_amount_to_add * 10**self.USDT_DECIMALS)).build_transaction({
            "chainId": self.CHAIN_ID, "gas": 500000, "gasPrice": self.GAS_PRICE, "nonce": nonce,
        })
        signed_tx = web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.send_raw_tx(web3, signed_tx)
        return self.wait_tx_receipt_and_status(web3, tx_hash)

    @with_retry(max_retries=5, base_delay=2)
    def withdraw_liquidity(self, web3):
        liquidity_contract = web3.eth.contract(address=self.LIQUIDITY_CONTRACT_ADDRESS, abi=self.LIQUIDITY_ABI)
        logger.step("Attempting to withdraw some liquidity...")
        lp_balance_wei = liquidity_contract.functions.balanceOf(self.wallet_address).call()
        if lp_balance_wei == 0:
            logger.info("No LP tokens to withdraw.")
            return True
        withdraw_percentage = random.randint(10, 50)
        lp_to_withdraw_wei = (lp_balance_wei * withdraw_percentage) // 100
        logger.info(f"LP Balance: {lp_balance_wei/10**18:.4f}. Will withdraw: {lp_to_withdraw_wei/10**18:.4f} LP ({withdraw_percentage}%)")
        nonce = self.get_nonce(web3, self.wallet_address)
        tx = liquidity_contract.functions.withdrawLiquidity(lp_to_withdraw_wei).build_transaction({
            "chainId": self.CHAIN_ID, "gas": 500000, "gasPrice": self.GAS_PRICE, "nonce": nonce,
        })
        signed_tx = web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.send_raw_tx(web3, signed_tx)
        return self.wait_tx_receipt_and_status(web3, tx_hash)

    @with_retry(max_retries=5, base_delay=2)
    def place_limit_order(self, web3):
        if not self.asset_data:
            logger.error("Asset data not available for limit order.")
            return False
        asset_index_str = random.choice(list(self.asset_data.keys()))
        asset_info = self.asset_data[asset_index_str]
        asset_name, current_price = asset_info["name"], asset_info["price"]
        usd_size_float = round(random.uniform(10.1, 20.5), 2)
        if self.get_usdt_balance(web3) < usd_size_float:
            logger.warn("Insufficient USDT balance for limit order.")
            return False
        is_long = random.choice([True, False])
        leverage = random.randint(2, 10)
        target_price_float = current_price * random.uniform(0.995, 1.005)
        target_price = int(target_price_float * 10**18)
        sl_price = int(target_price * (0.95 if is_long else 1.05))
        tp_price = int(target_price * (1.05 if is_long else 0.95))
        logger.step(f"Placing Limit Order: {asset_name.upper()} | {'LONG' if is_long else 'SHORT'}, Size={usd_size_float:.2f} USDT, Lev={leverage}x, Target=${target_price_float:.4f}")
        if self.get_usdt_balance(web3) < usd_size_float:
             logger.warn("Insufficient USDT balance for limit order.")
             return False
        usdt_contract = web3.eth.contract(address=self.USDT_ADDRESS, abi=self.USDT_ABI)
        allowance = usdt_contract.functions.allowance(self.wallet_address, self.BROKEX_ADDRESS).call()
        if allowance < usd_size_float * 10**self.USDT_DECIMALS:
            if not self.approve_usdt(web3, self.BROKEX_ADDRESS):
                return False
            time.sleep(10)
        nonce = self.get_nonce(web3, self.wallet_address)
        tx = web3.eth.contract(address=self.BROKEX_ADDRESS, abi=self.BROKEX_ABI).functions.placeOrder(
            int(asset_index_str), is_long, leverage, target_price, int(usd_size_float * 10**self.USDT_DECIMALS), sl_price, tp_price
        ).build_transaction({
            "chainId": self.CHAIN_ID, "gas": 1500000, "gasPrice": self.GAS_PRICE, "nonce": nonce,
        })
        signed_tx = web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.send_raw_tx(web3, signed_tx)
        if self.wait_tx_receipt_and_status(web3, tx_hash):
            logger.success(f"Limit Order {asset_name.upper()} successful! Tx: 0x{tx_hash.hex()}")
            return True
        else:
            logger.error(f"Limit Order {asset_name.upper()} failed. Tx: 0x{tx_hash.hex()}")
            return False

    @with_retry(max_retries=5, base_delay=2)
    def open_market_position(self, web3):
        if not self.asset_data:
            logger.error("Asset data not available for market order.")
            return False
        asset_index_str = random.choice(list(self.asset_data.keys()))
        asset_info = self.asset_data[asset_index_str]
        asset_name, current_price = asset_info["name"], asset_info["price"]
        usd_size_float = round(random.uniform(10.1, 20.5), 2)
        if self.get_usdt_balance(web3) < usd_size_float:
            logger.warn("Insufficient USDT balance for market order.")
            return False
        is_long = random.choice([True, False])
        leverage = random.randint(2, 10)
        sl_price = int(current_price * (0.95 if is_long else 1.05) * 10**18)
        tp_price = int(current_price * (1.05 if is_long else 0.95) * 10**18)
        logger.step(f"Opening Market Position: {asset_name.upper()} | {'LONG' if is_long else 'SHORT'}, Size={usd_size_float:.2f} USDT, Lev={leverage}x")
        logger.loading("Oracle: Getting proof...")
        proof_response = requests.get(self.ORACLE_PROOF_URL.format(asset_index_str), timeout=10)
        if proof_response.status_code != 200:
            logger.error(f"Oracle: Failed to get proof, status {proof_response.status_code}")
            return False
        proof = proof_response.json().get('proof')
        if not proof:
            logger.error("Oracle: Proof not found in response.")
            return False
        logger.success("Oracle: Proof successfully obtained.")
        usdt_contract = web3.eth.contract(address=self.USDT_ADDRESS, abi=self.USDT_ABI)
        allowance = usdt_contract.functions.allowance(self.wallet_address, self.BROKEX_ADDRESS).call()
        if allowance < usd_size_float * 10**self.USDT_DECIMALS:
            if not self.approve_usdt(web3, self.BROKEX_ADDRESS):
                return False
            time.sleep(10)
        nonce = self.get_nonce(web3, self.wallet_address)
        tx = web3.eth.contract(address=self.BROKEX_ADDRESS, abi=self.BROKEX_ABI).functions.openPosition(
            int(asset_index_str), bytes.fromhex(proof[2:]), is_long, leverage, int(usd_size_float * 10**self.USDT_DECIMALS), sl_price, tp_price
        ).build_transaction({
            "chainId": self.CHAIN_ID, "gas": 2000000, "gasPrice": self.GAS_PRICE, "nonce": nonce
        })
        signed_tx = web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.send_raw_tx(web3, signed_tx)
        if self.wait_tx_receipt_and_status(web3, tx_hash):
            logger.success(f"Market Position {asset_name.upper()} opened successfully! Tx: 0x{tx_hash.hex()}")
            return True
        else:
            logger.error(f"Market Position {asset_name.upper()} failed. Tx: 0x{tx_hash.hex()}")
            return False

    @with_retry(max_retries=3, base_delay=5)
    def close_position(self, web3, position_id, asset_index):
        logger.step(f"Attempting to close position ID: {position_id}...")
        logger.loading("Oracle: Getting proof to close...")
        proof_response = requests.get(self.ORACLE_PROOF_URL.format(asset_index), timeout=10)
        if proof_response.status_code != 200:
            logger.error(f"Oracle: Failed to get proof, status {proof_response.status_code}")
            return False
        proof = proof_response.json().get('proof')
        if not proof:
            logger.error("Oracle: Proof not found in response.")
            return False
        logger.success("Oracle: Proof successfully obtained.")
        nonce = self.get_nonce(web3, self.wallet_address)
        tx = web3.eth.contract(address=self.BROKEX_ADDRESS, abi=self.BROKEX_ABI).functions.closePosition(
            position_id, bytes.fromhex(proof[2:])
        ).build_transaction({
            "chainId": self.CHAIN_ID, "gas": 2000000, "gasPrice": self.GAS_PRICE, "nonce": nonce
        })
        signed_tx = web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.send_raw_tx(web3, signed_tx)
        if self.wait_tx_receipt_and_status(web3, tx_hash):
            logger.success(f"Position ID {position_id} closed successfully! Tx: 0x{tx_hash.hex()}")
            return True
        else:
            logger.error(f"Failed to close position ID {position_id}. Tx: 0x{tx_hash.hex()}")
            return False

    @with_retry(max_retries=5, base_delay=2)
    def check_and_manage_open_positions(self, web3):
        logger.step("Checking PnL of open positions...")
        brokex_contract = web3.eth.contract(address=self.BROKEX_ADDRESS, abi=self.BROKEX_ABI)
        try:
            open_ids = brokex_contract.functions.getUserOpenIds(self.wallet_address).call()
            if not open_ids:
                logger.info("No open positions to check.")
                return
            for pos_id in open_ids:
                pos = brokex_contract.functions.getOpenById(pos_id).call()
                asset_index, is_long, leverage, open_price_wei, size_usd_wei = pos[2], pos[3], pos[4], pos[5], pos[6]
                asset_str_index = str(asset_index)
                if asset_str_index not in self.asset_data:
                    logger.warn(f"No price data found for asset ID {asset_index}, skipping position.")
                    continue
                asset_name = self.asset_data[asset_str_index].get("name", f"Unknown (ID: {asset_index})")
                current_price = self.asset_data[asset_str_index].get("price")
                open_price = open_price_wei / 10**18
                size_usd = size_usd_wei / 10**self.USDT_DECIMALS
                if current_price == 0 or open_price == 0:
                    logger.warn(f"Invalid price data for asset {asset_name}, skipping position.")
                    continue
                pnl_usd = (current_price / open_price - 1) * size_usd if is_long else (open_price / current_price - 1) * size_usd
                margin = size_usd / leverage
                pnl_percentage = (pnl_usd / margin) * 100 if margin > 0 else 0
                pnl_color = Colors.GREEN if pnl_percentage >= 0 else Colors.RED
                logger.info(f"  - Position {pos_id} [{asset_name}]: Current PnL: {pnl_color}{pnl_percentage:.2f}%{Colors.RESET}")
                if pnl_percentage >= 100:
                    logger.success(f"TAKE PROFIT: PnL for position {pos_id} reached {pnl_percentage:.2f}%! Closing position...")
                    self.close_position(web3, pos_id, asset_index)
                    logger.warn("Pausing for 15 seconds after closing position...")
                    time.sleep(15)
                elif pnl_percentage <= -50:
                    logger.error(f"STOP LOSS: PnL for position {pos_id} reached {pnl_percentage:.2f}%! Closing position...")
                    self.close_position(web3, pos_id, asset_index)
                    logger.warn("Pausing for 15 seconds after closing position...")
                    time.sleep(15)
        except Exception as e:
            logger.error(f"Error while checking PnL: {e}")

    @with_retry(max_retries=5, base_delay=2)
    def cancel_limit_order(self, web3, order_id):
        logger.step(f"Attempting to cancel limit order ID: {order_id}...")
        brokex_contract = web3.eth.contract(address=self.BROKEX_ADDRESS, abi=self.BROKEX_ABI)
        nonce = self.get_nonce(web3, self.wallet_address)
        tx = brokex_contract.functions.cancelOrder(order_id).build_transaction({
            "chainId": self.CHAIN_ID, "gas": 500000, "gasPrice": self.GAS_PRICE, "nonce": nonce
        })
        signed_tx = web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.send_raw_tx(web3, signed_tx)
        if self.wait_tx_receipt_and_status(web3, tx_hash):
            logger.success(f"Order ID {order_id} successfully cancelled! Tx: 0x{tx_hash.hex()}")
            return True
        else:
            logger.error(f"Failed to cancel order ID {order_id}. Tx: 0x{tx_hash.hex()}")
            return False

    @with_retry(max_retries=5, base_delay=2)
    def check_and_cancel_stale_orders(self, web3):
        logger.step("Checking for pending limit orders...")
        brokex_contract = web3.eth.contract(address=self.BROKEX_ADDRESS, abi=self.BROKEX_ABI)
        try:
            order_ids = brokex_contract.functions.getUserOrderIds(self.wallet_address).call()
            if not order_ids:
                logger.info("No pending limit orders.")
                return
            for order_id in order_ids:
                order = brokex_contract.functions.getOrderById(order_id).call()
                asset_index, target_price_wei = order[2], order[5]
                asset_str_index = str(asset_index)
                if asset_str_index not in self.asset_data:
                    logger.warn(f"No price data found for asset ID {asset_index} for order {order_id}, skipping.")
                    continue
                current_price = self.asset_data[asset_str_index].get("price")
                target_price = target_price_wei / 10**18
                if current_price == 0 or target_price == 0:
                    continue
                deviation_pct = (abs(current_price - target_price) / target_price) * 100
                logger.info(f"  - Order {order_id}: Current price deviation is {deviation_pct:.2f}% from target.")
                if deviation_pct > self.STALE_ORDER_DEVIATION_PCT:
                    logger.warn(f"   - Deviation {deviation_pct:.2f}% exceeds threshold ({self.STALE_ORDER_DEVIATION_PCT}%). Cancelling order...")
                    self.cancel_limit_order(web3, order_id)
                    logger.warn("Pausing for 15 seconds after cancelling order...")
                    time.sleep(15)
        except Exception as e:
            logger.error(f"Error while checking limit orders: {e}")

    @with_retry(max_retries=5, base_delay=2)
    def check_my_liquidity(self, web3):
        liquidity_contract = web3.eth.contract(address=self.LIQUIDITY_CONTRACT_ADDRESS, abi=self.LIQUIDITY_ABI)
        lp_balance_wei = liquidity_contract.functions.balanceOf(self.wallet_address).call()
        if lp_balance_wei > 0:
            lp_price_wei = liquidity_contract.functions.getLpPrice().call()
            total_value_usdt = (lp_balance_wei / 10**18) * (lp_price_wei / 10**6)
            logger.info(f"Liquidity Balance: {lp_balance_wei/10**18:.4f} LP (~${total_value_usdt:.2f} USDT)")
        return lp_balance_wei

    @with_retry(max_retries=5, base_delay=2)
    def check_and_join_competition(self, web3):
        response = self.supabase.table('traders').select('address').eq('address', self.wallet_address.lower()).execute()
        if response.data:
            logger.info("Competition Status: Already joined.")
            return True
        logger.step("Competition Status: Not joined. Attempting to join...")
        response = self.supabase.table('traders').insert({'address': self.wallet_address.lower(), 'pnl': 0}).execute()
        if (hasattr(response, 'data') and response.data and response.data[0]['address'] == self.wallet_address.lower()) or (hasattr(response, 'error') and response.error is None):
            logger.success("Successfully joined the competition!")
            return True
        else:
            error_message = response.error.message if hasattr(response, 'error') and response.error else "Unknown error"
            logger.error(f"Failed to join competition: {error_message}")
            return False

    @with_retry(max_retries=3, base_delay=2)
    def check_competition_rank(self):
        logger.step("Checking competition rank and points...")
        try:
            response = self.supabase.table('traders').select('address, pnl').order('pnl', desc=True).execute()
            if not response.data:
                logger.info("Competition leaderboard is empty.")
                return
            leaderboard = response.data
            my_rank = -1
            my_pnl = 0
            for i, trader in enumerate(leaderboard):
                if trader['address'].lower() == self.wallet_address.lower():
                    my_rank = i + 1
                    my_pnl = trader['pnl']
                    break
            if my_rank != -1:
                logger.success(f"Your Rank: #{my_rank} | Points (PnL): {my_pnl:.4f}")
            else:
                logger.info("You are not yet on the competition leaderboard.")
        except Exception as e:
            logger.error(f"Error while checking competition rank: {e}")

    def read_private_keys(self, file_path="accounts.txt"):
        try:
            with open(file_path, 'r') as f:
                keys = [line.strip() for line in f if line.strip()]
                if not keys:
                    logger.error(f"File '{file_path}' is empty or does not contain valid keys.")
                    return []
                logger.success(f"Found {len(keys)} private keys in '{file_path}'.")
                return keys
        except FileNotFoundError:
            logger.error(f"Error: File '{file_path}' not found. Please create the file and populate it with your private keys.")
            return []

    def get_address_from_pk(self, private_key):
        account = Account.from_key(private_key)
        return account.address

    def run(self):
        asyncio.run(display_welcome_screen()) # Display the new welcome screen
        while True:
            self.clear_terminal()
            # self.display_banner() # Banner display is removed

            w3 = None
            for attempt in range(1, self.MAX_RETRIES + 1):
                try:
                    w3 = self.connect_web3()
                    logger.success(f"Connected to chain ID: {self.CHAIN_ID}")
                    break
                except Exception as e:
                    logger.error(f"Failed to connect to RPC on attempt {attempt}/{self.MAX_RETRIES}: {e}")
                    if attempt < self.MAX_RETRIES:
                        delay = self.RETRY_BASE_DELAY * (2 ** (attempt - 1))
                        logger.warn(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error("Max retries reached. Aborting run.")
                        return

            private_keys = self.read_private_keys()
            if not private_keys:
                logger.warn("Program will stop because no private keys were found to process.")
                break

            for index, pk in enumerate(private_keys):
                logger.step("=")
                logger.step(f"Starting process for Account {index + 1}/{len(private_keys)}")
                logger.step("=")

                try:
                    self.wallet_address = self.get_address_from_pk(pk)
                    self.private_key = pk
                    self.account = Account.from_key(pk)
                    logger.info(f"Processing Wallet: {self.wallet_address}")

                    if not self.update_asset_data_from_websocket():
                        logger.error("Failed to retrieve asset data. Skipping Brokex Ecosystem.")
                        continue

                    if self.check_and_join_competition(w3):
                        self.check_competition_rank()

                    balance = self.get_usdt_balance(w3)
                    logger.info(f"USDT Balance: {balance:.4f}")

                    if balance < self.MIN_USDT_BALANCE:
                        logger.warn(f"USDT balance ({balance:.2f}) is insufficient. Attempting to claim...")
                        if not self.claim_usdt(w3):
                            logger.error("Failed to claim USDT. Skipping Brokex Ecosystem.")
                            continue
                        balance = self.get_usdt_balance(w3)
                        logger.info(f"USDT Balance after claim: {balance:.4f}")
                        if balance < self.MIN_USDT_BALANCE:
                            logger.error("Balance still insufficient after claim. Skipping Brokex Ecosystem.")
                            continue

                    logger.step("Initiating initial checks...")
                    self.check_and_manage_open_positions(w3)
                    time.sleep(5)
                    self.check_and_cancel_stale_orders(w3)
                    time.sleep(5)
                    self.check_my_liquidity(w3)

                    logger.step("Starting main action sequence...")
                    core_actions = [
                        ("Open Market Position", self.open_market_position),
                        ("Place Limit Order", self.place_limit_order),
                        ("Open Market Position", self.open_market_position),
                        ("Place Limit Order", self.place_limit_order),
                        ("Open Market Position", self.open_market_position),
                        ("Place Limit Order", self.place_limit_order),
                        ("Open Market Position", self.open_market_position),
                        ("Place Limit Order", self.place_limit_order),
                        ("Open Market Position", self.open_market_position),
                        ("Place Limit Order", self.place_limit_order),
                        ("Add Liquidity", self.add_liquidity)
                    ]
                    random.shuffle(core_actions)
                    actions = core_actions + [("Withdraw Liquidity", self.withdraw_liquidity)]

                    for i, (name, func) in enumerate(actions, 1):
                        logger.action(f"--- Action {i}/{len(actions)}: {name} ---")
                        if func.__name__ == 'withdraw_liquidity':
                            if self.check_my_liquidity(w3) == 0:
                                logger.info("No liquidity to withdraw, skipping action.")
                                continue
                        try:
                            if not func(w3):
                                logger.warn(f"Action '{name}' was not successful, proceeding to next action.")
                        except Exception as e:
                            logger.error(f"Error during action {name}: {e}")
                        if i < len(actions):
                            delay = random.randint(15, 25)
                            logger.warn(f"Pausing for {delay} seconds...")
                            time.sleep(delay)

                    logger.success("Successfully processed Brokex Ecosystem for this wallet.\n")

                except Exception as e:
                    logger.error(f"A fatal error occurred for Account {index + 1}: {e}")
                    logger.warn("Proceeding to the next account...")

                if index < len(private_keys) - 1:
                    inter_account_delay = random.randint(30, 60)
                    logger.step(f"--- Pausing for {inter_account_delay} seconds before switching to next account ---")
                    time.sleep(inter_account_delay)

            w3 = None # Reset w3 connection for the next loop to ensure fresh connection
            
            logger.step("=")
            logger.success("All accounts have been processed.")
            logger.info("Will sleep for 24 hours before restarting...")
            logger.step("=")
            time.sleep(24 * 60 * 60)

if __name__ == "__main__":
    bot = BrokexBot()
    bot.run()
    
