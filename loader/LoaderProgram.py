import asyncio
from loader.TransactionLoader import TransactionLoader
from loader.TransactionVerifier import TransactionVerifier


class LoaderProgram:
    def __init__(self):
        self.loader = TransactionLoader()
        self.verifier = TransactionVerifier()
        self.refresh_sec = 5

    async def loop(self):
        while True:
            try:
                hash = ""
                transaction = await self.loader.get_transaction(hash)
                valid_transaction = await self.verifier.verify_transaction(transaction)
                if valid_transaction:
                    print("valid transaction")
                else:
                    print("invalid transaction")
            except Exception as err:
                pass
            await asyncio.sleep(self.refresh_sec)
