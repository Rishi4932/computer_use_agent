from perception.perception_controller import (
    PerceptionController,
)


def test_perception_controller_creation():

    controller = PerceptionController()

    assert controller.screenshot_capture is not None
    assert controller.ocr_reader is not None
    assert controller.vision_system is not None
    assert controller.ui_tree is not None
    assert controller.reasoner is not None


def test_initial_state_is_none():

    controller = PerceptionController()

    assert controller.get_last_state() is None


def test_summarize_without_state():

    controller = PerceptionController()

    result = controller.summarize()

    assert result == (
        "No visual observation available."
    )