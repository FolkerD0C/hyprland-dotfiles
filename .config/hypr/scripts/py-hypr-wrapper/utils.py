import asyncio
import logging

from constants import TRACE_LVL


class TimedAction:
    def __init__(
        self,
        action_name: str,
        timer_seconds: int,
        action: callable,
        *,
        action_args: list,
        action_kwargs: dict
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
        logging.debug(
            "Setting the timer seconds of %r from %r to %r",
            self.__action_name,
            self.timer_seconds,
            new_value,
        )
        self.__timer_seconds = new_value

    async def __trigger_action(self) -> None:
        logging.info("Triggering %r", self.__action_name)
        if asyncio.iscoroutinefunction(self.__action):
            await self.__action(self.__action_args, self.__action_kwargs)
        else:
            self.__action(self.__action_args, self.__action_kwargs)

    async def secondly_tick(self) -> None:
        logging.log(
            TRACE_LVL, "Secondly trigger has arrived for %r", self.__action_name
        )
        self.__remaining_seconds = self.__remaining_seconds - 1
        if self.__remaining_seconds == 0:
            await self.__trigger_action()
            self.__remaining_seconds = self.__timer_seconds
