import ctypes as C

import logging
import atexit
import typing as t
import weakref
import types

from .constants import (
    LogLevel,
    MOSQ_MIN_MAJOR_VERSION,
    ErrorCode,
    ConnackCode,
    Option,
    PropertyId,
    PropertyType,
)
from .bindings import lib, Struct, Function, call
from .core import LibraryError


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

PROPERTY_TYPE_MAP = {
    PropertyId.PAYLOAD_FORMAT_INDICATOR: PropertyType.BYTE,
    PropertyId.MESSAGE_EXPIRY_INTERVAL: PropertyType.INT32,
    PropertyId.CONTENT_TYPE: PropertyType.STRING,
    PropertyId.RESPONSE_TOPIC: PropertyType.STRING,
    PropertyId.CORRELATION_DATA: PropertyType.BINARY,
    PropertyId.SUBSCRIPTION_IDENTIFIER: PropertyType.VARINT,
    PropertyId.SESSION_EXPIRY_INTERVAL: PropertyType.INT32,
    PropertyId.ASSIGNED_CLIENT_IDENTIFIER: PropertyType.STRING,
    PropertyId.SERVER_KEEP_ALIVE: PropertyType.INT16,
    PropertyId.AUTHENTICATION_METHOD: PropertyType.STRING,
    PropertyId.AUTHENTICATION_DATA: PropertyType.BINARY,
    PropertyId.REQUEST_PROBLEM_INFORMATION: PropertyType.BYTE,
    PropertyId.WILL_DELAY_INTERVAL: PropertyType.INT32,
    PropertyId.REQUEST_RESPONSE_INFORMATION: PropertyType.BYTE,
    PropertyId.RESPONSE_INFORMATION: PropertyType.STRING,
    PropertyId.SERVER_REFERENCE: PropertyType.STRING,
    PropertyId.REASON_STRING: PropertyType.STRING,
    PropertyId.RECEIVE_MAXIMUM: PropertyType.INT16,
    PropertyId.TOPIC_ALIAS_MAXIMUM: PropertyType.INT16,
    PropertyId.TOPIC_ALIAS: PropertyType.INT16,
    PropertyId.MAXIMUM_QOS: PropertyType.BYTE,
    PropertyId.RETAIN_AVAILABLE: PropertyType.BYTE,
    PropertyId.USER_PROPERTY: PropertyType.STRING_PAIR,
    PropertyId.MAXIMUM_PACKET_SIZE: PropertyType.INT32,
    PropertyId.WILDCARD_SUB_AVAILABLE: PropertyType.BYTE,
    PropertyId.SUBSCRIPTION_ID_AVAILABLE: PropertyType.BYTE,
    PropertyId.SHARED_SUB_AVAILABLE: PropertyType.BYTE,
}

PROPERTY_FUNC_MAP = {
    PropertyType.BYTE: lib.mosquitto_property_add_byte,
    PropertyType.INT16: lib.mosquitto_property_add_int16,
    PropertyType.INT32: lib.mosquitto_property_add_int32,
    PropertyType.VARINT: lib.mosquitto_property_add_varint,
    PropertyType.BINARY: lib.mosquitto_property_add_binary,
    PropertyType.STRING: lib.mosquitto_property_add_string,
    PropertyType.STRING_PAIR: lib.mosquitto_property_add_string_pair,
}


class Message:
    __slots__ = ("mid", "topic", "payload", "qos", "retain")

    def __init__(self, msg: Struct.Message):
        self.mid = msg.mid
        self.topic = msg.topic.decode()
        self.payload = C.string_at(msg.payload, msg.payloadlen)
        self.qos = msg.qos
        self.retain = msg.retain


