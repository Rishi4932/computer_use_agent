from pathlib import Path

import cv2


class VisionSystem:
    """
    Basic computer vision utilities.

    This layer will later be connected to an AI vision model.
    """

    def load_image(self, image_path):
        """
        Load an image using OpenCV.
        """

        image_path = Path(image_path)

        image = cv2.imread(
            str(image_path)
        )

        if image is None:
            raise FileNotFoundError(
                f"Could not load image: {image_path}"
            )

        return image

    def get_dimensions(self, image):
        """
        Return image dimensions.
        """

        height, width = image.shape[:2]

        return {
            "width": width,
            "height": height,
        }

    def detect_edges(self, image):
        """
        Basic edge detection.

        This is only a foundation for future
        visual understanding.
        """

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        edges = cv2.Canny(
            gray,
            100,
            200,
        )

        return edges