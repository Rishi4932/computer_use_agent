from typing import Any, Dict, List, Optional

from intelligence.action_selector import ActionSelector
from intelligence.vision_reasoner import VisualElement


class RecoveryRelocator:
    """
    Re-locates a previously targeted visual element after
    an action fails verification.

    Pipeline:

        Fresh VisualState
              ↓
        Visual Elements
              ↓
        ActionSelector
              ↓
        Locate original target
              ↓
        Generate corrected action
    """

    def __init__(
        self,
        selector: Optional[ActionSelector] = None,
    ):
        self.selector = selector or ActionSelector()

    def relocate_click(
        self,
        elements: List[VisualElement],
        original_action: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Locate the original click target again and return
        a new click action using the target's current position.

        Returns None if the target cannot be found.
        """

        target = original_action.get("target")

        if not target:
            return None

        element_type = original_action.get(
            "element_type"
        )

        selected_action = self.selector.click_element(
            elements=elements,
            text=target,
            element_type=element_type,
        )

        if selected_action is None:
            return None

        return {
            "action": "click",
            "x": selected_action["x"],
            "y": selected_action["y"],
            "target": selected_action["target"],
            "element_type": selected_action["element_type"],
            "confidence": selected_action["confidence"],
        }