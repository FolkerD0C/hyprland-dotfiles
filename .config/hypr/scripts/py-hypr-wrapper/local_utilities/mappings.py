from enum import IntEnum
from typing import Dict

from local_objects.triggerable_action import TriggerableAction


class WaybarSignals(IntEnum):
    KEYBOARD_LAYOUT_SWITCHED: int = 1
    SPECIAL_WORKSPACE_TOGGLED: int = 2


KEYBOARD_LAYOUTS: Dict[str, str] = {"Hungarian": "HU_HU", "English (US)": "EN_US"}


def create_triggerable_actions():
    triggerable_actions = {}
    _bsw_id: str = "btop_special_workspace"
    triggerable_actions[_bsw_id] = TriggerableAction(
        action_id=_bsw_id,
        short_argname="-b",
        long_argname="--btop-special-workspace",
        description="Toggle a scratchpad/special workspace for btop",
    )
    _kls_id: str = "keyboard_layout_switched"
    triggerable_actions[_kls_id] = TriggerableAction(
        action_id=_kls_id,
        long_argname="--keyboard-layout-switched",
        description="Should be called when the keyboard layout has been switched",
    )
    _swbo_id: str = "special_workspace_button_onclick"
    triggerable_actions[_swbo_id] = TriggerableAction(
        action_id=_swbo_id,
        long_argname="--special-workspace-button-onclick",
        description="Toggle active scratchpad",
    )
    _swd_id: str = "special_workspace_displayname"
    triggerable_actions[_swd_id] = TriggerableAction(
        action_id=_swd_id,
        long_argname="--special-workspace-displayname",
        description="Should be called when a special workspace is toggled",
    )
    _skl_id: str = "switch_keyboard_layout"
    triggerable_actions[_skl_id] = TriggerableAction(
        action_id=_skl_id,
        short_argname="-l",
        long_argname="--switch-keyboard-layout",
        description="Switch active keyboard layout to the next one",
    )
    _twc_id: str = "toggle_wallpaper_changing"
    triggerable_actions[_twc_id] = TriggerableAction(
        action_id=_twc_id,
        short_argname="-w",
        long_argname="--toggle-wallpaper-changing",
        description="Toggle the changing of the wallpapers (default: Enabled)",
    )
    return triggerable_actions
