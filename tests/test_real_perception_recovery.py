from core.observation import ObservationManager
from intelligence.recovery_relocator import RecoveryRelocator


def test_real_perception_can_relocate_target():
    """
    Uses the real Windows perception pipeline:

        Screenshot
            ↓
        OCR
            ↓
        VisualState
            ↓
        VisualElement[]
            ↓
        RecoveryRelocator

    No real click is performed.
    """

    observation_manager = ObservationManager()

    print()
    print("=" * 60)
    print("REAL PERCEPTION RECOVERY TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # Capture the actual Windows screen
    # ---------------------------------------------------------

    observation = observation_manager.observe()

    print(
        f"Screen: "
        f"{observation.screen_width}x"
        f"{observation.screen_height}"
    )

    print(
        f"Detected elements: "
        f"{len(observation.elements)}"
    )

    # ---------------------------------------------------------
    # Display detected button-like elements
    # ---------------------------------------------------------

    buttons = [
        element
        for element in observation.elements
        if element.element_type == "button"
    ]

    print(
        f"Detected buttons: {len(buttons)}"
    )

    for button in buttons[:20]:
        print(
            f"  {button.text!r} "
            f"at ({button.x}, {button.y}) "
            f"size={button.width}x{button.height}"
        )

    # ---------------------------------------------------------
    # We need at least one real detected button
    # ---------------------------------------------------------

    assert buttons, (
        "No buttons were detected on the current "
        "Windows screen. Open a simple application "
        "such as Notepad before running this test."
    )

    target = buttons[0]

    print()
    print(
        f"Selected target: {target.text!r}"
    )

    # ---------------------------------------------------------
    # Create an intentionally incorrect action.
    #
    # IMPORTANT:
    # We DO NOT execute this action.
    # It is only used to test relocation.
    # ---------------------------------------------------------

    original_action = {
        "action": "click",
        "x": 0,
        "y": 0,
        "target": target.text,
        "element_type": target.element_type,
    }

    # ---------------------------------------------------------
    # Perform semantic relocation using the REAL
    # detected elements.
    # ---------------------------------------------------------

    relocator = RecoveryRelocator()

    corrected_action = (
        relocator.relocate_click(
            elements=observation.elements,
            original_action=original_action,
        )
    )

    assert corrected_action is not None

    print()
    print(
        "Recovered action:"
    )

    print(
        corrected_action
    )

    # ---------------------------------------------------------
    # Validate that relocation points to the detected
    # element's center.
    # ---------------------------------------------------------

    expected_x = (
        target.x
        + target.width // 2
    )

    expected_y = (
        target.y
        + target.height // 2
    )

    assert (
        corrected_action["x"]
        == expected_x
    )

    assert (
        corrected_action["y"]
        == expected_y
    )

    assert (
        corrected_action["target"]
        == target.text
    )

    assert (
        corrected_action["element_type"]
        == target.element_type
    )

    print()
    print("=" * 60)
    print("REAL PERCEPTION RECOVERY PASSED")
    print("=" * 60)
    print(
        f"Target: {target.text!r}"
    )
    print(
        f"Recovered coordinates: "
        f"({corrected_action['x']}, "
        f"{corrected_action['y']})"
    )
    print("=" * 60)