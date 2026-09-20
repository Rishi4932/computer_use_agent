from intelligence.element_classifier import (
    ElementClassifier,
)
from intelligence.vision_reasoner import (
    VisualElement,
)


def test_button_classification():

    classifier = ElementClassifier()

    element = VisualElement(
        element_type="text",
        text="Submit",
    )

    result = classifier.classify(element)

    assert result.element_type == "button"


def test_text_field_classification():

    classifier = ElementClassifier()

    element = VisualElement(
        element_type="text",
        text="Username",
    )

    result = classifier.classify(element)

    assert result.element_type == "text_field"


def test_link_classification():

    classifier = ElementClassifier()

    element = VisualElement(
        element_type="text",
        text="Learn More",
    )

    result = classifier.classify(element)

    assert result.element_type == "link"


def test_heading_classification():

    classifier = ElementClassifier()

    element = VisualElement(
        element_type="text",
        text="Dashboard",
    )

    result = classifier.classify(element)

    assert result.element_type == "heading"


def test_label_classification():

    classifier = ElementClassifier()

    element = VisualElement(
        element_type="text",
        text="Username:",
    )

    result = classifier.classify(element)

    assert result.element_type == "label"


def test_normal_text_classification():

    classifier = ElementClassifier()

    element = VisualElement(
        element_type="text",
        text="This is normal page content",
    )

    result = classifier.classify(element)

    assert result.element_type == "text"


def test_empty_text_classification():

    classifier = ElementClassifier()

    element = VisualElement(
        element_type="text",
        text="",
    )

    result = classifier.classify(element)

    assert result.element_type == "unknown"


def test_classify_all():

    classifier = ElementClassifier()

    elements = [
        VisualElement(
            element_type="text",
            text="Submit",
        ),
        VisualElement(
            element_type="text",
            text="Username",
        ),
        VisualElement(
            element_type="text",
            text="Learn More",
        ),
    ]

    result = classifier.classify_all(elements)

    assert result[0].element_type == "button"
    assert result[1].element_type == "text_field"
    assert result[2].element_type == "link"