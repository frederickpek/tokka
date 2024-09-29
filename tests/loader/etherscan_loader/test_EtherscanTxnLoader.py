from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock
from loader.etherscan_loader.EtherscanTxnLoader import EtherscanTxnLoader


class TestEtherscanTxnLoader(IsolatedAsyncioTestCase):
    def setUp(self):
        self.etherscan_loader = EtherscanTxnLoader()
        self.etherscan_loader.api = AsyncMock()

    async def test_get_transactions(self):
        mock_result = MagicMock()
        mock_resp = {"result": mock_result}
        self.etherscan_loader.api.get_token_transfer_events_by_address = AsyncMock(
            return_value=mock_resp
        )
        result = await self.etherscan_loader.get_transactions(
            start_block=0, end_block=1
        )
        self.assertEqual(result, mock_result)
