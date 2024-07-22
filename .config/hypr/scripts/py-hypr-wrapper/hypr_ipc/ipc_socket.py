import asyncio
import json
import socket

from local_utilities.constants import LOGGING_TRACE_LEVEL
from local_utilities.local_logging import HYPR_IPC_LOGGER
from local_utilities.paths import HYPRLAND_EVENT_SOCKET, HYPRLAND_IPC_SOCKET


class InvalidCommand(Exception): ...


class UnknownRequest(Exception): ...


def command_send(cmd: str, return_json=True, check_ok=False):
    HYPR_IPC_LOGGER.log(LOGGING_TRACE_LEVEL, "Executing %r", cmd)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(HYPRLAND_IPC_SOCKET)
        if return_json:
            cmd = f"[j]/{cmd}"
        sock.send(cmd.encode())
        resp = sock.recv(8192)

        while True:
            new_data = sock.recv(8192)
            if not new_data:
                break
            resp += new_data

        match resp:
            case b"ok" if check_ok:
                return True
            case b"unknown request":
                raise UnknownRequest(f"{cmd.encode()!r} : {resp}")
            case _:

                if check_ok and resp != b"ok":
                    raise Exception(f"Command failed: {cmd.encode()!r} : {resp}")

                if return_json and not check_ok:
                    return json.loads(resp.decode())

                return resp.decode()


async def async_command_send(cmd: str, return_json=True):
    HYPR_IPC_LOGGER.log(LOGGING_TRACE_LEVEL, "Executing %r", cmd)
    reader, writer = await asyncio.open_unix_connection(HYPRLAND_IPC_SOCKET)
    if return_json:
        cmd = f"[j]/{cmd}"
    writer.write(cmd.encode())
    await writer.drain()
    resp = await reader.read(8192)

    while True:
        new_data = await reader.read(8192)
        if not new_data:
            break
        resp += new_data

    writer.close()

    match resp:
        case b"unknown request":
            raise UnknownRequest(f"{cmd.encode()!r} : {resp}")
        case _:
            if return_json:
                return json.loads(resp.decode())
            return resp.decode()


class HyprEventListener:
    async def start(self):
        reader, _ = await asyncio.open_unix_connection(HYPRLAND_EVENT_SOCKET)
        yield "connect"

        buffer = b""
        while True:
            new_data = await reader.read(8192)
            if not new_data:
                break
            buffer += new_data
            while b"\n" in buffer:
                data, buffer = buffer.split(b"\n", 1)
                yield data.decode("utf-8")
