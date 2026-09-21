from dataclasses import dataclass
from typing import Any, Dict, Optional

from execution.mouse_keyboard import MouseKeyboardController
from execution.windows_uia import WindowsUIAutomation
from execution.browser_playwright import BrowserPlaywright
from safety.permissions import ActionPermissionChecker


@dataclass
class ActionResult:
    success: bool
    action: str
    message: str
    data: Optional[Dict[str, Any]] = None
    executor: Optional[str] = None


class ActionRouter:

    def __init__(self):
        self.mouse_keyboard = MouseKeyboardController()

        self.windows_uia = WindowsUIAutomation()

        self.browser = BrowserPlaywright(
            headless=False
        )

        self.permission_checker = (
            ActionPermissionChecker()
        )

    # =========================================================
    # Main dispatcher
    # =========================================================

    def execute(
        self,
        action: Dict[str, Any],
    ) -> ActionResult:

        action_type = action.get("action")

        if not action_type:
            return ActionResult(
                success=False,
                action="unknown",
                message="Action type is missing.",
            )

        # =====================================================
        # Safety validation
        # =====================================================

        permission = self.permission_checker.validate(
            action
        )

        if not permission["allowed"]:

            return ActionResult(
                success=False,
                action=action_type,
                message=permission["reason"],
                data={
                    "allowed": False,
                    "requires_confirmation": False,
                    "reason": permission["reason"],
                },
                executor="safety",
            )

        if permission["requires_confirmation"]:

            return ActionResult(
                success=False,
                action=action_type,
                message=(
                    "Action requires user confirmation: "
                    + permission["reason"]
                ),
                data={
                    "allowed": True,
                    "requires_confirmation": True,
                    "reason": permission["reason"],
                },
                executor="safety",
            )

        # =====================================================
        # Execute action
        # =====================================================

        try:

            # =================================================
            # Mouse / Keyboard
            # =================================================

            if action_type == "move":

                self.mouse_keyboard.move(
                    action["x"],
                    action["y"],
                    action.get("duration"),
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Mouse moved successfully.",
                    executor="mouse_keyboard",
                )

            if action_type == "click":

                self.mouse_keyboard.click(
                    action["x"],
                    action["y"],
                    action.get(
                        "button",
                        "left",
                    ),
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Mouse clicked successfully.",
                    executor="mouse_keyboard",
                )

            if action_type == "double_click":

                self.mouse_keyboard.double_click(
                    action["x"],
                    action["y"],
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Double click completed.",
                    executor="mouse_keyboard",
                )

            if action_type == "right_click":

                self.mouse_keyboard.right_click(
                    action["x"],
                    action["y"],
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Right click completed.",
                    executor="mouse_keyboard",
                )

            if action_type == "type":

                self.mouse_keyboard.type_text(
                    action["text"],
                    action.get(
                        "interval",
                        0.03,
                    ),
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Text typed successfully.",
                    executor="mouse_keyboard",
                )

            if action_type == "press":

                self.mouse_keyboard.press(
                    action["key"]
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Key pressed successfully.",
                    executor="mouse_keyboard",
                )

            if action_type == "hotkey":

                self.mouse_keyboard.hotkey(
                    *action["keys"]
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Hotkey executed successfully.",
                    executor="mouse_keyboard",
                )

            if action_type == "scroll":

                self.mouse_keyboard.scroll(
                    action["amount"]
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Scroll completed.",
                    executor="mouse_keyboard",
                )

            if action_type == "wait":

                self.mouse_keyboard.wait(
                    action["seconds"]
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Wait completed.",
                    executor="system",
                )

            # =================================================
            # Screenshot
            # =================================================

            if action_type == "screenshot":

                path = action.get(
                    "path",
                    "data/screenshots/action_router.png",
                )

                self.mouse_keyboard.screenshot(
                    path
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Screenshot captured.",
                    data={
                        "path": path
                    },
                    executor="perception",
                )

            # =================================================
            # Windows UI Automation - Existing path
            # =================================================

            if action_type == "open_application":

                application = (
                    self.windows_uia.open_application(
                        action["executable"]
                    )
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Application opened successfully.",
                    data={
                        "application": str(application)
                    },
                    executor="windows_uia",
                )

            if action_type == "inspect_window":

                window = self.windows_uia.find_window(
                    title=action.get(
                        "window_title"
                    ),
                    title_re=action.get(
                        "window_title_re"
                    ),
                )

                self.windows_uia.print_window_controls(
                    window,
                    depth=action.get(
                        "depth",
                        3,
                    ),
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Window inspected successfully.",
                    executor="windows_uia",
                )

            if action_type == "click_control":

                window = self.windows_uia.find_window(
                    title=action.get(
                        "window_title"
                    ),
                    title_re=action.get(
                        "window_title_re"
                    ),
                )

                self.windows_uia.click_control(
                    window=window,
                    title=action.get(
                        "control_title"
                    ),
                    control_type=action.get(
                        "control_type"
                    ),
                    auto_id=action.get(
                        "auto_id"
                    ),
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Windows UI control clicked.",
                    executor="windows_uia",
                )

            if action_type == "type_into_control":

                window = self.windows_uia.find_window(
                    title=action.get(
                        "window_title"
                    ),
                    title_re=action.get(
                        "window_title_re"
                    ),
                )

                self.windows_uia.type_into_control(
                    window=window,
                    text=action["text"],
                    title=action.get(
                        "control_title"
                    ),
                    control_type=action.get(
                        "control_type"
                    ),
                    auto_id=action.get(
                        "auto_id"
                    ),
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message=(
                        "Text entered into Windows UI control."
                    ),
                    executor="windows_uia",
                )

            if action_type == "get_control_text":

                window = self.windows_uia.find_window(
                    title=action.get(
                        "window_title"
                    ),
                    title_re=action.get(
                        "window_title_re"
                    ),
                )

                text = self.windows_uia.get_control_text(
                    window=window,
                    title=action.get(
                        "control_title"
                    ),
                    control_type=action.get(
                        "control_type"
                    ),
                    auto_id=action.get(
                        "auto_id"
                    ),
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Control text retrieved.",
                    data={
                        "text": text
                    },
                    executor="windows_uia",
                )

            # =================================================
            # Windows UI Automation - Fresh Raw UIA path
            # =================================================

            if action_type == "uia_click_control":

                window_title = action.get(
                    "window_title"
                )

                if not window_title:
                    return ActionResult(
                        success=False,
                        action=action_type,
                        message=(
                            "window_title is required for "
                            "uia_click_control."
                        ),
                        executor="windows_uia",
                    )

                control = self.windows_uia.click_by_window(
                    window_title=window_title,
                    title=action.get(
                        "control_title"
                    ),
                    control_type=action.get(
                        "control_type"
                    ),
                    auto_id=action.get(
                        "auto_id"
                    ),
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message=(
                        "Native Windows UI control clicked "
                        "using fresh UIA discovery."
                    ),
                    data={
                        "control_name": getattr(
                            control,
                            "name",
                            "",
                        ),
                        "control_type": getattr(
                            control,
                            "control_type",
                            "",
                        ),
                        "automation_id": getattr(
                            control,
                            "automation_id",
                            "",
                        ),
                        "window_title": window_title,
                    },
                    executor="windows_uia_raw",
                )

            if action_type == "uia_invoke_control":

                window_title = action.get(
                    "window_title"
                )

                if not window_title:
                    return ActionResult(
                        success=False,
                        action=action_type,
                        message=(
                            "window_title is required for "
                            "uia_invoke_control."
                        ),
                        executor="windows_uia",
                    )

                control = self.windows_uia.invoke_by_window(
                    window_title=window_title,
                    title=action.get(
                        "control_title"
                    ),
                    control_type=action.get(
                        "control_type"
                    ),
                    auto_id=action.get(
                        "auto_id"
                    ),
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message=(
                        "Native Windows UI control invoked "
                        "using fresh UIA discovery."
                    ),
                    data={
                        "control_name": getattr(
                            control,
                            "name",
                            "",
                        ),
                        "control_type": getattr(
                            control,
                            "control_type",
                            "",
                        ),
                        "automation_id": getattr(
                            control,
                            "automation_id",
                            "",
                        ),
                        "window_title": window_title,
                    },
                    executor="windows_uia_raw",
                )

            if action_type == "uia_get_control_text":

                window_title = action.get(
                    "window_title"
                )

                if not window_title:
                    return ActionResult(
                        success=False,
                        action=action_type,
                        message=(
                            "window_title is required for "
                            "uia_get_control_text."
                        ),
                        executor="windows_uia",
                    )

                window = self.windows_uia.find_raw_window(
                    title=window_title
                )

                if window is None:
                    return ActionResult(
                        success=False,
                        action=action_type,
                        message=(
                            f"Window '{window_title}' "
                            "could not be found."
                        ),
                        executor="windows_uia_raw",
                    )

                text = self.windows_uia.get_raw_control_text(
                    window=window,
                    title=action.get(
                        "control_title"
                    ),
                    control_type=action.get(
                        "control_type"
                    ),
                    auto_id=action.get(
                        "auto_id"
                    ),
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message=(
                        "Native Windows UI control text "
                        "retrieved using fresh UIA discovery."
                    ),
                    data={
                        "text": text,
                        "window_title": window_title,
                    },
                    executor="windows_uia_raw",
                )

            # =================================================
            # Playwright Browser
            # =================================================

            if action_type == "browser_start":

                self.browser.start()

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Browser started successfully.",
                    executor="playwright",
                )

            if action_type == "browser_open_url":

                url = self.browser.open_url(
                    action["url"]
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="URL opened successfully.",
                    data={
                        "url": url
                    },
                    executor="playwright",
                )

            if action_type == "browser_click":

                self.browser.click(
                    action["selector"]
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Browser element clicked.",
                    executor="playwright",
                )

            if action_type == "browser_fill":

                self.browser.fill(
                    action["selector"],
                    action["text"],
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Browser field filled.",
                    executor="playwright",
                )

            if action_type == "browser_press":

                self.browser.press(
                    action["selector"],
                    action["key"],
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Browser key pressed.",
                    executor="playwright",
                )

            if action_type == "browser_get_title":

                title = self.browser.get_title()

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Browser title retrieved.",
                    data={
                        "title": title
                    },
                    executor="playwright",
                )

            if action_type == "browser_get_url":

                url = self.browser.get_url()

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Browser URL retrieved.",
                    data={
                        "url": url
                    },
                    executor="playwright",
                )

            if action_type == "browser_get_text":

                selector = action.get(
                    "selector",
                    "body",
                )

                text = self.browser.get_text(
                    selector
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Browser text retrieved.",
                    data={
                        "text": text
                    },
                    executor="playwright",
                )

            if action_type == "browser_screenshot":

                path = action.get(
                    "path",
                    "data/screenshots/browser_action.png",
                )

                screenshot_path = (
                    self.browser.screenshot(
                        path
                    )
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Browser screenshot captured.",
                    data={
                        "path": screenshot_path
                    },
                    executor="playwright",
                )

            if action_type == "browser_wait":

                milliseconds = action.get(
                    "milliseconds",
                    1000,
                )

                self.browser.wait(
                    milliseconds
                )

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Browser wait completed.",
                    executor="playwright",
                )

            if action_type == "browser_state":

                state = self.browser.get_state()

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Browser state retrieved.",
                    data=state,
                    executor="playwright",
                )

            if action_type == "browser_close":

                self.browser.close()

                return ActionResult(
                    success=True,
                    action=action_type,
                    message="Browser closed successfully.",
                    executor="playwright",
                )

            # =================================================
            # Unknown action
            # =================================================

            return ActionResult(
                success=False,
                action=action_type,
                message=f"Unknown action: {action_type}",
            )

        except Exception as error:

            return ActionResult(
                success=False,
                action=action_type,
                message=f"Action failed: {error}",
            )