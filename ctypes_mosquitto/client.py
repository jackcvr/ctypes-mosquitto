import ctypes as C

import logging
import atexit
import enum
import typing as t
import weakref
import types

from .constants import (
    LogLevel,
    MOSQ_MIN_MAJOR_VERSION,
    ErrorCode,
    ConnackCode,
    Option,
    MQTT5PropertyID,
)
from .bindings import lib, Struct, Function, call
from .core import LibraryError, unpack_struct


def lib_version():
    maj, min_, patch = (C.c_int(), C.c_int(), C.c_int())
    lib.mosquitto_lib_version(C.byref(maj), C.byref(min_), C.byref(patch))
    return maj.value, min_.value, patch.value


MOSQ_VERSION = lib_version()

if MOSQ_VERSION[0] < MOSQ_MIN_MAJOR_VERSION:
    raise RuntimeError(f"libmosquitto version {MOSQ_MIN_MAJOR_VERSION}+ is required")

if lib.mosquitto_lib_init() != 0:
    raise RuntimeError("libmosquitto initialization failed")
atexit.register(lib.mosquitto_lib_cleanup)


class PropertyFactory(enum.Enum):
    BYTE = lib.mosquitto_property_add_byte
    INT16 = lib.mosquitto_property_add_int16
    INT32 = lib.mosquitto_property_add_int32
    VARINT = lib.mosquitto_property_add_varint
    BIN = lib.mosquitto_property_add_binary
    STRING = lib.mosquitto_property_add_string
    STRING_PAIR = lib.mosquitto_property_add_string_pair

    def __call__(self, identifier: MQTT5PropertyID, *args: t.Any) -> C._Pointer:
        prop = C.POINTER(Struct.MQTT5Property)()
        call(self.value, C.byref(prop), identifier, *args)
        return prop


def find_prop(prop, identifier: MQTT5PropertyID):
    while True:
        if prop.identifier == identifier:
            return prop
        if not prop.next:
            break
        prop = prop.next
    return None


class Callback:
    def __init__(self, setter, decorator, wrapper):
        self._setter = setter
        self._decorator = decorator
        self._wrapper = wrapper
        self._wrapped_callback = None

    def __set_name__(self, owner, name):
        self._attr_name = f"__{name[3:]}_callback"

    def __set__(self, obj, callback):
        setattr(obj, self._attr_name, callback)
        if callback and not self._wrapped_callback:
            self._wrapped_callback = self._decorator(self._wrapper)
        elif not callback:
            self._wrapped_callback = self._decorator(0)
        obj.call(self._setter, obj.ptr, self._wrapped_callback)

    def __get__(self, obj, objtype=None):
        return getattr(obj, self._attr_name)


def _connect_callback_wrapper(_, userdata, rc):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_connect:
        client.on_connect(client, client.userdata(), ConnackCode(rc))


def _connect_with_flags_callback_wrapper(_, userdata, rc, flags):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_connect_with_flags:
        client.on_connect_with_flags(client, client.userdata(), ConnackCode(rc), flags)


def _connect_v5_callback_wrapper(_, userdata, rc, flags, prop):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_connect_v5:
        client.on_connect_v5(
            client,
            client.userdata(),
            ConnackCode(rc),
            flags,
            unpack_struct(prop),
        )


def _disconnect_callback_wrapper(_, userdata, rc):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_disconnect:
        client.on_disconnect(client, client.userdata(), ConnackCode(rc))


def _disconnect_v5_callback_wrapper(_, userdata, rc, prop):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_disconnect_v5:
        client.on_disconnect_v5(
            client,
            client.userdata(),
            ConnackCode(rc),
            unpack_struct(prop),
        )


def _publish_callback_wrapper(_, userdata, mid):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_publish:
        client.on_publish(client, client.userdata(), mid)


def _publish_v5_callback_wrapper(_, userdata, mid, prop):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_publish_v5:
        client.on_publish_v5(
            client,
            client.userdata(),
            mid,
            unpack_struct(prop),
        )


def _message_callback_wrapper(_, userdata, msg):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_message:
        client.on_message(client, client.userdata(), unpack_struct(msg))


