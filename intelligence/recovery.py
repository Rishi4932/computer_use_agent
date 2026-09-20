from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RecoveryDecision:
    should_retry: bool
    strategy: str
    reason: str
    modified_action: Optional[Dict[str, Any]] = None
    attempt_number: int = 0
    details: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self):
        return {
            "should_retry": self.should_retry,
            "strategy": self.strategy,
            "reason": self.reason,
            "modified_action": self.modified_action,
            "attempt_number": self.attempt_number,
            "details": self.details,
        }


class RecoveryEngine:
    """
    Determines how the agent should recover after
    an action fails verification.

    Recovery strategies are intentionally deterministic
    at this stage. AI-based recovery reasoning can be
    added later.
    """

    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def decide(
        self,
        action: Dict[str, Any],
        verification: Any,
        attempt_number: int,
    ) -> RecoveryDecision:

        # ---------------------------------------------
        # Maximum retry limit
        # ---------------------------------------------

        if attempt_number >= self.max_attempts:

            return RecoveryDecision(
                should_retry=False,
                strategy="stop",
                reason=(
                    "Maximum recovery attempts "
                    "have been reached."
                ),
                modified_action=None,
                attempt_number=attempt_number,
                details={
                    "max_attempts": self.max_attempts
                },
            )

        # ---------------------------------------------
        # Missing verification
        # ---------------------------------------------

        if verification is None:

            return RecoveryDecision(
                should_retry=True,
                strategy="reobserve",
                reason=(
                    "Verification information is "
                    "missing. Re-observe the screen "
                    "before retrying."
                ),
                modified_action=action.copy(),
                attempt_number=attempt_number,
            )

        # ---------------------------------------------
        # Verification succeeded
        # ---------------------------------------------

        if getattr(verification, "success", False):

            return RecoveryDecision(
                should_retry=False,
                strategy="none",
                reason=(
                    "Verification succeeded. "
                    "No recovery is required."
                ),
                modified_action=None,
                attempt_number=attempt_number,
            )

        action_type = action.get("action")

        # ---------------------------------------------
        # Click recovery
        # ---------------------------------------------

        if action_type in {
            "click",
            "double_click",
            "right_click",
        }:

            return RecoveryDecision(
                should_retry=True,
                strategy="reobserve_and_relocate",
                reason=(
                    "The click action was not verified. "
                    "Re-observe the screen and locate "
                    "the target again."
                ),
                modified_action=action.copy(),
                attempt_number=attempt_number,
                details={
                    "original_action": action_type
                },
            )

        # ---------------------------------------------
        # Typing recovery
        # ---------------------------------------------

        if action_type in {
            "type",
            "type_into_control",
        }:

            return RecoveryDecision(
                should_retry=True,
                strategy="refocus_and_retry",
                reason=(
                    "The typing action was not verified. "
                    "Refocus the target control and "
                    "retry the input."
                ),
                modified_action=action.copy(),
                attempt_number=attempt_number,
                details={
                    "original_action": action_type
                },
            )

        # ---------------------------------------------
        # Browser navigation recovery
        # ---------------------------------------------

        if action_type in {
            "browser_navigate",
            "navigate",
        }:

            return RecoveryDecision(
                should_retry=True,
                strategy="reload_and_retry",
                reason=(
                    "Navigation was not verified. "
                    "Retry navigation after re-observing "
                    "the browser."
                ),
                modified_action=action.copy(),
                attempt_number=attempt_number,
                details={
                    "original_action": action_type
                },
            )

        # ---------------------------------------------
        # Screenshot / observation recovery
        # ---------------------------------------------

        if action_type in {
            "screenshot",
            "observe",
        }:

            return RecoveryDecision(
                should_retry=True,
                strategy="reobserve",
                reason=(
                    "Observation did not produce the "
                    "expected result. Capture the screen "
                    "again."
                ),
                modified_action=action.copy(),
                attempt_number=attempt_number,
            )

        # ---------------------------------------------
        # Generic fallback
        # ---------------------------------------------

        return RecoveryDecision(
            should_retry=True,
            strategy="reobserve_and_retry",
            reason=(
                "The action failed verification. "
                "Re-observe the environment and retry "
                "the action."
            ),
            modified_action=action.copy(),
            attempt_number=attempt_number,
            details={
                "original_action": action_type
            },
        )