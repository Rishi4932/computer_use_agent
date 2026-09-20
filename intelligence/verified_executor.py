from typing import Optional, Dict, Any

from execution.action_router import ActionRouter
from perception.screenshot import ScreenshotCapture
from intelligence.vision_reasoner import VisionReasoner
from intelligence.verifier import ActionVerifier


class VerifiedActionExecutor:
    """
    Executes an action and verifies the resulting
    computer state.

    Pipeline:

        Action
          ↓
        Execute
          ↓
        Screenshot
          ↓
        Vision
          ↓
        Verification
    """

    def __init__(
        self,
        router: Optional[ActionRouter] = None,
        screenshot_capture: Optional[ScreenshotCapture] = None,
        vision_reasoner: Optional[VisionReasoner] = None,
        verifier: Optional[ActionVerifier] = None,
    ):
        self.router = router or ActionRouter()
        self.screenshot_capture = (
            screenshot_capture or ScreenshotCapture()
        )
        self.vision_reasoner = (
            vision_reasoner or VisionReasoner()
        )
        self.verifier = verifier or ActionVerifier()

    def execute_and_verify(
        self,
        action: Dict[str, Any],
        expected: Dict[str, Any],
    ) -> Dict[str, Any]:

        # -------------------------------------------------
        # Step 1: Execute action
        # -------------------------------------------------

        action_result = self.router.execute(action)

        if not action_result.success:
            return {
                "success": False,
                "action_result": action_result,
                "verification": None,
                "screenshot": None,
                "message": (
                    "Action execution failed."
                ),
            }

        # -------------------------------------------------
        # Step 2: Capture new screen
        # -------------------------------------------------

        screenshot_path = (
            self.screenshot_capture.capture()
        )

        # -------------------------------------------------
        # Step 3: Analyze new screen
        # -------------------------------------------------

        visual_state = (
            self.vision_reasoner.analyze_screenshot(
                str(screenshot_path)
            )
        )

        # -------------------------------------------------
        # Step 4: Verify expected result
        # -------------------------------------------------

        verification_type = expected.get(
            "type",
            "text_contains",
        )

        expected_text = expected.get(
            "text",
            "",
        )

        expected_element_type = expected.get(
            "element_type"
        )

        if verification_type == "present":

            verification = (
                self.verifier.verify_element_present(
                    visual_state.elements,
                    expected_text,
                    expected_element_type,
                )
            )

        elif verification_type == "absent":

            verification = (
                self.verifier.verify_element_absent(
                    visual_state.elements,
                    expected_text,
                    expected_element_type,
                )
            )

        elif verification_type == "text_contains":

            verification = (
                self.verifier.verify_text_contains(
                    visual_state.elements,
                    expected_text,
                )
            )

        else:

            return {
                "success": False,
                "action_result": action_result,
                "verification": None,
                "screenshot": str(
                    screenshot_path
                ),
                "message": (
                    f"Unknown verification type: "
                    f"{verification_type}"
                ),
            }

        # -------------------------------------------------
        # Step 5: Final result
        # -------------------------------------------------

        return {
            "success": verification.success,
            "action_result": action_result,
            "verification": verification,
            "screenshot": str(
                screenshot_path
            ),
            "message": verification.reason,
        }