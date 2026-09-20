from pywinauto import Desktop


class WindowsUITree:
    """
    Reads the Windows UI Automation tree.

    This allows the agent to inspect native Windows
    controls such as buttons, text boxes and menus.
    """

    def __init__(self):
        self.desktop = Desktop(
            backend="uia"
        )

    def get_windows(self):
        """
        Return visible top-level windows.
        """

        return self.desktop.windows()

    def get_window_titles(self):
        """
        Return titles of visible windows.
        """

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
        title=None,
        title_re=None,
        depth=3,
    ):
        """
        Inspect controls inside a Windows application.
        """

        if title:
            window = self.desktop.window(
                title=title
            )

        elif title_re:
            window = self.desktop.window(
                title_re=title_re
            )

        else:
            raise ValueError(
                "Provide title or title_re."
            )

        window.print_control_identifiers(
            depth=depth
        )

        return window