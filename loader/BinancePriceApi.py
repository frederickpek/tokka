import time
import aiohttp


class BinancePriceApi:
    """
    Asynchronous Binance API Client
    Solely used to get eth usdt price
    """

    url = "https://api.binance.com/api/v3/klines"

    async def get_eth_usdt_price(self, timestamp: int = None) -> float:
        # timestamp in UTC
        end_time = timestamp or int(time.time() * 1000)
        start_time = end_time - 300_000  # 5min window of data
        if not timestamp:
            timestamp = time.time()
        params = {
            "interval": "1m",
            "symbol": "ETHUSDT",
            "startTime": start_time,
            "endTime": end_time,
        }
        resp = await self.request(params)
        return float(resp[-1][4])  # return the close price in this 1min window

    async def request(self, params: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, params=params) as response:
                response.raise_for_status()
                return await response.json()
