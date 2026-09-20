from execution.action_router import ActionRouter


def test_type_action():
    router = ActionRouter()

    result = router.execute(
        {
            "action": "type",
            "text": "Hello",
        }
    )

    assert result.success is True


def test_wait_action():
    router = ActionRouter()

    result = router.execute(
        {
            "action": "wait",
            "seconds": 0.1,
        }
    )

    assert result.success is True