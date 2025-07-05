from web3 import Web3
from eth_utils import to_hex
from eth_abi.abi import encode
from eth_account import Account
from eth_account.messages import encode_defunct
from aiohttp import ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, random, secrets, json, time, os, pytz

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
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api.pharosnetwork.xyz"
        self.RPC_URL = "https://testnet.dplabs-internal.com"
        self.WPHRS_CONTRACT_ADDRESS = "0x76aaaDA469D23216bE5f7C596fA25F282Ff9b364"
        self.USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
        self.USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
        self.SWAP_ROUTER_ADDRESS = "0xbc3813206c3cb99347c96a18a757ed39386d12b8"
        self.POSITION_MANAGER_ADDRESS = "0x7ec504ae0771ec2aa1900f117e609868d0650043"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"deposit","stateMutability":"payable","inputs":[],"outputs":[]},
            {"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"wad","type":"uint256"}],"outputs":[]}
        ]''')
        self.SWAP_CONTRACT_ABI = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "bytes[]", "name": "data", "type": "bytes[]"}
                ],
                "name": "multicall",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        self.ADD_LP_CONTRACT_ABI = [
            {
                "inputs": [
                    {
                        "components": [
                            { "internalType": "address", "name": "token0", "type": "address" },
                            { "internalType": "address", "name": "token1", "type": "address" },
                            { "internalType": "uint24", "name": "fee", "type": "uint24" },
                            { "internalType": "int24", "name": "tickLower", "type": "int24" },
                            { "internalType": "int24", "name": "tickUpper", "type": "int24" },
                            { "internalType": "uint256", "name": "amount0Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount0Min", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Min", "type": "uint256" },
                            { "internalType": "address", "name": "recipient", "type": "address" },
                            { "internalType": "uint256", "name": "deadline", "type": "uint256" },
                        ],
                        "internalType": "struct INonfungiblePositionManager.MintParams",
                        "name": "params",
                        "type": "tuple",
                    },
                ],
                "name": "mint",
                "outputs": [
                    { "internalType": "uint256", "name": "tokenId", "type": "uint256" },
                    { "internalType": "uint128", "name": "liquidity", "type": "uint128" },
                    { "internalType": "uint256", "name": "amount0", "type": "uint256" },
                    { "internalType": "uint256", "name": "amount1", "type": "uint256" },
                ],
                "stateMutability": "payable",
                "type": "function"
            }
        ]

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\n" + "═" * 60)
        print(Fore.GREEN + Style.BRIGHT + "    ⚡ Pharos X Zentrafi Tesnet ⚡")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.YELLOW + Style.BRIGHT + "    Team : Zonaairdrop")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.RED + Style.BRIGHT + "   Channel telegram : @ZonaAirdr0p")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.MAGENTA + Style.BRIGHT + "   Powered by Zonaairdrop")
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

    def generate_signature(self, privkey: str):
        try:
            encoded_message = encode_defunct(text="pharos")
            signed_message = Account.sign_message(encoded_message, private_key=privkey)
            return to_hex(signed_message.signature)
        except Exception:
            return None

    async def get_web3(self):
        return Web3(Web3.HTTPProvider(self.RPC_URL))

    async def approving_token(self, privkey, address, spender, contract_addr, amount):
        web3 = await self.get_web3()
        spender = web3.to_checksum_address(spender)
        contract = web3.eth.contract(address=web3.to_checksum_address(contract_addr), abi=self.ERC20_CONTRACT_ABI)
        decimals = contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        allowance = contract.functions.allowance(address, spender).call()
        if allowance < amount_wei:
            tx = contract.functions.approve(spender, 2**256-1).build_transaction({
                "from": address,
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "gas": 60000,
                "maxFeePerGas": web3.to_wei(1, "gwei"),
                "maxPriorityFeePerGas": web3.to_wei(1, "gwei"),
                "chainId": web3.eth.chain_id
            })
            signed = web3.eth.account.sign_transaction(tx, privkey)
            web3.eth.send_raw_transaction(signed.raw_transaction)
            await asyncio.sleep(5)

    async def perform_wrapped(self, privkey, address, amount, wrap=True):
        web3 = await self.get_web3()
        contract = web3.eth.contract(address=web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS), abi=self.ERC20_CONTRACT_ABI)
        amount_wei = web3.to_wei(amount, "ether")
        if wrap:
            tx = contract.functions.deposit().build_transaction({
                "from": address,
                "value": amount_wei,
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "gas": 70000,
                "maxFeePerGas": web3.to_wei(1, "gwei"),
                "maxPriorityFeePerGas": web3.to_wei(1, "gwei"),
                "chainId": web3.eth.chain_id
            })
        else:
            tx = contract.functions.withdraw(amount_wei).build_transaction({
                "from": address,
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "gas": 70000,
                "maxFeePerGas": web3.to_wei(1, "gwei"),
                "maxPriorityFeePerGas": web3.to_wei(1, "gwei"),
                "chainId": web3.eth.chain_id
            })
        signed = web3.eth.account.sign_transaction(tx, privkey)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        return web3.to_hex(tx_hash)

    async def perform_swap(self, privkey, address, from_token, to_token, amount):
        web3 = await self.get_web3()
        await self.approving_token(privkey, address, self.SWAP_ROUTER_ADDRESS, from_token, amount)
        token_contract = web3.eth.contract(address=web3.to_checksum_address(from_token), abi=self.ERC20_CONTRACT_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        encoded_data = encode(
            ["address", "address", "uint256", "address", "uint256", "uint256", "uint256"],
            [
                web3.to_checksum_address(from_token),
                web3.to_checksum_address(to_token),
                500,
                web3.to_checksum_address(address),
                amount_wei,
                0,
                0
            ]
        )
        multicall_data = [b'\x04\xe4\x5a\xaf' + encoded_data]
        swap_contract = web3.eth.contract(address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), abi=self.SWAP_CONTRACT_ABI)
        deadline = int(time.time()) + 300
        swap_tx = swap_contract.functions.multicall(deadline, multicall_data)
        tx = swap_tx.build_transaction({
            "from": address,
            "nonce": web3.eth.get_transaction_count(address, "pending"),
            "gas": 350000,
            "maxFeePerGas": web3.to_wei(1, "gwei"),
            "maxPriorityFeePerGas": web3.to_wei(1, "gwei"),
            "chainId": web3.eth.chain_id
        })
        signed = web3.eth.account.sign_transaction(tx, privkey)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        return web3.to_hex(tx_hash)

    async def perform_add_liquidity(self, privkey, address, token0, token1, amount0, amount1):
        web3 = await self.get_web3()
        await self.approving_token(privkey, address, self.POSITION_MANAGER_ADDRESS, token0, amount0)
        await self.approving_token(privkey, address, self.POSITION_MANAGER_ADDRESS, token1, amount1)
        token0_contract = web3.eth.contract(address=web3.to_checksum_address(token0), abi=self.ERC20_CONTRACT_ABI)
        token1_contract = web3.eth.contract(address=web3.to_checksum_address(token1), abi=self.ERC20_CONTRACT_ABI)
        amount0_desired = int(amount0 * (10 ** token0_contract.functions.decimals().call()))
        amount1_desired = int(amount1 * (10 ** token1_contract.functions.decimals().call()))
        mint_params = {
            "token0": web3.to_checksum_address(token0),
            "token1": web3.to_checksum_address(token1),
            "fee": 500,
            "tickLower": -887270,
            "tickUpper": 887270,
            "amount0Desired": amount0_desired,
            "amount1Desired": amount1_desired,
            "amount0Min": 0,
            "amount1Min": 0,
            "recipient": web3.to_checksum_address(address),
            "deadline": int(time.time()) + 600
        }
        contract = web3.eth.contract(address=web3.to_checksum_address(self.POSITION_MANAGER_ADDRESS), abi=self.ADD_LP_CONTRACT_ABI)
        lp_tx = contract.functions.mint(mint_params)
        tx = lp_tx.build_transaction({
            "from": address,
            "nonce": web3.eth.get_transaction_count(address, "pending"),
            "gas": 400000,
            "maxFeePerGas": web3.to_wei(1, "gwei"),
            "maxPriorityFeePerGas": web3.to_wei(1, "gwei"),
            "chainId": web3.eth.chain_id
        })
        signed = web3.eth.account.sign_transaction(tx, privkey)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        return web3.to_hex(tx_hash)

    async def run(self):
        with open('accounts.txt', 'r') as file:
            accounts = [line.strip() for line in file if line.strip()]
        self.welcome()
        # Input simple interactive
        try:
            wrap_count = int(input("Berapa kali Wrapped atau Unwrapped? (contoh: 5): "))
        except:
            wrap_count = 5
        try:
            swap_count = int(input("Berapa kali Swap? (contoh: 5): "))
        except:
            swap_count = 5
        try:
            addlp_count = int(input("Berapa kali Add Liquidity? (contoh: 5): "))
        except:
            addlp_count = 5
        try:
            min_delay = int(input("Min delay antar TX (detik): "))
        except:
            min_delay = 10
        try:
            max_delay = int(input("Max delay antar TX (detik): "))
        except:
            max_delay = 30

        for priv in accounts:
            address = self.generate_address(priv)
            self.log(f"Mulai {self.mask_account(address)}")
            # WRAP/UNWRAP (random)
            for i in range(wrap_count):
                wrap_type = random.choice(["wrap", "unwrap"])
                amount = round(random.uniform(0.001, 0.01), 4)
                tx_hash = await self.perform_wrapped(priv, address, amount, wrap=(wrap_type=="wrap"))
                self.log(f"{wrap_type.title()} {i+1} Explorer: https://testnet.pharosscan.xyz/tx/{tx_hash} Complete")
                await asyncio.sleep(random.randint(min_delay, max_delay))
            # SWAP (random choice)
            swap_pairs = [
                (self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, "WPHRS", "USDC"),
                (self.USDC_CONTRACT_ADDRESS, self.WPHRS_CONTRACT_ADDRESS, "USDC", "WPHRS"),
                (self.USDT_CONTRACT_ADDRESS, self.WPHRS_CONTRACT_ADDRESS, "USDT", "WPHRS"),
                (self.WPHRS_CONTRACT_ADDRESS, self.USDT_CONTRACT_ADDRESS, "WPHRS", "USDT"),
            ]
            for i in range(swap_count):
                from_token, to_token, from_ticker, to_ticker = random.choice(swap_pairs)
                amount = round(random.uniform(0.001, 0.01), 4)
                tx_hash = await self.perform_swap(priv, address, from_token, to_token, amount)
                self.log(f"Swap {i+1} {from_ticker}→{to_ticker} Explorer: https://testnet.pharosscan.xyz/tx/{tx_hash} Completed")
                await asyncio.sleep(random.randint(min_delay, max_delay))
            # ADD LP
            addlp_pairs = [
                (self.WPHRS_CONTRACT_ADDRESS, self.USDT_CONTRACT_ADDRESS, "WPHRS", "USDT"),
                (self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, "WPHRS", "USDC"),
            ]
            for i in range(addlp_count):
                token0, token1, tk0, tk1 = random.choice(addlp_pairs)
                amount0 = round(random.uniform(0.001, 0.01), 4)
                amount1 = round(random.uniform(0.001, 0.01), 4)
                tx_hash = await self.perform_add_liquidity(priv, address, token0, token1, amount0, amount1)
                self.log(f"Add LP {i+1} {tk0}/{tk1} Explorer: https://testnet.pharosscan.xyz/tx/{tx_hash} Completed")
                await asyncio.sleep(random.randint(min_delay, max_delay))
            self.log("="*50 + f" Selesai untuk {self.mask_account(address)} " + "="*50)

if __name__ == "__main__":
    try:
        bot = PharosTestnet()
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Pharos Testnet - BOT{Style.RESET_ALL}                                       "                              
        )
