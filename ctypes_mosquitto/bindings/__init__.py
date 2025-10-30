import ctypes as C

from ..core import load_library, LibraryError, check_errno
from ..constants import ErrorCode, PropertyId
from .mosquitto import bind_all, bind

lib = load_library("mosquitto")


class Struct:
    class Message(C.Structure):
        _fields_ = (
            ("mid", C.c_int),
            ("topic", C.c_char_p),
            ("payload", C.c_void_p),
            ("payloadlen", C.c_int),
            ("qos", C.c_int),
            ("retain", C.c_bool),
        )

    class String(C.Structure):
        _fields_ = [
            ("v", C.c_void_p),
            ("len", C.c_uint16),
        ]

    class PropertyValue(C.Union):
        pass

    PropertyValue._fields_ = [
        ("i8", C.c_uint8),
        ("i16", C.c_uint16),
        ("i32", C.c_uint32),
        ("varint", C.c_uint32),
        ("bin", String),
        ("s", String),
    ]

    class Property(C.Structure):
        pass

    Property._fields_ = [
        ("next", C.POINTER(Property)),
        ("value", PropertyValue),
        ("name", String),
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

    class TLS(C.Structure):
        _fields_ = [
            ("cafile", C.c_char_p),
            ("capath", C.c_char_p),
            ("certfile", C.c_char_p),
            ("keyfile", C.c_char_p),
            ("ciphers", C.c_char_p),
            ("tls_version", C.c_char_p),
            ("pw_callback", C.c_void_p),
            ("cert_reqs", C.c_int),
        ]


class Function:
    ON_CONNECT = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.c_int)
    ON_CONNECT_WITH_FLAGS = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.c_int, C.c_int)
    ON_CONNECT_V5 = C.CFUNCTYPE(
        None, C.c_void_p, C.py_object, C.c_int, C.c_int, C.POINTER(Struct.Property)
    )
    ON_DISCONNECT = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.c_int)
    ON_DISCONNECT_V5 = C.CFUNCTYPE(
        None, C.c_void_p, C.py_object, C.c_int, C.POINTER(Struct.Property)
    )
    ON_PUBLISH = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.c_int)
    ON_PUBLISH_V5 = C.CFUNCTYPE(
        None, C.c_void_p, C.py_object, C.c_int, C.POINTER(Struct.Property)
    )
    ON_MESSAGE = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.POINTER(Struct.Message))
    ON_MESSAGE_V5 = C.CFUNCTYPE(
        None,
        C.c_void_p,
        C.py_object,
        C.POINTER(Struct.Message),
        C.POINTER(Struct.Property),
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
        C.POINTER(Struct.Property),
    )
    ON_UNSUBSCRIBE = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.c_int)
    ON_UNSUBSCRIBE_V5 = C.CFUNCTYPE(
        None, C.c_void_p, C.py_object, C.c_int, C.POINTER(Struct.Property)
    )
    ON_LOG = C.CFUNCTYPE(None, C.c_void_p, C.py_object, C.c_int, C.c_char_p)
    PW_CALLBACK = C.CFUNCTYPE(C.c_char_p, C.c_int, C.c_int, C.py_object)


Struct.TLS._fields_[6] = ("pw_callback", C.POINTER(Function.PW_CALLBACK))


class CType:
    int_p = C.POINTER(C.c_int)
    mosquitto_p = C.c_void_p
    mosquitto_property_p = C.POINTER(Struct.Property)
    char_pp = C.POINTER(C.c_char_p)
    mosquitto_message_p = C.POINTER(Struct.Message)
    mosquitto_message_pp = C.POINTER(mosquitto_message_p)
    mosq_opt_t = C.c_int
    char_ppp = C.POINTER(char_pp)
    bool_p = C.POINTER(C.c_bool)
    libmosquitto_will_p = C.POINTER(Struct.Will)
    libmosquitto_tls_p = C.POINTER(Struct.TLS)
    mosquitto_property_pp = C.POINTER(mosquitto_property_p)
    uint8_t_p = C.POINTER(C.c_int8)
    uint16_t_p = C.POINTER(C.c_int16)
    uint32_t_p = C.POINTER(C.c_int32)
    void_pp = C.POINTER(C.c_void_p)


bind_all(lib, CType)

bind(CType.mosquitto_p, lib.mosquitto_new, C.c_char_p, C.c_bool, C.py_object)
bind(C.py_object, lib.mosquitto_userdata, CType.mosquitto_p)

