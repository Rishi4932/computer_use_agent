from perception.screenshot import ScreenshotCapture
from perception.ocr import OCRReader
from perception.vision import VisionSystem
from perception.windows_ui_tree import WindowsUITree


def main():

    print("=" * 60)
    print(" COMPUTER USE AI AGENT - PERCEPTION TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Screenshot
    # ---------------------------------------------------------

    print("\n[1] Capturing screen...")

    screenshot = ScreenshotCapture()

    path = screenshot.capture(
        "manual_perception_test.png"
    )

    print(
        f"Screenshot saved to: {path}"
    )

    # ---------------------------------------------------------
    # 2. Vision
    # ---------------------------------------------------------

    print("\n[2] Analyzing image...")

    vision = VisionSystem()

    image = vision.load_image(
        path
    )

    dimensions = vision.get_dimensions(
        image
    )

    print(
        f"Screen size: "
        f"{dimensions['width']} x "
        f"{dimensions['height']}"
    )

    # ---------------------------------------------------------
    # 3. OCR
    # ---------------------------------------------------------

    print("\n[3] Running OCR...")

    ocr = OCRReader()

    try:

        text = ocr.read_file(
            path
        )

        print("\nDetected text:")
        print("-" * 40)
        print(text)
        print("-" * 40)

    except Exception as exc:

        print(
            f"OCR failed: {exc}"
        )

    # ---------------------------------------------------------
    # 4. Windows UI Tree
    # ---------------------------------------------------------

    print("\n[4] Inspecting Windows UI...")

    ui_tree = WindowsUITree()

    titles = ui_tree.get_window_titles()

    print("\nVisible windows:")

    for title in titles:
        print(
            f"  - {title}"
        )

    print("\nPerception test completed.")


if __name__ == "__main__":
    main()