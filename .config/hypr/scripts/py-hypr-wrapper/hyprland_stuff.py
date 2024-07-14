import logging
from os import kill as send_signal
from signal import Signals

from constants import TRACE_LVL, WaybarSignals
from helpers import logged_async
from hyprsocket import async_command_send
from waybar_stuff import get_waybar_pid

BTOP_SW_NAME: str = "btop_sw"
btop_sw_toggled: bool = False


@logged_async
async def btop_special_workspace():
    global btop_sw_toggled
    workspaces_list: list = await async_command_send("workspaces")
    btop_sw_exists: bool = False
    for workspace in workspaces_list:
        if workspace["name"] == f"special:{BTOP_SW_NAME}":
            logging.debug("Special workspace %r exists", BTOP_SW_NAME)
            btop_sw_exists = True
            break
    if not btop_sw_exists:
        logging.info("Starting special workspace %r", BTOP_SW_NAME)
        dispatch_exec_resp = await async_command_send(
            f'dispatch exec [workspace special:{BTOP_SW_NAME} silent] kitty btop',
            return_json=False,
        )
        logging.log(
            TRACE_LVL, "Response for dispatch exec btop was %r", dispatch_exec_resp
        )
    logging.debug("Toggling special workspace %r", BTOP_SW_NAME)
    dispatch_togglespecialworkspace_resp = await async_command_send(
        f"dispatch togglespecialworkspace {BTOP_SW_NAME}", return_json=False
    )
    logging.log(
        TRACE_LVL,
        "Response for dispatch togglespecialworkspace was %r",
        dispatch_togglespecialworkspace_resp,
    )


@logged_async
async def switch_keyboard_layout():
    device_list: list = await async_command_send("devices")
    keyboard_list: list = device_list["keyboards"]
    active_keyboard: str = ""
    for keyboard in keyboard_list:
        if keyboard["main"]:
            active_keyboard = keyboard["name"]
            logging.debug("Found active keyboard: %r", active_keyboard)
            break
    if not active_keyboard:
        logging.warn("Active keyboard layout not found")
        return
    switchxkblayout_resp = await async_command_send(
        f"switchxkblayout {active_keyboard} next", return_json=False
    )
    logging.log(TRACE_LVL, "Response for switchxkblayout was %r", switchxkblayout_resp)
    logging.debug("Sending signal to waybar")
    send_signal(
        get_waybar_pid(),
        int(Signals.SIGRTMIN.value) + WaybarSignals.KEYBOARD_LAYOUT_SWITCHED,
    )
