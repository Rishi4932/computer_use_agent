from typing import Optional, Dict, Any, List

from intelligence.vision_reasoner import VisualElement


class ActionSelector:
    """
    Selects executable actions from perceived visual elements.

    This is currently rule-based and deterministic.
    A learned/LLM-based action selector can be added later
    as the research version.
    """

    def find_element(
        self,
        elements: List[VisualElement],
        text: str,
        element_type: Optional[str] = None,
    ) -> Optional[VisualElement]:

        target = text.strip().lower()

        candidates = []

        for element in elements:
            element_text = element.text.strip().lower()

            if element_text == target:
                if element_type is None:
                    candidates.append(element)

                elif element.element_type == element_type:
                    candidates.append(element)

        if candidates:
            return candidates[0]

        # Partial text match
        for element in elements:
            element_text = element.text.strip().lower()

            if target in element_text:

                if element_type is None:
                    return element

                if element.element_type == element_type:
                    return element

        return None

    def click_element(
        self,
        elements: List[VisualElement],
        text: str,
        element_type: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:

        element = self.find_element(
            elements=elements,
            text=text,
            element_type=element_type,
        )

        if element is None:
            return None

        center_x = element.x + (element.width // 2)
        center_y = element.y + (element.height // 2)

        return {
            "action": "click",
            "x": center_x,
            "y": center_y,
            "target": element.text,
            "element_type": element.element_type,
            "confidence": element.confidence,
        }

    def type_into_element(
        self,
        elements: List[VisualElement],
        text: str,
        value: str,
    ) -> Optional[Dict[str, Any]]:

        element = self.find_element(
            elements=elements,
            text=text,
            element_type="text_field",
        )

        if element is None:
            return None

        center_x = element.x + (element.width // 2)
        center_y = element.y + (element.height // 2)

        return {
            "action": "click_and_type",
            "x": center_x,
            "y": center_y,
            "text": value,
            "target": element.text,
            "element_type": element.element_type,
            "confidence": element.confidence,
        }