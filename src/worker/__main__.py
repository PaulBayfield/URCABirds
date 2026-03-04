import asyncio

from .worker import Worker
from aiohttp import ClientSession


async def main():
    """
    Main function to run the worker.
    """
    session = ClientSession()

    worker = Worker(session)
    await worker.run()
    await worker.close()

    await session.close()


if __name__ == "__main__":
    asyncio.run(main())
