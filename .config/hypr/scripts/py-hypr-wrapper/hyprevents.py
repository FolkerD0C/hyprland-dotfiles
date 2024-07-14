import asyncio
import logging

from helpers import logged, logged_async
from hyprsocket import HyprEventListener


class HyprEvents:
    def __init__(self):
        self.__events: dict = {}
        self.__listener: HyprEventListener | None = None

    @logged_async
    async def async_connect(self):
        self.__listener = HyprEventListener()
        async for event in self.__listener.start():
            if ">>" in event:
                event_name, args = event.split(">>")
                args = args.split(",")
                await self.emit(event_name, *args)
            else:
                await self.emit(event)

    @logged
    def add_handle(self, event: str, callback: callable):
        if self.__events.get(event):
            self.__events[event].append(callback)
        else:
            self.__events[event] = [callback]
        logging.info("Current events registered are %r", self.__events)

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
