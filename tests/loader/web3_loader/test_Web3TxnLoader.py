from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock
from loader.web3_loader.Web3TxnLoader import Web3TxnLoader
from web3.exceptions import TransactionNotFound


class TestWeb3TxnLoader(IsolatedAsyncioTestCase):
    hash = "0x0"

    def setUp(self):
        self.web3_client = AsyncMock()
        self.web3_loader = Web3TxnLoader(self.web3_client)

    async def test_get_transaction_receipt(self):
        mock_txn_receipt = MagicMock()
        self.web3_client.eth.get_transaction_receipt = AsyncMock(
            return_value=mock_txn_receipt
        )
        txn_receipt = await self.web3_loader.get_transaction_receipt(self.hash)
        self.assertEqual(txn_receipt, mock_txn_receipt)

    async def test_get_transaction_receipt_transaction_not_found(self):
        async def raises(hash):
            raise TransactionNotFound(hash)

        self.web3_client.eth.get_transaction_receipt = AsyncMock(side_effect=raises)
        txn_receipt = await self.web3_loader.get_transaction_receipt(self.hash)
        self.assertEqual(txn_receipt, None)

    async def test_get_transaction_receipt_transaction_error_raises(self):
        async def raises(hash):
            raise ValueError(hash)

        self.web3_client.eth.get_transaction_receipt = AsyncMock(side_effect=raises)
        with self.assertRaises(ValueError):
            await self.web3_loader.get_transaction_receipt(self.hash)
