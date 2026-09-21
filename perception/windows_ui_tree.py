from typing import List, Dict, Any, Optional

from pywinauto import Desktop


class WindowsUITree:
    def __init__(self):
        self.desktop = Desktop(backend="uia")

    def get_windows(self):
        return self.desktop.windows()

    def get_window_titles(self):
        windows = self.get_windows()

        titles = []

        for window in windows:
            try:
                title = window.window_text()

                if title:
                    titles.append(title)

            except Exception:
                continue

        return titles

    def inspect_window(
        self,
        title: Optional[str] = None,
        title_re: Optional[str] = None,
        depth: int = 3,
    ):
        if title:
            window = self.desktop.window(title=title)

        elif title_re:
            window = self.desktop.window(title_re=title_re)

        else:
            raise ValueError(
                "Provide title or title_re."
            )

        window.print_control_identifiers(
            depth=depth
        )

        return window

    # ---------------------------------------------------------
    # New: get a specific window
    # ---------------------------------------------------------

    def get_window(
        self,
        title: Optional[str] = None,
        title_re: Optional[str] = None,
    ):
        if title:
            return self.desktop.window(
                title=title
            )

        if title_re:
            return self.desktop.window(
                title_re=title_re
            )

        raise ValueError(
            "Provide title or title_re."
        )

    # ---------------------------------------------------------
    # New: extract UI Automation elements
    # ---------------------------------------------------------

    def get_ui_elements(
        self,
        window,
        control_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:

        if control_types is None:
            control_types = [
                "Button",
                "Edit",
                "Text",
                "Link",
                "CheckBox",
                "ComboBox",
                "List",
                "Tab",
                "MenuItem",
            ]

        elements = []

        try:
            controls = window.descendants()

        except Exception:
            return elements

        for control in controls:

            try:
                control_type = control.element_info.control_type

                if control_type not in control_types:
                    continue

                text = control.window_text().strip()

                rectangle = control.rectangle()

                width = rectangle.width()
                height = rectangle.height()

                # Ignore controls with invalid geometry.
                if width <= 0 or height <= 0:
                    continue

                element = {
                    "element_type": self._map_control_type(
                        control_type
                    ),
                    "control_type": control_type,
                    "text": text,
                    "x": rectangle.left,
                    "y": rectangle.top,
                    "width": width,
                    "height": height,
                    "confidence": 0.98,
                    "source": "uia",
                    "auto_id": getattr(
                        control.element_info,
                        "automation_id",
                        "",
                    ),
                    "control": control,
                }

                elements.append(element)

            except Exception:
                continue

        return elements

    # ---------------------------------------------------------
    # New: inspect UIA elements by window title
    # ---------------------------------------------------------

    def get_window_elements(
        self,
        title: Optional[str] = None,
        title_re: Optional[str] = None,
        control_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:

        window = self.get_window(
            title=title,
            title_re=title_re,
        )

        return self.get_ui_elements(
            window=window,
            control_types=control_types,
        )

    # ---------------------------------------------------------
    # Map Windows UIA control types to our element types
    # ---------------------------------------------------------

    @staticmethod
    def _map_control_type(
        control_type: str,
    ) -> str:

        mapping = {
            "Button": "button",
            "Edit": "text_field",
            "Text": "text",
            "Link": "link",
            "CheckBox": "checkbox",
            "ComboBox": "combobox",
            "List": "list",
            "Tab": "tab",
            "MenuItem": "menu_item",
        }

        return mapping.get(
            control_type,
            "unknown",
        )