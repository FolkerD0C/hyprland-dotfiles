import logging
from functools import wraps

from local_utilities.constants import LOGGING_TRACE_LEVEL


def logged_async(func: callable):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            logging.log(
                LOGGING_TRACE_LEVEL,
                "ENTER %r( args=%r | kwargs=%r )",
                func.__qualname__,
                args,
                kwargs,
            )
            retval = await func(*args, **kwargs)
            logging.log(
                LOGGING_TRACE_LEVEL,
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
                LOGGING_TRACE_LEVEL,
                "ENTER %r( args=%r | kwargs=%r )",
                func.__qualname__,
                args,
                kwargs,
            )
            retval = func(*args, **kwargs)
            logging.log(
                LOGGING_TRACE_LEVEL,
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
