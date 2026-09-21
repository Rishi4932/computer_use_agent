from core.observation import ObservationManager
from intelligence.recovery import RecoveryEngine
from intelligence.recovery_relocator import RecoveryRelocator


class FakeVerification:
    success = False
    reason = "The original click was not verified."


def test_real_adaptive_recovery_pipeline():
    """
    Real adaptive recovery experiment.

    Pipeline:

        Real Windows Screen
                ↓
           Observation
                ↓
        Detect GUI target
                ↓
        Intentionally wrong action
                ↓
          Failed verification
                ↓
          Recovery Engine
                ↓
            Re-observe
                ↓
        Relocate target
                ↓
        Corrected action

    No real click is performed.
    """

    print()
    print("=" * 70)
    print("REAL ADAPTIVE RECOVERY PIPELINE")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Observe the real Windows screen
    # ---------------------------------------------------------

    observation_manager = ObservationManager()

    observation = observation_manager.observe()

    print()
    print("STEP 1: REAL OBSERVATION")
    print("-" * 70)

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
    # 2. Find a button detected by the real perception system
    # ---------------------------------------------------------

    buttons = [
        element
        for element in observation.elements
        if element.element_type == "button"
    ]

    print(
        f"Detected buttons: "
        f"{len(buttons)}"
    )

    assert buttons, (
        "No buttons were detected. "
        "Open a simple application such as Notepad "
        "and run the test again."
    )

    target = buttons[0]

    print()
    print(
        f"Selected target: "
        f"{target.text!r}"
    )

    print(
        f"Actual target position: "
        f"({target.x}, {target.y})"
    )

    print(
        f"Target size: "
        f"{target.width}x{target.height}"
    )

    # ---------------------------------------------------------
    # 3. Create an intentionally incorrect action
    # ---------------------------------------------------------

    wrong_action = {
        "action": "click",
        "x": 0,
        "y": 0,
        "target": target.text,
        "element_type": target.element_type,
    }

    print()
    print("STEP 2: INTENTIONALLY WRONG ACTION")
    print("-" * 70)

    print(wrong_action)

    # ---------------------------------------------------------
    # 4. Simulate failed verification
    # ---------------------------------------------------------

    verification = FakeVerification()

    print()
    print("STEP 3: FAILED VERIFICATION")
    print("-" * 70)

    print(
        f"Verification success: "
        f"{verification.success}"
    )

    print(
        f"Reason: "
        f"{verification.reason}"
    )

    # ---------------------------------------------------------
    # 5. Ask RecoveryEngine what to do
    # ---------------------------------------------------------

    recovery_engine = RecoveryEngine(max_attempts=3)

    recovery = recovery_engine.decide(
        action=wrong_action,
        verification=verification,
        attempt_number=1,
    )

    print()
    print("STEP 4: RECOVERY ENGINE")
    print("-" * 70)

    print(
        f"Should retry: "
        f"{recovery.should_retry}"
    )

    print(
        f"Strategy: "
        f"{recovery.strategy}"
    )

    print(
        f"Reason: "
        f"{recovery.reason}"
    )

    assert recovery.should_retry
    assert recovery.strategy == "reobserve_and_relocate"

    # ---------------------------------------------------------
    # 6. Re-observe the real screen
    # ---------------------------------------------------------

    print()
    print("STEP 5: RE-OBSERVATION")
    print("-" * 70)

    fresh_observation = observation_manager.observe()

    print(
        f"Fresh elements detected: "
        f"{len(fresh_observation.elements)}"
    )

    # ---------------------------------------------------------
    # 7. Relocate the target
    # ---------------------------------------------------------

    relocator = RecoveryRelocator()

    corrected_action = relocator.relocate_click(
        elements=fresh_observation.elements,
        original_action=wrong_action,
    )

    print()
    print("STEP 6: TARGET RELOCATION")
    print("-" * 70)

    print(
        "Corrected action:"
    )

    print(corrected_action)

    assert corrected_action is not None

    # ---------------------------------------------------------
    # 8. Verify corrected coordinates
    # ---------------------------------------------------------

    relocated_x = (
        target.x +
        target.width // 2
    )

    relocated_y = (
        target.y +
        target.height // 2
    )

    print()
    print("STEP 7: RECOVERY VALIDATION")
    print("-" * 70)

    print(
        f"Expected recovered position: "
        f"({relocated_x}, {relocated_y})"
    )

    print(
        f"Actual recovered position: "
        f"({corrected_action['x']}, "
        f"{corrected_action['y']})"
    )

    assert corrected_action["target"] == target.text

    assert corrected_action["element_type"] == target.element_type

    assert corrected_action["x"] == relocated_x

    assert corrected_action["y"] == relocated_y

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("REAL ADAPTIVE RECOVERY PIPELINE PASSED")
    print("=" * 70)

    print()
    print("Observe")
    print("   ↓")
    print("Wrong Action")
    print("   ↓")
    print("Verification Failure")
    print("   ↓")
    print("Recovery Engine")
    print("   ↓")
    print("Re-observe")
    print("   ↓")
    print("Target Relocation")
    print("   ↓")
    print("Corrected Action")

    print()
    print(
        f"Recovered target: "
        f"{corrected_action['target']!r}"
    )

    print(
        f"Recovered coordinates: "
        f"({corrected_action['x']}, "
        f"{corrected_action['y']})"
    )

    print()
    print("=" * 70)