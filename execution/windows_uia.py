from typing import Optional, List, Any

from pywinauto import Desktop
from pywinauto.application import Application
from pywinauto.uia_element_info import UIAElementInfo
from pywinauto.controls.uiawrapper import UIAWrapper


class WindowsUIAutomation:
    """
    Windows UI Automation layer.

    Supports:

    1. High-level pywinauto operations.
    2. Raw UIA discovery for reliable native Windows inspection.
    3. Fresh control resolution immediately before interaction.
    """

    def __init__(self):
        self.application: Optional[Application] = None

    # ============================================================
    # HIGH-LEVEL PYWINAUTO
    # ============================================================

    def open_application(self, executable: str):
        self.application = Application(
            backend="uia"
        ).start(executable)

        try:
            window = self.application.top_window()
            window.wait("visible", timeout=10)

            try:
                window.restore()
            except Exception:
                pass

            try:
                window.set_focus()
            except Exception:
                pass

        except Exception:
            pass

        return self.application

    def connect(self, title=None, process=None):
        if title:
            self.application = Application(
                backend="uia"
            ).connect(title=title)

        elif process:
            self.application = Application(
                backend="uia"
            ).connect(process=process)

        else:
            raise ValueError(
                "Either title or process must be provided."
            )

        return self.application

    def desktop(self):
        return Desktop(backend="uia")

    def find_window(self, title=None, title_re=None):
        desktop = self.desktop()

        if title:
            return desktop.window(title=title)

        if title_re:
            return desktop.window(title_re=title_re)

        raise ValueError(
            "Provide title or title_re."
        )

    def get_window(self, title=None, title_re=None):
        return self.find_window(
            title=title,
            title_re=title_re
        )

    def list_windows(self):
        return self.desktop().windows()

    def list_window_titles(self):
        windows = self.list_windows()

        titles = []

        for window in windows:
            try:
                title = window.window_text()

                if title:
                    titles.append(title)

            except Exception:
                continue

        return titles

    def find_control(
        self,
        window,
        title=None,
        control_type=None,
        auto_id=None
    ):
        criteria = {}

        if title is not None:
            criteria["title"] = title

        if control_type is not None:
            criteria["control_type"] = control_type

        if auto_id is not None:
            criteria["auto_id"] = auto_id

        if not criteria:
            raise ValueError(
                "At least one control identifier must be provided."
            )

        return window.child_window(**criteria)

    def click_control(
        self,
        window,
        title=None,
        control_type=None,
        auto_id=None
    ):
        control = self.find_control(
            window=window,
            title=title,
            control_type=control_type,
            auto_id=auto_id
        )

        control.wait(
            "visible",
            timeout=10
        )

        control.click_input()

        return control

    def type_into_control(
        self,
        window,
        text,
        title=None,
        control_type=None,
        auto_id=None
    ):
        control = self.find_control(
            window=window,
            title=title,
            control_type=control_type,
            auto_id=auto_id
        )

        control.wait(
            "visible",
            timeout=10
        )

        control.click_input()

        control.type_keys(
            text,
            with_spaces=True,
            pause=0.02
        )

        return control

    def get_control_text(
        self,
        window,
        title=None,
        control_type=None,
        auto_id=None
    ):
        control = self.find_control(
            window=window,
            title=title,
            control_type=control_type,
            auto_id=auto_id
        )

        return control.window_text()

    def print_window_controls(
        self,
        window,
        depth=3
    ):
        window.print_control_identifiers(
            depth=depth
        )

    # ============================================================
    # RAW UIA
    # ============================================================

    def raw_uia_root(self):
        return UIAElementInfo()

    def raw_top_level_windows(self):
        """
        Get a fresh snapshot of top-level UIA windows.
        """
        root = self.raw_uia_root()
        return root.children()

    def find_raw_window(
        self,
        title: Optional[str] = None,
        process: Optional[int] = None
    ):
        """
        Find a fresh raw UIA window.

        A new UIA snapshot is obtained every time this method
        is called.
        """

        if title is None and process is None:
            raise ValueError(
                "Provide title or process."
            )

        windows = self.raw_top_level_windows()

        for window in windows:
            try:

                if title is not None:
                    if window.name != title:
                        continue

                if process is not None:
                    if window.process_id != process:
                        continue

                return window

            except Exception:
                continue

        return None

    def find_raw_control(
        self,
        window,
        title: Optional[str] = None,
        control_type: Optional[str] = None,
        auto_id: Optional[str] = None
    ):
        """
        Find a control from a fresh UIA tree.

        IMPORTANT:
        UIA elements are treated as observations, not permanent
        references. The tree can change after any UI action.
        """

        if (
            title is None
            and control_type is None
            and auto_id is None
        ):
            raise ValueError(
                "Provide title, control_type, or auto_id."
            )

        try:
            controls = window.descendants()

        except Exception:
            return None

        for control in controls:

            try:

                if title is not None:
                    if control.name != title:
                        continue

                if control_type is not None:
                    if control.control_type != control_type:
                        continue

                if auto_id is not None:
                    if control.automation_id != auto_id:
                        continue

                return control

            except Exception:
                continue

        return None

    def list_raw_controls(
        self,
        window
    ) -> List[Any]:

        try:
            return window.descendants()

        except Exception:
            return []

    # ============================================================
    # RAW CONTROL WRAPPER
    # ============================================================

    def _wrap_raw_control(self, control):
        """
        Convert UIAElementInfo into a pywinauto UIAWrapper.

        UIAElementInfo describes an element.
        UIAWrapper provides interaction methods.
        """

        return UIAWrapper(control)

    # ============================================================
    # RAW CLICK
    # ============================================================

    def click_raw_control(
        self,
        window,
        title: Optional[str] = None,
        control_type: Optional[str] = None,
        auto_id: Optional[str] = None
    ):
        """
        Click a control found through raw UIA.
        """

        control = self.find_raw_control(
            window=window,
            title=title,
            control_type=control_type,
            auto_id=auto_id
        )

        if control is None:
            raise RuntimeError(
                "Raw UIA control could not be found."
            )

        wrapper = self._wrap_raw_control(control)

        try:
            wrapper.click_input()

        except Exception as click_error:

            try:
                wrapper.invoke()

            except Exception as invoke_error:

                raise RuntimeError(
                    "UIA control was found, but interaction failed. "
                    f"click_input={click_error}; "
                    f"invoke={invoke_error}"
                ) from invoke_error

        return control

    # ============================================================
    # RAW INVOKE
    # ============================================================

    def invoke_raw_control(
        self,
        window,
        title: Optional[str] = None,
        control_type: Optional[str] = None,
        auto_id: Optional[str] = None
    ):
        """
        Invoke a native Windows control.

        The control is located through raw UIA and then wrapped
        only for the actual interaction.
        """

        control = self.find_raw_control(
            window=window,
            title=title,
            control_type=control_type,
            auto_id=auto_id
        )

        if control is None:
            raise RuntimeError(
                "Raw UIA control could not be found."
            )

        wrapper = self._wrap_raw_control(control)

        try:
            wrapper.invoke()

        except Exception as invoke_error:

            try:
                wrapper.click_input()

            except Exception as click_error:

                raise RuntimeError(
                    "UIA control was found, but interaction failed. "
                    f"invoke={invoke_error}; "
                    f"click_input={click_error}"
                ) from invoke_error

        return control

    # ============================================================
    # RAW TEXT
    # ============================================================

    def get_raw_control_text(
        self,
        window,
        title: Optional[str] = None,
        control_type: Optional[str] = None,
        auto_id: Optional[str] = None
    ):

        control = self.find_raw_control(
            window=window,
            title=title,
            control_type=control_type,
            auto_id=auto_id
        )

        if control is None:
            raise RuntimeError(
                "Raw UIA control could not be found."
            )

        return control.name

    # ============================================================
    # MAIN INVOKE API
    # ============================================================

    def invoke_control(
        self,
        window,
        title=None,
        control_type=None,
        auto_id=None
    ):
        """
        Main native-control interaction API.

        If a high-level pywinauto window is supplied, its current
        UIA element is extracted.

        The control itself is ALWAYS freshly searched.
        """

        if window is None:
            raise ValueError(
                "A window must be provided."
            )

        try:
            raw_window = window.element_info

        except Exception:
            raw_window = window

        return self.invoke_raw_control(
            window=raw_window,
            title=title,
            control_type=control_type,
            auto_id=auto_id
        )

    # ============================================================
    # FRESH WINDOW + CONTROL API
    # ============================================================

    def invoke_by_window(
        self,
        window_title: str,
        control_type: Optional[str] = None,
        auto_id: Optional[str] = None,
        title: Optional[str] = None
    ):
        """
        Safest API for the agent.

        It reacquires BOTH the window and control immediately
        before the action.
        """

        window = self.find_raw_window(
            title=window_title
        )

        if window is None:
            raise RuntimeError(
                f"Window '{window_title}' could not be found."
            )

        return self.invoke_raw_control(
            window=window,
            title=title,
            control_type=control_type,
            auto_id=auto_id
        )

    def click_by_window(
        self,
        window_title: str,
        control_type: Optional[str] = None,
        auto_id: Optional[str] = None,
        title: Optional[str] = None
    ):
        """
        Safest click API.

        Reacquires the window and control immediately before
        interaction.
        """

        window = self.find_raw_window(
            title=window_title
        )

        if window is None:
            raise RuntimeError(
                f"Window '{window_title}' could not be found."
            )

        return self.click_raw_control(
            window=window,
            title=title,
            control_type=control_type,
            auto_id=auto_id
        )