class Property:
    __slots__ = ("next", "value", "name", "identifier", "client_generated")

    def __init__(self, prop: Struct.Property):
        self.next = self.__class__(prop.next.contents) if prop.next else None
        self.name = C.string_at(prop.name.v, prop.name.len).decode()
        self.identifier = prop.identifier
        self.client_generated = prop.client_generated
        self.value = self._get_value(prop.value)

    def _get_value(self, value: Struct.PropertyValue):
        type_ = PROPERTY_TYPE_MAP[self.identifier]
        if type_ == PropertyType.BYTE:
            return value.i8
        elif type_ == PropertyType.INT16:
            return value.i16
        elif type_ == PropertyType.INT32:
            return value.i32
        elif type_ == PropertyType.VARINT:
            return value.varint
        elif type_ == PropertyType.BINARY:
            return C.string_at(value.bin.v, value.bin.len)
        elif type_ == PropertyType.STRING:
            return C.string_at(value.s.v, value.s.len).decode()
        raise RuntimeError(f"unknown property type: {type_}")

    @staticmethod
    def add(
        prop: t.Optional[C._Pointer], identifier: PropertyId, *args: t.Any
    ) -> C._Pointer:
        if not prop:
            prop = C.POINTER(Struct.Property)()
        type_ = PROPERTY_TYPE_MAP[identifier]
        func = PROPERTY_FUNC_MAP[type_]
        call(func, C.byref(prop), identifier, *args)
        return prop

    def find(self, identifier: PropertyId) -> t.Optional["Property"]:
        prop = self
        while True:
            if prop.identifier == identifier:
                return prop
            if not prop.next:
                break
            prop = prop.next
        return None


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

        self.__on_connect_callback = None
        self.__on_connect_with_flags_callback = None
        self.__on_connect_v5_callback = None
        self.__on_disconnect_callback = None
        self.__on_disconnect_v5_callback = None
        self.__on_publish_callback = None
        self.__on_publish_v5_callback = None
        self.__on_message_callback = None
        self.__on_message_v5_callback = None
        self.__on_subscribe_callback = None
        self.__on_subscribe_v5_callback = None
        self.__on_unsubscribe_callback = None
        self.__on_unsubscribe_v5_callback = None
        self.__on_log_callback = None

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
    def connect_callback_set(self, callback):
        self.__on_connect_callback = self._make_wrapper(
            Function.ON_CONNECT,
            callback,
            lambda mosq, ud, rc: callback(self, self.userdata(), ConnackCode(rc)),
        )
        self._connect_callback_set(self.__on_connect_callback)

    def connect_with_flags_callback_set(self, callback):
        self.__on_connect_with_flags_callback = self._make_wrapper(
            Function.ON_CONNECT_WITH_FLAGS,
            callback,
            lambda mosq, ud, rc, flags: callback(
                self, self.userdata(), ConnackCode(rc), flags
            ),
        )
        self._connect_with_flags_callback_set(self.__on_connect_with_flags_callback)

    def connect_v5_callback_set(self, callback):
        self.__on_connect_v5_callback = self._make_wrapper(
            Function.ON_CONNECT_V5,
            callback,
            lambda mosq, ud, rc, flags, props: callback(
                self,
                self.userdata(),
                ConnackCode(rc),
                flags,
                Property(props.contents) if props else None,
            ),
        )
        self._connect_v5_callback_set(self.__on_connect_v5_callback)

    def disconnect_callback_set(self, callback):
        self.__on_disconnect_callback = self._make_wrapper(
            Function.ON_DISCONNECT,
            callback,
            lambda mosq, ud, rc: callback(self, self.userdata(), rc),
        )
        self._disconnect_callback_set(self.__on_disconnect_callback)

    def disconnect_v5_callback_set(self, callback):
        self.__on_disconnect_v5_callback = self._make_wrapper(
            Function.ON_DISCONNECT_V5,
            callback,
            lambda mosq, ud, rc, props: callback(
                self, self.userdata(), rc, Property(props.contents) if props else None
            ),
        )
        self._disconnect_v5_callback_set(self.__on_disconnect_v5_callback)

    def publish_callback_set(self, callback):
        self.__on_publish_callback = self._make_wrapper(
            Function.ON_PUBLISH,
            callback,
            lambda mosq, ud, mid: callback(self, self.userdata(), mid),
        )
        self._publish_callback_set(self.__on_publish_callback)

    def publish_v5_callback_set(self, callback):
        self.__on_publish_v5_callback = self._make_wrapper(
            Function.ON_PUBLISH_V5,
            callback,
            lambda mosq, ud, mid, rc, props: callback(
                self,
                self.userdata(),
                mid,
                rc,
                Property(props.contents) if props else None,
            ),
        )
        self._publish_v5_callback_set(self.__on_publish_v5_callback)

    def message_callback_set(self, callback):
        self.__on_message_callback = self._make_wrapper(
            Function.ON_MESSAGE,
            callback,
            lambda mosq, ud, msg: callback(
                self, self.userdata(), Message(msg.contents)
            ),
        )
        self._message_callback_set(self.__on_message_callback)

    def message_v5_callback_set(self, callback):
        self.__on_message_v5_callback = self._make_wrapper(
            Function.ON_MESSAGE_V5,
            callback,
            lambda mosq, ud, msg, props: callback(
                self,
                self.userdata(),
                Message(msg.contents),
                Property(props.contents) if props else None,
            ),
        )
        self._message_v5_callback_set(self.__on_message_v5_callback)

    def subscribe_callback_set(self, callback):
        self.__on_subscribe_callback = self._make_wrapper(
            Function.ON_SUBSCRIBE,
            callback,
            lambda mosq, ud, mid, qos_count, granted_qos: callback(
                self,
                self.userdata(),
                mid,
                qos_count,
                [granted_qos[i] for i in range(qos_count)],
            ),
        )
        self._subscribe_callback_set(self.__on_subscribe_callback)

    def subscribe_v5_callback_set(self, callback):
        self.__on_subscribe_v5_callback = self._make_wrapper(
            Function.ON_SUBSCRIBE_V5,
            callback,
            lambda mosq, ud, mid, qos_count, granted_qos, props: callback(
                self,
                self.userdata(),
                mid,
                qos_count,
                [granted_qos[i] for i in range(qos_count)],
                Property(props.contents) if props else None,
            ),
        )
        self._subscribe_v5_callback_set(self.__on_subscribe_v5_callback)

    def unsubscribe_callback_set(self, callback):
        self.__on_unsubscribe_callback = self._make_wrapper(
            Function.ON_UNSUBSCRIBE,
            callback,
            lambda mosq, ud, mid: callback(self, self.userdata(), mid),
        )
        self._unsubscribe_callback_set(self.__on_unsubscribe_callback)

    def unsubscribe_v5_callback_set(self, callback):
        self.__on_unsubscribe_v5_callback = self._make_wrapper(
            Function.ON_UNSUBSCRIBE_V5,
            callback,
            lambda mosq, ud, mid, props: callback(
                self,
                self.userdata(),
                mid,
                Property(props.contents) if props else None,
            ),
        )
        self._unsubscribe_v5_callback_set(self.__on_unsubscribe_v5_callback)

    def log_callback_set(self, callback):
        self.__on_log_callback = self._make_wrapper(
            Function.ON_LOG,
            callback,
            lambda mosq, ud, level, msg: callback(
                self, self.userdata(), LogLevel(level), msg.decode()
            ),
        )
        self._log_callback_set(self.__on_log_callback)

    @staticmethod
    def _make_wrapper(decorator, callback, wrapper):
        if not callback:
            wrapper = 0
        return decorator(wrapper)

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
