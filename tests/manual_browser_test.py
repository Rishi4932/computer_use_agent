import time

from execution.browser_playwright import BrowserPlaywright


def main():
    print("=" * 60)
    print(" PLAYWRIGHT BROWSER TEST")
    print("=" * 60)

    browser = BrowserPlaywright(headless=False)

    try:
        print("\n[1] Starting browser...")

        browser.start()

        print("[OK] Browser started.")

        print("\n[2] Opening example.com...")

        browser.open_url(
            "https://example.com"
        )

        print("[OK] Page opened.")

        print("\n[3] Reading page information...")

        print("Title:", browser.get_title())
        print("URL:", browser.get_url())

        print("\n[4] Reading page text...")

        text = browser.get_text("body")

        print(text[:500])

        print("\n[5] Taking screenshot...")

        browser.screenshot(
            "data/screenshots/browser_test.png"
        )

        print(
            "[OK] Screenshot saved to "
            "data/screenshots/browser_test.png"
        )

        print("\nBrowser will remain open for 5 seconds...")

        time.sleep(5)

    finally:
        print("\n[6] Closing browser...")

        browser.close()

        print("[OK] Browser closed.")

        print("\nTest completed.")


if __name__ == "__main__":
    main()