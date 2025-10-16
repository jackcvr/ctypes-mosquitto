import asyncio
import weakref

from ctypes_mosquitto.client import Mosquitto
from ctypes_mosquitto.bindings import connack_string
from ctypes_mosquitto.constants import ConnackCode

MidDict = weakref.WeakValueDictionary[int, asyncio.Future]


class AIO:
    MISC_INTERVAL = 1

    def __init__(self, mosq: Mosquitto, loop=None):
        self._mosq = mosq
        self._loop = loop or asyncio.get_event_loop()
        self._conn_future = None
        self._disconn_future = None
        self._pub_mids: MidDict = weakref.WeakValueDictionary()
        self._sub_mids: MidDict = weakref.WeakValueDictionary()
        self._unsub_mids: MidDict = weakref.WeakValueDictionary()
        self._messages: asyncio.Queue = asyncio.Queue()
        self._fd = None
        self._misc_task = None
        self._set_default_callbacks()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.disconnect(strict=False)

    @property
    def mosq(self):
        return self._mosq

    @property
    def loop(self):
        return self._loop

    @property
    def messages(self):
        return self._messages

    def _set_default_callbacks(self):
        self._mosq.connect_callback_set(self._on_connect)
        self._mosq.disconnect_callback_set(self._on_disconnect)
        self._mosq.subscribe_callback_set(self._on_subscribe)
        self._mosq.unsubscribe_callback_set(self._on_unsubscribe)
        self._mosq.publish_callback_set(self._on_publish)
        self._mosq.message_callback_set(self._on_message)

    def _on_connect(self, mosq, userdata, rc):
        self._conn_future.set_result(rc)

    def _on_disconnect(self, mosq, userdata, rc):
        try:
            self._messages.put_nowait(None)
            if self._fd:
                self._loop.remove_reader(self._fd)
                self._loop.remove_writer(self._fd)
            self._fd = None
            if self._misc_task and not self._misc_task.done():
                self._misc_task.cancel()
                self._misc_task = None
        finally:
            if self._disconn_future:
                self._disconn_future.set_result(rc)

    def _on_publish(self, mosq, userdata, mid):
        self._pub_mids[mid].set_result(mid)
        self._check_writable()

    def _on_subscribe(self, mosq, userdata, mid, qos_count, granted_qos):
        self._sub_mids[mid].set_result(granted_qos)
        self._check_writable()

    def _on_unsubscribe(self, mosq, userdata, mid):
        self._unsub_mids[mid].set_result(mid)
        self._check_writable()

    def _on_message(self, mosq, userdata, msg):
        self._messages.put_nowait(msg)

    async def connect(self, *args, **kwargs):
        if self._conn_future:
            return await self._conn_future
        self._conn_future = self._loop.create_future()
        self._mosq.connect(*args, **kwargs)
        self._loop.call_soon(self._add_reader)
        rc = await self._conn_future
        self._conn_future = None
        if rc != ConnackCode.ACCEPTED:
            raise ConnectionError(connack_string(rc))
        self._misc_task = self._loop.create_task(self._misc_loop())
        return rc

    async def disconnect(self, strict=True):
        if self._disconn_future:
            return await self._disconn_future
        self._disconn_future = self._loop.create_future()
        self._mosq.disconnect(strict=strict)
        rc = await self._disconn_future
        self._disconn_future = None
        return rc

    async def publish(self, *args, **kwargs):
        mid = self._mosq.publish(*args, **kwargs)
        await self._wait_future(self._pub_mids, mid)
        return mid

    async def subscribe(self, *args, **kwargs):
        mid = self._mosq.subscribe(*args, **kwargs)
        await self._wait_future(self._sub_mids, mid)
        return mid

    async def unsubscribe(self, *args, **kwargs):
        mid = self._mosq.unsubscribe(*args, **kwargs)
        await self._wait_future(self._unsub_mids, mid)
        return mid

    async def _wait_future(self, mapping, mid):
        fut = self._loop.create_future()
        mapping[mid] = fut
        await fut

    async def read_messages(self):
        while True:
            msg = await self._messages.get()
            if msg is None:
                return
            yield msg

    def _add_reader(self):
        self._fd = self._mosq.socket()
        if self._fd:
            self._loop.add_reader(self._fd, self._loop_read)
        else:
            raise RuntimeError("No socket")

    def _loop_read(self):
        try:
            self._mosq.loop_read(1)
        except BlockingIOError:
            pass

    async def _misc_loop(self):
        while True:
            try:
                self._check_writable()
                self._mosq.loop_misc()
                await asyncio.sleep(self.MISC_INTERVAL)
            except asyncio.CancelledError:
                break

    def _check_writable(self):
        if self._fd and self._mosq.want_write():
            self._loop.add_writer(self._fd, self._loop_write)

    def _loop_write(self):
        self._mosq.loop_write()
        self._loop.remove_writer(self._fd)
