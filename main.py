import asyncio
from util.logs import setup_logger
from loader.LoaderProgram import LoaderProgram


async def main():
    setup_logger(log_file_name="main")
    loader = LoaderProgram()
    await asyncio.gather(
        asyncio.create_task(loader.periodic_loop()),
        asyncio.create_task(loader.subscription_loop()),
    )


if __name__ == "__main__":
    asyncio.run(main())
