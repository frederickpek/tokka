import json
import asyncio
from pydantic import BaseModel
from util import is_valid_tx_hash
from util.RedisClient import RedisClient
from consts import ETH_UNISWAPV3_USDC_ETH_POOL_ADDR
from api.response_model import GetTransactionFeeResponse, PostTransactionFeeResponse


class TxnFeeClient:
    def __init__(self) -> None:
        self.retry_times = 10
        self.redis = RedisClient()

    async def get_fee_responses(self, hashes: list[str]) -> BaseModel:
        fees = await asyncio.gather(*[self.get_fee_response(hash) for hash in hashes])
        return PostTransactionFeeResponse(fees=fees)

    async def get_fee_response(self, hash: str, _inner=False) -> BaseModel:
        response = GetTransactionFeeResponse(hash=hash)
        if not is_valid_tx_hash(hash):
            response.msg = "invalid hash"
            return response
        fee = await self.redis.hget_json(ETH_UNISWAPV3_USDC_ETH_POOL_ADDR, hash)
        if _inner and fee is None:
            return
        if fee is None:
            await self.redis.publish_to_channel(ETH_UNISWAPV3_USDC_ETH_POOL_ADDR, hash)
            for _ in range(self.retry_times):
                # try waiting for 1s for it to appear
                await asyncio.sleep(0.1)
                if resp := await self.get_fee_response(hash, _inner=True):
                    return resp
            response.msg = "queued for processing, query again after some time"
            return response
        if isinstance(fee, float):
            response.fee = format(fee, "f")
        else:
            response.msg = fee
        return response
