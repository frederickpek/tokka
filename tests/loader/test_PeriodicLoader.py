from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from loader.PeriodicLoader import PeriodicLoader
from consts import ETH_FINALITY_BLOCKS


class TestPeriodicLoader(IsolatedAsyncioTestCase):
    def setUp(self):
        self.loader = PeriodicLoader()
        self.loader.redis = AsyncMock()
        self.loader.etherscan_loader = AsyncMock()
        self.loader.bn_api.get_eth_usdt_price = AsyncMock(return_value=2000)

    async def test_process_etherscan_transaction(self):
        hash = "0x0"
        txn = {
            "gasUsed": 138000,
            "gasPrice": 6800000000,
            "timeStamp": 1727000000,
        }
        await self.loader.process_etherscan_transaction(hash, txn)
        self.loader.redis.hset_json.assert_called_once()

    async def test_get_latest_block_number(self):
        block_number = 200_000
        block = {"number": block_number}
        self.loader.web3_client.eth.get_block = AsyncMock(return_value=block)
        latest_block_number = await self.loader.get_latest_block_number()
        self.assertEqual(latest_block_number, block_number - ETH_FINALITY_BLOCKS)

    async def test_get_block_range(self):
        latest_block_number = 12
        self.loader.get_latest_block_number = AsyncMock(
            return_value=latest_block_number
        )
        self.loader.last_processed_block_number = 10
        start_block, end_block = await self.loader.get_block_range()
        self.assertEqual(start_block, 11)
        self.assertEqual(end_block, 12)

    async def test_get_block_range_first_cycle(self):
        latest_block_number = 12
        self.loader.get_latest_block_number = AsyncMock(
            return_value=latest_block_number
        )
        self.loader.last_processed_block_number = None
        start_block, end_block = await self.loader.get_block_range()
        self.assertEqual(start_block, end_block)
        self.assertEqual(end_block, 12)

    async def test_loop_fn(self):
        transactions = [{"hash": "0xaaa"}, {"hash": "0xaaa"}]
        self.loader.get_block_range = AsyncMock(return_value=(0, 1))
        self.loader.etherscan_loader.get_transactions = AsyncMock(
            return_value=transactions
        )
        self.loader.process_etherscan_transaction = AsyncMock()
        self.loader.last_processed_block_number = None
        await self.loader.loop_fn()
        self.loader.process_etherscan_transaction.assert_called_once()
        self.loader.last_processed_block_number = 1
