from __future__ import annotations

from yutto.utils.console.formatter import get_string_width


class StatusBar:

    _enabled = False
    tip = ""
    _snippers = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    _count = 0
    _last_line_width = 0

    @classmethod
    def enable(cls):
        cls._enabled = True

    @classmethod
    def disable(cls):
        cls._enabled = False

    @classmethod
    def is_enabled(cls) -> bool:
        return cls._enabled

    @classmethod
    def set_snippers(cls, snippers: list[str]):
        cls._snippers = snippers

    @classmethod
    def clear(cls):
        if not cls._enabled:
            return
        print("\r" + cls._last_line_width * " " + "\r", end="")

    @classmethod
    def set(cls, text: str):
        if not cls._enabled:
            return
        cls.clear()
        print(text, end="\r")
        cls._last_line_width = get_string_width(text)

    @classmethod
    def set_tip(cls, tip: str):
        cls.tip = tip

    @classmethod
    def next_tick(cls):
        cls.set(cls._snippers[cls._count] + " " + cls.tip)
        cls._count += 1
        cls._count %= len(cls._snippers)
