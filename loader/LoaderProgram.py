import asyncio
from util.RedisClient import RedisClient
from loader.TransactionLoader import TransactionLoader
from loader.TransactionVerifier import TransactionVerifier


class LoaderProgram:
    def __init__(self):
        self.redis = RedisClient()
        self.loader = TransactionLoader()
        self.verifier = TransactionVerifier()
        self.refresh_sec = 5

    async def process_invalid_hash(hash: str):
        pass

    async def process_valid_hash(hash: str, transaction: dict):
        pass

    async def process_hash(self, hash: str):
        transaction = await self.loader.get_transaction(hash)
        valid_transaction = await self.verifier.verify_transaction(transaction)
        if valid_transaction:
            print(f"valid transaction -- {hash}")
            await self.process_valid_hash(hash)
        else:
            print(f"invalid transaction -- {hash}")
            await self.process_invalid_hash(hash)

    async def loop(self):
        while True:
            try:
                hash = "0x0"
                self.process_hash(hash)
            except Exception as err:
                pass
            await asyncio.sleep(self.refresh_sec)
