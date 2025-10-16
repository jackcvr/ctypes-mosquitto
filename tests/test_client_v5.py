import threading

import pytest

from ctypes_mosquitto.constants import ConnackCode, ProtocolVersion, PropertyId
from ctypes_mosquitto.client import Property

import constants as c


@pytest.fixture
def client(client_factory):
    def _on_connect(client, userdata, rc):
        if rc != ConnackCode.ACCEPTED:
            raise RuntimeError(f"Client connection error: {rc.value}/{rc.name}")
        is_connected.set()

    client = client_factory(protocol=ProtocolVersion.MQTTv5)
    is_connected = threading.Event()
    client.connect_callback_set(_on_connect)
    client.connect(c.HOST, c.PORT)
    client.loop_start()
    assert is_connected.wait(1)
    client.on_connect = None
    try:
        yield client
    finally:
        client.disconnect(strict=False)


def test_v5_props(client):
    def _on_sub(client, userdata, mid, count, granted_qos, props):
        is_sub.set()

    def _on_message(client, userdata, msg, props):
        userdata.prop = props.find(PropertyId.MESSAGE_EXPIRY_INTERVAL)
        is_recv.set()

    is_sub = threading.Event()
    is_recv = threading.Event()
    client.subscribe_v5_callback_set(_on_sub)
    client.message_v5_callback_set(_on_message)

    client.subscribe("test", 1)
    assert is_sub.wait(1)

    test_value = 69
    prop = Property.add(None, PropertyId.MESSAGE_EXPIRY_INTERVAL, test_value)
    client.publish("test", "123", qos=1, props=prop)

    assert is_recv.wait(1)
    ud = client.userdata()
    assert ud.prop.value == test_value
