import asyncio
from typing import Callable, List

from local_utilities.constants import LOGGING_TRACE_LEVEL
from local_utilities.local_logging import LOCAL_OBJECTS_LOGGER


class TimedAction:
    def __init__(
        self,
        action_name: str,
        timer_seconds: int,
        action: Callable[..., None],
        *,
        action_args: list = [],
        action_kwargs: dict = {}
    ):
        self.__action_name: str = action_name
        self.__timer_seconds: int = timer_seconds
        self.__action: function = action
        self.__action_args: list = action_args
        self.__action_kwargs: dict = action_kwargs
        self.__remaining_seconds: int = 1

    @property
    def action_name(self) -> str:
        return self.__action_name

    @property
    def timer_seconds(self) -> int:
        return self.__timer_seconds

    @timer_seconds.setter
    def timer_seconds(self, new_value: int) -> None:
        LOCAL_OBJECTS_LOGGER.debug(
            "Setting the timer seconds of %r from %r to %r",
            self.__action_name,
            self.timer_seconds,
            new_value,
        )
        self.__timer_seconds = new_value

    async def __trigger_action(self) -> None:
        LOCAL_OBJECTS_LOGGER.info("Triggering %r", self.__action_name)
        if asyncio.iscoroutinefunction(self.__action):
            await self.__action(*self.__action_args, **self.__action_kwargs)
        else:
            self.__action(*self.__action_args, **self.__action_kwargs)

    async def secondly_tick(self) -> None:
        LOCAL_OBJECTS_LOGGER.log(
            LOGGING_TRACE_LEVEL,
            "Secondly trigger has arrived for %r",
            self.__action_name,
        )
        self.__remaining_seconds = self.__remaining_seconds - 1
        if self.__remaining_seconds == 0:
            await self.__trigger_action()
            self.__remaining_seconds = self.__timer_seconds


class TimedActionManager:
    def __init__(self, *timed_actions: List[TimedAction]):
        self.__timed_actions: List[TimedAction] = timed_actions

    async def tick_indefinitely(self):
        while True:
            awaitable_actions = [
                asyncio.create_task(timed_action.secondly_tick())
                for timed_action in self.__timed_actions
            ]
            sleep_task = asyncio.create_task(asyncio.sleep(1))
            await asyncio.wait(
                [*awaitable_actions, sleep_task],
                return_when=asyncio.ALL_COMPLETED,
            )
