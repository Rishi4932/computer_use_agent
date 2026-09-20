from unittest.mock import MagicMock

from intelligence.agent_executor import AgentExecutor


def create_executor():

    verified_executor = MagicMock()
    recovery_engine = MagicMock()

    executor = AgentExecutor(
        verified_executor=verified_executor,
        recovery_engine=recovery_engine,
    )

    return (
        executor,
        verified_executor,
        recovery_engine,
    )


def test_successful_execution():

    executor, verified, recovery = (
        create_executor()
    )

    verified.execute_and_verify.return_value = {
        "success": True,
        "message": "Verified.",
        "verification": MagicMock(
            success=True
        ),
    }

    result = executor.execute(
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

    assert result["success"] is True
    assert result["attempts"] == 1
    assert result["recovered"] is False

    recovery.decide.assert_not_called()


def test_failed_action_triggers_recovery():

    executor, verified, recovery = (
        create_executor()
    )

    verified.execute_and_verify.side_effect = [
        {
            "success": False,
            "message": "Verification failed.",
            "verification": MagicMock(
                success=False
            ),
        },
        {
            "success": True,
            "message": "Verified after retry.",
            "verification": MagicMock(
                success=True
            ),
        },
    ]

    recovery_decision = MagicMock()

    recovery_decision.should_retry = True

    recovery_decision.modified_action = {
        "action": "click",
        "x": 300,
        "y": 400,
    }

    recovery_decision.to_dict.return_value = {
        "should_retry": True,
        "strategy": "reobserve_and_relocate",
    }

    recovery.decide.return_value = (
        recovery_decision
    )

    result = executor.execute(
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

    assert result["success"] is True
    assert result["attempts"] == 2
    assert result["recovered"] is True

    assert (
        verified.execute_and_verify.call_count
        == 2
    )

    recovery.decide.assert_called_once()


def test_recovery_can_fail():

    executor, verified, recovery = (
        create_executor()
    )

    verified.execute_and_verify.return_value = {
        "success": False,
        "message": "Verification failed.",
        "verification": MagicMock(
            success=False
        ),
    }

    recovery_decision = MagicMock()

    recovery_decision.should_retry = False
    recovery_decision.modified_action = None

    recovery_decision.to_dict.return_value = {
        "should_retry": False,
        "strategy": "stop",
    }

    recovery.decide.return_value = (
        recovery_decision
    )

    result = executor.execute(
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

    assert result["success"] is False
    assert result["attempts"] == 1
    assert result["recovered"] is False

    recovery.decide.assert_called_once()


def test_action_history_is_recorded():

    executor, verified, recovery = (
        create_executor()
    )

    verified.execute_and_verify.side_effect = [
        {
            "success": False,
            "message": "Failed.",
            "verification": MagicMock(
                success=False
            ),
        },
        {
            "success": True,
            "message": "Success.",
            "verification": MagicMock(
                success=True
            ),
        },
    ]

    recovery_decision = MagicMock()

    recovery_decision.should_retry = True

    recovery_decision.modified_action = {
        "action": "click",
        "x": 300,
        "y": 400,
    }

    recovery_decision.to_dict.return_value = {
        "should_retry": True,
        "strategy": "reobserve_and_relocate",
    }

    recovery.decide.return_value = (
        recovery_decision
    )

    result = executor.execute(
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

    assert len(result["history"]) == 2

    assert result["history"][0]["success"] is False
    assert result["history"][1]["success"] is True


def test_modified_action_is_used_on_retry():

    executor, verified, recovery = (
        create_executor()
    )

    verified.execute_and_verify.side_effect = [
        {
            "success": False,
            "message": "Failed.",
            "verification": MagicMock(
                success=False
            ),
        },
        {
            "success": True,
            "message": "Success.",
            "verification": MagicMock(
                success=True
            ),
        },
    ]

    recovery_decision = MagicMock()

    recovery_decision.should_retry = True

    recovery_decision.modified_action = {
        "action": "click",
        "x": 500,
        "y": 600,
    }

    recovery_decision.to_dict.return_value = {
        "should_retry": True,
        "strategy": "reobserve_and_relocate",
    }

    recovery.decide.return_value = (
        recovery_decision
    )

    executor.execute(
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

    calls = (
        verified.execute_and_verify.call_args_list
    )

    assert calls[0].kwargs["action"] == {
        "action": "click",
        "x": 100,
        "y": 200,
    }

    assert calls[1].kwargs["action"] == {
        "action": "click",
        "x": 500,
        "y": 600,
    }