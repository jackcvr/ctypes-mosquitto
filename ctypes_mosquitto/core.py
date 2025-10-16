import ctypes as C
import os
from ctypes.util import find_library


def load_library(name: str) -> C.CDLL:
    if name is None:
        path = None
    else:
        path = find_library(name)
        if path is None:
            raise ImportError(f"{name} library not found")
    return C.CDLL(path, use_errno=True)


def bind(restype, func, *argtypes) -> None:
    func.restype = restype
    func.argtypes = argtypes


def check_errno(code: int = None):
    if code is None:
        code = C.get_errno()
    if code != 0:
        raise OSError(code, os.strerror(code))


class LibraryError(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return f"{self.code}/{self.strerror()}"

    def strerror(self):
        return "Unknown error"
