import logging
from os import kill as send_signal
from signal import Signals
from subprocess import check_output

from constants import TRACE_LVL, KEYBOARD_LAYOUTS, WaybarOutputFiles, WaybarSignals
from helpers import logged, logged_async
from hyprsocket import async_command_send

__waybar_pid: int = -1
__DEFAULT_KEYBOARD_LAYOUT_DISPLAYNAME: str = "DEF_0"
__current_special_workspace: str = ""

__ACTIVE_SPECIAL_DISPLAY_STRING: str = '<span size="125%">󰰢</span>'
__INACTIVE_SPECIAL_DISPLAY_STRING: str = '<span size="125%">󰰣</span>'

__MAIN_SPECIAL_WORKSPACE_NAME: str = "status"


def get_waybar_pid() -> int:
    global __waybar_pid
    if __waybar_pid < 0:
        __waybar_pid = int(check_output(["pidof", "waybar"]).decode().strip())
    return __waybar_pid


@logged_async
async def keyboard_layout_switched():
    device_list: dict = await async_command_send("devices")
    keyboard_list: list = device_list["keyboards"]
    active_layout: str = ""
    for keyboard in keyboard_list:
        if keyboard["main"]:
            active_layout = keyboard["active_keymap"]
            logging.debug("Found active keyboard layout: %r", active_layout)
            break
    if not active_layout:
        logging.warn("Active keyboard layout not found")
        return
    active_layout_displayname: str = (
        KEYBOARD_LAYOUTS[active_layout]
        if active_layout in KEYBOARD_LAYOUTS
        else __DEFAULT_KEYBOARD_LAYOUT_DISPLAYNAME
    )
    if active_layout_displayname == __DEFAULT_KEYBOARD_LAYOUT_DISPLAYNAME:
        logging.warn("No displayname found for %r", active_layout)
    logging.debug("Writing active layout to output file")
    with open(WaybarOutputFiles.ACTIVE_KEYBOARD_LAYOUT.value, mode="tw") as outfile:
        outfile.write(f"{active_layout_displayname}\n{active_layout}")


@logged_async
async def special_workspace_displayname():
    displaystring: str = (
        __ACTIVE_SPECIAL_DISPLAY_STRING
        if __current_special_workspace
        else __INACTIVE_SPECIAL_DISPLAY_STRING
    )
    logging.debug(
        "Got current special workspace name (if any): %r", __current_special_workspace
    )
    with open(
        WaybarOutputFiles.SPECIAL_WORKSPACE_DISPLAYNAME.value, mode="tw"
    ) as outfile:
        outfile.write((f"{displaystring}\n{__current_special_workspace}"))


@logged
def on_activespecial(workspace_name: str, _: str):
    global __current_special_workspace
    logging.debug("Current special workspace (if any) is %r", workspace_name)
    __current_special_workspace = workspace_name.replace("special:", "")
    logging.debug("Sending signal to waybar")
    send_signal(
        get_waybar_pid(), Signals.SIGRTMIN + WaybarSignals.SPECIAL_WORKSPACE_TOGGLED
    )


@logged_async
async def special_workspace_button_onclick():
    logging.debug("Toggling special workspace")
    if __current_special_workspace:
        dispatch_togglespecialworkspace_resp: str = await async_command_send(
            f"dispatch togglespecialworkspace {__current_special_workspace}",
            return_json=False,
        )
        logging.log(
            TRACE_LVL,
            "Response for dispatch togglespecialworkspace was %r",
            dispatch_togglespecialworkspace_resp,
        )
    else:
        dispatch_togglespecialworkspace_resp: str = await async_command_send(
            f"dispatch togglespecialworkspace {__MAIN_SPECIAL_WORKSPACE_NAME}",
            return_json=False,
        )
        logging.log(
            TRACE_LVL,
            "Response for dispatch togglespecialworkspace was %r",
            dispatch_togglespecialworkspace_resp,
        )
