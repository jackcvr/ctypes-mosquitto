import ctypes as C
import os
import typing as t
import types
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


def unpack_struct(
    obj: t.Union[C.Structure, C._Pointer],
) -> t.Optional[types.SimpleNamespace]:
    if not obj:
        return None
    if isinstance(obj, C._Pointer):
        obj = obj.contents
    if t.TYPE_CHECKING:
        obj = t.cast(C.Structure, obj)
    values = {}
    for name, _ in obj._fields_:  # type: ignore[misc]
        value = getattr(obj, name)
        if isinstance(value, bytes):
            value = value.decode()
        values[name] = value
    if hasattr(obj, "_payloads_"):
        for name in obj._payloads_:
            values[name] = C.string_at(values[name], values[obj._payloads_[name]])
    if hasattr(obj, "_objects_"):
        for name in obj._objects_:
            values[name] = unpack_struct(values[name])
    return types.SimpleNamespace(**values)
