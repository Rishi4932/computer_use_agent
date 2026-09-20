import time

from execution.browser_playwright import (
    PlaywrightBrowser,
)


def main():

    print("=" * 60)
    print(" PLAYWRIGHT BROWSER AUTOMATION TEST")
    print("=" * 60)

    browser = PlaywrightBrowser(
        headless=False
    )

    try:

        print("\n[1] Starting Chromium...")

        browser.start()

        print("[OK] Browser started.")

        print("\n[2] Opening example.com...")

        url = browser.open_url(
            "https://example.com"
        )

        print(
            "[OK] Current URL:",
            url,
        )

        print("\n[3] Reading page title...")

        title = browser.get_title()

        print(
            "[OK] Page title:",
            title,
        )

        print("\n[4] Reading page text...")

        text = browser.get_text()

        print("[OK] Page text:")

        print(text)

        print("\n[5] Checking page elements...")

        print(
            "H1 exists:",
            browser.element_exists("h1"),
        )

        print(
            "Body exists:",
            browser.element_exists("body"),
        )

        print("\n[6] Reading H1...")

        heading = browser.get_element_text(
            "h1"
        )

        print(
            "[OK] H1:",
            heading,
        )

        print("\n[7] Taking screenshot...")

        screenshot_path = browser.screenshot(
            "data/screenshots/"
            "browser_playwright_test.png"
        )

        print(
            "[OK] Screenshot saved:",
            screenshot_path,
        )

        print("\n[8] Browser state...")

        state = browser.get_state()

        print(state)

        print(
            "\nBrowser will remain open "
            "for 5 seconds..."
        )

        time.sleep(5)

    finally:

        print("\n[9] Closing browser...")

        browser.close()

        print("[OK] Browser closed.")

    print("\nTest completed.")


if __name__ == "__main__":
    main()