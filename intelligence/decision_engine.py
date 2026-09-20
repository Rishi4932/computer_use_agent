from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class DecisionResult:
    success: bool
    action: Optional[Dict[str, Any]]
    reasoning: str
    message: str


class DecisionEngine:
    """
    Selects the next action based on:

    - Current task step
    - Current computer state
    - Previous execution history
    - Available action information

    A real LLM decision provider can be connected later.
    """

    def __init__(self, provider=None):
        self.provider = provider

    def choose_action(
        self,
        task: str,
        current_step: Dict[str, Any],
        computer_state: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> DecisionResult:

        if not task.strip():
            return DecisionResult(
                success=False,
                action=None,
                reasoning="No task was provided.",
                message="Decision failed: empty task.",
            )

        if not current_step:
            return DecisionResult(
                success=False,
                action=None,
                reasoning="No current step was provided.",
                message="Decision failed: no current step.",
            )

        if self.provider is not None:

            try:
                return self._provider_decision(
                    task=task,
                    current_step=current_step,
                    computer_state=computer_state or {},
                    history=history or [],
                )

            except Exception as error:

                return DecisionResult(
                    success=False,
                    action=None,
                    reasoning="Provider decision failed.",
                    message=f"Decision provider error: {error}",
                )

        return self._deterministic_decision(
            task=task,
            current_step=current_step,
            computer_state=computer_state or {},
            history=history or [],
        )

    def _deterministic_decision(
        self,
        task: str,
        current_step: Dict[str, Any],
        computer_state: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> DecisionResult:

        action_type = current_step.get("action")

        if not action_type:
            return DecisionResult(
                success=False,
                action=None,
                reasoning="Current step has no action.",
                message="Decision failed: action missing.",
            )

        parameters = current_step.get(
            "parameters",
            {},
        )

        action = {
            "action": action_type,
            **parameters,
        }

        reasoning = self._generate_reasoning(
            current_step=current_step,
            computer_state=computer_state,
            history=history,
        )

        return DecisionResult(
            success=True,
            action=action,
            reasoning=reasoning,
            message="Next action selected successfully.",
        )

    def _generate_reasoning(
        self,
        current_step: Dict[str, Any],
        computer_state: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> str:

        action = current_step.get(
            "action",
            "unknown",
        )

        description = current_step.get(
            "description",
            "",
        )

        expected_result = current_step.get(
            "expected_result",
            "",
        )

        history_count = len(history)

        return (
            f"Current step: {description}. "
            f"Selected action '{action}' because it "
            f"corresponds to the current planned step. "
            f"Expected result: {expected_result}. "
            f"Previous actions recorded: {history_count}."
        )

    def _provider_decision(
        self,
        task: str,
        current_step: Dict[str, Any],
        computer_state: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> DecisionResult:

        response = self.provider.generate(
            task=task,
            current_step=current_step,
            computer_state=computer_state,
            history=history,
        )

        if not isinstance(response, dict):
            raise ValueError(
                "Decision provider must return a dictionary."
            )

        action = response.get("action")

        if not isinstance(action, dict):
            raise ValueError(
                "Decision provider response must contain "
                "an action dictionary."
            )

        return DecisionResult(
            success=True,
            action=action,
            reasoning=response.get(
                "reasoning",
                "Provider selected the action.",
            ),
            message="Provider selected next action.",
        )


class MockDecisionProvider:
    """
    Development-only decision provider.

    Returns a predefined decision so the decision
    engine can be tested without an external AI API.
    """

    def __init__(
        self,
        action: Dict[str, Any],
        reasoning: str = "Mock decision.",
    ):
        self.action = action
        self.reasoning = reasoning

    def generate(
        self,
        task: str,
        current_step: Dict[str, Any],
        computer_state: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        return {
            "action": self.action,
            "reasoning": self.reasoning,
        }