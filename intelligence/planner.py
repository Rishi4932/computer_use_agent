import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class PlanResult:
    success: bool
    goal: str
    steps: List[Dict[str, Any]]
    message: str


class Planner:
    """
    Converts an understood task into an ordered execution plan.

    A real LLM can be connected later through the provider
    interface. A deterministic fallback is included so the
    planner can be tested without an API.
    """

    SYSTEM_PROMPT = """
You are the planning component of a Windows computer-use AI agent.

Your job is to convert a structured task into an ordered execution plan.

Return ONLY valid JSON.

Required format:

{
    "goal": "short goal description",
    "steps": [
        {
            "step_number": 1,
            "description": "human-readable description",
            "action": "action_type",
            "parameters": {},
            "expected_result": "what should happen"
        }
    ]
}

Rules:

1. Steps must be in execution order.
2. Each step should have one primary action.
3. Do not execute any action.
4. Do not invent unnecessary steps.
5. Include an expected result for every step.
6. Use only supported action types.
"""

    SUPPORTED_ACTIONS = {
        "browser_start",
        "browser_open_url",
        "browser_click",
        "browser_fill",
        "browser_get_text",
        "browser_screenshot",
        "browser_close",
        "open_application",
        "click_control",
        "type_into_control",
        "get_control_text",
        "uia_click_control",
        "uia_invoke_control",
        "uia_get_control_text",
        "click",
        "double_click",
        "right_click",
        "type",
        "press",
        "hotkey",
        "scroll",
        "wait",
        "screenshot",
    }

    def __init__(self, provider=None):
        self.provider = provider

    def create_plan(
        self,
        task_description: str,
        understood_steps: List[Dict[str, Any]],
    ) -> PlanResult:

        if not task_description.strip():
            return PlanResult(
                success=False,
                goal="",
                steps=[],
                message="Task description is empty.",
            )

        if not understood_steps:
            return PlanResult(
                success=False,
                goal=task_description,
                steps=[],
                message="No understood steps were provided.",
            )

        if self.provider is None:
            return self._deterministic_plan(
                task_description,
                understood_steps,
            )

        try:
            response = self.provider.generate(
                system_prompt=self.SYSTEM_PROMPT,
                user_prompt=json.dumps({
                    "task_description": task_description,
                    "steps": understood_steps,
                }),
            )

            return self._parse_response(
                task_description,
                response,
            )

        except Exception as error:
            return PlanResult(
                success=False,
                goal=task_description,
                steps=[],
                message=f"Planning failed: {error}",
            )

    def _deterministic_plan(
        self,
        task_description: str,
        understood_steps: List[Dict[str, Any]],
    ) -> PlanResult:

        planned_steps = []

        for index, step in enumerate(
            understood_steps,
            start=1,
        ):
            action = step.get("action")

            if action not in self.SUPPORTED_ACTIONS:
                return PlanResult(
                    success=False,
                    goal=task_description,
                    steps=[],
                    message=(
                        f"Unsupported action: {action}"
                    ),
                )

            description = step.get(
                "description",
                f"Execute {action}",
            )

            parameters = step.get(
                "parameters",
                {},
            )

            expected_result = (
                self._default_expected_result(
                    action
                )
            )

            planned_steps.append({
                "step_number": index,
                "description": description,
                "action": action,
                "parameters": parameters,
                "expected_result": expected_result,
            })

        return PlanResult(
            success=True,
            goal=task_description,
            steps=planned_steps,
            message=(
                "Execution plan created successfully."
            ),
        )

    def _default_expected_result(
        self,
        action: str,
    ) -> str:

        expected_results = {
            "browser_start":
                "A browser window is open.",

            "browser_open_url":
                "The requested webpage is loaded.",

            "browser_click":
                "The requested web element is activated.",

            "browser_fill":
                "The requested field contains the provided text.",

            "browser_get_text":
                "The requested webpage text is retrieved.",

            "browser_screenshot":
                "A browser screenshot is saved.",

            "browser_close":
                "The browser is closed.",

            "open_application":
                "The requested Windows application is open.",

            "click_control":
                "The requested Windows control is activated.",

            "type_into_control":
                "The requested Windows control contains the text.",

            "get_control_text":
                "The requested control text is retrieved.",

            "uia_click_control":
                "The requested native Windows UI control is clicked.",

            "uia_invoke_control":
                "The requested native Windows UI control is invoked.",

            "uia_get_control_text":
                "The requested native Windows UI control text is retrieved.",

            "click":
                "The requested screen location is clicked.",

            "double_click":
                "The requested screen location is double-clicked.",

            "right_click":
                "The requested screen location is right-clicked.",

            "type":
                "The requested text is entered.",

            "press":
                "The requested keyboard key is pressed.",

            "hotkey":
                "The requested keyboard shortcut is executed.",

            "scroll":
                "The screen is scrolled as requested.",

            "wait":
                "The requested wait period has completed.",

            "screenshot":
                "A screenshot is saved.",
        }

        return expected_results.get(
            action,
            f"Action '{action}' completed successfully.",
        )

    def _parse_response(
        self,
        task_description: str,
        response: str,
    ) -> PlanResult:

        try:
            data = json.loads(response)

        except json.JSONDecodeError:
            cleaned = self._extract_json(response)

            try:
                data = json.loads(cleaned)

            except json.JSONDecodeError as error:
                return PlanResult(
                    success=False,
                    goal=task_description,
                    steps=[],
                    message=(
                        f"Invalid planner JSON: {error}"
                    ),
                )

        if not isinstance(data, dict):
            return PlanResult(
                success=False,
                goal=task_description,
                steps=[],
                message="Planner response must be a JSON object.",
            )

        raw_steps = data.get("steps", [])

        if not isinstance(raw_steps, list):
            return PlanResult(
                success=False,
                goal=task_description,
                steps=[],
                message="'steps' must be a list.",
            )

        validated_steps = []

        for index, step in enumerate(
            raw_steps,
            start=1,
        ):

            if not isinstance(step, dict):
                continue

            action = step.get("action")

            if action not in self.SUPPORTED_ACTIONS:
                return PlanResult(
                    success=False,
                    goal=task_description,
                    steps=[],
                    message=(
                        f"Unsupported action in plan: {action}"
                    ),
                )

            description = step.get(
                "description",
                f"Execute {action}",
            )

            parameters = step.get(
                "parameters",
                {},
            )

            expected_result = step.get(
                "expected_result",
                self._default_expected_result(action),
            )

            validated_steps.append({
                "step_number": index,
                "description": description,
                "action": action,
                "parameters": parameters,
                "expected_result": expected_result,
            })

        if not validated_steps:
            return PlanResult(
                success=False,
                goal=task_description,
                steps=[],
                message="No valid plan steps were produced.",
            )

        return PlanResult(
            success=True,
            goal=data.get(
                "goal",
                task_description,
            ),
            steps=validated_steps,
            message="Plan created successfully.",
        )

    def _extract_json(
        self,
        response: str,
    ) -> str:

        match = re.search(
            r"\{.*\}",
            response,
            re.DOTALL,
        )

        if match:
            return match.group(0)

        return response


class MockPlannerProvider:
    """
    Development-only planner provider.

    Used to test LLM-style planner responses without
    requiring an external API.
    """

    def __init__(self, response: str):
        self.response = response

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        return self.response