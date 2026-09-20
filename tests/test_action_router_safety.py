from execution.action_router import ActionRouter


def test_blocked_action_never_executes():
    router = ActionRouter()

    result = router.execute({
        "action": "shutdown"
    })

    assert result.success is False
    assert result.executor == "safety"
    assert "blocked" in result.message.lower()


def test_risky_action_requires_confirmation():
    router = ActionRouter()

    result = router.execute({
        "action": "delete_file",
        "path": "test.txt"
    })

    assert result.success is False
    assert result.executor == "safety"
    assert result.data["requires_confirmation"] is True


def test_normal_action_passes_safety():
    router = ActionRouter()

    result = router.execute({
        "action": "wait",
        "seconds": 0.01
    })

    assert result.success is True
    assert result.executor == "system"