import ctypes as C
import errno

import pytest

from ctypes_mosquitto.core import (
    load_library,
    check_errno,
    bind,
    LibraryError,
)

libc = load_library(None)

# int printf(const char *restrict format, ...)
bind(C.c_int, libc.printf, C.c_char_p)

# ssize_t read(int fd, void *buf, size_t count)
bind(C.c_int, libc.read, C.c_void_p, C.c_int)


def test_success():
    text = b"test"
    ret = libc.printf(text)
    assert ret == len(text)


def test_check_errno():
    libc.read(C.byref(C.c_int()), 1)
    with pytest.raises(OSError) as e:
        check_errno()
    assert e.value.errno == errno.EBADF


def test_library_error():
    class TestError(LibraryError):
        def strerror(self):
            return "Test error description"

    code = 69
    desc = TestError(code).strerror()

    def doerr():
        raise TestError(code)

    with pytest.raises(LibraryError) as e:
        doerr()

    assert e.value.code == code
    assert str(e.value) == f"{code}/{desc}"