def _message_v5_callback_wrapper(_, userdata, msg, prop):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_message_v5:
        client.on_message_v5(
            client,
            client.userdata(),
            unpack_struct(msg),
            unpack_struct(prop),
        )


def _subscribe_callback_wrapper(_, userdata, mid, count, granted_qos):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_subscribe:
        client.on_subscribe(
            client,
            client.userdata(),
            mid,
            count,
            [granted_qos[i] for i in range(count)],
        )


def _subscribe_v5_callback_wrapper(_, userdata, mid, count, granted_qos, prop):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_subscribe_v5:
        client.on_subscribe_v5(
            client,
            client.userdata(),
            mid,
            count,
            [granted_qos[i] for i in range(count)],
            unpack_struct(prop),
        )


def _unsubscribe_callback_wrapper(_, userdata, mid):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_unsubscribe:
        client.on_unsubscribe(client, client.userdata(), mid)


def _unsubscribe_v5_callback_wrapper(_, userdata, mid, prop):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_unsubscribe_v5:
        client.on_unsubscribe_v5(
            client,
            client.userdata(),
            mid,
            unpack_struct(prop),
        )


def _log_callback_wrapper(_, userdata, level, msg):
    client = t.cast(Mosquitto, userdata)
    if client and client.on_log:
        client.on_log(client, client.userdata(), LogLevel(level), msg.decode())
    elif client and client.logger:
        client.logger.debug("MOSQ/%s %s", LogLevel(level).name, msg.decode())


