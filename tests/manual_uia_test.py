import time

from execution.action_router import ActionRouter


def main():

    router = ActionRouter()

    print("=" * 60)
    print(" WINDOWS UI AUTOMATION TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Open Notepad
    # ---------------------------------------------------------

    print("\n[1] Opening Notepad...")

    result = router.execute(
        {
            "action": "open_application",
            "executable": "notepad.exe",
        }
    )

    print(result)

    if not result.success:
        return

    time.sleep(2)

    # ---------------------------------------------------------
    # 2. Inspect Notepad
    # ---------------------------------------------------------

    print("\n[2] Inspecting Notepad UI...")

    result = router.execute(
        {
            "action": "inspect_window",
            "window_title": "Untitled - Notepad",
            "depth": 3,
        }
    )

    print(result)

    # ---------------------------------------------------------
    # 3. Type using UI Automation
    # ---------------------------------------------------------

    print("\n[3] Typing using Windows UI Automation...")

    result = router.execute(
        {
            "action": "type_into_control",
            "window_title": "Untitled - Notepad",
            "control_type": "Document",
            "text": "This text was entered using Windows UI Automation.",
        }
    )

    print(result)

    time.sleep(3)

    print("\nTest completed.")


if __name__ == "__main__":
    main()