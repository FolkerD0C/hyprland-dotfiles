import asyncio
import logging
from typing import Dict

from hypr_ipc.ipc_socket import HyprEventListener
from local_utilities.constants import LOGGING_TRACE_LEVEL
from local_utilities.local_logging import HYPR_IPC_LOGGER
from local_utilities.wrappers import logged, logged_async


class HyprEvents:
    def __init__(self):
        self.__events: Dict[str, list] = {}
        self.__listener: HyprEventListener | None = None

    @logged_async
    async def async_connect(self):
        self.__listener = HyprEventListener()
        async for event in self.__listener.start():
            HYPR_IPC_LOGGER.log(LOGGING_TRACE_LEVEL, "Got event: %r", event)
            try:
                if ">>" in event:
                    event_details = event.split(">>")
                    event_name = event_details[0]
                    args_str = "".join(event_details[1:])
                    args = args_str.split(",")
                    await self.emit(event_name, *args)
                else:
                    await self.emit(event)
            except Exception as exc:
                logging.exception(
                    "While processing event (%r) we got an exception: %r",
                    event,
                    repr(exc),
                    stack_info=True,
                )
                raise exc

    @logged
    def add_handle(self, event: str, callback: callable):
        if self.__events.get(event):
            self.__events[event].append(callback)
        else:
            self.__events[event] = [callback]
        HYPR_IPC_LOGGER.info("Current events registered are %r", self.__events)

    def remove_handle(self, event: str, callback: callable):
        if self.__events.get(event):
            self.__events[event].remove(callback)
        else:
            raise AttributeError(f"Event {event} not found")

    async def emit(self, event: str, *args, **kwargs):
        if event in self.__events:
            for callback in self.__events[event]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)


__main_event_handler: HyprEvents | None = None


def get_event_handler():
    global __main_event_handler
    if __main_event_handler == None:
        __main_event_handler = HyprEvents()
    return __main_event_handler
