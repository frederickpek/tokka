import asyncio
from loader.LoaderProgram import LoaderProgram


if __name__ == "__main__":
    loader = LoaderProgram()
    asyncio.run(loader.loop())
