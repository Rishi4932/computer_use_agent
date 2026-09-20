from intelligence.task_understanding import (
    MockLLMProvider,
    TaskUnderstanding,
)


def test_empty_instruction():

    understanding = TaskUnderstanding()

    result = understanding.understand("")

    assert result.success is False
    assert result.steps == []


def test_rule_based_browser_task():

    understanding = TaskUnderstanding()

    result = understanding.understand(
        "Open Chrome and visit https://example.com"
    )

    assert result.success is True

    assert len(result.steps) == 2

    assert (
        result.steps[0]["action"]
        == "browser_start"
    )

    assert (
        result.steps[1]["action"]
        == "browser_open_url"
    )

    assert (
        result.steps[1]["parameters"]["url"]
        == "https://example.com"
    )


def test_rule_based_page_reading():

    understanding = TaskUnderstanding()

    result = understanding.understand(
        "Open Chrome, visit https://example.com "
        "and read the page"
    )

    assert result.success is True

    actions = [
        step["action"]
        for step in result.steps
    ]

    assert "browser_start" in actions
    assert "browser_open_url" in actions
    assert "browser_get_text" in actions


def test_mock_llm_provider():

    response = """
    {
        "task_description": "Open example website",
        "steps": [
            {
                "description": "Start browser",
                "action": "browser_start",
                "parameters": {}
            },
            {
                "description": "Open example website",
                "action": "browser_open_url",
                "parameters": {
                    "url": "https://example.com"
                }
            }
        ]
    }
    """

    provider = MockLLMProvider(response)

    understanding = TaskUnderstanding(
        provider=provider
    )

    result = understanding.understand(
        "Open example.com"
    )

    assert result.success is True

    assert len(result.steps) == 2

    assert (
        result.steps[1]["parameters"]["url"]
        == "https://example.com"
    )


def test_invalid_llm_response():

    provider = MockLLMProvider(
        "This is not JSON"
    )

    understanding = TaskUnderstanding(
        provider=provider
    )

    result = understanding.understand(
        "Do something"
    )

    assert result.success is False


def test_markdown_json_response():

    response = """
    ```json
    {
        "task_description": "Open example",
        "steps": [
            {
                "description": "Start browser",
                "action": "browser_start",
                "parameters": {}
            }
        ]
    }
    ```
    """

    provider = MockLLMProvider(response)

    understanding = TaskUnderstanding(
        provider=provider
    )

    result = understanding.understand(
        "Open example"
    )

    assert result.success is True
    assert len(result.steps) == 1