from typing import Any, Dict, Optional

from intelligence.verified_executor import VerifiedActionExecutor
from intelligence.recovery import RecoveryEngine


class AgentExecutor:
    """
    Executes actions with verification and controlled recovery.

    Important:
    - If an action itself failed, recovery may retry it.
    - If an action succeeded but verification failed, we do NOT blindly
      repeat non-idempotent actions such as typing.
    """

    NON_IDEMPOTENT_ACTIONS = {
        "type",
        "type_text",
        "type_into_control",
    }

    def __init__(
        self,
        verified_executor: Optional[VerifiedActionExecutor] = None,
        recovery_engine: Optional[RecoveryEngine] = None,
    ):
        self.verified_executor = (
            verified_executor or VerifiedActionExecutor()
        )
        self.recovery_engine = (
            recovery_engine or RecoveryEngine()
        )

    def execute(
        self,
        action: Dict[str, Any],
        expected: Dict[str, Any],
    ) -> Dict[str, Any]:

        attempt = 0
        history = []
        current_action = dict(action)

        while True:
            attempt += 1

            result = self.verified_executor.execute_and_verify(
                action=current_action,
                expected=expected,
            )

            if result is None:
                return {
                    "success": False,
                    "attempts": attempt,
                    "final_result": None,
                    "history": history,
                    "recovered": False,
                    "message": "Executor returned no result.",
                }

            action_result = result.get("action_result")
            verification = result.get("verification")

            action_succeeded = (
                action_result is not None
                and getattr(action_result, "success", False)
            )

            verification_succeeded = (
                verification is not None
                and getattr(verification, "success", False)
            )

            # ---------------------------------------------------------
            # SUCCESS
            # ---------------------------------------------------------
            if action_succeeded and verification_succeeded:

                history.append(
                    {
                        "attempt": attempt,
                        "action": current_action,
                        "success": True,
                        "message": getattr(
                            verification,
                            "reason",
                            "Action verified successfully.",
                        ),
                    }
                )

                return {
                    "success": True,
                    "attempts": attempt,
                    "final_result": result,
                    "history": history,
                    "recovered": attempt > 1,
                }

            # ---------------------------------------------------------
            # ACTION FAILED
            # ---------------------------------------------------------
            if not action_succeeded:

                history.append(
                    {
                        "attempt": attempt,
                        "action": current_action,
                        "success": False,
                        "message": getattr(
                            action_result,
                            "message",
                            "Action execution failed.",
                        ),
                    }
                )

                recovery = self.recovery_engine.decide(
                    action=current_action,
                    verification=verification,
                    attempt=attempt,
                )

                if not recovery.should_retry:

                    return {
                        "success": False,
                        "attempts": attempt,
                        "final_result": result,
                        "history": history,
                        "recovered": False,
                        "recovery": recovery.to_dict(),
                    }

                history[-1]["recovery"] = recovery.to_dict()

                current_action = dict(
                    recovery.modified_action or current_action
                )

                continue

            # ---------------------------------------------------------
            # ACTION SUCCEEDED BUT VERIFICATION FAILED
            # ---------------------------------------------------------
            #
            # This is the critical fix.
            #
            # Typing is non-idempotent. If pyautogui successfully typed
            # the text but OCR failed to detect it, repeating the action
            # creates duplicate text.
            #
            # Therefore STOP here instead of typing again.
            # ---------------------------------------------------------

            if (
                action_succeeded
                and not verification_succeeded
                and current_action.get("action")
                in self.NON_IDEMPOTENT_ACTIONS
            ):

                history.append(
                    {
                        "attempt": attempt,
                        "action": current_action,
                        "success": False,
                        "message": (
                            "Action executed successfully, but verification "
                            "failed. Retry suppressed because the action is "
                            "non-idempotent."
                        ),
                    }
                )

                return {
                    "success": False,
                    "attempts": attempt,
                    "final_result": result,
                    "history": history,
                    "recovered": False,
                    "recovery": {
                        "should_retry": False,
                        "strategy": "stop_after_action_success",
                        "reason": (
                            "The action succeeded but verification failed. "
                            "The action was not repeated because repeating "
                            "a non-idempotent action could duplicate its effect."
                        ),
                    },
                }

            # ---------------------------------------------------------
            # GENERIC VERIFICATION FAILURE
            # ---------------------------------------------------------

            history.append(
                {
                    "attempt": attempt,
                    "action": current_action,
                    "success": False,
                    "message": getattr(
                        verification,
                        "reason",
                        "Verification failed.",
                    ),
                }
            )

            recovery = self.recovery_engine.decide(
                action=current_action,
                verification=verification,
                attempt=attempt,
            )

            if not recovery.should_retry:

                return {
                    "success": False,
                    "attempts": attempt,
                    "final_result": result,
                    "history": history,
                    "recovered": False,
                    "recovery": recovery.to_dict(),
                }

            history[-1]["recovery"] = recovery.to_dict()

            current_action = dict(
                recovery.modified_action or current_action
            )