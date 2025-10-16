import ctypes as C

from ..core import load_library, LibraryError, check_errno
from ..constants import ErrorCode
from .mosquitto import bind_all, bind

lib = load_library("mosquitto")


class Struct:
    class MQTTMessage(C.Structure):
        _fields_ = (
            ("mid", C.c_int),
            ("topic", C.c_char_p),
            ("payload", C.c_void_p),
            ("payloadlen", C.c_int),
            ("qos", C.c_int),
            ("retain", C.c_bool),
        )
        _payloads_ = {
            "payload": "payloadlen",
        }

    class MQTTString(C.Structure):
        _fields_ = [
            ("v", C.c_void_p),
            ("len", C.c_uint16),
        ]
        _payloads_ = {
            "v": "len",
        }

    class MQTT5PropertyValue(C.Union):
        _objects_ = ("bin", "s")

    MQTT5PropertyValue._fields_ = [
        ("i8", C.c_uint8),
        ("i16", C.c_uint16),
        ("i32", C.c_uint32),
        ("varint", C.c_uint32),
        ("bin", MQTTString),
        ("s", MQTTString),
    ]

    class MQTT5Property(C.Structure):
        _objects_ = ("next", "value")

    MQTT5Property._fields_ = [
        ("next", C.POINTER(MQTT5Property)),
        ("value", MQTT5PropertyValue),
        ("name", MQTTString),
        ("identifier", C.c_int32),
        ("client_generated", C.c_bool),
    ]

    class Will(C.Structure):
        _fields_ = (
            ("topic", C.c_char_p),
            ("payload", C.c_void_p),
            ("payloadlen", C.c_int),
            ("qos", C.c_int),
            ("retain", C.c_bool),
        )
        _payloads_ = {
            "payload": "payloadlen",
        }

    class TLS(C.Structure):
        _fields_ = (
            ("cafile", C.c_char_p),
            ("capath", C.c_char_p),
            ("certfile", C.c_char_p),
            ("keyfile", C.c_char_p),
            ("ciphers", C.c_char_p),
            ("tls_version", C.c_char_p),
            ("pw_callback", C.c_void_p),  # FIXIT
            ("cert_reqs", C.c_int),
        )


class Function:
    ON_CONNECT = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.c_int)
    ON_CONNECT_WITH_FLAGS = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.c_int, C.c_int)
    ON_CONNECT_V5 = C.CFUNCTYPE(
        None, C.c_void_p, C.py_object, C.c_int, C.c_int, C.POINTER(Struct.MQTT5Property)
    )
    ON_DISCONNECT = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.c_int)
    ON_DISCONNECT_V5 = C.CFUNCTYPE(
        None, C.c_void_p, C.py_object, C.c_int, C.POINTER(Struct.MQTT5Property)
    )
    ON_PUBLISH = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.c_int)
    ON_PUBLISH_V5 = C.CFUNCTYPE(
        None, C.c_void_p, C.py_object, C.c_int, C.POINTER(Struct.MQTT5Property)
    )
    ON_MESSAGE = C.CFUNCTYPE(
        None, C.c_void_p, C.py_object, C.POINTER(Struct.MQTTMessage)
    )
    ON_MESSAGE_V5 = C.CFUNCTYPE(
        None,
        C.c_void_p,
        C.py_object,
        C.POINTER(Struct.MQTTMessage),
        C.POINTER(Struct.MQTT5Property),
    )
    ON_SUBSCRIBE = C.CFUNCTYPE(
        None, C.c_void_p, C.py_object, C.c_int, C.c_int, C.POINTER(C.c_int)
    )
    ON_SUBSCRIBE_V5 = C.CFUNCTYPE(
        None,
        C.c_void_p,
        C.py_object,
        C.c_int,
        C.c_int,
        C.POINTER(C.c_int),
        C.POINTER(Struct.MQTT5Property),
    )
    ON_UNSUBSCRIBE = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.c_int)
    ON_UNSUBSCRIBE_V5 = C.CFUNCTYPE(
        None, C.c_void_p, C.py_object, C.c_int, C.POINTER(Struct.MQTT5Property)
    )
    ON_LOG = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.c_int, C.c_char_p)
    PW_CALLBACK = C.CFUNCTYPE(C.c_char_p, C.c_int, C.c_int, C.py_object)


