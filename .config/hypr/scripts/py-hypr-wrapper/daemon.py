import asyncio
import logging
from typing import Dict, Set

from hypr_ipc.event_socket import HyprEvents
from local_ipc.listener import PyHyprWrapperListenerListener
from local_objects.ipc_objects import LocalIPCRequest, LocalIPCResponse
from local_objects.timed_action import TimedActionManager
from local_objects.triggerable_action import TriggerableAction
from local_utilities.constants import LOGGING_TRACE_LEVEL

triggerable_action_map: Dict[str, TriggerableAction] = {}


async def handle_triggerable_action_requests(
    ipc_request: LocalIPCRequest,
) -> LocalIPCResponse:
    if not ipc_request.requested_action_name in triggerable_action_map:
        logging.warning("Action %r not in triggerable_actions", triggerable_action_map)
        return LocalIPCResponse(
            ipc_request.initiator_id,
            False,
            {
                "error_message": f"{ipc_request.requested_action_name} is not a valid requested action."
            },
        )
    response_dict: dict = {}
    try:
        logging.log(LOGGING_TRACE_LEVEL, "Trying to handle request %r", ipc_request)
        response_dict = await triggerable_action_map[
            ipc_request.requested_action_name
        ].trigger(**ipc_request.requested_action_parameters)
    except Exception as exc:
        logging.warn("Caught an exception: %r", type(exc).__name__, stack_info=True)
        return LocalIPCResponse(
            ipc_request.initiator_id, False, {"error_message": repr(exc)}
        )
    return LocalIPCResponse(ipc_request.initiator_id, True, response_dict)


class Daemon:
    def __init__(
        self,
        timed_action_manager: TimedActionManager,
        hypr_event_listener: HyprEvents,
        triggerable_actions: Dict[str, TriggerableAction],
    ):
        global triggerable_action_map
        self.__timed_action_manager: TimedActionManager = timed_action_manager
        self.__hypr_event_listener: HyprEvents = hypr_event_listener
        self.__local_request_handler: PyHyprWrapperListenerListener = (
            PyHyprWrapperListenerListener(
                request_handler=handle_triggerable_action_requests
            )
        )
        triggerable_action_map = triggerable_actions

    async def start_daemon(self) -> int:
        logging.debug("Creating tasks")
        timed_actions_task = asyncio.create_task(
            self.__timed_action_manager.tick_indefinitely()
        )
        hypr_events_task = asyncio.create_task(
            self.__hypr_event_listener.async_connect()
        )
        local_requests_task = asyncio.create_task(
            self.__local_request_handler.start_listening_to_requests()
        )
        logging.info("Starting daemon")
        return_value = 0
        pending_tasks: Set[asyncio.Future] | None = None
        try:
            _, pending_tasks = await asyncio.wait(
                [timed_actions_task, hypr_events_task, local_requests_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
        except Exception as exc:
            logging.fatal(
                "An unexpected exception has happened: %r", str(exc), stack_info=True
            )
            return_value = 1
        if pending_tasks:
            logging.warn("There are running tasks that are going to be cancelled")
            for pending_task in pending_tasks:
                pending_task.cancel()
        logging.info("Daemon has stopped")
        return return_value
