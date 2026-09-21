from typing import Any, Dict, Optional

from intelligence.verified_executor import VerifiedActionExecutor
from intelligence.recovery import RecoveryEngine
from intelligence.recovery_relocator import RecoveryRelocator
from core.observation import ObservationManager


class AgentExecutor:
    """
    Executes actions through VerifiedActionExecutor and performs
    adaptive recovery when verification fails.

    Recovery flow:

        Execute
           ↓
        Verify
           ↓
        RecoveryEngine
           ↓
        Re-observe
           ↓
        Re-locate target
           ↓
        Corrected action
           ↓
        Execute again
           ↓
        Verify
    """

    NON_IDEMPOTENT_ACTIONS = {
        "type",
        "type_text",
        "type_into_control",
    }

    def __init__(
        self,
        verified_executor: Optional[
            VerifiedActionExecutor
        ] = None,
        recovery_engine: Optional[
            RecoveryEngine
        ] = None,
        observation_manager: Optional[
            ObservationManager
        ] = None,
        recovery_relocator: Optional[
            RecoveryRelocator
        ] = None,
    ):
        self.verified_executor = (
            verified_executor
            or VerifiedActionExecutor()
        )

        self.recovery_engine = (
            recovery_engine
            or RecoveryEngine()
        )

        self.observation_manager = (
            observation_manager
            or ObservationManager()
        )

        self.recovery_relocator = (
            recovery_relocator
            or RecoveryRelocator()
        )

    def _get_observation_elements(
        self,
        observation: Any,
    ):
        """
        Extract visual elements from a VisualState
        or dictionary observation.
        """

        if observation is None:
            return []

        if hasattr(observation, "elements"):
            return observation.elements

        if isinstance(observation, dict):
            return observation.get(
                "elements",
                [],
            )

        return []

    def _perform_relocation(
        self,
        action: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Capture a fresh observation and relocate the
        semantic target.

        Returns:
            Corrected action if target is found.
            None otherwise.
        """

        try:
            observation = (
                self.observation_manager.observe()
            )

            elements = (
                self._get_observation_elements(
                    observation
                )
            )

            if not elements:
                return None

            return (
                self.recovery_relocator.relocate_click(
                    elements=elements,
                    original_action=action,
                )
            )

        except Exception:
            return None

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

            result = (
                self.verified_executor
                .execute_and_verify(
                    action=current_action,
                    expected=expected,
                )
            )

            if result is None:

                return {
                    "success": False,
                    "attempts": attempt,
                    "final_result": None,
                    "history": history,
                    "recovered": False,
                    "message": (
                        "Executor returned no result."
                    ),
                }

            action_result = result.get(
                "action_result"
            )

            verification = result.get(
                "verification"
            )

            # -------------------------------------------------
            # Determine action success
            # -------------------------------------------------

            if action_result is not None:

                action_succeeded = bool(
                    getattr(
                        action_result,
                        "success",
                        False,
                    )
                )

            else:

                action_succeeded = bool(
                    result.get(
                        "success",
                        False,
                    )
                )

            verification_succeeded = (
                verification is not None
                and bool(
                    getattr(
                        verification,
                        "success",
                        False,
                    )
                )
            )

            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            if (
                action_succeeded
                and verification_succeeded
            ):

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

            # -------------------------------------------------
            # ACTION EXECUTION FAILED
            # -------------------------------------------------

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

                recovery = (
                    self.recovery_engine.decide(
                        action=current_action,
                        verification=verification,
                        attempt_number=attempt,
                    )
                )

                if not recovery.should_retry:

                    return {
                        "success": False,
                        "attempts": attempt,
                        "final_result": result,
                        "history": history,
                        "recovered": False,
                        "recovery": (
                            recovery.to_dict()
                        ),
                    }

                # ---------------------------------------------
                # Adaptive click relocation
                # ---------------------------------------------

                if (
                    recovery.strategy
                    == "reobserve_and_relocate"
                ):

                    corrected_action = (
                        self._perform_relocation(
                            current_action
                        )
                    )

                    if corrected_action is None:

                        history[-1][
                            "recovery"
                        ] = {
                            "strategy": (
                                "reobserve_and_relocate"
                            ),
                            "success": False,
                            "reason": (
                                "Target could not be "
                                "relocated after "
                                "re-observation."
                            ),
                        }

                        return {
                            "success": False,
                            "attempts": attempt,
                            "final_result": result,
                            "history": history,
                            "recovered": False,
                            "recovery": {
                                "should_retry": False,
                                "strategy": (
                                    "relocation_failed"
                                ),
                                "reason": (
                                    "The target could "
                                    "not be located "
                                    "after re-observation."
                                ),
                            },
                        }

                    history[-1][
                        "recovery"
                    ] = {
                        "strategy": (
                            "reobserve_and_relocate"
                        ),
                        "success": True,
                        "old_action": current_action,
                        "new_action": corrected_action,
                    }

                    current_action = (
                        corrected_action
                    )

                    continue

                history[-1][
                    "recovery"
                ] = recovery.to_dict()

                current_action = dict(
                    recovery.modified_action
                    or current_action
                )

                continue

            # -------------------------------------------------
            # ACTION SUCCEEDED BUT VERIFICATION FAILED
            # -------------------------------------------------

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
                            "Action executed successfully, "
                            "but verification failed. "
                            "Retry suppressed because "
                            "the action is non-idempotent."
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
                        "strategy": (
                            "stop_after_action_success"
                        ),
                        "reason": (
                            "The action succeeded but "
                            "verification failed. The "
                            "action was not repeated "
                            "because repeating a "
                            "non-idempotent action "
                            "could duplicate its effect."
                        ),
                    },
                }

            # -------------------------------------------------
            # VERIFICATION FAILED
            # -------------------------------------------------

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

            recovery = (
                self.recovery_engine.decide(
                    action=current_action,
                    verification=verification,
                    attempt_number=attempt,
                )
            )

            if not recovery.should_retry:

                return {
                    "success": False,
                    "attempts": attempt,
                    "final_result": result,
                    "history": history,
                    "recovered": False,
                    "recovery": (
                        recovery.to_dict()
                    ),
                }

            # -------------------------------------------------
            # Adaptive click relocation
            # -------------------------------------------------

            if (
                recovery.strategy
                == "reobserve_and_relocate"
            ):

                corrected_action = (
                    self._perform_relocation(
                        current_action
                    )
                )

                if corrected_action is None:

                    history[-1][
                        "recovery"
                    ] = {
                        "strategy": (
                            "reobserve_and_relocate"
                        ),
                        "success": False,
                        "reason": (
                            "Target could not be "
                            "relocated after "
                            "re-observation."
                        ),
                    }

                    return {
                        "success": False,
                        "attempts": attempt,
                        "final_result": result,
                        "history": history,
                        "recovered": False,
                        "recovery": {
                            "should_retry": False,
                            "strategy": (
                                "relocation_failed"
                            ),
                            "reason": (
                                "The target could "
                                "not be located "
                                "after re-observation."
                            ),
                        },
                    }

                history[-1][
                    "recovery"
                ] = {
                    "strategy": (
                        "reobserve_and_relocate"
                    ),
                    "success": True,
                    "old_action": current_action,
                    "new_action": corrected_action,
                }

                current_action = (
                    corrected_action
                )

                continue

            history[-1][
                "recovery"
            ] = recovery.to_dict()

            current_action = dict(
                recovery.modified_action
                or current_action
            )