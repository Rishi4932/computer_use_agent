from pathlib import Path
from typing import Any, Dict, List

import pytesseract
from PIL import Image


class OCRReader:

    def __init__(self, tesseract_path=None):

        if tesseract_path is None:
            tesseract_path = (
                r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            )

        if Path(tesseract_path).exists():
            pytesseract.pytesseract.tesseract_cmd = (
                tesseract_path
            )

    # =========================================================
    # Basic OCR
    # =========================================================

    def read_image(self, image):

        return pytesseract.image_to_string(
            image
        )

    def read_file(self, image_path):

        image = Image.open(image_path)

        return self.read_image(image)

    # =========================================================
    # OCR with positions
    # =========================================================

    def read_data(self, image) -> List[Dict[str, Any]]:
        """
        Extract detected text together with
        bounding-box coordinates and confidence.
        """

        data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT,
        )

        elements = []

        count = len(data["text"])

        for i in range(count):

            text = data["text"][i].strip()

            if not text:
                continue

            try:
                confidence = float(
                    data["conf"][i]
                )
            except (
                ValueError,
                TypeError,
            ):
                confidence = 0.0

            if confidence < 0:
                continue

            x = int(data["left"][i])
            y = int(data["top"][i])
            width = int(data["width"][i])
            height = int(data["height"][i])

            elements.append(
                {
                    "text": text,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "confidence": confidence,
                }
            )

        return elements

    def read_file_data(
        self,
        image_path,
    ) -> List[Dict[str, Any]]:
        """
        Extract OCR text and coordinates from
        an image file.
        """

        image = Image.open(image_path)

        return self.read_data(image)