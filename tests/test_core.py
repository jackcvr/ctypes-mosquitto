import ctypes as C
import errno

import pytest

from ctypes_mosquitto.core import (
    load_library,
    check_errno,
    bind,
    LibraryError,
    unpack_struct,
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


def test_unpack_char_p():
    class S(C.Structure):
        _fields_ = [("msg", C.c_char_p)]

    s = S(b"hello")
    res = unpack_struct(s)
    assert res.msg == "hello"


def test_unpack_void_p_with_size():
    class S(C.Structure):
        _fields_ = [
            ("data", C.c_void_p),
            ("size", C.c_int),
        ]
        _payloads_ = {
            "data": "size",
        }

    data = b"abcde"
    buf = C.create_string_buffer(data)
    s = S(C.addressof(buf), len(data))
    res = unpack_struct(s)
    assert res.data == data


def test_unpack_from_pointer():
    class S(C.Structure):
        _fields_ = [("value", C.c_int)]

    s = S(42)
    res = unpack_struct(C.pointer(s))
    assert res.value == 42


def test_unpack_recursive():
    class Inner(C.Structure):
        _fields_ = [
            ("msg", C.c_char_p),
            ("num", C.c_int),
        ]

    class Outer(C.Structure):
        _fields_ = [
            ("id", C.c_int),
            ("inner", Inner),
            ("inner_p", C.POINTER(Inner)),
        ]
        _objects_ = ("inner", "inner_p")

    inner = Inner(b"nested", 99)
    outer = Outer(1, inner, C.pointer(inner))

    res = unpack_struct(outer)
    assert res.id == 1
    assert res.inner.msg == "nested"
    assert res.inner.num == 99
    assert res.inner.msg == res.inner_p.msg
    assert res.inner.num == res.inner_p.num
