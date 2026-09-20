from pathlib import Path

from perception.screenshot import ScreenshotCapture
from perception.ocr import OCRReader
from perception.vision import VisionSystem
from perception.windows_ui_tree import WindowsUITree


def test_screenshot_capture():

    capture = ScreenshotCapture()

    path = capture.capture(
        "test_screen.png"
    )

    assert path.exists()

    print(
        f"\nScreenshot saved to: {path}"
    )


def test_vision_dimensions():

    capture = ScreenshotCapture()

    path = capture.capture(
        "vision_test.png"
    )

    vision = VisionSystem()

    image = vision.load_image(
        path
    )

    dimensions = vision.get_dimensions(
        image
    )

    assert dimensions["width"] > 0
    assert dimensions["height"] > 0

    print(
        f"\nScreen dimensions: "
        f"{dimensions['width']}x"
        f"{dimensions['height']}"
    )


def test_windows_ui_tree():

    ui_tree = WindowsUITree()

    titles = ui_tree.get_window_titles()

    print("\nVisible windows:")

    for title in titles:
        print(f"  - {title}")

    assert isinstance(
        titles,
        list
    )


def test_ocr_reader():

    ocr = OCRReader()

    assert ocr is not None