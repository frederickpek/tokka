import aiohttp


class EtherscanApi:
    """
    Asynchronous Etherscan API Client
    """

    base_url = "https://api.etherscan.io/api"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_token_transfer_events_by_address(
        self,
        address: str,
        page: int = 1,
        offset: int = 100,
        start_block: int = 0,
        end_block: int = 99999999,
        sort: str = "asc",
    ) -> dict:
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "page": page,
            "offset": offset,
            "startblock": start_block,
            "endblock": end_block,
            "sort": sort,
            "apikey": self.api_key,
        }
        return await self.request(params)

    async def request(self, params: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                response.raise_for_status()
                return await response.json()