class Mosquitto:
    def __init__(
        self,
        client_id=None,
        clean_start=True,
        userdata=None,
        logger=None,
        protocol=None,
    ):
        if client_id is not None:
            client_id = client_id.encode()
        self._userdata = userdata
        self._logger = logger
        self._is_debug = (
            self._logger and self._logger.getEffectiveLevel() <= logging.DEBUG
        )
        self._ptr = call(lib.mosquitto_new, client_id, clean_start, self, check=False)
        if protocol is not None:
            self.int_option(Option.PROTOCOL_VERSION, protocol)

    @property
    def ptr(self):
        return self._ptr

    @property
    def logger(self):
        return self._logger

    def __del__(self):
        lib.mosquitto_destroy(self._ptr)

    def _method_factory(self, func):
        if func.argtypes and func.argtypes[0] == C.c_void_p:

            def _call(self_, *args, **kwargs):
                return self_.call(func, self._ptr, *args, **kwargs)
        else:

            def _call(self_, *args, **kwargs):
                return self_.call(func, *args, **kwargs)

        return types.MethodType(_call, weakref.proxy(self))

    def __getattr__(self, name):
        key = f"mosquitto_{name.lstrip('_')}"
        func = getattr(lib, key, None)
        if func is None:
            raise AttributeError(key)
        method = self._method_factory(func)
        setattr(self, name, method)
        return method

    def set_log_level(self, level):
        if self._logger:
            self._logger.setLevel(level)
            self._is_debug = level <= logging.DEBUG

    def call(self, func, *args, check=True, auto_encode=True, auto_decode=True):
        if self._is_debug:
            self._logger.debug("CALL: %s%s", func.__name__, args)
        if auto_encode:
            args = [arg.encode() if isinstance(arg, str) else arg for arg in args]
        ret = call(func, *args, check=check)
        if auto_decode and func.restype == C.c_char_p:
            ret = ret.decode()
        return ret

    # Callbacks
    on_connect = Callback(
        lib.mosquitto_connect_callback_set,
        Function.ON_CONNECT,
        _connect_callback_wrapper,
    )
    on_connect_with_flags = Callback(
        lib.mosquitto_connect_with_flags_callback_set,
        Function.ON_CONNECT_WITH_FLAGS,
        _connect_with_flags_callback_wrapper,
    )
    on_connect_v5 = Callback(
        lib.mosquitto_connect_v5_callback_set,
        Function.ON_CONNECT_V5,
        _connect_v5_callback_wrapper,
    )
    on_disconnect = Callback(
        lib.mosquitto_disconnect_callback_set,
        Function.ON_DISCONNECT,
        _disconnect_callback_wrapper,
    )
    on_disconnect_v5 = Callback(
        lib.mosquitto_disconnect_v5_callback_set,
        Function.ON_DISCONNECT_V5,
        _disconnect_v5_callback_wrapper,
    )
    on_publish = Callback(
        lib.mosquitto_publish_callback_set,
        Function.ON_PUBLISH,
        _publish_callback_wrapper,
    )
    on_publish_v5 = Callback(
        lib.mosquitto_publish_v5_callback_set,
        Function.ON_PUBLISH_V5,
        _publish_v5_callback_wrapper,
    )
    on_message = Callback(
        lib.mosquitto_message_callback_set,
        Function.ON_MESSAGE,
        _message_callback_wrapper,
    )
    on_message_v5 = Callback(
        lib.mosquitto_message_v5_callback_set,
        Function.ON_MESSAGE_V5,
        _message_v5_callback_wrapper,
    )
    on_subscribe = Callback(
        lib.mosquitto_subscribe_callback_set,
        Function.ON_SUBSCRIBE,
        _subscribe_callback_wrapper,
    )
    on_subscribe_v5 = Callback(
        lib.mosquitto_subscribe_v5_callback_set,
        Function.ON_SUBSCRIBE_V5,
        _subscribe_v5_callback_wrapper,
    )
    on_unsubscribe = Callback(
        lib.mosquitto_unsubscribe_callback_set,
        Function.ON_UNSUBSCRIBE,
        _unsubscribe_callback_wrapper,
    )
    on_unsubscribe_v5 = Callback(
        lib.mosquitto_unsubscribe_v5_callback_set,
        Function.ON_UNSUBSCRIBE_V5,
        _unsubscribe_v5_callback_wrapper,
    )
    on_log = Callback(
        lib.mosquitto_log_callback_set,
        Function.ON_LOG,
        _log_callback_wrapper,
    )

    def connect(self, host, port=1883, keepalive=60, bind_address=None, props=None):
        host = host.encode()
        bind_address = bind_address.encode() if bind_address else None
        if bind_address and props:
            return self.connect_bind_v5(host, port, keepalive, bind_address, props)
        elif bind_address:
            return self.connect_bind(host, port, keepalive, bind_address)
        elif props:
            return self.connect_bind_v5(host, port, keepalive, None, props)
        return self._connect(host, port, keepalive)

    def connect_async(self, host, port=1883, keepalive=60):
        return self._connect_async(host, port, keepalive)

    def disconnect(self, strict=True):
        if strict:
            self._disconnect()
        else:
            try:
                self._disconnect()
            except LibraryError as e:
                if e.code != ErrorCode.NO_CONN:
                    raise e

    def socket(self):
        fd = self._socket(check=False)
        return None if fd == -1 else fd

    def loop_forever(self, timeout=-1):
        return self._loop_forever(timeout, 1)

    def publish(self, topic, payload, qos=0, retain=False, props=None):
        mid = C.c_int(0)
        if isinstance(payload, str):
            payload = payload.encode()
        if props:
            self.publish_v5(
                C.byref(mid),
                topic.encode(),
                len(payload),
                C.c_char_p(payload),
                qos,
                retain,
                props,
            )
        else:
            self._publish(
                C.byref(mid),
                topic.encode(),
                len(payload),
                C.c_char_p(payload),
                qos,
                retain,
            )
        return mid.value

    def subscribe(self, topic, qos=0, props=None):
        mid = C.c_int(0)
        if props:
            self.subscribe_v5(C.byref(mid), topic.encode(), qos, props)
        else:
            self._subscribe(C.byref(mid), topic.encode(), qos)
        return mid.value

    def unsubscribe(self, topic, props=None):
        mid = C.c_int(0)
        if props:
            self.unsubscribe_v5(C.byref(mid), topic.encode(), props)
        else:
            self._unsubscribe(C.byref(mid), topic.encode())
        return mid.value

    def user_data_set(self, userdata):
        self._userdata = userdata

    def userdata(self):
        return self._userdata
