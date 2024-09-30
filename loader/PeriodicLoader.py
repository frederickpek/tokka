import asyncio
import logging
from consts import ETH_FINALITY_BLOCKS
from loader.BaseLoader import BaseLoader
from loader.etherscan_loader.EtherscanTxnLoader import EtherscanTxnLoader


class PeriodicLoader(BaseLoader):
    def __init__(self):
        self.etherscan_loader = EtherscanTxnLoader()
        self.last_processed_block_number = None

    async def process_etherscan_transaction(self, hash: str, txn: dict):
        gas_used = int(txn["gasUsed"])
        gas_price = int(txn["gasPrice"])
        timestamp = int(txn["timeStamp"])
        cost_in_wei = gas_used * gas_price
        gas_in_eth = self.wei_to_ether(cost_in_wei)
        eth_usdt_price = await self.get_eth_usdt_price(timestamp)
        gas_in_usdt = gas_in_eth * eth_usdt_price
        await self.publish_gas(hash, gas_in_usdt)
        logging.info(f"periodic loop processed {hash=}, {gas_in_usdt=}")

    async def get_latest_block_number(self) -> int:
        """
        Lag `ETH_FINALITY_BLOCKS` blocks behind for
        etherscan api to backfill unfinalized blocks
        """
        latest_block = await self.web3_client.eth.get_block("latest")
        return latest_block["number"] - ETH_FINALITY_BLOCKS

    async def get_block_range(self):
        latest_block_number = await self.get_latest_block_number()
        if self.last_processed_block_number:
            start_block = min(latest_block_number, self.last_processed_block_number + 1)
        else:
            start_block = latest_block_number
        return start_block, latest_block_number

    async def loop_fn(self):
        start_block, end_block = await self.get_block_range()
        if start_block == self.last_processed_block_number:
            return
        transactions = await self.etherscan_loader.get_transactions(
            start_block=start_block, end_block=end_block
        )

        # filter duplicate hashes
        hash_to_transactions = dict()
        for txn in transactions:
            hash = str(txn["hash"]).lower()
            hash_to_transactions[hash] = txn

        logging.info(
            f"Loaded {len(hash_to_transactions)} unique hashes form {start_block=} to {end_block=}"
        )

        await asyncio.gather(
            *[
                self.process_etherscan_transaction(hash, txn)
                for hash, txn in hash_to_transactions.items()
            ]
        )
        self.last_processed_block_number = end_block
