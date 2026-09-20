from typing import Optional

from perception.screenshot import ScreenshotCapture
from perception.ocr import OCRReader
from perception.vision import VisionSystem
from perception.windows_ui_tree import WindowsUITree

from intelligence.vision_reasoner import (
    VisionReasoner,
    VisualState,
)


class PerceptionController:
    """
    Unified perception layer for the computer-use agent.

    Combines:
    - screenshots
    - OCR
    - OpenCV
    - Windows UI Automation
    """

    def __init__(
        self,
        screenshot_directory: str = "data/screenshots",
    ):
        self.screenshot_capture = ScreenshotCapture(
            output_directory=screenshot_directory
        )

        self.ocr_reader = OCRReader()

        self.vision_system = VisionSystem()

        self.ui_tree = WindowsUITree()

        self.reasoner = VisionReasoner(
            screenshot_capture=self.screenshot_capture,
            ocr_reader=self.ocr_reader,
            vision_system=self.vision_system,
            ui_tree=self.ui_tree,
        )

        self.last_state: Optional[VisualState] = None

    # =========================================================
    # Observe computer
    # =========================================================

    def observe(self) -> VisualState:
        """
        Capture and analyze the current computer state.
        """

        state = self.reasoner.observe()

        self.last_state = state

        return state

    # =========================================================
    # Get last observation
    # =========================================================

    def get_last_state(self) -> Optional[VisualState]:
        """
        Return the most recent visual state.
        """

        return self.last_state

    # =========================================================
    # Summarize current screen
    # =========================================================

    def summarize(
        self,
        state: Optional[VisualState] = None,
    ) -> str:
        """
        Return a human-readable description
        of the current visual state.
        """

        if state is None:
            state = self.last_state

        if state is None:
            return "No visual observation available."

        return self.reasoner.summarize(state)