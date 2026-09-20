from intelligence.action_selector import ActionSelector
from intelligence.vision_reasoner import VisualElement


def test_find_exact_element():

    selector = ActionSelector()

    elements = [
        VisualElement(
            element_type="button",
            text="Submit",
            x=700,
            y=600,
            width=100,
            height=40,
            confidence=0.95,
            source="ocr",
        )
    ]

    result = selector.find_element(
        elements,
        "Submit",
        "button",
    )

    assert result is not None
    assert result.text == "Submit"


def test_find_element_returns_none():

    selector = ActionSelector()

    elements = [
        VisualElement(
            element_type="button",
            text="Submit",
        )
    ]

    result = selector.find_element(
        elements,
        "Download",
        "button",
    )

    assert result is None


def test_partial_text_match():

    selector = ActionSelector()

    elements = [
        VisualElement(
            element_type="button",
            text="Download PDF",
        )
    ]

    result = selector.find_element(
        elements,
        "Download",
        "button",
    )

    assert result is not None


def test_click_element():

    selector = ActionSelector()

    elements = [
        VisualElement(
            element_type="button",
            text="Submit",
            x=700,
            y=600,
            width=100,
            height=40,
            confidence=0.95,
            source="ocr",
        )
    ]

    action = selector.click_element(
        elements,
        "Submit",
        "button",
    )

    assert action is not None
    assert action["action"] == "click"
    assert action["x"] == 750
    assert action["y"] == 620
    assert action["target"] == "Submit"


def test_click_missing_element():

    selector = ActionSelector()

    elements = []

    action = selector.click_element(
        elements,
        "Submit",
        "button",
    )

    assert action is None


def test_type_into_element():

    selector = ActionSelector()

    elements = [
        VisualElement(
            element_type="text_field",
            text="Username",
            x=500,
            y=300,
            width=200,
            height=40,
            confidence=0.92,
            source="ocr",
        )
    ]

    action = selector.type_into_element(
        elements,
        "Username",
        "rishi",
    )

    assert action is not None
    assert action["action"] == "click_and_type"
    assert action["x"] == 600
    assert action["y"] == 320
    assert action["text"] == "rishi"


def test_type_requires_text_field():

    selector = ActionSelector()

    elements = [
        VisualElement(
            element_type="button",
            text="Username",
        )
    ]

    action = selector.type_into_element(
        elements,
        "Username",
        "rishi",
    )

    assert action is None


def test_exact_match_preferred():

    selector = ActionSelector()

    elements = [
        VisualElement(
            element_type="button",
            text="Download PDF",
        ),
        VisualElement(
            element_type="button",
            text="Download",
        ),
    ]

    result = selector.find_element(
        elements,
        "Download",
        "button",
    )

    assert result.text == "Download"