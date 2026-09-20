import time

from perception.perception_controller import (
    PerceptionController,
)


def main():

    print("=" * 60)
    print(" COMPUTER USE AI AGENT")
    print(" REAL SCREEN PERCEPTION TEST")
    print("=" * 60)

    controller = PerceptionController()

    print()
    print("[1] Waiting 2 seconds...")
    time.sleep(2)

    print()
    print("[2] Observing computer screen...")

    state = controller.observe()

    print()
    print("[3] Observation completed.")

    print()
    print("Screenshot:")
    print(
        state.screenshot_path
    )

    print()
    print("Screen dimensions:")
    print(
        f"{state.screen_width} x "
        f"{state.screen_height}"
    )

    print()
    print("Visible windows:")

    for title in state.window_titles:
        print(
            f"  - {title}"
        )

    print()
    print("OCR text preview:")

    if state.visible_text:

        print(
            state.visible_text[:1000]
        )

    else:

        print(
            "No text detected."
        )

    print()
    print("Visual metadata:")

    for key, value in state.metadata.items():

        print(
            f"  {key}: {value}"
        )

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(
        controller.summarize(state)
    )

    print()
    print("Test completed.")


if __name__ == "__main__":
    main()