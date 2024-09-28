import asyncio


class Web3TxnVerifier:
    @staticmethod
    async def verify_transaction(hash: str) -> bool:
        await asyncio.sleep(1)
        return True
