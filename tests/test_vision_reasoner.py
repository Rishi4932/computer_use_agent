from intelligence.vision_reasoner import (
    VisualElement,
    VisualState,
    VisionReasoner,
)


def test_visual_element_to_dict():

    element = VisualElement(
        element_type="button",
        text="Submit",
        x=100,
        y=200,
        width=120,
        height=40,
        confidence=0.95,
        source="vision",
    )

    data = element.to_dict()

    assert data["element_type"] == "button"
    assert data["text"] == "Submit"
    assert data["x"] == 100
    assert data["y"] == 200
    assert data["confidence"] == 0.95


def test_visual_state_creation():

    state = VisualState(
        screenshot_path="test.png",
        screen_width=1920,
        screen_height=1080,
    )

    assert state.screen_width == 1920
    assert state.screen_height == 1080
    assert state.elements == []


def test_visual_state_add_element():

    state = VisualState()

    element = VisualElement(
        element_type="button",
        text="OK",
    )

    state.add_element(element)

    assert len(state.elements) == 1
    assert state.elements[0].text == "OK"


def test_visual_state_to_dict():

    state = VisualState(
        screen_width=1920,
        screen_height=1080,
        visible_text="Hello World",
    )

    data = state.to_dict()

    assert data["screen_width"] == 1920
    assert data["screen_height"] == 1080
    assert data["visible_text"] == "Hello World"
    assert data["elements"] == []


def test_vision_reasoner_requires_capture():

    reasoner = VisionReasoner()

    try:
        reasoner.capture_screen()
        assert False
    except RuntimeError as error:
        assert "Screenshot capture" in str(error)


def test_vision_reasoner_requires_vision():

    reasoner = VisionReasoner()

    try:
        reasoner.analyze_screenshot(
            "test.png"
        )
        assert False
    except RuntimeError as error:
        assert "Vision system" in str(error)


def test_visual_element_position():

    element = VisualElement(
        element_type="text",
        text="Download",
        x=720,
        y=650,
        width=90,
        height=30,
        confidence=0.94,
        source="ocr",
    )

    assert element.text == "Download"
    assert element.x == 720
    assert element.y == 650
    assert element.width == 90
    assert element.height == 30
    assert element.source == "ocr"


def test_visual_state_contains_elements():

    state = VisualState()

    state.add_element(
        VisualElement(
            element_type="text",
            text="Search",
            x=500,
            y=300,
            confidence=0.90,
            source="ocr",
        )
    )

    assert len(state.elements) == 1
    assert state.elements[0].text == "Search"
    assert state.elements[0].x == 500


def test_vision_reasoner_has_element_classifier():

    reasoner = VisionReasoner()

    assert reasoner.element_classifier is not None