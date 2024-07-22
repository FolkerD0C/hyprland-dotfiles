import logging
import logging.handlers as logging_handlers
from pathlib import Path
from sys import stdout as sys_stdout

from local_utilities.constants import LOGGING_TRACE_LEVEL

HYPR_IPC_LOGGER: logging.Logger = logging.getLogger("hypc")
LOCAL_IPC_LOGGER: logging.Logger = logging.getLogger("locipc")
LOCAL_ACTIONS_LOGGER: logging.Logger = logging.getLogger("actions")
LOCAL_OBJECTS_LOGGER: logging.Logger = logging.getLogger("objects")
LOCAL_UTILITIES_LOGGER: logging.Logger = logging.getLogger("utils")


def logger_setup(*, logfile: Path, handlers: list, debug_mode: bool = False):
    logging.addLevelName(LOGGING_TRACE_LEVEL, "TRACE")
    logging.getLogger().setLevel(logging.NOTSET)

    if "console" in handlers:
        console_handler = logging.StreamHandler(sys_stdout)
        console_handler.setLevel(LOGGING_TRACE_LEVEL if debug_mode else logging.INFO)
        console_handler.setFormatter(
            logging.Formatter("[%(asctime)-2s][%(levelname)-8s]: %(message)s")
        )
        logging.getLogger().addHandler(console_handler)

    if "rotating_file" in handlers:
        logfile.parent.mkdir(exist_ok=True)
        file_handler = logging_handlers.RotatingFileHandler(
            logfile, maxBytes=5242880, backupCount=5
        )
        file_handler.setLevel(LOGGING_TRACE_LEVEL if debug_mode else logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)-2s][%(name)-8s][%(funcName)-32s][%(levelname)-8s]: %(message)s"
            )
        )
        logging.getLogger().addHandler(file_handler)

    if debug_mode:
        logging.getLogger("asyncio").setLevel(1)
