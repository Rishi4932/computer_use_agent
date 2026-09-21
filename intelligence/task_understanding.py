import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class UnderstandingResult:
    success: bool
    task_description: str
    steps: List[Dict[str, Any]]
    message: str


class TaskUnderstanding:
    """
    Converts natural-language user instructions into
    structured executable task steps.

    The actual LLM can be connected later through
    the LLMProvider interface.
    """

    SYSTEM_PROMPT = """
You are the task-understanding component of a Windows
computer-use AI agent.

Your job is to convert a user's natural-language request
into a structured list of executable steps.

Return ONLY valid JSON.

Required format:

{
    "task_description": "short description",
    "steps": [
        {
            "description": "human-readable step",
            "action": "action_type",
            "parameters": {}
        }
    ]
}

Available action types include:

- browser_start
- browser_open_url
- browser_click
- browser_fill
- browser_get_text
- browser_screenshot
- browser_close

- open_application
- click_control
- type_into_control
- get_control_text

- uia_click_control
- uia_invoke_control
- uia_get_control_text

- click
- double_click
- right_click
- type
- press
- hotkey
- scroll
- wait
- screenshot

Do not invent unnecessary actions.

Do not execute the task.

Only understand and structure the task.
"""

    def __init__(self, provider=None):
        self.provider = provider

    def understand(
        self,
        user_instruction: str,
    ) -> UnderstandingResult:

        if not user_instruction.strip():
            return UnderstandingResult(
                success=False,
                task_description="",
                steps=[],
                message="Task instruction is empty.",
            )

        if self.provider is None:
            return self._rule_based_understanding(
                user_instruction
            )

        try:
            response = self.provider.generate(
                system_prompt=self.SYSTEM_PROMPT,
                user_prompt=user_instruction,
            )

            return self._parse_response(
                user_instruction,
                response,
            )

        except Exception as error:
            return UnderstandingResult(
                success=False,
                task_description=user_instruction,
                steps=[],
                message=f"Task understanding failed: {error}",
            )

    def _parse_response(
        self,
        user_instruction: str,
        response: str,
    ) -> UnderstandingResult:

        try:
            data = json.loads(response)

        except json.JSONDecodeError:
            # Sometimes an LLM may wrap JSON in markdown.
            cleaned = self._extract_json(response)

            try:
                data = json.loads(cleaned)
            except json.JSONDecodeError as error:
                return UnderstandingResult(
                    success=False,
                    task_description=user_instruction,
                    steps=[],
                    message=f"Invalid JSON response: {error}",
                )

        if not isinstance(data, dict):
            return UnderstandingResult(
                success=False,
                task_description=user_instruction,
                steps=[],
                message="LLM response must be a JSON object.",
            )

        steps = data.get("steps", [])

        if not isinstance(steps, list):
            return UnderstandingResult(
                success=False,
                task_description=user_instruction,
                steps=[],
                message="'steps' must be a list.",
            )

        validated_steps = []

        for step in steps:

            if not isinstance(step, dict):
                continue

            description = step.get(
                "description",
                "",
            )

            action = step.get(
                "action",
                "",
            )

            parameters = step.get(
                "parameters",
                {},
            )

            if not description or not action:
                continue

            validated_steps.append({
                "description": description,
                "action": action,
                "parameters": parameters,
            })

        if not validated_steps:
            return UnderstandingResult(
                success=False,
                task_description=user_instruction,
                steps=[],
                message="No valid task steps were produced.",
            )

        return UnderstandingResult(
            success=True,
            task_description=data.get(
                "task_description",
                user_instruction,
            ),
            steps=validated_steps,
            message="Task understood successfully.",
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

    def _rule_based_understanding(
        self,
        instruction: str,
    ) -> UnderstandingResult:

        """
        Temporary deterministic fallback.

        This lets us test the complete pipeline before
        connecting a real LLM provider.
        """

        text = instruction.strip()

        steps = []

        lower = text.lower()

        # ---------------------------------------------
        # Browser startup
        # ---------------------------------------------

        if (
            "open chrome" in lower
            or "open browser" in lower
            or "start chrome" in lower
        ):
            steps.append({
                "description": "Open the browser",
                "action": "browser_start",
                "parameters": {},
            })

        # ---------------------------------------------
        # URL detection
        # ---------------------------------------------

        url_match = re.search(
            r"https?://[^\s]+",
            text,
        )

        if url_match:

            url = url_match.group(0).rstrip(
                ".,)"
            )

            steps.append({
                "description": f"Open {url}",
                "action": "browser_open_url",
                "parameters": {
                    "url": url,
                },
            })

        # ---------------------------------------------
        # Read page
        # ---------------------------------------------

        if (
            "read the page" in lower
            or "read page" in lower
            or "get the page text" in lower
        ):
            steps.append({
                "description": "Read the page text",
                "action": "browser_get_text",
                "parameters": {
                    "selector": "body",
                },
            })

        # ---------------------------------------------
        # Screenshot
        # ---------------------------------------------

        if "screenshot" in lower:

            steps.append({
                "description": "Take a screenshot",
                "action": "browser_screenshot",
                "parameters": {
                    "path": (
                        "data/screenshots/"
                        "task_screenshot.png"
                    ),
                },
            })

        # ---------------------------------------------
        # Close browser
        # ---------------------------------------------

        if (
            "close browser" in lower
            or "close chrome" in lower
        ):
            steps.append({
                "description": "Close the browser",
                "action": "browser_close",
                "parameters": {},
            })

        # ---------------------------------------------
        # Result
        # ---------------------------------------------

        if not steps:
            return UnderstandingResult(
                success=False,
                task_description=text,
                steps=[],
                message=(
                    "The temporary task-understanding "
                    "fallback could not identify any actions."
                ),
            )

        return UnderstandingResult(
            success=True,
            task_description=text,
            steps=steps,
            message=(
                "Task understood using the "
                "temporary rule-based provider."
            ),
        )


class MockLLMProvider:
    """
    Test provider that behaves like an LLM.

    This is only for development/testing.
    """

    def __init__(self, response: str):
        self.response = response

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        return self.response