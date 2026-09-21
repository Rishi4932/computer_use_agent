from intelligence.recovery_relocator import RecoveryRelocator
from intelligence.vision_reasoner import VisualElement


def test_relocate_click_finds_target_at_new_position():

    elements = [
        VisualElement(
            element_type="button",
            text="Submit",
            x=700,
            y=400,
            width=120,
            height=40,
            confidence=0.95,
            source="ocr",
        )
    ]

    original_action = {
        "action": "click",
        "x": 100,
        "y": 100,
        "target": "Submit",
        "element_type": "button",
    }

    relocator = RecoveryRelocator()

    corrected_action = relocator.relocate_click(
        elements=elements,
        original_action=original_action,
    )

    assert corrected_action is not None

    assert corrected_action["action"] == "click"

    assert corrected_action["target"] == "Submit"

    assert corrected_action["element_type"] == "button"

    # New position should be the center of the newly
    # detected element: 700 + 120/2 = 760
    #                         400 + 40/2  = 420
    assert corrected_action["x"] == 760
    assert corrected_action["y"] == 420


def test_relocate_click_returns_none_when_target_disappears():

    elements = [
        VisualElement(
            element_type="button",
            text="Cancel",
            x=700,
            y=400,
            width=120,
            height=40,
            confidence=0.95,
            source="ocr",
        )
    ]

    original_action = {
        "action": "click",
        "x": 100,
        "y": 100,
        "target": "Submit",
        "element_type": "button",
    }

    relocator = RecoveryRelocator()

    corrected_action = relocator.relocate_click(
        elements=elements,
        original_action=original_action,
    )

    assert corrected_action is None