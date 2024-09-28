import asyncio
from util.logs import setup_logger
from loader.LoaderProgram import LoaderProgram


if __name__ == "__main__":
    setup_logger(log_file_name="main")
    loader = LoaderProgram()
    asyncio.run(loader.periodic_loop())
