from intelligence.verifier import (
    ActionVerifier,
    VerificationResult,
)

from intelligence.vision_reasoner import VisualElement


def create_submit_button():

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


def create_success_message():

    return VisualElement(
        element_type="text",
        text="Successfully submitted",
        x=500,
        y=400,
        width=300,
        height=40,
        confidence=0.90,
        source="ocr",
    )


def test_verification_result_to_dict():

    result = VerificationResult(
        success=True,
        confidence=0.95,
        reason="Element found.",
    )

    data = result.to_dict()

    assert data["success"] is True
    assert data["confidence"] == 0.95
    assert data["reason"] == "Element found."
    assert data["matched_elements"] == []


def test_verify_element_present():

    verifier = ActionVerifier()

    elements = [
        create_submit_button()
    ]

    result = verifier.verify_element_present(
        elements,
        "Submit",
        "button",
    )

    assert result.success is True
    assert result.confidence == 0.95
    assert len(result.matched_elements) == 1


def test_verify_element_present_missing():

    verifier = ActionVerifier()

    elements = [
        create_submit_button()
    ]

    result = verifier.verify_element_present(
        elements,
        "Cancel",
        "button",
    )

    assert result.success is False
    assert result.confidence == 0.0
    assert len(result.matched_elements) == 0


def test_verify_element_wrong_type():

    verifier = ActionVerifier()

    elements = [
        create_submit_button()
    ]

    result = verifier.verify_element_present(
        elements,
        "Submit",
        "text_field",
    )

    assert result.success is False


def test_verify_element_absent():

    verifier = ActionVerifier()

    elements = []

    result = verifier.verify_element_absent(
        elements,
        "Submit",
        "button",
    )

    assert result.success is True
    assert result.confidence == 1.0


def test_verify_element_not_absent():

    verifier = ActionVerifier()

    elements = [
        create_submit_button()
    ]

    result = verifier.verify_element_absent(
        elements,
        "Submit",
        "button",
    )

    assert result.success is False
    assert len(result.matched_elements) == 1


def test_verify_text_contains():

    verifier = ActionVerifier()

    elements = [
        create_success_message()
    ]

    result = verifier.verify_text_contains(
        elements,
        "submitted",
    )

    assert result.success is True
    assert result.confidence == 0.90
    assert len(result.matched_elements) == 1


def test_verify_text_missing():

    verifier = ActionVerifier()

    elements = [
        create_success_message()
    ]

    result = verifier.verify_text_contains(
        elements,
        "failed",
    )

    assert result.success is False
    assert result.confidence == 0.0