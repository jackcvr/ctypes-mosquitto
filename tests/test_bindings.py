import ctypes as C
import threading

from ctypes_mosquitto.bindings import (
    lib,
    strerror,
    connack_string,
    reason_string,
    call,
    Function,
)
from ctypes_mosquitto import constants as c

from constants import USERNAME, PASSWORD, HOST, PORT


def test_strerror():
    msg = strerror(c.ErrorCode.NOMEM)
    assert msg == "Out of memory."


def test_connack_string():
    msg = connack_string(c.ConnackCode.REFUSED_NOT_AUTHORIZED)
    assert msg == "Connection Refused: not authorised."


def test_reason_string():
    msg = reason_string(c.ReasonCode.BANNED)
    assert msg == "Banned"


def test_minimal_workflow():
    @Function.ON_CONNECT
    def on_connect(mosq_p, userdata, rc):
        assert rc == c.ConnackCode.ACCEPTED
        is_connected.set()

    @Function.ON_SUBSCRIBE
    def on_subscribe(mosq_p, userdata, rc, qos, qos_granted):
        assert qos == 1
        assert qos_granted[0] == 1
        is_subscribed.set()

    @Function.ON_MESSAGE
    def on_message(mosq_p, userdata, msg):
        msg = msg.contents
        assert C.string_at(msg.payload, msg.payloadlen) == b"123"
        is_received.set()

    is_connected = threading.Event()
    is_subscribed = threading.Event()
    is_received = threading.Event()

    call(lib.mosquitto_lib_init)
    mosq_p = None
    try:
        mosq_p = call(lib.mosquitto_new, None, True, None, check=False)
        call(
            lib.mosquitto_username_pw_set, mosq_p, USERNAME.encode(), PASSWORD.encode()
        )
        call(lib.mosquitto_connect_callback_set, mosq_p, on_connect)
        call(lib.mosquitto_subscribe_callback_set, mosq_p, on_subscribe)
        call(lib.mosquitto_message_callback_set, mosq_p, on_message)
        call(lib.mosquitto_connect, mosq_p, HOST.encode(), PORT, 60)
        call(lib.mosquitto_loop_start, mosq_p)
        assert is_connected.wait(1)
        mid = C.c_int(0)
        call(lib.mosquitto_subscribe, mosq_p, C.byref(mid), b"test", 1)
        assert is_subscribed.wait(1)
        call(lib.mosquitto_publish, mosq_p, C.byref(mid), b"test", 3, b"123", 1, False)
        assert is_received.wait(1)
        call(lib.mosquitto_disconnect, mosq_p)
    finally:
        if mosq_p:
            lib.mosquitto_destroy(mosq_p)
        lib.mosquitto_lib_cleanup()
