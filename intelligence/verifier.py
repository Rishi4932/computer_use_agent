from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from intelligence.vision_reasoner import VisualElement


@dataclass
class VerificationResult:
    success: bool
    confidence: float
    reason: str
    matched_elements: List[VisualElement] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "success": self.success,
            "confidence": self.confidence,
            "reason": self.reason,
            "matched_elements": [
                element.to_dict()
                for element in self.matched_elements
            ],
            "details": self.details,
        }


class ActionVerifier:

    def _normalize_text(self, text: str) -> str:
        """
        Normalize OCR/UI text so small differences in whitespace,
        punctuation and line breaks do not cause false failures.
        """

        if text is None:
            return ""

        text = str(text)

        # Normalize whitespace
        text = " ".join(text.split())

        # Normalize common OCR punctuation artifacts
        text = text.replace("‘", "'")
        text = text.replace("’", "'")
        text = text.replace("“", '"')
        text = text.replace("”", '"')

        return text.strip().lower()

    def verify_element_present(
        self,
        elements,
        text,
        element_type=None,
    ):
        expected = self._normalize_text(text)

        matches = []

        for element in elements:
            element_text = self._normalize_text(
                getattr(element, "text", "")
            )

            if expected in element_text:

                if (
                    element_type is None
                    or getattr(element, "element_type", None)
                    == element_type
                ):
                    matches.append(element)

        if matches:

            confidence = max(
                getattr(element, "confidence", 0.0)
                for element in matches
            )

            return VerificationResult(
                success=True,
                confidence=confidence,
                reason=f"Expected text '{text}' was detected.",
                matched_elements=matches,
                details={
                    "expected_text": text,
                },
            )

        return VerificationResult(
            success=False,
            confidence=0.0,
            reason=f"Expected text '{text}' was not detected.",
            matched_elements=[],
            details={
                "expected_text": text,
            },
        )

    def verify_element_absent(
        self,
        elements,
        text,
        element_type=None,
    ):
        expected = self._normalize_text(text)

        matches = []

        for element in elements:

            element_text = self._normalize_text(
                getattr(element, "text", "")
            )

            if expected in element_text:

                if (
                    element_type is None
                    or getattr(element, "element_type", None)
                    == element_type
                ):
                    matches.append(element)

        if matches:

            return VerificationResult(
                success=False,
                confidence=0.0,
                reason=f"Unexpected text '{text}' is present.",
                matched_elements=matches,
                details={
                    "expected_text": text,
                },
            )

        return VerificationResult(
            success=True,
            confidence=1.0,
            reason=f"Expected text '{text}' is absent.",
            matched_elements=[],
            details={
                "expected_text": text,
            },
        )

    def verify_text_contains(
        self,
        elements,
        text,
    ):
        """
        Verify that expected text exists somewhere in the observed
        visual elements.

        Handles:
        - OCR line breaks
        - multiple spaces
        - capitalization differences
        - common OCR punctuation artifacts
        """

        expected = self._normalize_text(text)

        # -------------------------------------------------------------
        # 1. Check individual elements
        # -------------------------------------------------------------

        individual_matches = []

        for element in elements:

            element_text = self._normalize_text(
                getattr(element, "text", "")
            )

            if expected in element_text:
                individual_matches.append(element)

        if individual_matches:

            confidence = max(
                getattr(element, "confidence", 0.0)
                for element in individual_matches
            )

            return VerificationResult(
                success=True,
                confidence=confidence,
                reason=f"Expected text '{text}' was detected.",
                matched_elements=individual_matches,
                details={
                    "expected_text": text,
                    "match_mode": "individual_element",
                },
            )

        # -------------------------------------------------------------
        # 2. Check combined OCR text
        # -------------------------------------------------------------

        combined_text = " ".join(
            self._normalize_text(
                getattr(element, "text", "")
            )
            for element in elements
            if getattr(element, "text", "")
        )

        if expected in combined_text:

            return VerificationResult(
                success=True,
                confidence=0.85,
                reason=f"Expected text '{text}' was detected in combined OCR.",
                matched_elements=[],
                details={
                    "expected_text": text,
                    "match_mode": "combined_elements",
                },
            )

        # -------------------------------------------------------------
        # 3. Failure
        # -------------------------------------------------------------

        return VerificationResult(
            success=False,
            confidence=0.0,
            reason=f"Expected text '{text}' was not detected.",
            matched_elements=[],
            details={
                "expected_text": text,
                "match_mode": "none",
            },
        )