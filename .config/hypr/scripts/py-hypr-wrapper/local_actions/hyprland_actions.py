from os import kill as send_signal
from signal import Signals

from hypr_ipc.ipc_socket import async_command_send
from local_actions.waybar_actions import get_waybar_pid
from local_utilities.constants import LOGGING_TRACE_LEVEL
from local_utilities.local_logging import LOCAL_ACTIONS_LOGGER
from local_utilities.mappings import WaybarSignals
from local_utilities.wrappers import logged_async

__BTOP_SW_NAME: str = "btop_sw"
__btop_sw_toggled: bool = False


@logged_async
async def btop_special_workspace(**_):
    global __btop_sw_toggled
    workspaces_list: list = await async_command_send("workspaces")
    btop_sw_exists: bool = False
    for workspace in workspaces_list:
        if workspace["name"] == f"special:{__BTOP_SW_NAME}":
            LOCAL_ACTIONS_LOGGER.debug("Special workspace %r exists", __BTOP_SW_NAME)
            btop_sw_exists = True
            break
    if not btop_sw_exists:
        LOCAL_ACTIONS_LOGGER.info("Starting special workspace %r", __BTOP_SW_NAME)
        dispatch_exec_resp = await async_command_send(
            f"dispatch exec [workspace special:{__BTOP_SW_NAME} silent] kitty btop",
            return_json=False,
        )
        LOCAL_ACTIONS_LOGGER.log(
            LOGGING_TRACE_LEVEL,
            "Response for dispatch exec btop was %r",
            dispatch_exec_resp,
        )
    LOCAL_ACTIONS_LOGGER.debug("Toggling special workspace %r", __BTOP_SW_NAME)
    dispatch_togglespecialworkspace_resp = await async_command_send(
        f"dispatch togglespecialworkspace {__BTOP_SW_NAME}", return_json=False
    )
    LOCAL_ACTIONS_LOGGER.log(
        LOGGING_TRACE_LEVEL,
        "Response for dispatch togglespecialworkspace was %r",
        dispatch_togglespecialworkspace_resp,
    )


@logged_async
async def switch_keyboard_layout(**_):
    device_list: list = await async_command_send("devices")
    keyboard_list: list = device_list["keyboards"]
    active_keyboard: str = ""
    for keyboard in keyboard_list:
        if keyboard["main"]:
            active_keyboard = keyboard["name"]
            LOCAL_ACTIONS_LOGGER.debug("Found active keyboard: %r", active_keyboard)
            break
    if not active_keyboard:
        LOCAL_ACTIONS_LOGGER.warn("Active keyboard layout not found")
        return
    switchxkblayout_resp = await async_command_send(
        f"switchxkblayout {active_keyboard} next", return_json=False
    )
    LOCAL_ACTIONS_LOGGER.log(
        LOGGING_TRACE_LEVEL, "Response for switchxkblayout was %r", switchxkblayout_resp
    )
    LOCAL_ACTIONS_LOGGER.debug("Sending signal to waybar")
    send_signal(
        get_waybar_pid(),
        int(Signals.SIGRTMIN.value) + WaybarSignals.KEYBOARD_LAYOUT_SWITCHED,
    )
