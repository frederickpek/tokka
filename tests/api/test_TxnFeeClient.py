from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock
from api.TxnFeeClient import TxnFeeClient


class TestTxnFeeClient(IsolatedAsyncioTestCase):
    valid_hash = "0x0e2bd4576e98193ab1ca2747112bd368daeba64dda3271114671b891e9408828"

    def setUp(self):
        self.client = TxnFeeClient()
        self.client.redis = AsyncMock()
        self.client.retry_times = 1

    async def test_get_fee_response_invalid_hash(self):
        resp = await self.client.get_fee_response("0x0")
        self.assertEqual(resp.msg, "invalid hash")
        self.assertEqual(resp.fee, "")

    async def test_get_fee_response_valid_fee(self):
        mock_fee = 10.750
        self.client.redis.hget_json = AsyncMock(return_value=mock_fee)
        resp = await self.client.get_fee_response(self.valid_hash)
        self.assertEqual(resp.msg, "ok")
        self.assertEqual(float(resp.fee), mock_fee)

    async def test_get_fee_response_non_uniswapv3_pool_txn(self):
        mock_fee = "non uniswapv3 pool txn"
        self.client.redis.hget_json = AsyncMock(return_value=mock_fee)
        resp = await self.client.get_fee_response(self.valid_hash)
        self.assertEqual(resp.msg, mock_fee)
        self.assertEqual(resp.fee, "")

    async def test_get_fee_response_queued(self):
        self.client.redis.hget_json = AsyncMock(return_value=None)
        resp = await self.client.get_fee_response(self.valid_hash)
        self.assertEqual(resp.msg, "queued for processing, query again after some time")
        self.assertEqual(resp.fee, "")

    async def test_get_fee_response_queued_and_processed(self):
        mock_fee = 10.750
        toggle = [False]

        async def hget_json(self, *args, **kwargs):
            if toggle[0]:
                return mock_fee
            toggle[0] = True
            return None

        self.client.redis.hget_json = AsyncMock(side_effect=hget_json)
        resp = await self.client.get_fee_response(self.valid_hash)
        self.assertEqual(resp.msg, "ok")
        self.assertEqual(float(resp.fee), mock_fee)

    async def test_get_fee_responses(self):
        resp = await self.client.get_fee_responses(["0x0"])
        self.assertEqual(resp.fees[0].msg, "invalid hash")