# void mosquitto_connect_with_flags_callback_set(struct mosquitto *mosq, void (*on_connect)(struct mosquitto *, void *, int, int));
bind(
    None,
    lib.mosquitto_connect_with_flags_callback_set,
    CType.mosquitto_p,
    Function.ON_CONNECT_WITH_FLAGS,
)
# int mosquitto_subscribe_callback( int (*callback)(struct mosquitto *, void *, const struct mosquitto_message *), void *userdata, const char *topic, int qos, const char *host, int port, const char *client_id, int keepalive, bool clean_session, const char *username, const char *password, const struct libmosquitto_will *will, const struct libmosquitto_tls *tls);
bind(
    C.c_int,
    lib.mosquitto_subscribe_callback,
    CType.mosquitto_p,
    Function.ON_SUBSCRIBE,
    C.py_object,
    C.c_char_p,
    C.c_int,
    C.c_char_p,
    C.c_int,
    C.c_char_p,
    C.c_int,
    C.c_bool,
    C.c_char_p,
    C.c_char_p,
    C.POINTER(Struct.Will),
    C.POINTER(Struct.TLS),
)
# int mosquitto_tls_set(struct mosquitto *mosq, const char *cafile, const char *capath, const char *certfile, const char *keyfile, int (*pw_callback)(char *buf, int size, int rwflag, void *userdata));
bind(
    C.c_int,
    lib.mosquitto_tls_set,
    CType.mosquitto_p,
    C.c_char_p,
    C.c_char_p,
    C.c_char_p,
    Function.PW_CALLBACK,
)
# void mosquitto_message_v5_callback_set(struct mosquitto *mosq, void (*on_message)(struct mosquitto *, void *, const struct mosquitto_message *, const mosquitto_property *props));
bind(
    None,
    lib.mosquitto_message_v5_callback_set,
    CType.mosquitto_p,
    Function.ON_MESSAGE_V5,
)
# void mosquitto_unsubscribe_v5_callback_set(struct mosquitto *mosq, void (*on_unsubscribe)(struct mosquitto *, void *, int, const mosquitto_property *props));
bind(
    None,
    lib.mosquitto_unsubscribe_v5_callback_set,
    CType.mosquitto_p,
    Function.ON_UNSUBSCRIBE_V5,
)
# void mosquitto_publish_v5_callback_set(struct mosquitto *mosq, void (*on_publish)(struct mosquitto *, void *, int, int, const mosquitto_property *props));
bind(
    None,
    lib.mosquitto_publish_v5_callback_set,
    CType.mosquitto_p,
    Function.ON_PUBLISH_V5,
)
# void mosquitto_subscribe_v5_callback_set(struct mosquitto *mosq, void (*on_subscribe)(struct mosquitto *, void *, int, int, const int *, const mosquitto_property *props));
bind(
    None,
    lib.mosquitto_subscribe_v5_callback_set,
    CType.mosquitto_p,
    Function.ON_SUBSCRIBE_V5,
)
# void mosquitto_connect_callback_set(struct mosquitto *mosq, void (*on_connect)(struct mosquitto *, void *, int));
bind(None, lib.mosquitto_connect_callback_set, CType.mosquitto_p, Function.ON_CONNECT)
# void mosquitto_unsubscribe_callback_set(struct mosquitto *mosq, void (*on_unsubscribe)(struct mosquitto *, void *, int));
bind(
    None,
    lib.mosquitto_unsubscribe_callback_set,
    CType.mosquitto_p,
    Function.ON_UNSUBSCRIBE,
)
# void mosquitto_subscribe_callback_set(struct mosquitto *mosq, void (*on_subscribe)(struct mosquitto *, void *, int, int, const int *));
bind(
    None, lib.mosquitto_subscribe_callback_set, CType.mosquitto_p, Function.ON_SUBSCRIBE
)
# void mosquitto_log_callback_set(struct mosquitto *mosq, void (*on_log)(struct mosquitto *, void *, int, const char *)); """
bind(
    None,
    lib.mosquitto_log_callback_set,
    CType.mosquitto_p,
    Function.ON_UNSUBSCRIBE_V5,
)
# void mosquitto_message_callback_set(struct mosquitto *mosq, void (*on_message)(struct mosquitto *, void *, const struct mosquitto_message *));
bind(None, lib.mosquitto_message_callback_set, CType.mosquitto_p, Function.ON_MESSAGE)
# void mosquitto_disconnect_v5_callback_set(struct mosquitto *mosq, void (*on_disconnect)(struct mosquitto *, void *, int, const mosquitto_property *props));
bind(
    None,
    lib.mosquitto_disconnect_v5_callback_set,
    CType.mosquitto_p,
    Function.ON_DISCONNECT_V5,
)
# void mosquitto_connect_v5_callback_set(struct mosquitto *mosq, void (*on_connect)(struct mosquitto *, void *, int, int, const mosquitto_property *props));
bind(
    None,
    lib.mosquitto_connect_v5_callback_set,
    CType.mosquitto_p,
    Function.ON_CONNECT_V5,
)
# void mosquitto_disconnect_callback_set(struct mosquitto *mosq, void (*on_disconnect)(struct mosquitto *, void *, int));
bind(
    None,
    lib.mosquitto_disconnect_callback_set,
    CType.mosquitto_p,
    Function.ON_DISCONNECT,
)
# void mosquitto_publish_callback_set(struct mosquitto *mosq, void (*on_publish)(struct mosquitto *, void *, int));
bind(
    None,
    lib.mosquitto_publish_callback_set,
    CType.mosquitto_p,
    Function.ON_PUBLISH,
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


def string_to_property_info(identifier: PropertyId):
    type_ = C.c_int(0)
    call(
        lib.mosquitto_string_to_property_info,
        identifier,
        C.byref(C.c_int(0)),
        C.byref(type_),
    )
    return type_.value
