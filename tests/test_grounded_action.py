from unittest.mock import MagicMock

from intelligence.grounded_action import GroundedActionExecutor
from intelligence.vision_reasoner import VisualElement


def create_button():

    return VisualElement(
        element_type="button",
        text="Submit",
        x=700,
        y=600,
        width=100,
        height=40,
        confidence=0.95,
        source="ocr",
    )


def create_text_field():

    return VisualElement(
        element_type="text_field",
        text="Username",
        x=500,
        y=300,
        width=200,
        height=40,
        confidence=0.92,
        source="ocr",
    )


def test_click_target_not_found():

    router = MagicMock()

    executor = GroundedActionExecutor(
        router=router,
    )

    result = executor.click_target(
        elements=[],
        target="Submit",
        element_type="button",
    )

    assert result["success"] is False
    assert result["action"] is None

    router.execute.assert_not_called()


def test_click_target():

    router = MagicMock()

    mock_result = MagicMock()
    mock_result.success = True
    mock_result.message = "Click successful"

    router.execute.return_value = mock_result

    executor = GroundedActionExecutor(
        router=router,
    )

    result = executor.click_target(
        elements=[create_button()],
        target="Submit",
        element_type="button",
    )

    assert result["success"] is True
    assert result["action"]["action"] == "click"
    assert result["action"]["x"] == 750
    assert result["action"]["y"] == 620

    router.execute.assert_called_once_with({
        "action": "click",
        "x": 750,
        "y": 620,
    })


def test_click_target_wrong_type():

    router = MagicMock()

    executor = GroundedActionExecutor(
        router=router,
    )

    result = executor.click_target(
        elements=[create_button()],
        target="Submit",
        element_type="text_field",
    )

    assert result["success"] is False

    router.execute.assert_not_called()


def test_type_target_not_found():

    router = MagicMock()

    executor = GroundedActionExecutor(
        router=router,
    )

    result = executor.type_into_target(
        elements=[],
        target="Username",
        value="rishi",
    )

    assert result["success"] is False
    assert result["action"] is None

    router.execute.assert_not_called()


def test_type_into_target():

    router = MagicMock()

    click_result = MagicMock()
    click_result.success = True
    click_result.message = "Click successful"

    type_result = MagicMock()
    type_result.success = True
    type_result.message = "Text typed"

    router.execute.side_effect = [
        click_result,
        type_result,
    ]

    executor = GroundedActionExecutor(
        router=router,
    )

    result = executor.type_into_target(
        elements=[create_text_field()],
        target="Username",
        value="rishi",
    )

    assert result["success"] is True
    assert result["action"]["action"] == "click_and_type"

    assert router.execute.call_count == 2

    calls = router.execute.call_args_list

    assert calls[0].args[0] == {
        "action": "click",
        "x": 600,
        "y": 320,
    }

    assert calls[1].args[0] == {
        "action": "type",
        "text": "rishi",
    }


def test_type_target_click_failure():

    router = MagicMock()

    click_result = MagicMock()
    click_result.success = False
    click_result.message = "Click failed"

    router.execute.return_value = click_result

    executor = GroundedActionExecutor(
        router=router,
    )

    result = executor.type_into_target(
        elements=[create_text_field()],
        target="Username",
        value="rishi",
    )

    assert result["success"] is False
    assert "focus" in result["message"].lower()

    assert router.execute.call_count == 1


def test_router_result_is_preserved():

    router = MagicMock()

    mock_result = MagicMock()
    mock_result.success = True
    mock_result.message = "Click successful"

    router.execute.return_value = mock_result

    executor = GroundedActionExecutor(
        router=router,
    )

    result = executor.click_target(
        elements=[create_button()],
        target="Submit",
        element_type="button",
    )

    assert result["router_result"] is mock_result


def test_default_selector_exists():

    router = MagicMock()

    executor = GroundedActionExecutor(
        router=router,
    )

    assert executor.selector is not None
    assert executor.router is router