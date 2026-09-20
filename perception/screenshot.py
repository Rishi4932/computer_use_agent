from pathlib import Path
from datetime import datetime

import pyautogui


class ScreenshotCapture:
    """
    Captures the current Windows screen.

    This is the first perception layer of the agent.
    """

    def __init__(self, output_directory="data/screenshots"):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def capture(self, filename=None):
        """
        Capture the current screen and save it.

        Returns:
            Path: path of the saved screenshot.
        """

        if filename is None:
            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S_%f"
            )

            filename = f"screen_{timestamp}.png"

        path = self.output_directory / filename

        screenshot = pyautogui.screenshot()

        screenshot.save(path)

        return path

    def capture_image(self):
        """
        Capture the current screen without saving it.

        Returns:
            PIL.Image
        """

        return pyautogui.screenshot()