from __future__ import annotations

import io
import sys


def wait_for_keypress(prompt: str = "Press any key to continue...") -> None:
    print(prompt)

    if sys.platform == "win32":
        import msvcrt
        msvcrt.getch()
        return

    if sys.platform in ("linux", "darwin"):
        import getch
        getch.getch()
        return