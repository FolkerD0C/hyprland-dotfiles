import logging
from logging import handlers as logging_handlers
from pathlib import Path
from sys import stdout as sys_stdout
from functools import wraps

from constants import TRACE_LVL


def logged_async(func: callable):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            logging.log(
                TRACE_LVL,
                "ENTER %r( args=%r | kwargs=%r )",
                func.__qualname__,
                args,
                kwargs,
            )
            retval = await func(*args, **kwargs)
            logging.log(
                TRACE_LVL,
                "RETURN from %r with %r | args=%r | kwargs=%r",
                func.__qualname__,
                retval,
                args,
                kwargs,
            )
        except Exception:
            logging.exception(
                "Exception occurred in %r : args=%r | kwargs=%r",
                func.__qualname__,
                args,
                kwargs,
                stack_info=True,
            )
            raise
        return retval

    return async_wrapper


def logged(func: callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.log(
                TRACE_LVL,
                "ENTER %r( args=%r | kwargs=%r )",
                func.__qualname__,
                args,
                kwargs,
            )
            retval = func(*args, **kwargs)
            logging.log(
                TRACE_LVL,
                "RETURN from %r with %r | args=%r | kwargs=%r",
                func.__qualname__,
                retval,
                args,
                kwargs,
            )
        except Exception:
            logging.exception(
                "Exception occurred in %r : args=%r | kwargs=%r",
                func.__qualname__,
                args,
                kwargs,
                stack_info=True,
            )
            raise
        return retval

    return wrapper


def logger_setup(filename: str, *, debug_mode: bool = False):
    logdir: Path = Path(filename).parent
    logdir.mkdir(parents=True, exist_ok=True)
    logging.addLevelName(TRACE_LVL, "TRACE")
    logging.getLogger().setLevel(logging.NOTSET)

    console_handler = logging.StreamHandler(sys_stdout)
    console_handler.setLevel(TRACE_LVL if debug_mode else logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("[%(asctime)-2s][%(levelname)-8s]: %(message)s")
    )
    logging.getLogger().addHandler(console_handler)

    file_handler = logging_handlers.RotatingFileHandler(
        filename, maxBytes=5242880, backupCount=5
    )
    file_handler.setLevel(TRACE_LVL if debug_mode else logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "[%(asctime)-2s][%(name)-8s][%(funcName)-32s][%(levelname)-8s]: %(message)s"
        )
    )
    logging.getLogger().addHandler(file_handler)
    if debug_mode:
        logging.getLogger("asyncio").setLevel(1)
