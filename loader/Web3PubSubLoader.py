import json
import logging
from consts import ETH_UNISWAPV3_USDC_ETH_POOL_ADDR
from loader.web3_loader.Web3TxnLoader import Web3TxnLoader
from loader.web3_loader.Web3TxnVerifier import Web3TxnVerifier
from loader.BaseLoader import BaseLoader
from web3.types import TxReceipt
from aioredis.client import PubSub


class Web3PubSubLoader(BaseLoader):
    def __init__(self):
        self.web3_loader = Web3TxnLoader(self.web3_client)
        self.web3_verifier = Web3TxnVerifier(self.web3_client)
        self.refresh_sec = 0.1
        self.pubsub: PubSub = None

    async def process_valid_hash(self, hash: str, txn_receipt: TxReceipt):
        gas_used = int(txn_receipt["gasUsed"])
        gas_price = float(self.wei_to_ether(txn_receipt["effectiveGasPrice"]))
        block = await self.web3_client.eth.get_block(txn_receipt["blockNumber"])
        timestamp = block["timestamp"]
        eth_usdt_price = await self.get_eth_usdt_price(timestamp)
        gas_in_usdt = gas_used * gas_price * eth_usdt_price
        await self.publish_gas(hash, gas_in_usdt)
        logging.info(f"adhoc valid hash processed {hash=}, {gas_in_usdt=}")

    async def process_invalid_hash(self, hash: str):
        """
        Hash is either not involved with uniswapv3 eth/usdc pool
        or is a valid hash value but non-existant,
        if such a hash appears in manual scanning, it will be overwritten
        """
        await self.publish_gas(hash, "non uniswapv3 pool txn")

    async def process_hash(self, hash: str):
        txn_receipt = await self.web3_loader.get_transaction_receipt(hash)
        is_valid_transaction = await self.web3_verifier.verify_transaction_receipt(
            txn_receipt
        )
        if is_valid_transaction:
            await self.process_valid_hash(hash, txn_receipt)
        else:
            await self.process_invalid_hash(hash)

    async def prepare(self):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(ETH_UNISWAPV3_USDC_ETH_POOL_ADDR)
        self.pubsub = pubsub
        logging.info(f"subcribed to channel {ETH_UNISWAPV3_USDC_ETH_POOL_ADDR}")

    async def loop_fn(self):
        msg = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
        if not msg:
            return
        hash = json.loads(msg["data"].decode())
        logging.info(f"Received message: {hash}")
        # avoided batch to prevent spamming rpc node...
        await self.process_hash(hash)
