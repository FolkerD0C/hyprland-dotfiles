from os import environ as environment_variables

HYPRLAND_COMMON_NAME: str = "hypr"
HYPRLAND_INSTANCE_SIGNATURE: str = environment_variables["HYPRLAND_INSTANCE_SIGNATURE"]
PACKAGE_NAME: str = f"py-{HYPRLAND_COMMON_NAME}-wrapper"

LOGGING_TRACE_LEVEL: int = 5

LOCAL_IPC_ENCODING: str = "utf-8"
