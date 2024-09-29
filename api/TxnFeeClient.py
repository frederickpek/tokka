import asyncio
from pydantic import BaseModel
from util import is_valid_tx_hash
from util.RedisClient import RedisClient
from consts import ETH_UNISWAPV3_USDC_ETH_POOL_ADDR
from api.response_model import GetTransactionFeeResponse, PostTransactionFeeResponse


class TxnFeeClient:
    def __init__(self) -> None:
        self.redis = RedisClient()

    async def get_fee_responses(self, hashes: list[str]) -> BaseModel:
        fees = await asyncio.gather(*[self.get_fee_response(hash) for hash in hashes])
        return PostTransactionFeeResponse(fees=fees)

    async def get_fee_response(self, hash: str) -> BaseModel:
        response = GetTransactionFeeResponse(hash=hash)
        if not is_valid_tx_hash(hash):
            response.msg = "in valid hash"
            return response
        fee = await self.redis.hget_json(ETH_UNISWAPV3_USDC_ETH_POOL_ADDR, hash)
        if fee is None:
            await self.redis.publish(ETH_UNISWAPV3_USDC_ETH_POOL_ADDR, hash)
            response.msg = "queued for processing, query again after some time"
            return response
        response.fee = format(fee, "f")
        return response