class CType:
    c_int_p = C.POINTER(C.c_int)
    c_mosquitto_p = C.c_void_p
    c_mosquitto_property_p = C.POINTER(Struct.MQTT5Property)
    c_char_pp = C.POINTER(C.c_char_p)
    c_mosquitto_message_p = C.POINTER(Struct.MQTTMessage)
    c_mosquitto_message_pp = C.POINTER(c_mosquitto_message_p)
    c_mosq_opt_t = C.c_int
    c_char_ppp = C.POINTER(c_char_pp)
    c_bool_p = C.POINTER(C.c_bool)
    c_libmosquitto_will_p = C.POINTER(Struct.Will)
    c_libmosquitto_tls_p = C.POINTER(Struct.TLS)
    c_mosquitto_property_pp = C.POINTER(c_mosquitto_property_p)
    c_uint8_t_p = C.POINTER(C.c_uint8)
    c_uint16_t_p = C.POINTER(C.c_uint16)
    c_uint32_t_p = C.POINTER(C.c_uint32)
    c_void_pp = C.POINTER(C.c_void_p)


bind_all(lib, CType)

bind(CType.c_mosquitto_p, lib.mosquitto_new, C.c_char_p, C.c_bool, C.py_object)

bind(C.py_object, lib.mosquitto_userdata, CType.c_mosquitto_p)

