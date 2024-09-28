from web3 import AsyncWeb3
from web3.types import TxReceipt
from typing import Optional
from web3.exceptions import TransactionNotFound, Web3ValueError


class Web3TxnLoader:

    """
    Class to load token transaction receipt given a hash
    """

    def __init__(self, web3_client: AsyncWeb3):
        self.web3_client = web3_client

    async def get_transaction_receipt(self, hash: str) -> Optional[TxReceipt]:
        try:
            txn_receipt = await self.web3_client.eth.get_transaction_receipt(hash)
            return txn_receipt
        except TransactionNotFound:
            return None
