from typing import Any, Dict, List, Optional

from core.state_machine import AgentStateMachine
from core.task_manager import TaskManager
from intelligence.planner import Planner
from intelligence.decision_engine import DecisionEngine
from intelligence.agent_executor import AgentExecutor
from core.observation import ObservationManager


class AgentController:
    """
    Central coordinator for the Computer Use AI Agent.

    Responsibilities:

        Task
          ↓
        TaskManager
          ↓
        Planner
          ↓
        DecisionEngine
          ↓
        AgentExecutor
          ↓
        Verification / Recovery

    This controller coordinates the existing components
    without replacing their individual responsibilities.
    """

    def __init__(
        self,
        task_manager: Optional[TaskManager] = None,
        planner: Optional[Planner] = None,
        decision_engine: Optional[DecisionEngine] = None,
        executor: Optional[AgentExecutor] = None,
        state_machine: Optional[AgentStateMachine] = None,
        observation_manager: Optional[ObservationManager] = None,
    ):
        self.task_manager = (
            task_manager or TaskManager()
        )

        self.planner = (
            planner or Planner()
        )

        self.decision_engine = (
            decision_engine or DecisionEngine()
        )

        self.executor = (
            executor or AgentExecutor()
        )

        self.state_machine = (
            state_machine or AgentStateMachine()
        )

        self.observation_manager = (
            observation_manager or ObservationManager()
        )

        self.current_task = None
        self.current_plan = None
        self.execution_history: List[Dict[str, Any]] = []
        self.last_observation = None

    def submit_task(
        self,
        task_description: str,
    ) -> Any:
        """
        Create and register a new task.
        """

        if not task_description:
            raise ValueError(
                "Task description cannot be empty."
            )

        task = self.task_manager.create_task(
            task_description
        )

        self.current_task = task
        self.current_plan = None
        self.execution_history = []

        return task

    def create_plan(self) -> Any:
        """
        Generate a plan for the current task.
        """

        if self.current_task is None:
            raise RuntimeError(
                "No active task. Call submit_task() first."
            )

        description = getattr(
            self.current_task,
            "description",
            None,
        )

        if description is None:
            description = getattr(
                self.current_task,
                "title",
                str(self.current_task),
            )

        self.current_plan = (
            self.planner.create_plan(
                description
            )
        )

        return self.current_plan


    def observe(self) -> Any:
        """
        Capture and analyze the current Windows screen.
        """
        self.last_observation = (
            self.observation_manager.observe()
        )

        return self.last_observation

    def get_last_observation(self) -> Any:
        """
        Return the most recent screen observation.
        """
        return self.last_observation

    def get_next_action(self, observation: Any = None) -> Any:
        """
        Observe the current task state and select the next action.
        """

        if self.current_task is None:
            raise RuntimeError("No active task.")

        if self.current_plan is None:
            raise RuntimeError(
                "No active plan. Call create_plan() first."
            )

        # Use the supplied observation, or observe the screen.
        if observation is None:
            observation = self.observe()

        # Convert VisualState to a dictionary for DecisionEngine.
        if hasattr(observation, "to_dict"):
            computer_state = observation.to_dict()
        elif isinstance(observation, dict):
            computer_state = observation
        else:
            computer_state = {
                "observation": observation
            }

        # Extract the task description.
        task_description = getattr(
            self.current_task,
            "description",
            None,
        )

        if task_description is None:
            task_description = getattr(
                self.current_task,
                "title",
                str(self.current_task),
            )

        # Extract the current planned step.
        current_step = self._get_current_plan_step()

        decision = self.decision_engine.choose_action(
            task=task_description,
            current_step=current_step,
            computer_state=computer_state,
            history=self.execution_history,
        )

        return decision

    def execute_action(
        self,
        action: Dict[str, Any],
        expected: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute an action through the verified
        execution and recovery pipeline.
        """

        result = self.executor.execute(
            action=action,
            expected=expected,
        )

        self.execution_history.append({
            "action": action,
            "expected": expected,
            "result": result,
        })

        return result

    def run_step(
        self,
        observation: Any = None,
        expected: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:
        """
        Execute one agent step.

        The step consists of:

            Decide → Execute → Verify → Recover
        """

        decision = self.get_next_action(
            observation=observation
        )

        if hasattr(decision, "action"):
            action = decision.action
        elif isinstance(decision, dict):
            action = decision.get(
                "action",
                decision,
            )
        else:
            action = decision

        if expected is None:

            if hasattr(decision, "expected"):
                expected = decision.expected

            elif (
                isinstance(decision, dict)
                and "expected" in decision
            ):
                expected = decision["expected"]

            else:
                expected = {}

        result = self.execute_action(
            action=action,
            expected=expected,
        )

        return {
            "decision": decision,
            "action": action,
            "expected": expected,
            "result": result,
        }

    def get_execution_history(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Return the execution trace for the current task.
        """

        return list(
            self.execution_history
        )

    def reset(self):
        self.current_task = None
        self.current_plan = None
        self.execution_history = []
        self.last_observation = None


    def _get_current_plan_step(self) -> Dict[str, Any]:
        """
        Extract the current step from the active plan.

        Supports the existing planner's plan representation
        without forcing the planner to change.
        """

        plan = self.current_plan

        if plan is None:
            raise RuntimeError("No active plan.")

        # Plan object containing a steps attribute.
        steps = getattr(plan, "steps", None)

        if steps is None and isinstance(plan, dict):
            steps = plan.get("steps")

        if steps is None:
            raise RuntimeError(
                "Active plan does not contain steps."
            )

        if not steps:
            raise RuntimeError(
                "Active plan contains no steps."
            )

        # For now, use the first incomplete step.
        for step in steps:

            if isinstance(step, dict):
                completed = step.get(
                    "completed",
                    step.get("status") == "completed",
                )

                if not completed:
                    return step

            else:
                completed = getattr(
                    step,
                    "completed",
                    False,
                )

                if not completed:
                    if hasattr(step, "to_dict"):
                        return step.to_dict()

                    if hasattr(step, "__dict__"):
                        return dict(step.__dict__)

                    return {
                        "description": str(step),
                        "action": str(step),
                    }

        raise RuntimeError(
            "All planned steps have been completed."
        )