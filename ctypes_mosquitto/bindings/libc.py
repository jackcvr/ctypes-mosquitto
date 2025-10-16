import ctypes as C
import typing as t

from ..core import load_library, bind, check_errno

libc = load_library(None)

SIGNAL_WRAPPER = C.CFUNCTYPE(None, C.c_int)

bind(SIGNAL_WRAPPER, libc.signal, C.c_int, SIGNAL_WRAPPER)

_signal_handlers: dict[int, t.Any] = {}


def signal(signum: int, func: t.Callable) -> t.Callable:
    """
    Sets signal handler via libc.

    Helpful if you call `loop_forever` in the main thread.
    """

    _signal_handlers[signum] = SIGNAL_WRAPPER(func)
    ret = libc.signal(signum, _signal_handlers[signum])
    check_errno()
    return ret
