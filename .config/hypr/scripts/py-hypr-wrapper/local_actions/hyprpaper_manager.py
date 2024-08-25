import asyncio
import random

from os import environ as environment_variables
from pathlib import Path
from uuid import UUID, uuid4

from hypr_ipc.ipc_socket import async_command_send
from local_utilities.constants import LOGGING_TRACE_LEVEL
from local_utilities.local_logging import LOCAL_ACTIONS_LOGGER
from local_utilities.wrappers import logged, logged_async


async def hyprpaper_preload(wallpaper_candidate: Path):
    proc_exec = await asyncio.create_subprocess_exec(
        "hyprctl",
        "hyprpaper",
        "preload",
        str(wallpaper_candidate),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc_exec.communicate()
    LOCAL_ACTIONS_LOGGER.log(
        LOGGING_TRACE_LEVEL, "stdout of 'hyprpaper preload': %r", stdout.decode()
    )
    LOCAL_ACTIONS_LOGGER.log(
        LOGGING_TRACE_LEVEL, "stderr of 'hyprpaper preload': %r", stderr.decode()
    )


async def hyprpaper_wallpaper(monitor: str, wallpaper_candidate: Path):
    proc_exec = await asyncio.create_subprocess_exec(
        "hyprctl",
        "hyprpaper",
        "wallpaper",
        f"{monitor},{str(wallpaper_candidate)}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc_exec.communicate()
    LOCAL_ACTIONS_LOGGER.log(
        LOGGING_TRACE_LEVEL, "stdout of 'hyprpaper wallpaper': %r", stdout.decode()
    )
    LOCAL_ACTIONS_LOGGER.log(
        LOGGING_TRACE_LEVEL, "stderr of 'hyprpaper wallpaper': %r", stderr.decode()
    )


async def hyprpaper_unload(wallpaper: Path):
    proc_exec = await asyncio.create_subprocess_exec(
        "hyprctl",
        "hyprpaper",
        "unload",
        str(wallpaper),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc_exec.communicate()
    LOCAL_ACTIONS_LOGGER.log(
        LOGGING_TRACE_LEVEL, "stdout of 'hyprpaper unload': %r", stdout.decode()
    )
    LOCAL_ACTIONS_LOGGER.log(
        LOGGING_TRACE_LEVEL, "stderr of 'hyprpaper unload': %r", stderr.decode()
    )


class HyprPaperManager:
    def __init__(
        self,
        wallpaper_directory: Path = Path(environment_variables["HOME"], "Pictures"),
        *,
        wallpaper_changing_enabled: bool = True,
    ) -> None:
        LOCAL_ACTIONS_LOGGER.debug(
            "Creating %r object with wallpaper_directory=%r and wallpaper_changing_enabled=%r",
            type(self).__name__,
            str(wallpaper_directory),
            wallpaper_changing_enabled,
        )
        self.__id: UUID = uuid4()
        self.__wallpaper_directory: Path = wallpaper_directory
        self.__current_wallpapers: dict = {}
        self.__previous_wallpapers: dict = {}
        self.__wallpaper_changing_enabled: bool = wallpaper_changing_enabled

    @property
    def wallpaper_directory(self) -> Path:
        return self.__wallpaper_directory

    @wallpaper_directory.setter
    def wallpaper_directory(self, new_wallpaper_directory: Path) -> None:
        LOCAL_ACTIONS_LOGGER.debug(
            "Wallpaper directory of %r object (%r) is going to be changed from %r to %r.",
            type(self).__name__,
            str(self.__id),
            str(self.__wallpaper_directory),
            str(new_wallpaper_directory),
        )
        self.__wallpaper_directory = new_wallpaper_directory

    @property
    def current_wallpapers(self) -> dict:
        return self.__current_wallpapers

    @logged_async
    async def set_wallpapers(self, *_: list, **__: dict):
        LOCAL_ACTIONS_LOGGER.debug(
            "%r[%r]: Wallpaper changing enabled is %r",
            type(self).__name__,
            str(self.__id),
            self.__wallpaper_changing_enabled,
        )
        if not self.__wallpaper_changing_enabled:
            return
        monitor_list = await async_command_send("monitors")
        monitors: list = []
        for monitor in monitor_list:
            monitors.append(monitor["name"])
        wallpaper_candidates = [wp for wp in self.__wallpaper_directory.glob("*.png")]
        wallpaper_candidates.extend(
            [wp for wp in self.__wallpaper_directory.glob("*.jpg")]
        )
        wallpaper_candidates.extend(
            [wp for wp in self.__wallpaper_directory.glob("*.jpeg")]
        )
        wallpaper_candidates.extend(
            [wp for wp in self.__wallpaper_directory.glob("*.webp")]
        )
        for monitor in monitors:
            found_wallpaper_candidate: bool = False
            while not found_wallpaper_candidate:
                wallpaper_candidate = random.choice(wallpaper_candidates)
                if (
                    monitor in self.__current_wallpapers
                    and self.__current_wallpapers[monitor] == wallpaper_candidate
                ):
                    LOCAL_ACTIONS_LOGGER.log(
                        LOGGING_TRACE_LEVEL,
                        "%r[%r]: Wallpaper would remain the same (%r) for %r, because of weak randomness",
                        type(self).__name__,
                        str(self.__id),
                        str(wallpaper_candidate),
                        monitor,
                    )
                    continue
                found_wallpaper_candidate = True
                LOCAL_ACTIONS_LOGGER.debug(
                    "%r[%r]: Wallpaper for %r is going to be set to %r",
                    type(self).__name__,
                    str(self.__id),
                    monitor,
                    str(wallpaper_candidate),
                )
                await hyprpaper_preload(wallpaper_candidate)
                await hyprpaper_wallpaper(monitor, wallpaper_candidate)
                if monitor in self.__previous_wallpapers:
                    await hyprpaper_unload(self.__previous_wallpapers[monitor])
                if monitor in self.__current_wallpapers:
                    self.__previous_wallpapers[monitor] = self.__current_wallpapers[
                        monitor
                    ]
                self.__current_wallpapers[monitor] = wallpaper_candidate

    @logged
    def toggle_wallpaper_changing(self, **_):
        LOCAL_ACTIONS_LOGGER.info(
            "%r[%r]: Toggling wallpaper changing from %r",
            type(self).__name__,
            str(self.__id),
            self.__wallpaper_changing_enabled,
        )
        self.__wallpaper_changing_enabled = not self.__wallpaper_changing_enabled
