import time
from typing import Optional

import pyautogui


class MouseKeyboardController:
    """
    Low-level controller for mouse and keyboard operations.

    This class does not decide WHAT to do.
    It only knows HOW to perform input actions.
    """

    def __init__(self, default_duration: float = 0.2):
        self.default_duration = default_duration

    # ---------------------------------------------------------
    # Mouse
    # ---------------------------------------------------------

    def move(self, x: int, y: int, duration: Optional[float] = None):
        duration = (
            self.default_duration
            if duration is None
            else duration
        )

        pyautogui.moveTo(
            x,
            y,
            duration=duration
        )

    def click(
        self,
        x: int,
        y: int,
        button: str = "left",
    ):
        pyautogui.click(
            x=x,
            y=y,
            button=button,
        )

    def double_click(self, x: int, y: int):
        pyautogui.doubleClick(
            x=x,
            y=y,
            interval=0.1,
        )

    def right_click(self, x: int, y: int):
        pyautogui.rightClick(
            x=x,
            y=y,
        )

    # ---------------------------------------------------------
    # Keyboard
    # ---------------------------------------------------------

    def type_text(
        self,
        text: str,
        interval: float = 0.03,
    ):
        pyautogui.write(
            text,
            interval=interval,
        )

    def press(self, key: str):
        pyautogui.press(key)

    def hotkey(self, *keys: str):
        pyautogui.hotkey(*keys)

    # ---------------------------------------------------------
    # Scrolling
    # ---------------------------------------------------------

    def scroll(self, amount: int):
        pyautogui.scroll(amount)

    # ---------------------------------------------------------
    # Waiting
    # ---------------------------------------------------------

    def wait(self, seconds: float):
        time.sleep(seconds)

    # ---------------------------------------------------------
    # Screenshot
    # ---------------------------------------------------------

    def screenshot(self, path: str):
        image = pyautogui.screenshot()
        image.save(path)

    # ---------------------------------------------------------
    # Emergency stop
    # ---------------------------------------------------------

    def fail_safe(self):
        """
        Enable PyAutoGUI's emergency corner protection.

        Moving the mouse rapidly to the top-left corner
        causes PyAutoGUI to raise FailSafeException.
        """

        pyautogui.FAILSAFE = True