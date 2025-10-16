import queue
import signal

from ctypes_mosquitto.bindings.libc import signal as c_signal


def test_libc_signal():
    q = queue.SimpleQueue()

    def handler(*args):
        q.put_nowait(args)

    assert not c_signal(signal.SIGHUP, handler)
    signal.raise_signal(signal.SIGHUP)
    assert q.get(timeout=1) == (signal.SIGHUP,)
