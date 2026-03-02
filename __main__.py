import asyncio

from src.worker.worker import main


if __name__ == "__main__":
    print("Main thread")

    asyncio.run(main())
