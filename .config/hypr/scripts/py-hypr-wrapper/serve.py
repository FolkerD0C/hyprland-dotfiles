import asyncio
import logging
from os import environ as environment_variables
from pathlib import Path
from sys import argv as sys_argv
from sys import exit as sys_exit
from typing import Dict, Tuple

from daemon import Daemon
from hypr_ipc.event_socket import HyprEvents
from local_actions.hyprland_actions import (
    btop_special_workspace,
    switch_keyboard_layout,
)
from local_actions.hyprpaper_manager import HyprPaperManager
from local_actions.waybar_actions import (
    keyboard_layout_switched,
    on_activespecial,
    special_workspace_button_onclick,
    special_workspace_displayname,
)
from local_objects.timed_action import TimedAction, TimedActionManager
from local_objects.triggerable_action import TriggerableAction, TriggerableActionManager
from local_utilities.local_logging import logger_setup
from local_utilities.mappings import create_triggerable_actions
from local_utilities.paths import (
    PY_HYPR_WRAPPER_DAEMON_LOCK,
    PY_HYPR_WRAPPER_DAEMON_LOG,
    PY_HYPR_WRAPPER_RUNTIME_DIR,
)


def __register_events() -> HyprEvents:
    logging.info("Registering events")
    hypr_event_listener = HyprEvents()
    hypr_event_listener.add_handle("activespecial", on_activespecial)
    return hypr_event_listener


def __set_triggerable_actions(
    triggerable_actions: Dict[str, TriggerableAction]
) -> Dict[str, TriggerableAction]:
    logging.info("Setting triggerable actions")
    triggerable_actions["btop_special_workspace"].set_action(btop_special_workspace)
    triggerable_actions["keyboard_layout_switched"].set_action(keyboard_layout_switched)
    triggerable_actions["special_workspace_button_onclick"].set_action(
        special_workspace_button_onclick
    )
    triggerable_actions["special_workspace_displayname"].set_action(
        special_workspace_displayname
    )
    triggerable_actions["switch_keyboard_layout"].set_action(switch_keyboard_layout)
    triggerable_actions["toggle_wallpaper_changing"].set_action(
        __hyprpaper_manager.toggle_wallpaper_changing
    )
    return triggerable_actions


def __register_timed_actions() -> TimedActionManager:
    logging.info("Registering timed actions")
    return TimedActionManager(
        [TimedAction("hyprpaper_setter", 10, __hyprpaper_manager.set_wallpapers)]
    )


def __register_triggerable_actions(
    actions: Dict[str, TriggerableActionManager]
) -> TriggerableActionManager:
    logging.info("Registering triggerable actions")
    return TriggerableActionManager(actions)


def setup(
    debug_mode,
) -> Tuple[HyprEvents, TimedActionManager, TriggerableActionManager]:
    global __hyprpaper_manager
    logger_setup(
        logfile=PY_HYPR_WRAPPER_DAEMON_LOG,
        handlers=["console", "rotating_file"],
        debug_mode=debug_mode,
    )
    logging.info("===Starting setup===")
    __hyprpaper_manager = HyprPaperManager(
        Path(environment_variables["HYPRPAPER_SETTER_WALLPAPER_DIR"])
    )
    hypr_event_listener = __register_events()
    timed_action_manager = __register_timed_actions()
    triggerable_actions = create_triggerable_actions()
    triggerable_actions = __set_triggerable_actions(triggerable_actions)
    triggerable_action_manager = __register_triggerable_actions(triggerable_actions)
    return (hypr_event_listener, timed_action_manager, triggerable_action_manager)


def create_lock():
    if PY_HYPR_WRAPPER_DAEMON_LOCK.exists():
        raise RuntimeError("Lockfile exists")
    PY_HYPR_WRAPPER_RUNTIME_DIR.mkdir(parents=False, exist_ok=True)
    PY_HYPR_WRAPPER_DAEMON_LOCK.touch()


def main():
    create_lock()
    hypr_event_listener, timed_action_manager, triggerable_action_manager = setup(
        "--debug" in sys_argv
    )
    py_hypr_wrapper_daemon = Daemon(
        timed_action_manager, hypr_event_listener, triggerable_action_manager
    )
    exit_code = asyncio.run(py_hypr_wrapper_daemon.start_daemon())
    logging.info("===Stopping application===")
    PY_HYPR_WRAPPER_DAEMON_LOCK.unlink(missing_ok=True)
    sys_exit(exit_code)


if __name__ == "__main__":
    main()
