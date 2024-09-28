import asyncio


class Web3TxnLoader:
    @staticmethod
    async def get_transaction(hash: str) -> dict:
        await asyncio.sleep(1)
        return dict()
