from os import environ as environment_variables
from pathlib import Path

from local_utilities.constants import (
    HYPRLAND_COMMON_NAME,
    HYPRLAND_INSTANCE_SIGNATURE,
    PACKAGE_NAME,
)

COMMON_RUNTIME_DIR: Path = Path(environment_variables["XDG_RUNTIME_DIR"])
PY_HYPR_WRAPPER_RUNTIME_DIR: Path = Path(COMMON_RUNTIME_DIR, PACKAGE_NAME)
HYPRLAND_RUNTIME_DIR: Path = Path(
    COMMON_RUNTIME_DIR, HYPRLAND_COMMON_NAME, HYPRLAND_INSTANCE_SIGNATURE
)
LOGS_DIR: Path = Path(environment_variables["HOME"], "misc", "logs", PACKAGE_NAME)

PY_HYPR_WRAPPER_IPC_SOCKET: Path = Path(
    PY_HYPR_WRAPPER_RUNTIME_DIR, f"{PACKAGE_NAME}.socket"
)
HYPRLAND_IPC_SOCKET: Path = Path(HYPRLAND_RUNTIME_DIR, ".socket.sock")
HYPRLAND_EVENT_SOCKET: Path = Path(HYPRLAND_RUNTIME_DIR, ".socket2.sock")

PY_HYPR_WRAPPER_DAEMON_LOCK: Path = Path(
    PY_HYPR_WRAPPER_RUNTIME_DIR, f"{PACKAGE_NAME}.lock"
)

PY_HYPR_WRAPPER_DAEMON_LOG: Path = Path(LOGS_DIR, f"{PACKAGE_NAME}-daemon.log")
PY_HYPR_WRAPPER_TRIGGER_LOG: Path = Path(LOGS_DIR, f"{PACKAGE_NAME}-trigger.log")
