import asyncio
from typing import Dict

from local_objects.ipc_objects import LocalIPCRequest, LocalIPCResponse
from local_utilities.local_logging import LOCAL_OBJECTS_LOGGER, LOGGING_TRACE_LEVEL


class TriggerableAction:
    def __init__(
        self,
        *,
        action_id: str,
        short_argname: str | None = None,
        long_argname: str,
        description: str,
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
        if asyncio.iscoroutinefunction(self.__action):
            return_candidate = await self.__action(**action_parameters)
        else:
            return_candidate = self.__action(**action_parameters)
        return return_candidate if return_candidate else {"placeholder": None}


class TriggerableActionManager:
    def __init__(self, triggerable_actions: Dict[str, TriggerableAction] = {}) -> None:
        self.__triggerable_actions: Dict[str, TriggerableAction] = triggerable_actions
        self.__async_lock: asyncio.Lock = asyncio.Lock()

    @property
    def triggerable_actions(self) -> Dict[str, TriggerableAction]:
        return self.__triggerable_actions

    async def add_action(self, action: TriggerableAction) -> None:
        async with self.__async_lock:
            self.triggerable_actions[action.action_id] = action

    async def handle_request(
        self,
        ipc_request: LocalIPCRequest,
    ) -> LocalIPCResponse:
        response_dict: dict = {}
        async with self.__async_lock:
            if not ipc_request.requested_action_name in self.__triggerable_actions:
                LOCAL_OBJECTS_LOGGER.warning(
                    "Action %r not in triggerable_actions",
                    ipc_request.requested_action_name,
                )
                return LocalIPCResponse(
                    ipc_request.initiator_id,
                    False,
                    {
                        "error_message": f"{ipc_request.requested_action_name} is not a valid requested action."
                    },
                )
            try:
                LOCAL_OBJECTS_LOGGER.log(
                    LOGGING_TRACE_LEVEL, "Trying to handle request %r", ipc_request
                )
                response_dict = await self.__triggerable_actions[
                    ipc_request.requested_action_name
                ].trigger(**ipc_request.requested_action_parameters)
            except Exception as exc:
                LOCAL_OBJECTS_LOGGER.warn(
                    "Caught an exception: %r", type(exc).__name__, stack_info=True
                )
                return LocalIPCResponse(
                    ipc_request.initiator_id, False, {"error_message": repr(exc)}
                )
        return LocalIPCResponse(ipc_request.initiator_id, True, response_dict)
