import asyncio

from ctypes_mosquitto.aio import AIO
from ctypes_mosquitto.client import Mosquitto

from benchmarks import config as c

logger = None

if c.INTERVAL:
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()


async def main():
    count = 0
    async with AIO(Mosquitto(logger=logger)) as client:
        await client.connect(c.HOST, c.PORT)
        await client.subscribe(c.TOPIC, c.QOS)
        async for _ in client.read_messages():
            count += 1
            if count == c.AMOUNT:
                print("DONE")
                break


asyncio.run(main())
