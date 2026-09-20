from typing import List, Any


class ElementClassifier:
    """
    Classifies visual elements into semantic categories.

    The classifier is intentionally rule-based at this stage.
    A multimodal AI classifier can be added later for comparison.
    """

    BUTTON_WORDS = {
        "ok",
        "cancel",
        "submit",
        "save",
        "close",
        "next",
        "back",
        "continue",
        "login",
        "sign in",
        "sign up",
        "download",
        "upload",
        "search",
        "start",
        "stop",
        "open",
        "send",
        "apply",
        "confirm",
    }

    INPUT_WORDS = {
        "search",
        "username",
        "password",
        "email",
        "name",
        "address",
        "phone",
        "query",
        "enter",
    }

    LINK_WORDS = {
        "learn more",
        "read more",
        "details",
        "documentation",
        "help",
        "contact us",
        "privacy",
        "terms",
    }

    HEADING_WORDS = {
        "welcome",
        "home",
        "dashboard",
        "settings",
        "about",
        "profile",
    }

    def classify(self, element: Any) -> Any:
        """
        Classify one visual element.
        """

        text = element.text.strip().lower()

        if not text:
            element.element_type = "unknown"
            return element

        # Exact button matches
        if text in self.BUTTON_WORDS:
            element.element_type = "button"
            return element

        # Input-field indicators
        if text in self.INPUT_WORDS:
            element.element_type = "text_field"
            return element

        # Link indicators
        if text in self.LINK_WORDS:
            element.element_type = "link"
            return element

        # Heading indicators
        if text in self.HEADING_WORDS:
            element.element_type = "heading"
            return element

        # Label indicators
        if text.endswith(":"):
            element.element_type = "label"
            return element

        # Longer text is ordinary page content
        if len(text.split()) >= 4:
            element.element_type = "text"
            return element

        # Default classification
        element.element_type = "text"

        return element

    def classify_all(
        self,
        elements: List[Any],
    ) -> List[Any]:
        """
        Classify all detected visual elements.
        """

        for element in elements:
            self.classify(element)

        return elements