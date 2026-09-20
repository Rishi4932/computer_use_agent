from unittest.mock import MagicMock

from intelligence.verified_executor import (
    VerifiedActionExecutor,
)


def create_executor():

    router = MagicMock()
    screenshot_capture = MagicMock()
    vision_reasoner = MagicMock()
    verifier = MagicMock()

    return (
        VerifiedActionExecutor(
            router=router,
            screenshot_capture=screenshot_capture,
            vision_reasoner=vision_reasoner,
            verifier=verifier,
        ),
        router,
        screenshot_capture,
        vision_reasoner,
        verifier,
    )


def test_action_execution_failure():

    executor, router, _, _, _ = create_executor()

    result = MagicMock()
    result.success = False

    router.execute.return_value = result

    output = executor.execute_and_verify(
        action={
            "action": "click",
            "x": 100,
            "y": 200,
        },
        expected={
            "type": "present",
            "text": "Success",
        },
    )

    assert output["success"] is False
    assert output["verification"] is None


def test_present_verification():

    executor, router, capture, vision, verifier = (
        create_executor()
    )

    action_result = MagicMock()
    action_result.success = True

    router.execute.return_value = action_result

    capture.capture.return_value = (
        "data/screenshots/test.png"
    )

    visual_state = MagicMock()
    visual_state.elements = []

    vision.analyze_screenshot.return_value = (
        visual_state
    )

    verification = MagicMock()
    verification.success = True
    verification.reason = "Element found."

    verifier.verify_element_present.return_value = (
        verification
    )

    output = executor.execute_and_verify(
        action={
            "action": "click",
            "x": 100,
            "y": 200,
        },
        expected={
            "type": "present",
            "text": "Success",
            "element_type": "text",
        },
    )

    assert output["success"] is True

    verifier.verify_element_present.assert_called_once()


def test_absent_verification():

    executor, router, capture, vision, verifier = (
        create_executor()
    )

    action_result = MagicMock()
    action_result.success = True

    router.execute.return_value = action_result

    capture.capture.return_value = (
        "data/screenshots/test.png"
    )

    visual_state = MagicMock()
    visual_state.elements = []

    vision.analyze_screenshot.return_value = (
        visual_state
    )

    verification = MagicMock()
    verification.success = True
    verification.reason = "Element absent."

    verifier.verify_element_absent.return_value = (
        verification
    )

    output = executor.execute_and_verify(
        action={
            "action": "click",
            "x": 100,
            "y": 200,
        },
        expected={
            "type": "absent",
            "text": "Submit",
            "element_type": "button",
        },
    )

    assert output["success"] is True

    verifier.verify_element_absent.assert_called_once()


def test_text_contains_verification():

    executor, router, capture, vision, verifier = (
        create_executor()
    )

    action_result = MagicMock()
    action_result.success = True

    router.execute.return_value = action_result

    capture.capture.return_value = (
        "data/screenshots/test.png"
    )

    visual_state = MagicMock()
    visual_state.elements = []

    vision.analyze_screenshot.return_value = (
        visual_state
    )

    verification = MagicMock()
    verification.success = True
    verification.reason = "Text found."

    verifier.verify_text_contains.return_value = (
        verification
    )

    output = executor.execute_and_verify(
        action={
            "action": "click",
            "x": 100,
            "y": 200,
        },
        expected={
            "type": "text_contains",
            "text": "Success",
        },
    )

    assert output["success"] is True

    verifier.verify_text_contains.assert_called_once()


def test_verification_failure():

    executor, router, capture, vision, verifier = (
        create_executor()
    )

    action_result = MagicMock()
    action_result.success = True

    router.execute.return_value = action_result

    capture.capture.return_value = (
        "data/screenshots/test.png"
    )

    visual_state = MagicMock()
    visual_state.elements = []

    vision.analyze_screenshot.return_value = (
        visual_state
    )

    verification = MagicMock()
    verification.success = False
    verification.reason = "Expected text not found."

    verifier.verify_text_contains.return_value = (
        verification
    )

    output = executor.execute_and_verify(
        action={
            "action": "click",
            "x": 100,
            "y": 200,
        },
        expected={
            "type": "text_contains",
            "text": "Success",
        },
    )

    assert output["success"] is False


def test_unknown_verification_type():

    executor, router, capture, vision, _ = (
        create_executor()
    )

    action_result = MagicMock()
    action_result.success = True

    router.execute.return_value = action_result

    capture.capture.return_value = (
        "data/screenshots/test.png"
    )

    visual_state = MagicMock()
    visual_state.elements = []

    vision.analyze_screenshot.return_value = (
        visual_state
    )

    output = executor.execute_and_verify(
        action={
            "action": "click",
            "x": 100,
            "y": 200,
        },
        expected={
            "type": "invalid_type",
            "text": "Success",
        },
    )

    assert output["success"] is False
    assert output["verification"] is None


def test_screenshot_is_captured():

    executor, router, capture, vision, verifier = (
        create_executor()
    )

    action_result = MagicMock()
    action_result.success = True

    router.execute.return_value = action_result

    capture.capture.return_value = (
        "test.png"
    )

    visual_state = MagicMock()
    visual_state.elements = []

    vision.analyze_screenshot.return_value = (
        visual_state
    )

    verification = MagicMock()
    verification.success = True
    verification.reason = "Found."

    verifier.verify_text_contains.return_value = (
        verification
    )

    executor.execute_and_verify(
        action={
            "action": "click",
            "x": 100,
            "y": 200,
        },
        expected={
            "type": "text_contains",
            "text": "Success",
        },
    )

    capture.capture.assert_called_once()


def test_new_screen_is_analyzed():

    executor, router, capture, vision, verifier = (
        create_executor()
    )

    action_result = MagicMock()
    action_result.success = True

    router.execute.return_value = action_result

    capture.capture.return_value = (
        "test.png"
    )

    visual_state = MagicMock()
    visual_state.elements = []

    vision.analyze_screenshot.return_value = (
        visual_state
    )

    verification = MagicMock()
    verification.success = True
    verification.reason = "Found."

    verifier.verify_text_contains.return_value = (
        verification
    )

    executor.execute_and_verify(
        action={
            "action": "click",
            "x": 100,
            "y": 200,
        },
        expected={
            "type": "text_contains",
            "text": "Success",
        },
    )

    vision.analyze_screenshot.assert_called_once_with(
        "test.png"
    )