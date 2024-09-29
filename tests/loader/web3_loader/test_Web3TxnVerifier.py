from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from loader.web3_loader.Web3TxnVerifier import Web3TxnVerifier
from consts import ETH_UNISWAPV3_USDC_ETH_POOL_ADDR
from web3 import AsyncWeb3


class TestWeb3TxnVerifier(IsolatedAsyncioTestCase):
    hash = "0x0"

    def setUp(self):
        self.web3_client = AsyncWeb3()
        self.web3_verifier = Web3TxnVerifier(self.web3_client)

    async def test_verify_transaction_receipt_null(self):
        self.assertFalse(await self.web3_verifier.verify_transaction_receipt(None))
        self.assertFalse(
            await self.web3_verifier.verify_transaction_receipt({"logs": list()})
        )

    async def test_verify_transaction_receipt_valid(self):
        def MockByte(hexadecimal: str):
            mock_byte = MagicMock()
            mock_byte.hex = MagicMock(return_value=hexadecimal)
            return mock_byte

        txn_receipt = {
            "logs": [
                {
                    "topics": [
                        MockByte("notTransferEventSig"),
                        MockByte("1" * 64),
                        MockByte("1" * 64),
                    ]
                },
                {
                    "topics": [
                        MockByte(self.web3_verifier.transfer_event_sig),
                        MockByte("1" * 64),
                        MockByte("0" * 22 + ETH_UNISWAPV3_USDC_ETH_POOL_ADDR),
                    ]
                },
            ]
        }

        self.assertTrue(
            await self.web3_verifier.verify_transaction_receipt(txn_receipt)
        )

    async def test_verify_transaction_receipt_invalid(self):
        def MockByte(hexadecimal: str):
            mock_byte = MagicMock()
            mock_byte.hex = MagicMock(return_value=hexadecimal)
            return mock_byte

        txn_receipt = {
            "logs": [
                {
                    "topics": [
                        MockByte("notTransferEventSig"),
                        MockByte("1" * 64),
                        MockByte("0" * 22 + ETH_UNISWAPV3_USDC_ETH_POOL_ADDR),
                    ]
                }
            ]
        }

        self.assertFalse(
            await self.web3_verifier.verify_transaction_receipt(txn_receipt)
        )
