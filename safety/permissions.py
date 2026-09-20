from typing import Any, Dict


class ActionPermissionChecker:
    """
    Validates whether an action is allowed to execute.

    This is an initial safety layer.
    The final system will have more detailed
    permission policies.
    """

    BLOCKED_ACTIONS = {
        "shutdown",
        "restart",
        "format_disk",
        "delete_system_files",
    }

    CONFIRMATION_REQUIRED = {
        "delete_file",
        "delete_folder",
        "send_email",
        "send_message",
        "install_software",
        "change_system_settings",
    }

    def validate(
        self,
        action: Dict[str, Any],
    ) -> Dict[str, Any]:

        action_type = action.get(
            "action"
        )

        if not action_type:

            return {
                "allowed": False,
                "requires_confirmation": False,
                "reason": "Action type is missing.",
            }

        if action_type in self.BLOCKED_ACTIONS:

            return {
                "allowed": False,
                "requires_confirmation": False,
                "reason": (
                    f"Action '{action_type}' "
                    "is blocked."
                ),
            }

        if action_type in self.CONFIRMATION_REQUIRED:

            return {
                "allowed": True,
                "requires_confirmation": True,
                "reason": (
                    f"Action '{action_type}' "
                    "requires user confirmation."
                ),
            }

        return {
            "allowed": True,
            "requires_confirmation": False,
            "reason": "Action allowed.",
        }