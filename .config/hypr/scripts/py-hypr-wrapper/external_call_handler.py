import asyncio
import logging
from pathlib import Path
from typing import Dict

from constants import RUNTIME_DIR, TRACE_LVL


class PyHyprWrapperEventListener:
    def __init__(self, func_table: Dict[str, callable]):
        self.__func_table: Dict[str, callable] = func_table

    async def __handle_event(self, event: str) -> bool:
        logging.log(TRACE_LVL, "Got external call: %r", event)
        if not event or event == "":
            return False
        if not event in self.__func_table:
            logging.warning("Event %r not in func_table", event)
            return False
        try:
            if asyncio.iscoroutinefunction(self.__func_table[event]):
                logging.log(
                    TRACE_LVL,
                    "%r is an async coroutine function, executing asynchronously",
                    self.__func_table[event],
                )
                await self.__func_table[event]()
            else:
                logging.log(
                    TRACE_LVL,
                    "Executing synchronous function %r",
                    self.__func_table[event],
                )
                self.__func_table[event]()
        except Exception as exc:
            logging.warn("Caught an exception: %r", type(exc).__name__, stack_info=True)
            return False
        return True

    async def __handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        data: bytes = await reader.read(1024)
        event = data.decode()
        peer = writer.get_extra_info("peername")
        logging.log(TRACE_LVL, "Got data from %r: %r", peer, event)
        for event_line in event.splitlines():
            resp = await self.__handle_event(event_line)
            if resp:
                writer.write(f"{event_line}: ok".encode())
            else:
                writer.write(f"{event_line}: no".encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def start(self):
        socket_path: Path = Path(
            RUNTIME_DIR,
            "py-hypr-wrapper.socket",
        )
        socket_path.unlink(missing_ok=True)
        unix_socket_server = await asyncio.start_unix_server(
            self.__handle_client, socket_path
        )
        logging.log(
            TRACE_LVL,
            "Creating %r object for handling unix domain socket",
            str(unix_socket_server),
        )
        async with unix_socket_server:
            logging.debug("Starting to serve external requests")
            await unix_socket_server.serve_forever()
