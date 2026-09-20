from pathlib import Path

import pytest

from execution.browser_playwright import (
    PlaywrightBrowser,
)


@pytest.fixture
def browser():

    instance = PlaywrightBrowser(
        headless=True
    )

    instance.start()

    yield instance

    instance.close()


def test_browser_starts():

    browser = PlaywrightBrowser(
        headless=True
    )

    page = browser.start()

    assert page is not None
    assert browser.page is not None

    browser.close()


def test_open_url(browser):

    url = browser.open_url(
        "https://example.com"
    )

    assert url == "https://example.com/"


def test_get_title(browser):

    browser.open_url(
        "https://example.com"
    )

    title = browser.get_title()

    assert title == "Example Domain"


def test_get_url(browser):

    browser.open_url(
        "https://example.com"
    )

    url = browser.get_url()

    assert url == "https://example.com/"


def test_get_text(browser):

    browser.open_url(
        "https://example.com"
    )

    text = browser.get_text()

    assert "Example Domain" in text
    assert "documentation examples" in text


def test_element_exists(browser):

    browser.open_url(
        "https://example.com"
    )

    assert browser.element_exists(
        "h1"
    ) is True

    assert browser.element_exists(
        "body"
    ) is True


def test_get_element_text(browser):

    browser.open_url(
        "https://example.com"
    )

    heading = browser.get_element_text(
        "h1"
    )

    assert heading == "Example Domain"


def test_screenshot(browser):

    browser.open_url(
        "https://example.com"
    )

    path = browser.screenshot(
        "data/screenshots/"
        "playwright_test.png"
    )

    assert Path(path).exists()


def test_browser_state(browser):

    browser.open_url(
        "https://example.com"
    )

    state = browser.get_state()

    assert state["browser_open"] is True

    assert (
        state["current_url"]
        == "https://example.com/"
    )

    assert (
        state["page_title"]
        == "Example Domain"
    )


def test_browser_requires_start():

    browser = PlaywrightBrowser(
        headless=True
    )

    with pytest.raises(RuntimeError):

        browser.get_title()