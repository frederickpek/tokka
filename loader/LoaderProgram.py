import asyncio
import logging
from util.RedisClient import RedisClient
from loader.web3_loader.Web3TxnLoader import Web3TxnLoader
from loader.web3_loader.Web3TxnVerifier import Web3TxnVerifier


class LoaderProgram:
    def __init__(self):
        self.redis = RedisClient()
        self.loader = Web3TxnLoader()
        self.verifier = Web3TxnVerifier()
        self.refresh_sec = 5

    async def process_invalid_hash(hash: str):
        pass

    async def process_valid_hash(hash: str, transaction: dict):
        pass

    async def process_hash(self, hash: str):
        transaction = await self.loader.get_transaction(hash)
        valid_transaction = await self.verifier.verify_transaction(transaction)
        if valid_transaction:
            logging.info(f"valid transaction -- {hash}")
            await self.process_valid_hash(hash)
        else:
            logging.info(f"invalid transaction -- {hash}")
            await self.process_invalid_hash(hash)

    async def loop(self):
        while True:
            try:
                hash = "0x0"
                await self.process_hash(hash)
            except Exception as err:
                pass
            await asyncio.sleep(self.refresh_sec)
