from perception.screenshot import ScreenshotCapture
from perception.ocr import OCRReader
from perception.vision import VisionSystem
from perception.windows_ui_tree import WindowsUITree

from intelligence.element_classifier import ElementClassifier

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class VisualElement:
    element_type: str
    text: str = ""

    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None

    confidence: float = 0.0
    source: str = "unknown"

    control_type: Optional[str] = None
    auto_id: Optional[str] = None

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
            "control_type": self.control_type,
            "auto_id": self.auto_id,
        }


@dataclass
class VisualState:
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

    def add_element(self, element):
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

    def __init__(
        self,
        screenshot_capture=None,
        ocr_reader=None,
        vision_system=None,
        ui_tree=None,
        target_window: Optional[str] = None,
    ):

        self.screenshot_capture = (
            screenshot_capture
        )

        self.ocr_reader = ocr_reader
        self.vision_system = vision_system
        self.ui_tree = ui_tree

        self.target_window = target_window

        self.element_classifier = (
            ElementClassifier()
        )

    # ---------------------------------------------------------
    # Target window configuration
    # ---------------------------------------------------------

    def set_target_window(self, title: Optional[str]):
        self.target_window = title

    def get_target_window(self):
        return self.target_window

    # ---------------------------------------------------------
    # Screenshot
    # ---------------------------------------------------------

    def capture_screen(self):

        if self.screenshot_capture is None:
            raise RuntimeError(
                "Screenshot capture system is not configured."
            )

        return self.screenshot_capture.capture()

    # ---------------------------------------------------------
    # OCR elements
    # ---------------------------------------------------------

    def detect_text_elements(
        self,
        screenshot_path,
        state,
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
                        item["confidence"]
                        / 100.0
                    ),
                    source="ocr",
                )

                state.add_element(element)

            state.metadata[
                "ocr_element_count"
            ] = len(detected)

        except Exception as error:

            state.metadata[
                "ocr_element_error"
            ] = str(error)

    # ---------------------------------------------------------
    # UI Automation elements
    # ---------------------------------------------------------

    def detect_uia_elements(
        self,
        state,
    ):

        if self.ui_tree is None:
            return

        try:

            # -------------------------------------------------
            # If a target window is configured, only inspect it
            # -------------------------------------------------

            if self.target_window:

                windows = [
                    self.ui_tree.get_window(
                        title=self.target_window
                    )
                ]

            else:

                windows = (
                    self.ui_tree.get_windows()
                )

            total_uia = 0

            for window in windows:

                try:

                    window_title = (
                        window.window_text()
                    )

                    if not window_title:
                        continue

                    elements = (
                        self.ui_tree.get_ui_elements(
                            window
                        )
                    )

                    for item in elements:

                        element = VisualElement(
                            element_type=item[
                                "element_type"
                            ],

                            text=item[
                                "text"
                            ],

                            x=item["x"],
                            y=item["y"],

                            width=item[
                                "width"
                            ],

                            height=item[
                                "height"
                            ],

                            confidence=item[
                                "confidence"
                            ],

                            source="uia",

                            control_type=item.get(
                                "control_type"
                            ),

                            auto_id=item.get(
                                "auto_id"
                            ),
                        )

                        state.add_element(
                            element
                        )

                        total_uia += 1

                except Exception:
                    continue

            state.metadata[
                "uia_element_count"
            ] = total_uia

            state.metadata[
                "uia_target_window"
            ] = self.target_window

        except Exception as error:

            state.metadata[
                "uia_element_error"
            ] = str(error)

    # ---------------------------------------------------------
    # Screenshot analysis
    # ---------------------------------------------------------

    def analyze_screenshot(
        self,
        screenshot_path,
    ):

        if self.vision_system is None:
            raise RuntimeError(
                "Vision system is not configured."
            )

        image = (
            self.vision_system.load_image(
                screenshot_path
            )
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
        # OCR visible text
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
        # OCR elements
        # -----------------------------------------------------

        self.detect_text_elements(
            screenshot_path,
            state,
        )

        # -----------------------------------------------------
        # Classify OCR elements
        # -----------------------------------------------------

        self.element_classifier.classify_all(
            [
                element
                for element in state.elements
                if element.source == "ocr"
            ]
        )

        # -----------------------------------------------------
        # UI Automation
        # -----------------------------------------------------

        self.detect_uia_elements(
            state
        )

        # -----------------------------------------------------
        # Vision
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

    # ---------------------------------------------------------
    # Window information
    # ---------------------------------------------------------

    def add_window_information(
        self,
        state,
    ):

        if self.ui_tree is None:
            return state

        try:

            titles = (
                self.ui_tree.get_window_titles()
            )

            state.window_titles = titles

            if self.target_window:

                state.active_window = (
                    self.target_window
                )

            elif titles:

                state.active_window = titles[0]

        except Exception as error:

            state.metadata[
                "ui_tree_error"
            ] = str(error)

        return state

    # ---------------------------------------------------------
    # Full observation
    # ---------------------------------------------------------

    def observe(self):

        screenshot_path = (
            self.capture_screen()
        )

        state = (
            self.analyze_screenshot(
                screenshot_path
            )
        )

        state = (
            self.add_window_information(
                state
            )
        )

        return state

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    def summarize(
        self,
        state,
    ):

        lines = [
            "Visual State",
            (
                f"Screen: "
                f"{state.screen_width}x"
                f"{state.screen_height}"
            ),
        ]

        if state.active_window:

            lines.append(
                f"Target window: "
                f"{state.active_window}"
            )

        if state.visible_text:

            lines.append(
                "Visible text:"
            )

            lines.append(
                state.visible_text[:500]
            )

        lines.append(
            "OCR elements: "
            + str(
                state.metadata.get(
                    "ocr_element_count",
                    0,
                )
            )
        )

        lines.append(
            "UIA elements: "
            + str(
                state.metadata.get(
                    "uia_element_count",
                    0,
                )
            )
        )

        lines.append(
            "Total elements: "
            + str(
                len(state.elements)
            )
        )

        return "\n".join(lines)