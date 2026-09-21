from typing import Optional, Dict, Any

from execution.action_router import ActionRouter
from perception.screenshot import ScreenshotCapture
from perception.ocr import OCRReader
from perception.vision import VisionSystem
from perception.windows_ui_tree import WindowsUITree

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
        Vision + UIA
          ↓
        Verification

    Native Windows UIA actions can use an
    application-scoped observation by supplying
    'window_title' in the action.
    """

    UIA_ACTIONS = {
        "uia_click_control",
        "uia_invoke_control",
        "uia_get_control_text",
    }

    def __init__(
        self,
        router: Optional[ActionRouter] = None,
        screenshot_capture: Optional[ScreenshotCapture] = None,
        vision_reasoner: Optional[VisionReasoner] = None,
        verifier: Optional[ActionVerifier] = None,
    ):
        self.router = router or ActionRouter()

        self.screenshot_capture = (
            screenshot_capture
            or ScreenshotCapture()
        )

        self.vision_reasoner = (
            vision_reasoner
            or VisionReasoner(
                screenshot_capture=self.screenshot_capture,
                ocr_reader=OCRReader(),
                vision_system=VisionSystem(),
                ui_tree=WindowsUITree(),
            )
        )

        self.verifier = (
            verifier
            or ActionVerifier()
        )

    # ---------------------------------------------------------
    # Vision reasoner selection
    # ---------------------------------------------------------

    def _get_vision_reasoner(
        self,
        action: Dict[str, Any],
    ) -> VisionReasoner:
        """
        Return the appropriate VisionReasoner for verification.

        For native Windows UIA actions with a window_title,
        verification is scoped to that application window.

        For all other actions, the existing VisionReasoner
        is reused unchanged.
        """

        action_type = action.get("action")

        if (
            action_type in self.UIA_ACTIONS
            and action.get("window_title")
        ):
            target_window = action.get(
                "window_title"
            )

            self.vision_reasoner.set_target_window(
                target_window
            )

        else:
            # Do not force application scoping for
            # normal screenshot/PyAutoGUI/browser actions.
            self.vision_reasoner.set_target_window(
                None
            )

        return self.vision_reasoner

    # ---------------------------------------------------------
    # Execute + verify
    # ---------------------------------------------------------

    def execute_and_verify(
        self,
        action: Dict[str, Any],
        expected: Dict[str, Any],
    ) -> Dict[str, Any]:

        # -----------------------------------------------------
        # 1. Execute action
        # -----------------------------------------------------

        action_result = self.router.execute(
            action
        )

        if not action_result.success:

            return {
                "success": False,
                "action_result": action_result,
                "verification": None,
                "screenshot": None,
                "message": "Action execution failed.",
            }

        # -----------------------------------------------------
        # 2. Capture fresh screenshot
        # -----------------------------------------------------

        screenshot_path = (
            self.screenshot_capture.capture()
        )

        # -----------------------------------------------------
        # 3. Select observation scope
        # -----------------------------------------------------

        vision_reasoner = (
            self._get_vision_reasoner(
                action
            )
        )

        # -----------------------------------------------------
        # 4. Analyze fresh computer state
        # -----------------------------------------------------

        visual_state = (
            vision_reasoner.analyze_screenshot(
                str(screenshot_path)
            )
        )

        visual_state = (
            vision_reasoner.add_window_information(
                visual_state
            )
        )

        # -----------------------------------------------------
        # 5. Select verification strategy
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # 6. Verify
        # -----------------------------------------------------

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
                    "Unknown verification type: "
                    f"{verification_type}"
                ),
            }

        # -----------------------------------------------------
        # 7. Return complete result
        # -----------------------------------------------------

        return {
            "success": verification.success,
            "action_result": action_result,
            "verification": verification,
            "screenshot": str(
                screenshot_path
            ),
            "visual_state": visual_state,
            "message": verification.reason,
        }