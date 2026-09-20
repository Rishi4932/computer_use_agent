from typing import Optional
from pywinauto import Desktop
from pywinauto.application import Application


class WindowsUIAutomation:

    def __init__(self):
        self.application: Optional[Application] = None

    def open_application(self, executable: str):
        """
        Start an application and bring its main window
        to the foreground so subsequent keyboard/mouse
        actions are directed to the newly opened application.
        """

        self.application = Application(
            backend="uia"
        ).start(executable)

        try:
            window = self.application.top_window()

            window.wait(
                "visible",
                timeout=10
            )

            try:
                window.restore()
            except Exception:
                pass

            try:
                window.set_focus()
            except Exception:
                pass

        except Exception:
            # The application was successfully started even
            # if its main window could not be focused here.
            pass

        return self.application

    def connect(
        self,
        title: Optional[str] = None,
        process: Optional[int] = None
    ):
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

    def find_window(
        self,
        title: Optional[str] = None,
        title_re: Optional[str] = None
    ):
        desktop = self.desktop()

        if title:
            return desktop.window(title=title)

        if title_re:
            return desktop.window(title_re=title_re)

        raise ValueError(
            "Provide title or title_re."
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
                "At least one control identifier "
                "must be provided."
            )

        return window.child_window(
            **criteria
        )

    def click_control(
        self,
        window,
        title=None,
        control_type=None,
        auto_id=None
    ):
        control = self.find_control(
            window,
            title,
            control_type,
            auto_id
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
            window,
            title,
            control_type,
            auto_id
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
            window,
            title,
            control_type,
            auto_id
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