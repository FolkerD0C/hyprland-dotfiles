import asyncio
import json
import socket

from local_objects.ipc_objects import (
    IPCRequestFailed,
    LocalIPCRequest,
    LocalIPCResponse,
    WrongInitiatorId,
)
from local_utilities.constants import LOCAL_IPC_ENCODING
from local_utilities.local_logging import LOCAL_IPC_LOGGER
from local_utilities.paths import PY_HYPR_WRAPPER_IPC_SOCKET
from local_utilities.wrappers import logged, logged_async


@logged
def send_request(
    initiator_id: str, requested_action_name: str, requested_action_parameters: dict
) -> dict:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as py_hypr_wrapper_socket:
        py_hypr_wrapper_socket.connect(str(PY_HYPR_WRAPPER_IPC_SOCKET))
        request = LocalIPCRequest(
            initiator_id, requested_action_name, requested_action_parameters
        )
        LOCAL_IPC_LOGGER.debug("Sending request: %r", request)
        py_hypr_wrapper_socket.send(
            json.dumps(vars(request)).encode(LOCAL_IPC_ENCODING)
        )

        response_bytes: bytes = py_hypr_wrapper_socket.recv(8192)
        while True:
            new_data = py_hypr_wrapper_socket.recv(8192)
            if not new_data:
                break
            response_bytes += new_data

        response_str: str = response_bytes.decode(LOCAL_IPC_ENCODING)
        response: LocalIPCResponse = LocalIPCResponse(**json.loads(response_str))

        LOCAL_IPC_LOGGER.debug("Got response: %r", response)

        if request.initiator_id != response.initiator_id:
            raise WrongInitiatorId(request, response)

        if not response.response_ok:
            raise IPCRequestFailed(request, response)

        return response.response


@logged_async
async def send_request_async(
    initiator_id: str, requested_action_name: str, requested_action_parameters: dict
) -> dict:
    reader, writer = await asyncio.open_unix_connection(PY_HYPR_WRAPPER_IPC_SOCKET)
    request: LocalIPCRequest = LocalIPCRequest(
        initiator_id, requested_action_name, requested_action_parameters
    )

    LOCAL_IPC_LOGGER.debug("Sending request (asynchronously): %r", request)

    writer.write(json.dumps(vars(request)).encode(LOCAL_IPC_ENCODING))
    await writer.drain()

    response_bytes: bytes = await reader.read(8192)
    while True:
        new_data = await reader.read(8192)
        if not new_data:
            break
        response_bytes += new_data
    writer.close()

    response_str: str = response_bytes.decode(LOCAL_IPC_ENCODING)
    response: LocalIPCResponse = LocalIPCResponse(**json.loads(response_str))

    LOCAL_IPC_LOGGER.debug("Got response: %r", response)

    if request.initiator_id != response.initiator_id:
        raise WrongInitiatorId(request, response)

    if not response.response_ok:
        raise IPCRequestFailed(request, response)

    return response.response
