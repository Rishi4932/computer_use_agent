from intelligence.recovery import (
    RecoveryEngine,
    RecoveryDecision,
)


class FakeVerification:
    def __init__(self, success):
        self.success = success


def test_recovery_decision_to_dict():

    decision = RecoveryDecision(
        should_retry=True,
        strategy="reobserve",
        reason="Retry required.",
        attempt_number=1,
    )

    data = decision.to_dict()

    assert data["should_retry"] is True
    assert data["strategy"] == "reobserve"
    assert data["attempt_number"] == 1


def test_successful_verification_requires_no_recovery():

    engine = RecoveryEngine()

    result = engine.decide(
        action={
            "action": "click",
            "x": 100,
            "y": 200,
        },
        verification=FakeVerification(True),
        attempt_number=1,
    )

    assert result.should_retry is False
    assert result.strategy == "none"


def test_click_failure_uses_reobserve_strategy():

    engine = RecoveryEngine()

    result = engine.decide(
        action={
            "action": "click",
            "x": 100,
            "y": 200,
        },
        verification=FakeVerification(False),
        attempt_number=1,
    )

    assert result.should_retry is True
    assert result.strategy == "reobserve_and_relocate"


def test_typing_failure_refocuses():

    engine = RecoveryEngine()

    result = engine.decide(
        action={
            "action": "type",
            "text": "Hello",
        },
        verification=FakeVerification(False),
        attempt_number=1,
    )

    assert result.should_retry is True
    assert result.strategy == "refocus_and_retry"


def test_browser_failure_reloads():

    engine = RecoveryEngine()

    result = engine.decide(
        action={
            "action": "browser_navigate",
            "url": "https://example.com",
        },
        verification=FakeVerification(False),
        attempt_number=1,
    )

    assert result.should_retry is True
    assert result.strategy == "reload_and_retry"


def test_missing_verification_reobserves():

    engine = RecoveryEngine()

    result = engine.decide(
        action={
            "action": "click",
            "x": 100,
            "y": 200,
        },
        verification=None,
        attempt_number=1,
    )

    assert result.should_retry is True
    assert result.strategy == "reobserve"


def test_max_attempts_stops():

    engine = RecoveryEngine(
        max_attempts=3
    )

    result = engine.decide(
        action={
            "action": "click",
            "x": 100,
            "y": 200,
        },
        verification=FakeVerification(False),
        attempt_number=3,
    )

    assert result.should_retry is False
    assert result.strategy == "stop"


def test_generic_action_uses_fallback():

    engine = RecoveryEngine()

    result = engine.decide(
        action={
            "action": "wait",
            "seconds": 2,
        },
        verification=FakeVerification(False),
        attempt_number=1,
    )

    assert result.should_retry is True
    assert result.strategy == "reobserve_and_retry"


def test_modified_action_is_copied():

    engine = RecoveryEngine()

    action = {
        "action": "click",
        "x": 100,
        "y": 200,
    }

    result = engine.decide(
        action=action,
        verification=FakeVerification(False),
        attempt_number=1,
    )

    assert result.modified_action == action
    assert result.modified_action is not action