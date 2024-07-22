import asyncio
import json
from typing import Awaitable

from local_objects.ipc_objects import LocalIPCRequest, LocalIPCResponse
from local_utilities.constants import LOCAL_IPC_ENCODING, LOGGING_TRACE_LEVEL
from local_utilities.local_logging import LOCAL_IPC_LOGGER
from local_utilities.paths import PY_HYPR_WRAPPER_IPC_SOCKET


class PyHyprWrapperListenerListener:
    def __init__(
        self,
        request_handler: Awaitable[LocalIPCResponse],
    ):
        self.__request_handler: Awaitable[LocalIPCResponse] = request_handler

    async def __handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        data: bytes = await reader.read(4096)
        request_str = data.decode(LOCAL_IPC_ENCODING)
        LOCAL_IPC_LOGGER.log(LOGGING_TRACE_LEVEL, "Got data: %r", request_str)
        try:
            request = LocalIPCRequest(**json.loads(request_str))
            LOCAL_IPC_LOGGER.debug("Got request: %r", request)
            response: LocalIPCResponse = await self.__request_handler(request)
            LOCAL_IPC_LOGGER.debug("Sending response: %r", response)
            writer.write(json.dumps(vars(response)).encode(LOCAL_IPC_ENCODING))
        except Exception as exc:
            LOCAL_IPC_LOGGER.exception(
                "Caught an exception: %r", type(exc).__name__, stack_info=True
            )
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def start_listening_to_requests(self):
        PY_HYPR_WRAPPER_IPC_SOCKET.unlink(missing_ok=True)
        LOCAL_IPC_LOGGER.log(
            LOGGING_TRACE_LEVEL, "Creating object for handling unix domain socket"
        )
        unix_socket_server = await asyncio.start_unix_server(
            self.__handle_client, PY_HYPR_WRAPPER_IPC_SOCKET
        )
        LOCAL_IPC_LOGGER.info(
            "Starting to listen to requests with %r", unix_socket_server
        )
        async with unix_socket_server:
            LOCAL_IPC_LOGGER.debug("Starting to serve external requests")
            await unix_socket_server.serve_forever()