# void mosquitto_connect_v5_callback_set(struct mosquitto *mosq, void (*on_connect)(struct mosquitto *, void *, int, int, const mosquitto_property *props));
bind(
    None,
    lib.mosquitto_connect_v5_callback_set,
    CType.c_mosquitto_p,
    Function.ON_CONNECT_V5,
)
# void mosquitto_unsubscribe_callback_set(struct mosquitto *mosq, void (*on_unsubscribe)(struct mosquitto *, void *, int));
bind(
    None,
    lib.mosquitto_unsubscribe_callback_set,
    CType.c_mosquitto_p,
    Function.ON_UNSUBSCRIBE,
)
# void mosquitto_log_callback_set(struct mosquitto *mosq, void (*on_log)(struct mosquitto *, void *, int, const char *));
bind(None, lib.mosquitto_log_callback_set, CType.c_mosquitto_p, Function.ON_LOG)
# void mosquitto_unsubscribe_v5_callback_set(struct mosquitto *mosq, void (*on_unsubscribe)(struct mosquitto *, void *, int, const mosquitto_property *props));
bind(
    None,
    lib.mosquitto_unsubscribe_v5_callback_set,
    CType.c_mosquitto_p,
    Function.ON_UNSUBSCRIBE_V5,
)
# void mosquitto_message_callback_set(struct mosquitto *mosq, void (*on_message)(struct mosquitto *, void *, const struct mosquitto_message *));
bind(None, lib.mosquitto_message_callback_set, CType.c_mosquitto_p, Function.ON_MESSAGE)
# void mosquitto_subscribe_v5_callback_set(struct mosquitto *mosq, void (*on_subscribe)(struct mosquitto *, void *, int, int, const int *, const mosquitto_property *props));
bind(
    None,
    lib.mosquitto_subscribe_v5_callback_set,
    CType.c_mosquitto_p,
    Function.ON_SUBSCRIBE_V5,
)
# void mosquitto_message_v5_callback_set(struct mosquitto *mosq, void (*on_message)(struct mosquitto *, void *, const struct mosquitto_message *, const mosquitto_property *props));
bind(
    None,
    lib.mosquitto_message_v5_callback_set,
    CType.c_mosquitto_p,
    Function.ON_MESSAGE_V5,
)
# int mosquitto_tls_set(struct mosquitto *mosq, const char *cafile, const char *capath, const char *certfile, const char *keyfile, int (*pw_callback)(char *buf, int size, int rwflag, void *userdata));
bind(
    C.c_int,
    lib.mosquitto_tls_set,
    CType.c_mosquitto_p,
    C.c_char_p,
    C.c_char_p,
    C.c_char_p,
    Function.PW_CALLBACK,
)
# void mosquitto_publish_v5_callback_set(struct mosquitto *mosq, void (*on_publish)(struct mosquitto *, void *, int, int, const mosquitto_property *props));
bind(
    None,
    lib.mosquitto_publish_v5_callback_set,
    CType.c_mosquitto_p,
    Function.ON_PUBLISH_V5,
)
# void mosquitto_disconnect_callback_set(struct mosquitto *mosq, void (*on_disconnect)(struct mosquitto *, void *, int));
bind(
    None,
    lib.mosquitto_disconnect_callback_set,
    CType.c_mosquitto_p,
    Function.ON_DISCONNECT,
)
# void mosquitto_disconnect_v5_callback_set(struct mosquitto *mosq, void (*on_disconnect)(struct mosquitto *, void *, int, const mosquitto_property *props));
bind(
    None,
    lib.mosquitto_disconnect_v5_callback_set,
    CType.c_mosquitto_p,
    Function.ON_DISCONNECT_V5,
)
# int mosquitto_subscribe_callback(int (*callback)(struct mosquitto *, void *, const struct mosquitto_message *), void *userdata, const char *topic, int qos, const char *host, int port, const char *client_id, int keepalive, bool clean_session, const char *username, const char *password, const struct libmosquitto_will *will, const struct libmosquitto_tls *tls);
bind(
    C.c_int,
    lib.mosquitto_subscribe_callback,
    CType.c_mosquitto_p,
    Function.ON_SUBSCRIBE,
)
# void mosquitto_publish_callback_set(struct mosquitto *mosq, void (*on_publish)(struct mosquitto *, void *, int));
bind(
    None,
    lib.mosquitto_publish_callback_set,
    CType.c_mosquitto_p,
    Function.ON_PUBLISH,
)
# void mosquitto_connect_callback_set(struct mosquitto *mosq, void (*on_connect)(struct mosquitto *, void *, int));
bind(None, lib.mosquitto_connect_callback_set, CType.c_mosquitto_p, Function.ON_CONNECT)
# void mosquitto_subscribe_callback_set(struct mosquitto *mosq, void (*on_subscribe)(struct mosquitto *, void *, int, int, const int *));
bind(
    None,
    lib.mosquitto_subscribe_callback_set,
    CType.c_mosquitto_p,
    Function.ON_SUBSCRIBE,
)
# void mosquitto_connect_with_flags_callback_set(struct mosquitto *mosq, void (*on_connect)(struct mosquitto *, void *, int, int));
bind(
    None,
    lib.mosquitto_connect_with_flags_callback_set,
    CType.c_mosquitto_p,
    Function.ON_CONNECT_WITH_FLAGS,
)


def strerror(code):
    return lib.mosquitto_strerror(code).decode()


def connack_string(code):
    return lib.mosquitto_connack_string(code).decode()


def reason_string(code):
    return lib.mosquitto_reason_string(code).decode()


class MosquittoError(LibraryError):
    def strerror(self):
        return strerror(self.code)


def check_code(code):
    if code != ErrorCode.SUCCESS:
        if code == ErrorCode.ERRNO:
            check_errno()
        else:
            raise MosquittoError(ErrorCode(code))
    return code


def call(func, *args, check=True):
    if not check:
        C.set_errno(0)
    ret = func(*args)
    if check and func.restype == C.c_int:
        return check_code(ret)
    check_errno()
    return ret
