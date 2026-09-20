from typing import Optional, Dict, Any, List

from intelligence.action_selector import ActionSelector
from intelligence.vision_reasoner import VisualElement
from execution.action_router import ActionRouter


class GroundedActionExecutor:
    """
    Connects visual perception and semantic action selection
    to the real ActionRouter.

    Pipeline:

        Visual Elements
             ↓
        ActionSelector
             ↓
        Grounded Action
             ↓
        ActionRouter
             ↓
        Windows
    """

    def __init__(
        self,
        selector: Optional[ActionSelector] = None,
        router: Optional[ActionRouter] = None,
    ):
        self.selector = selector or ActionSelector()
        self.router = router or ActionRouter()

    def click_target(
        self,
        elements: List[VisualElement],
        target: str,
        element_type: Optional[str] = None,
    ) -> Dict[str, Any]:

        selected_action = self.selector.click_element(
            elements=elements,
            text=target,
            element_type=element_type,
        )

        if selected_action is None:
            return {
                "success": False,
                "message": f"Target '{target}' was not found.",
                "action": None,
            }

        result = self.router.execute({
            "action": "click",
            "x": selected_action["x"],
            "y": selected_action["y"],
        })

        return {
            "success": result.success,
            "message": result.message,
            "action": selected_action,
            "router_result": result,
        }

    def type_into_target(
        self,
        elements: List[VisualElement],
        target: str,
        value: str,
    ) -> Dict[str, Any]:

        selected_action = self.selector.type_into_element(
            elements=elements,
            text=target,
            value=value,
        )

        if selected_action is None:
            return {
                "success": False,
                "message": f"Text field '{target}' was not found.",
                "action": None,
            }

        click_result = self.router.execute({
            "action": "click",
            "x": selected_action["x"],
            "y": selected_action["y"],
        })

        if not click_result.success:
            return {
                "success": False,
                "message": "Could not focus the target text field.",
                "action": selected_action,
                "router_result": click_result,
            }

        type_result = self.router.execute({
            "action": "type",
            "text": value,
        })

        return {
            "success": type_result.success,
            "message": type_result.message,
            "action": selected_action,
            "router_result": type_result,
        }