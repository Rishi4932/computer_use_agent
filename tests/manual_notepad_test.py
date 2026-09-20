import time

from execution.action_router import ActionRouter


def main():

    router = ActionRouter()

    print("Starting Notepad test...")
    print("Please watch your screen.")

    # Give the user a moment.
    time.sleep(2)

    # Open Notepad.
    result = router.execute(
        {
            "action": "open_application",
            "executable": "notepad.exe",
        }
    )

    print(result)

    if not result.success:
        print("Failed to open Notepad.")
        return

    # Give Notepad time to appear.
    router.execute(
        {
            "action": "wait",
            "seconds": 2,
        }
    )

    # Type text.
    result = router.execute(
        {
            "action": "type",
            "text": "Hello World! This was typed by the Computer Use AI Agent.",
        }
    )

    print(result)

    # Wait so you can see the result.
    router.execute(
        {
            "action": "wait",
            "seconds": 3,
        }
    )

    print("Test completed.")


if __name__ == "__main__":
    main()