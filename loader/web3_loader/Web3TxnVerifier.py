import asyncio
from web3 import AsyncWeb3
from consts import ETH_UNISWAPV3_USDC_ETH_POOL_ADDR
from web3.types import TxReceipt


class Web3TxnVerifier:

    """
    Class to verify if txn_receipt provided corresponds to
    transactions involving the ethereum univ3 eth/usdc pool
    """

    def __init__(self, web3_client: AsyncWeb3):
        self.web3_client = web3_client
        self.transfer_event_sig = web3_client.keccak(
            text="Transfer(address,address,uint256)"
        ).hex()

    async def verify_transaction_receipt(self, txn_receipt: TxReceipt) -> bool:
        if not txn_receipt or not txn_receipt.get("logs"):
            return False
        for log in txn_receipt.get("logs"):
            if log["topics"][0].hex() != self.transfer_event_sig:
                continue
            from_address = self.web3_client.to_checksum_address(
                "0x" + log["topics"][1].hex()[24:]
            )
            to_address = self.web3_client.to_checksum_address(
                "0x" + log["topics"][2].hex()[24:]
            )
            if (
                from_address == ETH_UNISWAPV3_USDC_ETH_POOL_ADDR
                or to_address == ETH_UNISWAPV3_USDC_ETH_POOL_ADDR
            ):
                return True
        return False
