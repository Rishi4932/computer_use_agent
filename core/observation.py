from typing import Any, Dict, Optional

from perception.screenshot import ScreenshotCapture
from perception.ocr import OCRReader
from perception.vision import VisionSystem
from perception.windows_ui_tree import WindowsUITree

from intelligence.vision_reasoner import VisionReasoner


class ObservationManager:
    """
    Manages real Windows screen observation.

    The ObservationManager is responsible for configuring
    VisionReasoner with the actual perception components.
    """

    def __init__(
        self,
        vision_reasoner: Optional[VisionReasoner] = None,
    ):
        self.vision_reasoner = (
            vision_reasoner
            if vision_reasoner is not None
            else VisionReasoner(
                screenshot_capture=ScreenshotCapture(),
                ocr_reader=OCRReader(),
                vision_system=VisionSystem(),
                ui_tree=WindowsUITree(),
            )
        )

        self.last_observation: Optional[Any] = None

    def observe(self) -> Any:
        """
        Capture and analyze the current Windows screen.
        """
        observation = self.vision_reasoner.observe()

        self.last_observation = observation

        return observation

    def get_last_observation(self) -> Any:
        """
        Return the most recent observation.
        """
        return self.last_observation

    def summarize(self) -> str:
        """
        Return a human-readable summary of the current screen.
        """
        if self.last_observation is None:
            self.observe()

        return self.vision_reasoner.summarize(
            self.last_observation
        )

    def observe_as_dict(self) -> Dict[str, Any]:
        """
        Convert the observation into a dictionary when possible.
        """
        observation = self.last_observation

        if observation is None:
            observation = self.observe()

        if hasattr(observation, "to_dict"):
            return observation.to_dict()

        if isinstance(observation, dict):
            return observation

        return {
            "observation": observation
        }

    def reset(self):
        """
        Clear the stored observation.
        """
        self.last_observation = None