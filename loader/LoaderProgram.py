import asyncio
import logging
from consts import RPC_URL, ETH_UNISWAPV3_USDC_ETH_POOL_ADDR
from util import is_valid_tx_hash
from util.RedisClient import RedisClient
from loader.web3_loader.Web3TxnLoader import Web3TxnLoader
from loader.web3_loader.Web3TxnVerifier import Web3TxnVerifier
from loader.etherscan_loader.EtherscanTxnLoader import EtherscanTxnLoader
from loader.BinancePriceApi import BinancePriceApi
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.types import TxReceipt


class LoaderProgram:
    def __init__(self):
        self.redis = RedisClient()
        self.bn_api = BinancePriceApi()
        self.etherscan_loader = EtherscanTxnLoader()
        self.web3_client = AsyncWeb3(AsyncHTTPProvider(RPC_URL))
        self.web3_loader = Web3TxnLoader(self.web3_client)
        self.web3_verifier = Web3TxnVerifier(self.web3_client)
        self.last_processed_block_number = None
        self.refresh_sec = 10

    async def process_valid_hash(self, hash: str, txn_receipt: TxReceipt):
        gas_in_eth = float(
            self.web3_client.from_wei(txn_receipt["effectiveGasPrice"], "ether")
        )
        block = await self.web3_client.eth.get_block(txn_receipt["blockNumber"])
        timestamp = block["timestamp"]
        eth_usdt_price = await self.bn_api.get_eth_usdt_price(
            timestamp=int(timestamp * 1000)
        )
        gas_in_usdt = gas_in_eth * eth_usdt_price
        await self.redis.hset_json(
            ETH_UNISWAPV3_USDC_ETH_POOL_ADDR, hash.lower(), gas_in_usdt
        )
        logging.info(f"valid hash processed {hash=}, {gas_in_usdt=}")

    async def process_hash(self, hash: str):
        if not is_valid_tx_hash(hash):
            logging.info(f"skip invalid {hash=}")
            return
        txn_receipt = await self.web3_loader.get_transaction_receipt(hash)
        is_valid_transaction = await self.web3_verifier.verify_transaction_receipt(
            txn_receipt
        )
        if is_valid_transaction:
            await self.process_valid_hash(hash, txn_receipt)

    async def process_etherscan_transaction(self, hash: str, txn: dict):
        gas_price = int(txn["gasPrice"])
        gas_used = int(txn["gasUsed"])
        timestamp = int(txn["timeStamp"])
        cost_in_wei = gas_used * gas_price
        gas_in_eth = float(self.web3_client.from_wei(cost_in_wei, "ether"))
        eth_usdt_price = await self.bn_api.get_eth_usdt_price(
            timestamp=int(timestamp * 1000)
        )
        gas_in_usdt = gas_in_eth * eth_usdt_price
        await self.redis.hset_json(
            ETH_UNISWAPV3_USDC_ETH_POOL_ADDR, hash.lower(), gas_in_usdt
        )
        logging.info(f"periodic loop processed {hash=}, {gas_in_usdt=}")

    async def get_latest_block_number(self) -> int:
        latest_block = await self.web3_client.eth.get_block("latest")
        return latest_block["number"]

    async def periodic_loop(self):
        """
        Periodically loads any new transactions from uniswapv3 eth/usdc pool
        """
        while True:
            try:
                latest_block_number = await self.get_latest_block_number()
                if self.last_processed_block_number:
                    start_block = min(
                        self.last_processed_block_number + 1, latest_block_number
                    )
                else:
                    start_block = latest_block_number

                transactions = await self.etherscan_loader.get_transactions(
                    start_block=start_block, end_block=latest_block_number
                )

                # filter duplicate hashes
                hash_to_transactions = dict()
                for txn in transactions:
                    hash = str(txn["hash"]).lower()
                    if hash in hash_to_transactions:
                        continue
                    hash_to_transactions[hash] = txn

                logging.info(
                    f"Loaded {len(hash_to_transactions)} unique hashes form {start_block=} to {latest_block_number=}"
                )

                await asyncio.gather(
                    *[
                        self.process_etherscan_transaction(hash, txn)
                        for hash, txn in hash_to_transactions.items()
                    ]
                )
                self.last_processed_block_number = latest_block_number
            except Exception as err:
                logging.exception(err)
            await asyncio.sleep(self.refresh_sec)
