from intelligence.planner import (
    MockPlannerProvider,
    Planner,
)


def test_deterministic_plan():

    planner = Planner()

    understood_steps = [
        {
            "description": "Open the browser",
            "action": "browser_start",
            "parameters": {},
        },
        {
            "description": "Open example.com",
            "action": "browser_open_url",
            "parameters": {
                "url": "https://example.com",
            },
        },
        {
            "description": "Read the page",
            "action": "browser_get_text",
            "parameters": {
                "selector": "body",
            },
        },
    ]

    result = planner.create_plan(
        "Open example.com and read the page",
        understood_steps,
    )

    assert result.success is True
    assert len(result.steps) == 3

    assert result.steps[0]["step_number"] == 1
    assert result.steps[1]["step_number"] == 2
    assert result.steps[2]["step_number"] == 3

    assert (
        result.steps[0]["action"]
        == "browser_start"
    )

    assert (
        result.steps[1]["action"]
        == "browser_open_url"
    )

    assert (
        result.steps[2]["action"]
        == "browser_get_text"
    )


def test_expected_results_are_created():

    planner = Planner()

    understood_steps = [
        {
            "description": "Start browser",
            "action": "browser_start",
            "parameters": {},
        }
    ]

    result = planner.create_plan(
        "Start browser",
        understood_steps,
    )

    assert result.success is True

    assert (
        result.steps[0]["expected_result"]
        == "A browser window is open."
    )


def test_unsupported_action_is_rejected():

    planner = Planner()

    understood_steps = [
        {
            "description": "Do something unknown",
            "action": "magic_action",
            "parameters": {},
        }
    ]

    result = planner.create_plan(
        "Do something",
        understood_steps,
    )

    assert result.success is False
    assert "Unsupported action" in result.message


def test_empty_task_is_rejected():

    planner = Planner()

    result = planner.create_plan(
        "",
        [],
    )

    assert result.success is False


def test_empty_steps_are_rejected():

    planner = Planner()

    result = planner.create_plan(
        "Open browser",
        [],
    )

    assert result.success is False


def test_mock_planner_provider():

    response = """
    {
        "goal": "Open example.com",
        "steps": [
            {
                "step_number": 1,
                "description": "Start browser",
                "action": "browser_start",
                "parameters": {},
                "expected_result": "Browser is open."
            },
            {
                "step_number": 2,
                "description": "Open example.com",
                "action": "browser_open_url",
                "parameters": {
                    "url": "https://example.com"
                },
                "expected_result": "Example website is loaded."
            }
        ]
    }
    """

    provider = MockPlannerProvider(response)

    planner = Planner(
        provider=provider
    )

    result = planner.create_plan(
        "Open example.com",
        [
            {
                "description": "Open example",
                "action": "browser_open_url",
                "parameters": {
                    "url": "https://example.com"
                },
            }
        ],
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


def test_invalid_mock_response():

    provider = MockPlannerProvider(
        "This is not valid JSON"
    )

    planner = Planner(
        provider=provider
    )

    result = planner.create_plan(
        "Test task",
        [
            {
                "description": "Test",
                "action": "wait",
                "parameters": {
                    "seconds": 1
                },
            }
        ],
    )

    assert result.success is False