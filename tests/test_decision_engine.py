from intelligence.decision_engine import (
    DecisionEngine,
    MockDecisionProvider,
)


def test_deterministic_decision():

    engine = DecisionEngine()

    step = {
        "step_number": 1,
        "description": "Open the browser",
        "action": "browser_start",
        "parameters": {},
        "expected_result": "A browser window is open.",
    }

    result = engine.choose_action(
        task="Open a browser",
        current_step=step,
    )

    assert result.success is True

    assert result.action == {
        "action": "browser_start"
    }

    assert (
        "browser_start"
        in result.reasoning
    )


def test_decision_with_parameters():

    engine = DecisionEngine()

    step = {
        "step_number": 2,
        "description": "Open example.com",
        "action": "browser_open_url",
        "parameters": {
            "url": "https://example.com"
        },
        "expected_result": "The webpage is loaded.",
    }

    result = engine.choose_action(
        task="Open example.com",
        current_step=step,
    )

    assert result.success is True

    assert result.action == {
        "action": "browser_open_url",
        "url": "https://example.com",
    }


def test_history_is_used_in_reasoning():

    engine = DecisionEngine()

    step = {
        "step_number": 2,
        "description": "Open example.com",
        "action": "browser_open_url",
        "parameters": {
            "url": "https://example.com"
        },
        "expected_result": "The webpage is loaded.",
    }

    history = [
        {
            "action": "browser_start",
            "success": True,
        }
    ]

    result = engine.choose_action(
        task="Open example.com",
        current_step=step,
        history=history,
    )

    assert result.success is True

    assert (
        "Previous actions recorded: 1"
        in result.reasoning
    )


def test_empty_task_is_rejected():

    engine = DecisionEngine()

    result = engine.choose_action(
        task="",
        current_step={
            "action": "wait",
            "parameters": {
                "seconds": 1
            },
        },
    )

    assert result.success is False
    assert result.action is None


def test_missing_step_is_rejected():

    engine = DecisionEngine()

    result = engine.choose_action(
        task="Test task",
        current_step={},
    )

    assert result.success is False
    assert result.action is None


def test_missing_action_is_rejected():

    engine = DecisionEngine()

    result = engine.choose_action(
        task="Test task",
        current_step={
            "description": "Do something"
        },
    )

    assert result.success is False
    assert result.action is None


def test_mock_decision_provider():

    provider = MockDecisionProvider(
        action={
            "action": "browser_start"
        },
        reasoning="The browser needs to be started.",
    )

    engine = DecisionEngine(
        provider=provider
    )

    result = engine.choose_action(
        task="Open browser",
        current_step={
            "description": "Open browser",
            "action": "browser_start",
            "parameters": {},
        },
    )

    assert result.success is True

    assert result.action == {
        "action": "browser_start"
    }

    assert (
        result.reasoning
        == "The browser needs to be started."
    )


def test_provider_receives_state_and_history():

    provider = MockDecisionProvider(
        action={
            "action": "browser_get_text",
            "selector": "body",
        }
    )

    engine = DecisionEngine(
        provider=provider
    )

    state = {
        "browser_open": True,
        "current_url": "https://example.com",
    }

    history = [
        {
            "action": "browser_start",
            "success": True,
        },
        {
            "action": "browser_open_url",
            "success": True,
        },
    ]

    result = engine.choose_action(
        task="Read example.com",
        current_step={
            "description": "Read page",
            "action": "browser_get_text",
            "parameters": {
                "selector": "body"
            },
        },
        computer_state=state,
        history=history,
    )

    assert result.success is True

    assert result.action["action"] == (
        "browser_get_text"
    )