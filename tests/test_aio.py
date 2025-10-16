import asyncio
import logging

import pytest

from ctypes_mosquitto.constants import ConnackCode
from ctypes_mosquitto.aio import AIO
from ctypes_mosquitto.client import Mosquitto

import constants as c

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope="session")
def client_factory():
    def _factory():
        client = AIO(Mosquitto(logger=logging.getLogger()))
        if c.USERNAME or c.PASSWORD:
            client.mosq.username_pw_set(c.USERNAME, c.PASSWORD)
        return client

    return _factory


@pytest.mark.asyncio
async def test_pub_sub(client_factory):
    count = 3

    async with client_factory() as client:
        await client.connect(c.HOST, c.PORT)
        await client.subscribe("test", qos=1)

        for i in range(count):
            await client.publish("test", str(i), qos=1)

        async def recv():
            messages = []
            async for msg in client.read_messages():
                messages.append(msg)
                if len(messages) == count:
                    break
            return messages

        async with asyncio.timeout(1):
            messages = await client.loop.create_task(recv())
        assert [msg.payload for msg in messages] == [b"0", b"1", b"2"]


@pytest.mark.asyncio
async def test_multi_connect(client_factory):
    async with client_factory() as client:
        task = client.loop.create_task(client.connect(c.HOST, c.PORT))
        rc1 = await client.connect(c.HOST, c.PORT)
        rc2 = await task
        assert rc1 == rc2 == ConnackCode.ACCEPTED
