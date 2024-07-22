from asyncio import iscoroutinefunction

from local_utilities.local_logging import LOCAL_OBJECTS_LOGGER


class TriggerableAction:
    def __init__(
        self,
        *,
        action_id: str,
        short_argname: str | None = None,
        long_argname: str,
        description: str
    ) -> None:
        self.__action_id: str = action_id
        self.__short_argname: str | None = short_argname or None
        self.__long_argname: str = long_argname
        self.__description: str = description
        self.__action: callable | None = None
        self.__action_set: bool = False

    @property
    def action_id(self) -> str:
        return self.__action_id

    @property
    def short_argname(self) -> str | None:
        return self.__short_argname

    @property
    def long_argname(self) -> str:
        return self.__long_argname

    @property
    def description(self) -> str:
        return self.__description

    def set_action(self, action: callable):
        if self.__action_set:
            raise RuntimeError("Action is already set.")
        LOCAL_OBJECTS_LOGGER.debug(
            "Setting action to %r for %r", str(action), self.__action_id
        )
        self.__action = action
        self.__action_set = True

    async def trigger(self, **action_parameters: dict) -> dict:
        if not self.__action_set:
            raise RuntimeError("There is no action to trigger.")
        LOCAL_OBJECTS_LOGGER.debug("Triggering action: %r", self.__action_id)
        return_candidate: dict = {}
        if iscoroutinefunction(self.__action):
            return_candidate = await self.__action(**action_parameters)
        else:
            return_candidate = self.__action(**action_parameters)
        return return_candidate if return_candidate else {"placeholder": None}
