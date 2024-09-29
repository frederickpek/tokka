from loader.etherscan_loader.EtherscanApi import EtherscanApi
from consts import ETHERSCAN_API_KEY, ETH_UNISWAPV3_USDC_ETH_POOL_ADDR


class EtherscanTxnLoader:
    def __init__(self):
        self.api = EtherscanApi(ETHERSCAN_API_KEY)

    async def get_transactions(self, start_block: int, end_block: int) -> list[dict]:
        """
        Returns token transactions from start_block to end_block inclusive.
        Only transactions which involves the uniswapv3 eth/usdc pool address are included.
        """
        page = 1
        offset = 10_000  # etherscan offset limit
        resp = await self.api.get_token_transfer_events_by_address(
            address=ETH_UNISWAPV3_USDC_ETH_POOL_ADDR,
            start_block=start_block,
            end_block=end_block,
            offset=offset,
            page=page,
        )
        result = resp.get("result", list())
        return result
