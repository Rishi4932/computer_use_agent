from safety.permissions import ActionPermissionChecker


def test_normal_action_allowed():

    checker = ActionPermissionChecker()

    result = checker.validate(
        {
            "action": "click"
        }
    )

    assert result["allowed"] is True
    assert result["requires_confirmation"] is False


def test_dangerous_action_blocked():

    checker = ActionPermissionChecker()

    result = checker.validate(
        {
            "action": "shutdown"
        }
    )

    assert result["allowed"] is False


def test_risky_action_requires_confirmation():

    checker = ActionPermissionChecker()

    result = checker.validate(
        {
            "action": "delete_file"
        }
    )

    assert result["allowed"] is True
    assert result["requires_confirmation"] is True