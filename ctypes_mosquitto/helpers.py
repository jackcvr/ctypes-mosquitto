import ctypes as C
import typing as t

from .bindings import lib, check_code


def topic_matches_sub(sub: str, topic: str) -> bool:
    res = C.c_bool(False)
    check_code(
        lib.mosquitto_topic_matches_sub(sub.encode(), topic.encode(), C.byref(res))
    )
    return res.value


class TopicMatcher:
    def __init__(self) -> None:
        self._handlers: dict[str, t.Callable] = {}

    def find(self, topic: str) -> t.Iterator[t.Callable]:
        for sub, func in self._handlers.items():
            if topic_matches_sub(sub, topic):
                yield func

    def set_topic_callback(self, topic: str, callback: t.Callable) -> None:
        if callback is None:
            if topic in self._handlers:
                del self._handlers[topic]
        else:
            self._handlers[topic] = callback

    def on_topic(self, topic: str) -> t.Callable:
        def decorator(func: t.Callable) -> t.Callable:
            self.set_topic_callback(topic, func)
            return func

        return decorator
