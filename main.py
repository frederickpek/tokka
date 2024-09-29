import asyncio
from util.logs import setup_logger
from loader.PeriodicLoader import PeriodicLoader
from loader.Web3PubSubLoader import Web3PubSubLoader


async def main():
    setup_logger(log_file_name="main")
    await asyncio.gather(
        asyncio.create_task(PeriodicLoader().loop()),
        asyncio.create_task(Web3PubSubLoader().loop()),
    )


if __name__ == "__main__":
    asyncio.run(main())
