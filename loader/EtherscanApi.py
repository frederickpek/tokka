import httpx


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
        startblock: int = 0,
        endblock: int = 99999999,
        sort: str = "asc",
    ) -> dict:
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "page": page,
            "offset": offset,
            "startblock": startblock,
            "endblock": endblock,
            "sort": sort,
            "apikey": self.api_key,
        }
        return await self.request(params)

    async def request(self, params: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
