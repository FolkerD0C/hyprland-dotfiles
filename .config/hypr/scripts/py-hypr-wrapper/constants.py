from enum import Enum, IntEnum
from os import environ
from pathlib import Path

PACKAGE_NAME: str = "py-hypr-wrapper"
TRACE_LVL: int = 5
RUNTIME_DIR: Path = Path(environ["XDG_RUNTIME_DIR"], PACKAGE_NAME)


class WaybarSignals(IntEnum):
    KEYBOARD_LAYOUT_SWITCHED: int = 1
    SPECIAL_WORKSPACE_TOGGLED: int = 2


class WaybarOutputFiles(Enum):
    ACTIVE_KEYBOARD_LAYOUT: Path = Path(RUNTIME_DIR, "waybar-active-keyboard-layout")
    SPECIAL_WORKSPACE_DISPLAYNAME: Path = Path(
        RUNTIME_DIR, "waybar-special-workspace-displayname"
    )


KEYBOARD_LAYOUTS: dict = {"Hungarian": "HU_HU", "English (US)": "EN_US"}
