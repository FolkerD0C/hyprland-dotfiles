import asyncio
import logging
from io import BytesIO, TextIOWrapper
from pathlib import Path
import random
from uuid import UUID, uuid4

from constants import TRACE_LVL
from helpers import logged, logged_async
from hyprsocket import async_command_send

# DUMMY_STDOUT_STREAM: TextIOWrapper = TextIOWrapper(BytesIO())
# DUMMY_STDERR_STREAM: TextIOWrapper = TextIOWrapper(BytesIO())


async def hyprpaper_preload(wallpaper_candidate: Path):
    await asyncio.create_subprocess_exec(
        "hyprctl",
        "hyprpaper",
        "preload",
        str(wallpaper_candidate),
        # stdout=DUMMY_STDOUT_STREAM,
        # stderr=DUMMY_STDERR_STREAM,
    )
    # for line in DUMMY_STDOUT_STREAM:
    #     logging.log(TRACE_LVL, "Got line for stdout of hyprpaper_preload: %r", line)
    # DUMMY_STDOUT_STREAM.flush()
    # for line in DUMMY_STDERR_STREAM:
    #     logging.log(TRACE_LVL, "Got line for stderr of hyprpaper_preload: %r", line)
    # DUMMY_STDERR_STREAM.flush()


async def hyprpaper_wallpaper(monitor: str, wallpaper_candidate: Path):
    await asyncio.create_subprocess_exec(
        "hyprctl", "hyprpaper", "wallpaper", f"{monitor},{str(wallpaper_candidate)}"
    )
    # for line in DUMMY_STDOUT_STREAM:
    #     logging.log(TRACE_LVL, "Got line for stdout of hyprpaper_wallpaper: %r", line)
    # DUMMY_STDOUT_STREAM.flush()
    # for line in DUMMY_STDERR_STREAM:
    #     logging.log(TRACE_LVL, "Got line for stderr of hyprpaper_wallpaper: %r", line)
    # DUMMY_STDERR_STREAM.flush()


async def hyprpaper_unload(wallpaper: Path):
    await asyncio.create_subprocess_exec(
        "hyprctl",
        "hyprpaper",
        "unload",
        str(wallpaper),
        # stdout=DUMMY_STDOUT_STREAM,
        # stderr=DUMMY_STDERR_STREAM,
    )
    # for line in DUMMY_STDOUT_STREAM:
    #     logging.log(TRACE_LVL, "Got line for stdout of hyprpaper_unload: %r", line)
    # DUMMY_STDOUT_STREAM.flush()
    # for line in DUMMY_STDERR_STREAM:
    #     logging.log(TRACE_LVL, "Got line for stderr of hyprpaper_unload: %r", line)
    # DUMMY_STDERR_STREAM.flush()


class HyprPaperManager:
    def __init__(
        self, wallpaper_directory: Path, wallpaper_changing_enabled: bool = True
    ) -> None:
        logging.debug(
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
        logging.debug(
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
    async def set_wallpapers(self, _: list, __: dict):
        logging.debug(
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
                    logging.log(
                        TRACE_LVL,
                        "%r[%r]: Wallpaper would remain the same (%r) for %r, because of weak randomness",
                        type(self).__name__,
                        str(self.__id),
                        str(wallpaper_candidate),
                        monitor,
                    )
                    continue
                found_wallpaper_candidate = True
                logging.debug(
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
                    self.__previous_wallpapers[monitor] = self.__current_wallpapers[monitor]
                self.__current_wallpapers[monitor] = wallpaper_candidate

    @logged
    def toggle_wallpaper_changing(self, *_):
        logging.info(
            "%r[%r]: Toggling wallpaper changing from %r",
            type(self).__name__,
            str(self.__id),
            self.__wallpaper_changing_enabled,
        )
        self.__wallpaper_changing_enabled = not self.__wallpaper_changing_enabled
