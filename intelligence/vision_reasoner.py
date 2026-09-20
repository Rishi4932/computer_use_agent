from perception.screenshot import ScreenshotCapture
from perception.ocr import OCRReader
from perception.vision import VisionSystem
from perception.windows_ui_tree import WindowsUITree

from intelligence.element_classifier import ElementClassifier

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class VisualElement:
    """
    Represents an element detected on the screen.
    """

    element_type: str
    text: str = ""
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    confidence: float = 0.0
    source: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:

        return {
            "element_type": self.element_type,
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "confidence": self.confidence,
            "source": self.source,
        }


@dataclass
class VisualState:
    """
    Structured representation of the current
    computer screen.
    """

    screenshot_path: Optional[str] = None

    screen_width: Optional[int] = None
    screen_height: Optional[int] = None

    visible_text: str = ""

    elements: List[VisualElement] = field(
        default_factory=list
    )

    active_window: Optional[str] = None

    window_titles: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def add_element(
        self,
        element: VisualElement,
    ):

        self.elements.append(element)

    def to_dict(self) -> Dict[str, Any]:

        return {
            "screenshot_path": self.screenshot_path,
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "visible_text": self.visible_text,
            "elements": [
                element.to_dict()
                for element in self.elements
            ],
            "active_window": self.active_window,
            "window_titles": self.window_titles,
            "metadata": self.metadata,
        }


class VisionReasoner:
    """
    Combines screenshot, OCR, OpenCV and
    Windows UI information.
    """

    def __init__(
        self,
        screenshot_capture=None,
        ocr_reader=None,
        vision_system=None,
        ui_tree=None,
    ):
        self.screenshot_capture = screenshot_capture

        self.ocr_reader = ocr_reader

        self.vision_system = vision_system

        self.ui_tree = ui_tree

        self.element_classifier = ElementClassifier()
    # =========================================================
    # Capture screen
    # =========================================================

    def capture_screen(self):

        if self.screenshot_capture is None:
            raise RuntimeError(
                "Screenshot capture system is not configured."
            )

        return self.screenshot_capture.capture()

    # =========================================================
    # Detect OCR elements
    # =========================================================

    def detect_text_elements(
        self,
        screenshot_path: str,
        state: VisualState,
    ):

        if self.ocr_reader is None:
            return

        try:

            detected = (
                self.ocr_reader.read_file_data(
                    screenshot_path
                )
            )

            for item in detected:

                element = VisualElement(
                    element_type="text",
                    text=item["text"],
                    x=item["x"],
                    y=item["y"],
                    width=item["width"],
                    height=item["height"],
                    confidence=(
                        item["confidence"] / 100.0
                    ),
                    source="ocr",
                )

                state.add_element(
                    element
                )

            state.metadata[
                "ocr_element_count"
            ] = len(detected)

        except Exception as error:

            state.metadata[
                "ocr_element_error"
            ] = str(error)

    # =========================================================
    # Analyze screenshot
    # =========================================================

    def analyze_screenshot(
        self,
        screenshot_path: str,
    ) -> VisualState:

        if self.vision_system is None:
            raise RuntimeError(
                "Vision system is not configured."
            )

        image = self.vision_system.load_image(
            screenshot_path
        )

        dimensions = (
            self.vision_system.get_dimensions(
                image
            )
        )

        state = VisualState(
            screenshot_path=screenshot_path,
            screen_width=dimensions["width"],
            screen_height=dimensions["height"],
        )

        # -----------------------------------------------------
        # Basic OCR text
        # -----------------------------------------------------

        if self.ocr_reader is not None:

            try:

                visible_text = (
                    self.ocr_reader.read_file(
                        screenshot_path
                    )
                )

                state.visible_text = (
                    visible_text.strip()
                )

            except Exception as error:

                state.metadata[
                    "ocr_error"
                ] = str(error)

        # -----------------------------------------------------
        # OCR visual elements
        # -----------------------------------------------------

        self.detect_text_elements(
            screenshot_path,
            state,
        )

        self.element_classifier.classify_all(
            state.elements
)

        # -----------------------------------------------------
        # OpenCV analysis
        # -----------------------------------------------------

        try:

            edges = (
                self.vision_system.detect_edges(
                    image
                )
            )

            state.metadata[
                "edge_pixels"
            ] = int(
                (edges > 0).sum()
            )

        except Exception as error:

            state.metadata[
                "vision_error"
            ] = str(error)

        return state

    # =========================================================
    # Windows UI information
    # =========================================================

    def add_window_information(
        self,
        state: VisualState,
    ):

        if self.ui_tree is None:
            return state

        try:

            titles = (
                self.ui_tree.get_window_titles()
            )

            state.window_titles = titles

            if titles:

                state.active_window = (
                    titles[0]
                )

        except Exception as error:

            state.metadata[
                "ui_tree_error"
            ] = str(error)

        return state

    # =========================================================
    # Complete observation
    # =========================================================

    def observe(self) -> VisualState:

        screenshot_path = (
            self.capture_screen()
        )

        state = self.analyze_screenshot(
            screenshot_path
        )

        state = self.add_window_information(
            state
        )

        return state

    # =========================================================
    # Human-readable summary
    # =========================================================

    def summarize(
        self,
        state: VisualState,
    ) -> str:

        lines = []

        lines.append(
            "Visual State"
        )

        lines.append(
            f"Screen: "
            f"{state.screen_width}x"
            f"{state.screen_height}"
        )

        if state.active_window:

            lines.append(
                f"Active window: "
                f"{state.active_window}"
            )

        if state.window_titles:

            lines.append(
                "Visible windows: "
                + ", ".join(
                    state.window_titles
                )
            )

        if state.visible_text:

            preview = (
                state.visible_text[:500]
            )

            lines.append(
                "Visible text:"
            )

            lines.append(
                preview
            )

        lines.append(
            f"Detected elements: "
            f"{len(state.elements)}"
        )

        return "\n".join(lines)