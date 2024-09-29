import logging
import asyncio
from abc import ABC, abstractmethod
from util.RedisClient import RedisClient
from loader.BinancePriceApi import BinancePriceApi
from web3 import AsyncWeb3, AsyncHTTPProvider
from consts import RPC_URL, ETH_UNISWAPV3_USDC_ETH_POOL_ADDR


class BaseLoader(ABC):
    refresh_sec = 10
    redis = RedisClient()
    bn_api = BinancePriceApi()
    web3_client = AsyncWeb3(AsyncHTTPProvider(RPC_URL))

    async def publish_gas(self, hash: str, gas_in_usdt):
        """
        Publishes the gas in USDT value to respective hash in redis
        """
        await self.redis.hset_json(
            name=ETH_UNISWAPV3_USDC_ETH_POOL_ADDR,
            key=hash.lower(),
            value=gas_in_usdt,
        )

    async def get_eth_usdt_price(self, timestamp: int) -> float:
        """
        Returns ETHUSDT price at specified timestamp
        """
        return await self.bn_api.get_eth_usdt_price(timestamp=int(timestamp * 1000))

    def wei_to_ether(self, amount_in_wei: int) -> float:
        return float(self.web3_client.from_wei(amount_in_wei, "ether"))

    async def prepare(self):
        pass

    @abstractmethod
    async def loop_fn(self):
        """
        The inner loop function to be implemented
        """
        raise NotImplementedError

    async def loop(self):
        """
        The main periodic loop function of each loader module
        """
        await self.prepare()
        while True:
            try:
                await self.loop_fn()
            except Exception as err:
                logging.exception(err)
            await asyncio.sleep(self.refresh_sec)
