import time

from execution.action_router import ActionRouter


def main():
    print("=" * 60)
    print(" BROWSER ACTION ROUTER TEST")
    print("=" * 60)

    router = ActionRouter()

    print("\n[1] Starting browser...")

    result = router.execute({
        "action": "browser_start"
    })

    print(result)

    if not result.success:
        return

    print("\n[2] Opening example.com...")

    result = router.execute({
        "action": "browser_open_url",
        "url": "https://example.com"
    })

    print(result)

    if not result.success:
        router.execute({
            "action": "browser_close"
        })
        return

    print("\n[3] Reading page text...")

    result = router.execute({
        "action": "browser_get_text",
        "selector": "body"
    })

    print(result)

    if result.success:
        print("\nPage text:")
        print(result.data["text"])

    print("\n[4] Taking browser screenshot...")

    result = router.execute({
        "action": "browser_screenshot",
        "path": "data/screenshots/router_browser_test.png"
    })

    print(result)

    print("\n[5] Browser will remain open for 5 seconds...")

    time.sleep(5)

    print("\n[6] Closing browser...")

    result = router.execute({
        "action": "browser_close"
    })

    print(result)

    print("\nTest completed.")


if __name__ == "__main__":
    main()