from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock
from loader.etherscan_loader.EtherscanApi import EtherscanApi
from consts import ETH_UNISWAPV3_USDC_ETH_POOL_ADDR


class TestEtherscanApi(IsolatedAsyncioTestCase):
    def setUp(self):
        self.api = EtherscanApi("api_key")

    async def test_get_token_transfer_events_by_address(self):
        address = ETH_UNISWAPV3_USDC_ETH_POOL_ADDR
        mock_resp = MagicMock()
        self.api.request = AsyncMock(return_value=mock_resp)
        resp = await self.api.get_token_transfer_events_by_address(address=address)
        self.assertEqual(resp, mock_resp)
        self.assertEqual(self.api.request.call_args.args[0]["address"], address)
