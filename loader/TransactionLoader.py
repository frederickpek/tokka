import asyncio


class TransactionLoader:
    @staticmethod
    async def get_transaction(hash: str) -> dict:
        await asyncio.sleep(1)
        return dict()
