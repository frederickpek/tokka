import asyncio
import logging
from consts import RPC_URL
from util.RedisClient import RedisClient
from loader.web3_loader.Web3TxnLoader import Web3TxnLoader
from loader.web3_loader.Web3TxnVerifier import Web3TxnVerifier
from loader.etherscan_loader.EtherscanTxnLoader import EtherscanTxnLoader
from web3 import AsyncWeb3, AsyncHTTPProvider


class LoaderProgram:
    def __init__(self):
        self.redis = RedisClient()
        self.web3_loader = Web3TxnLoader()
        self.web3_verifier = Web3TxnVerifier()
        self.etherscan_loader = EtherscanTxnLoader()
        self.web3_client = AsyncWeb3(AsyncHTTPProvider(RPC_URL))
        self.last_processed_block_number = None
        self.refresh_sec = 10

    async def process_invalid_hash(hash: str):
        pass

    async def process_valid_hash(hash: str, transaction: dict):
        pass

    async def process_hash(self, hash: str):
        transaction = await self.web3_loader.get_transaction(hash)
        valid_transaction = await self.web3_verifier.verify_transaction(transaction)
        if valid_transaction:
            logging.info(f"valid transaction -- {hash}")
            await self.process_valid_hash(hash)
        else:
            logging.info(f"invalid transaction -- {hash}")
            await self.process_invalid_hash(hash)

    async def process_transactions(self, transactions: list[dict]):
        for txn in transactions:
            hash = str(txn["hash"]).lower()
            gas_price = int(txn["gasPrice"])
            gas_used = int(txn["gasUsed"])
            cost_in_wei = gas_used * gas_price
            cost_in_eth = self.web3_client.from_wei(cost_in_wei, "ether")
            logging.info(f"{hash=}, {cost_in_eth=}")

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
