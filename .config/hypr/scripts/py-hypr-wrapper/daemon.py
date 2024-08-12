import asyncio
import logging
from typing import Set

from hypr_ipc.event_socket import HyprEvents
from local_ipc.listener import PyHyprWrapperListener
from local_objects.timed_action import TimedActionManager
from local_objects.triggerable_action import TriggerableActionManager


class Daemon:
    def __init__(
        self,
        timed_action_manager: TimedActionManager,
        hypr_event_listener: HyprEvents,
        triggerable_action_manager: TriggerableActionManager,
    ):
        self.__timed_action_manager: TimedActionManager = timed_action_manager
        self.__hypr_event_listener: HyprEvents = hypr_event_listener
        self.__triggerable_action_manager: TriggerableActionManager = (
            triggerable_action_manager
        )
        self.__local_request_handler: PyHyprWrapperListener = PyHyprWrapperListener(
            request_handler=self.__triggerable_action_manager.handle_request
        )

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
