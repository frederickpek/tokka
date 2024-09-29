import json
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock
from loader.Web3PubSubLoader import Web3PubSubLoader


class TestWeb3PubSubLoader(IsolatedAsyncioTestCase):
    hash = "0x0"

    def setUp(self):
        self.loader = Web3PubSubLoader()
        self.loader.redis = AsyncMock()
        self.loader.bn_api.get_eth_usdt_price = AsyncMock(return_value=2000)
        self.loader.web3_loader = AsyncMock()
        self.loader.web3_verifier = AsyncMock()

    async def test_process_valid_hash(self):
        txn_receipt = {
            "gasUsed": 138000,
            "effectiveGasPrice": 6800000000,
            "blockNumber": 200000,
        }
        block_number = 1720000000
        block = {"timestamp": block_number}
        self.loader.web3_client.eth.get_block = AsyncMock(return_value=block)
        await self.loader.process_valid_hash(self.hash, txn_receipt)
        self.loader.redis.hset_json.assert_called_once()

    async def test_process_invalid_hash(self):
        await self.loader.process_invalid_hash(self.hash)
        self.assertEqual(
            self.loader.redis.hset_json.call_args.kwargs["value"],
            "non uniswapv3 pool txn",
        )

    async def test_process_hash_valid(self):
        self.loader.web3_verifier.verify_transaction_receipt = AsyncMock(
            return_value=True
        )
        self.loader.process_valid_hash = AsyncMock()
        await self.loader.process_hash(self.hash)
        self.loader.process_valid_hash.assert_called_once()

    async def test_process_hash_invalid(self):
        self.loader.web3_verifier.verify_transaction_receipt = AsyncMock(
            return_value=False
        )
        self.loader.process_invalid_hash = AsyncMock()
        await self.loader.process_hash(self.hash)
        self.loader.process_invalid_hash.assert_called_once()

    async def test_prepare(self):
        pubsub = AsyncMock()
        self.loader.redis.pubsub = MagicMock(return_value=pubsub)
        await self.loader.prepare()
        pubsub.subscribe.assert_called_once()
        self.assertEqual(self.loader.pubsub, pubsub)

    async def test_loop_fn_no_msg(self):
        self.loader.process_hash = AsyncMock()
        self.loader.pubsub = AsyncMock()
        self.loader.pubsub.get_message = AsyncMock(return_value=None)
        await self.loader.loop_fn()
        self.loader.process_hash.assert_not_called()

    async def test_loop_fn_msg_received(self):
        self.loader.process_hash = AsyncMock()
        self.loader.pubsub = AsyncMock()
        mock_byte = MagicMock()
        mock_byte.decode = MagicMock(return_value=json.dumps(self.hash))
        msg = {"data": mock_byte}
        self.loader.pubsub.get_message = AsyncMock(return_value=msg)
        await self.loader.loop_fn()
        self.loader.process_hash.assert_called_once_with(self.hash)
