from pathlib import Path
from typing import Optional

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)


class BrowserPlaywright:
    """
    Browser automation layer using Playwright.

    Provides browser operations for the
    Computer Use AI Agent.
    """

    def __init__(self, headless: bool = False):
        self.headless = headless

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    # ---------------------------------------------------------
    # Browser lifecycle
    # ---------------------------------------------------------

    def start(self):
        """Start Chromium and create a page."""

        if self.playwright is not None:
            return self.page

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless
        )

        self.context = self.browser.new_context()

        self.page = self.context.new_page()

        return self.page

    def close(self):
        """Close the browser and release resources."""

        if self.context is not None:
            self.context.close()

        if self.browser is not None:
            self.browser.close()

        if self.playwright is not None:
            self.playwright.stop()

        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None

    # ---------------------------------------------------------
    # Internal validation
    # ---------------------------------------------------------

    def _require_page(self) -> Page:
        """Ensure that a browser page exists."""

        if self.page is None:
            raise RuntimeError(
                "Browser is not started. "
                "Call start() first."
            )

        return self.page

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------

    def open_url(
        self,
        url: str,
        wait_until: str = "domcontentloaded",
    ):
        """Navigate to a URL."""

        page = self._require_page()

        page.goto(
            url,
            wait_until=wait_until,
        )

        return page.url

    # ---------------------------------------------------------
    # Page information
    # ---------------------------------------------------------

    def get_title(self) -> str:
        """Return the current webpage title."""

        page = self._require_page()

        return page.title()

    def get_url(self) -> str:
        """Return the current URL."""

        page = self._require_page()

        return page.url

    def get_text(
        self,
        selector: str = "body",
    ) -> str:
        """Read text from a webpage element."""

        page = self._require_page()

        return page.locator(selector).inner_text()

    # ---------------------------------------------------------
    # Element interaction
    # ---------------------------------------------------------

    def click(self, selector: str):
        """Click a webpage element."""

        page = self._require_page()

        page.locator(selector).click()

    def fill(
        self,
        selector: str,
        text: str,
    ):
        """Fill a webpage input field."""

        page = self._require_page()

        page.locator(selector).fill(text)

    def press(
        self,
        selector: str,
        key: str,
    ):
        """Press a keyboard key on a webpage element."""

        page = self._require_page()

        page.locator(selector).press(key)

    # ---------------------------------------------------------
    # Screenshot
    # ---------------------------------------------------------

    def screenshot(
        self,
        path: str = "data/screenshots/browser.png",
        full_page: bool = False,
    ) -> str:
        """Save a screenshot of the current webpage."""

        page = self._require_page()

        output_path = Path(path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        page.screenshot(
            path=str(output_path),
            full_page=full_page,
        )

        return str(output_path)

    # ---------------------------------------------------------
    # Waiting
    # ---------------------------------------------------------

    def wait(
        self,
        milliseconds: int = 1000,
    ):
        """Wait for the specified number of milliseconds."""

        page = self._require_page()

        page.wait_for_timeout(
            milliseconds
        )

    # ---------------------------------------------------------
    # Element inspection
    # ---------------------------------------------------------

    def element_exists(
        self,
        selector: str,
    ) -> bool:
        """Check whether an element exists."""

        page = self._require_page()

        return (
            page.locator(selector).count() > 0
        )

    def get_element_text(
        self,
        selector: str,
    ) -> str:
        """Get text from a specific element."""

        page = self._require_page()

        return page.locator(
            selector
        ).inner_text()

    # ---------------------------------------------------------
    # Browser state
    # ---------------------------------------------------------

    def get_state(self) -> dict:
        """Return basic browser state."""

        page = self._require_page()

        return {
            "browser_open": True,
            "current_url": page.url,
            "page_title": page.title(),
        }


# Backward-compatible alias.
#
# Some existing project files use PlaywrightBrowser.
# Keeping this alias means both names work.
PlaywrightBrowser = BrowserPlaywright