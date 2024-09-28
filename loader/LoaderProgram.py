import asyncio
import logging
from consts import RPC_URL, ETH_UNISWAPV3_USDC_ETH_POOL_ADDR
from util import is_valid_tx_hash
from util.RedisClient import RedisClient
from loader.web3_loader.Web3TxnLoader import Web3TxnLoader
from loader.web3_loader.Web3TxnVerifier import Web3TxnVerifier
from loader.etherscan_loader.EtherscanTxnLoader import EtherscanTxnLoader
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.types import TxReceipt


class LoaderProgram:
    def __init__(self):
        self.redis = RedisClient()
        self.etherscan_loader = EtherscanTxnLoader()
        self.web3_client = AsyncWeb3(AsyncHTTPProvider(RPC_URL))
        self.web3_loader = Web3TxnLoader(self.web3_client)
        self.web3_verifier = Web3TxnVerifier(self.web3_client)
        self.last_processed_block_number = None
        self.refresh_sec = 10

    async def process_valid_hash(self, hash: str, txn_receipt: TxReceipt):
        gas_in_eth = self.web3_client.from_wei(
            txn_receipt["effectiveGasPrice"], "ether"
        )
        block = await self.web3_client.eth.get_block(txn_receipt["blockNumber"])
        timestamp = block["timestamp"]
        payload = {
            "valid": True,
            "timestamp": timestamp,
            "gas_in_eth": gas_in_eth,
        }
        await self.redis.hset_json(
            ETH_UNISWAPV3_USDC_ETH_POOL_ADDR, hash.lower(), payload
        )
        logging.info(f"valid hash processed {hash=}, {payload=}")

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

    async def process_transactions(self, transactions: list[dict]):
        hash_to_payload = dict()
        for txn in transactions:
            hash = str(txn["hash"]).lower()
            if hash in hash_to_payload:
                continue
            gas_price = int(txn["gasPrice"])
            gas_used = int(txn["gasUsed"])
            timestamp = int(txn["timeStamp"])
            cost_in_wei = gas_used * gas_price
            gas_in_eth = self.web3_client.from_wei(cost_in_wei, "ether")
            hash_to_payload[hash] = {
                "valid": True,
                "timestamp": timestamp,
                "gas_in_eth": gas_in_eth,
            }
        await asyncio.gather(
            *[
                self.redis.hset_json(
                    ETH_UNISWAPV3_USDC_ETH_POOL_ADDR, hash.lower(), payload
                )
                for hash, payload in hash_to_payload.items()
            ]
        )
        logging.info(f"published {hash_to_payload=}")

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
                logging.info(
                    f"Loaded {len(transactions)} transactions form {start_block=} to {latest_block_number=}"
                )
                await self.process_transactions(transactions)
                self.last_processed_block_number = latest_block_number
            except Exception as err:
                logging.exception(err)
            await asyncio.sleep(self.refresh_sec)
