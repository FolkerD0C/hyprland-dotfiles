import asyncio
import logging
from os import environ
from pathlib import Path
from sys import argv as sys_argv, exit as sys_exit

from constants import PACKAGE_NAME, RUNTIME_DIR
from external_call_handler import PyHyprWrapperEventListener
from helpers import logger_setup
from hyprevents import get_event_handler
from hyprland_stuff import btop_special_workspace, switch_keyboard_layout
from hyprpaper_manager import HyprPaperManager

from utils import TimedAction
from waybar_stuff import (
    keyboard_layout_switched,
    special_workspace_button_onclick,
    special_workspace_displayname,
    on_activespecial,
)

__LOGFILE: Path = Path(
    environ["HOME"], "misc", "logs", PACKAGE_NAME, f"{PACKAGE_NAME}.log"
)

__HYPRPAPER_MANAGER: HyprPaperManager = HyprPaperManager(
    Path(environ["HYPRPAPER_SETTER_WALLPAPER_DIR"])
)

__TIMED_ACTIONS: list = []
__STR_TO_FUNC_TABLE: dict = {
    "_BSW": btop_special_workspace,
    "_SKL": switch_keyboard_layout,
    "_TWC": __HYPRPAPER_MANAGER.toggle_wallpaper_changing,
    "_KLS": keyboard_layout_switched,
    "_SWBO": special_workspace_button_onclick,
    "_SWD": special_workspace_displayname,
}


def register_events():
    logging.info("Registering events")
    get_event_handler().add_handle("activespecial", on_activespecial)


def register_timed_actions():
    logging.info("Registering timed actions")
    __TIMED_ACTIONS.append(
        TimedAction(
            "hyprpaper-setter",
            10,
            __HYPRPAPER_MANAGER.set_wallpapers,
            action_args=[],
            action_kwargs={},
        )
    )


def startup(*, debug_mode: bool = False):
    logger_setup(__LOGFILE, debug_mode=debug_mode)
    logging.info("===STARTING APPLICATION===")
    RUNTIME_DIR.mkdir(exist_ok=True)
    register_events()
    register_timed_actions()


async def timed_action_loop():
    while True:
        for timed_action in __TIMED_ACTIONS:
            await timed_action.secondly_tick()
        await asyncio.sleep(1)


async def async_main():
    logging.info("Entering the (async) main function")
    timed_actions = asyncio.create_task(timed_action_loop())
    event_loop = asyncio.create_task(get_event_handler().async_connect())
    external_call_handler = asyncio.create_task(
        PyHyprWrapperEventListener(__STR_TO_FUNC_TABLE).start()
    )
    return_value = 0
    try:
        await asyncio.wait([timed_actions, event_loop, external_call_handler])
    except Exception as exc:
        logging.fatal(
            "An unexpected exception has happened: %r", str(exc), stack_info=True
        )
        return_value = 1
    finally:
        logging.info("===STOPPING APPLICATION===")
        sys_exit(return_value)


def main():
    debug_mode: bool = (
        "--debug" in sys_argv
        or "--verbose" in sys_argv
        or "debug" in sys_argv
        or "verbose" in sys_argv
    )
    startup(debug_mode=debug_mode)
    asyncio.run(async_main(), debug=debug_mode)


if __name__ == "__main__":
    if not "HYPRLAND_INSTANCE_SIGNATURE" in environ:
        raise EnvironmentError(
            "'HYPRLAND_INSTANCE_SIGNATURE' not found in environment."
        )
    main()
