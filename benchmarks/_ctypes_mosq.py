from ctypes_mosquitto import Mosquitto

from benchmarks import config as c

logger = None

if c.INTERVAL:
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()


def on_message(client, userdata, msg):
    global count
    count += 1
    if c.INTERVAL:
        logger.info("%d: %s %s", count, msg.topic, msg.payload)
    if count == c.AMOUNT:
        print("DONE")
        client.disconnect()


count = 0
client = Mosquitto(logger=logger)
client.connect_callback_set(lambda *_: client.subscribe(c.TOPIC, c.QOS))
client.message_callback_set(on_message)
client.connect_async(c.HOST, c.PORT)

if c.INTERVAL:
    import signal
    from ctypes_mosquitto.bindings import libc

    libc.signal(signal.SIGINT, client.disconnect)

client.loop_forever()
