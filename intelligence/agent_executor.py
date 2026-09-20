from typing import Any, Dict, Optional

from intelligence.verified_executor import VerifiedActionExecutor
from intelligence.recovery import RecoveryEngine


class AgentExecutor:
    """
    Executes actions through VerifiedActionExecutor and uses RecoveryEngine
    when an action or its verification fails.

    The executor supports both:
    1. The real VerifiedActionExecutor result format containing
       'action_result' and 'verification'.
    2. The simpler mocked/test result format containing
       'success' and 'verification'.
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

            # ---------------------------------------------------------
            # Extract action execution result.
            #
            # Real executor:
            # {
            #     "action_result": ActionResult(...),
            #     "verification": VerificationResult(...)
            # }
            #
            # Tests/mocks may use:
            # {
            #     "success": True/False,
            #     "verification": ...
            # }
            # ---------------------------------------------------------

            action_result = result.get("action_result")
            verification = result.get("verification")

            if action_result is not None:
                action_succeeded = bool(
                    getattr(action_result, "success", False)
                )
            else:
                action_succeeded = bool(
                    result.get("success", False)
                )

            verification_succeeded = (
                verification is not None
                and bool(getattr(verification, "success", False))
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
                            result.get(
                                "message",
                                "Action verified successfully.",
                            ),
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
            # ACTION EXECUTION FAILED
            # ---------------------------------------------------------

            if not action_succeeded:

                failure_message = getattr(
                    action_result,
                    "message",
                    result.get(
                        "message",
                        "Action execution failed.",
                    ),
                )

                history.append(
                    {
                        "attempt": attempt,
                        "action": current_action,
                        "success": False,
                        "message": failure_message,
                    }
                )

                recovery = self.recovery_engine.decide(
                    action=current_action,
                    verification=verification,
                    attempt_number=attempt,
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
                    recovery.modified_action
                    or current_action
                )

                continue

            # ---------------------------------------------------------
            # ACTION SUCCEEDED BUT VERIFICATION FAILED
            #
            # Important:
            # Do NOT blindly repeat non-idempotent actions such as
            # typing because that could duplicate their effect.
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
                            "Action executed successfully, but "
                            "verification failed. Retry suppressed "
                            "because the action is non-idempotent."
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
                            "The action succeeded but verification "
                            "failed. The action was not repeated "
                            "because repeating a non-idempotent "
                            "action could duplicate its effect."
                        ),
                    },
                }

            # ---------------------------------------------------------
            # ACTION SUCCEEDED BUT VERIFICATION FAILED
            #
            # For idempotent actions, recovery may retry.
            # ---------------------------------------------------------

            history.append(
                {
                    "attempt": attempt,
                    "action": current_action,
                    "success": False,
                    "message": getattr(
                        verification,
                        "reason",
                        result.get(
                            "message",
                            "Verification failed.",
                        ),
                    ),
                }
            )

            recovery = self.recovery_engine.decide(
                action=current_action,
                verification=verification,
                attempt_number=attempt,
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
                recovery.modified_action
                or current_action
            )