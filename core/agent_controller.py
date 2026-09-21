from typing import Any, Dict, List, Optional

from core.task_manager import TaskManager
from core.observation import ObservationManager
from core.state_machine import AgentStateMachine

from intelligence.task_understanding import TaskUnderstanding
from intelligence.planner import Planner
from intelligence.decision_engine import DecisionEngine
from intelligence.agent_executor import AgentExecutor


class AgentController:
    """
    Central controller for the computer-use agent.

    Main pipeline:

        User Task
            ↓
        Task Understanding
            ↓
        Planning
            ↓
        Observation
            ↓
        Decision
            ↓
        Execution
            ↓
        Verification / Recovery
            ↓
        Next Step
    """

    def __init__(
        self,
        task_manager: Optional[TaskManager] = None,
        task_understanding: Optional[TaskUnderstanding] = None,
        planner: Optional[Planner] = None,
        decision_engine: Optional[DecisionEngine] = None,
        executor: Optional[AgentExecutor] = None,
        state_machine: Optional[AgentStateMachine] = None,
        observation_manager: Optional[ObservationManager] = None,
    ):
        self.task_manager = (
            task_manager
            if task_manager is not None
            else TaskManager()
        )

        self.task_understanding = (
            task_understanding
            if task_understanding is not None
            else TaskUnderstanding()
        )

        self.planner = (
            planner
            if planner is not None
            else Planner()
        )

        self.decision_engine = (
            decision_engine
            if decision_engine is not None
            else DecisionEngine()
        )

        self.executor = (
            executor
            if executor is not None
            else AgentExecutor()
        )

        self.state_machine = (
            state_machine
            if state_machine is not None
            else AgentStateMachine()
        )

        self.observation_manager = (
            observation_manager
            if observation_manager is not None
            else ObservationManager()
        )

        # ---------------------------------------------------------
        # Runtime state
        # ---------------------------------------------------------

        self.current_task = None

        self.current_task_description: Optional[str] = None

        self.current_understanding = None

        self.current_plan = None

        self.last_observation = None

        self.execution_history: List[
            Dict[str, Any]
        ] = []

    # =============================================================
    # TASK SUBMISSION
    # =============================================================

    def submit_task(self, description: str):
        """
        Create and register a new task.
        """

        if not isinstance(description, str):
            raise ValueError(
                "Task description must be a string."
            )

        description = description.strip()

        if not description:
            raise ValueError(
                "Task description cannot be empty."
            )

        self.current_task = (
            self.task_manager.create_task(
                description
            )
        )

        self.current_task_description = description

        self.current_understanding = None
        self.current_plan = None
        self.last_observation = None
        self.execution_history = []

        return self.current_task

    # =============================================================
    # TASK UNDERSTANDING
    # =============================================================

    def understand_task(self) -> Any:
        """
        Understand the current natural-language task.
        """

        if self.current_task is None:
            raise RuntimeError(
                "No active task. Call submit_task() first."
            )

        description = self.current_task_description

        if not description:
            description = getattr(
                self.current_task,
                "description",
                None,
            )

        if not description:
            raise RuntimeError(
                "Active task has no description."
            )

        understanding = (
            self.task_understanding.understand(
                description
            )
        )

        if not getattr(
            understanding,
            "success",
            False,
        ):
            raise RuntimeError(
                "Task understanding failed: "
                + getattr(
                    understanding,
                    "message",
                    "Unknown error.",
                )
            )

        self.current_understanding = understanding

        return understanding

    # =============================================================
    # PLAN CREATION
    # =============================================================

    def create_plan(self) -> Any:
        """
        Create an executable plan for the current task.
        """

        if self.current_task is None:
            raise RuntimeError(
                "No active task. Call submit_task() first."
            )

        if self.current_understanding is None:
            self.understand_task()

        description = self.current_task_description

        if not description:
            description = getattr(
                self.current_task,
                "description",
                None,
            )

        if not description:
            raise RuntimeError(
                "Active task has no description."
            )

        understood_steps = getattr(
            self.current_understanding,
            "steps",
            [],
        )

        plan = self.planner.create_plan(
            description,
            understood_steps,
        )

        if not getattr(
            plan,
            "success",
            True,
        ):
            raise RuntimeError(
                "Planning failed: "
                + getattr(
                    plan,
                    "message",
                    "Unknown error.",
                )
            )

        self.current_plan = plan

        plan_steps = getattr(
            plan,
            "steps",
            [],
        )

        self.task_manager.add_plan_steps(
            self.current_task.task_id,
            plan_steps,
        )

        return plan

    # =============================================================
    # OBSERVATION
    # =============================================================

    def observe(self):
        """
        Capture and analyze the current Windows screen.
        """

        observation = (
            self.observation_manager.observe()
        )

        self.last_observation = observation

        return observation

    # =============================================================
    # LAST OBSERVATION
    # =============================================================

    def get_last_observation(self):
        """
        Return the latest observation.
        """

        return self.last_observation

    # =============================================================
    # CONVERT OBSERVATION FOR DECISION ENGINE
    # =============================================================

    def _observation_to_dict(
        self,
        observation: Any,
    ) -> Dict[str, Any]:
        """
        Convert a VisualState or dictionary observation into
        the dictionary format expected by DecisionEngine.
        """

        if observation is None:
            return {}

        # Already a dictionary.
        if isinstance(observation, dict):
            return observation

        # VisualState or similar object with to_dict().
        if hasattr(observation, "to_dict"):
            try:
                result = observation.to_dict()

                if isinstance(result, dict):
                    return result

            except Exception:
                pass

        # Explicitly construct a useful computer state from
        # VisualState-style objects.
        result: Dict[str, Any] = {}

        attributes = [
            "screenshot_path",
            "screen_width",
            "screen_height",
            "active_window",
            "window_titles",
            "visible_text",
            "elements",
            "metadata",
        ]

        for attribute in attributes:
            if hasattr(
                observation,
                attribute,
            ):
                value = getattr(
                    observation,
                    attribute,
                )

                # Convert Path objects into strings.
                if attribute == "screenshot_path":
                    value = str(value)

                result[attribute] = value

        return result

    # =============================================================
    # GET NEXT ACTION
    # =============================================================

    def get_next_action(
        self,
        observation: Optional[Any] = None,
    ):
        """
        Determine the next action using the real DecisionEngine API.

        DecisionEngine contract:

            choose_action(
                task,
                current_step,
                computer_state,
                history
            )
        """

        if self.current_task is None:
            raise RuntimeError(
                "No active task. Call submit_task() first."
            )

        if self.current_plan is None:
            raise RuntimeError(
                "No active plan. Call create_plan() first."
            )

        # ---------------------------------------------------------
        # Store supplied observation
        # ---------------------------------------------------------

        if observation is not None:
            self.last_observation = observation

        current_observation = (
            observation
            if observation is not None
            else self.last_observation
        )

        # ---------------------------------------------------------
        # Current plan step
        # ---------------------------------------------------------

        current_step = (
            self._get_current_plan_step()
        )

        if current_step is None:
            return None

        # ---------------------------------------------------------
        # Original user task
        # ---------------------------------------------------------

        task_description = (
            self.current_task_description
        )

        if not task_description:
            task_description = getattr(
                self.current_task,
                "description",
                "",
            )

        if not isinstance(
            task_description,
            str,
        ):
            task_description = str(
                task_description
            )

        # ---------------------------------------------------------
        # Convert observation to computer state
        # ---------------------------------------------------------

        computer_state = (
            self._observation_to_dict(
                current_observation
            )
        )

        # ---------------------------------------------------------
        # Decision history
        # ---------------------------------------------------------

        history = self.execution_history

        # ---------------------------------------------------------
        # IMPORTANT:
        #
        # DecisionEngine expects:
        #
        #   task
        #   current_step
        #   computer_state
        #   history
        #
        # Do NOT pass current_step as task.
        # ---------------------------------------------------------

        decision = (
            self.decision_engine.choose_action(
                task_description,
                current_step,
                computer_state,
                history,
            )
        )

        return decision

    # =============================================================
    # EXECUTE ACTION
    # =============================================================

    def execute_action(
        self,
        action: Dict[str, Any],
        expected: Optional[Dict[str, Any]] = None,
    ):
        """
        Execute one action through AgentExecutor.
        """

        if action is None:
            raise ValueError(
                "Action cannot be None."
            )

        if expected is not None:
            result = self.executor.execute(
                action=action,
                expected=expected,
            )
        else:
            result = self.executor.execute(
                action=action,
            )

        history_entry = {
            "action": action,
            "result": result,
        }

        if expected is not None:
            history_entry["expected"] = expected

        self.execution_history.append(
            history_entry
        )

        return result

    # =============================================================
    # RUN ONE COMPLETE STEP
    # =============================================================

    def run_step(self):
        """
        Run one complete:

            Observe → Decide → Execute

        cycle.

        AgentExecutor handles verification and recovery.
        """

        if self.current_task is None:
            raise RuntimeError(
                "No active task. Call submit_task() first."
            )

        if self.current_plan is None:
            raise RuntimeError(
                "No active plan. Call create_plan() first."
            )

        # ---------------------------------------------------------
        # 1. Observe
        # ---------------------------------------------------------

        observation = self.observe()

        # ---------------------------------------------------------
        # 2. Decide
        # ---------------------------------------------------------

        decision = self.get_next_action(
            observation=observation
        )

        if decision is None:
            return {
                "success": False,
                "message": "No action available.",
                "observation": observation,
                "decision": None,
                "action": None,
                "expected": None,
                "result": None,
            }

        # ---------------------------------------------------------
        # 3. Extract decision action
        # ---------------------------------------------------------

        action = getattr(
            decision,
            "action",
            None,
        )

        expected = getattr(
            decision,
            "expected",
            None,
        )

        # ---------------------------------------------------------
        # Support dictionary decisions
        # ---------------------------------------------------------

        if isinstance(
            decision,
            dict,
        ):
            action = decision.get(
                "action"
            )

            expected = decision.get(
                "expected"
            )

            if "action" in decision:
                action = decision

        # ---------------------------------------------------------
        # Validate action
        # ---------------------------------------------------------

        if action is None:
            return {
                "success": False,
                "message": (
                    "Decision did not contain an action."
                ),
                "observation": observation,
                "decision": decision,
                "action": None,
                "expected": expected,
                "result": None,
            }

        # ---------------------------------------------------------
        # 4. Execute
        # ---------------------------------------------------------

        result = self.execute_action(
            action,
            expected,
        )

        # ---------------------------------------------------------
        # Determine success
        # ---------------------------------------------------------

        if isinstance(
            result,
            dict,
        ):
            success = result.get(
                "success",
                True,
            )
        else:
            success = getattr(
                result,
                "success",
                True,
            )

        # ---------------------------------------------------------
        # Return complete cycle
        # ---------------------------------------------------------

        return {
            "success": success,
            "observation": observation,
            "decision": decision,
            "action": action,
            "expected": expected,
            "result": result,
        }

    # =============================================================
    # EXECUTION HISTORY
    # =============================================================

    def get_execution_history(self):
        """
        Return execution history for the current task.
        """

        return self.execution_history

    # =============================================================
    # RESET
    # =============================================================

    def reset(self):
        """
        Reset the controller to an empty state.
        """

        self.current_task = None
        self.current_task_description = None
        self.current_understanding = None
        self.current_plan = None
        self.last_observation = None
        self.execution_history = []

    # =============================================================
    # CURRENT PLAN STEP
    # =============================================================

    def _get_current_plan_step(self):
        """
        Return the currently active plan step.

        Supports both:

        1. PlanResult objects:
               plan.steps

        2. Dictionary plans:
               plan["steps"]
        """

        if self.current_plan is None:
            return None

        # ---------------------------------------------------------
        # Extract steps
        # ---------------------------------------------------------

        if isinstance(
            self.current_plan,
            dict,
        ):
            steps = self.current_plan.get(
                "steps"
            )
        else:
            steps = getattr(
                self.current_plan,
                "steps",
                None,
            )

        if not steps:
            return None

        # ---------------------------------------------------------
        # Current step index
        # ---------------------------------------------------------

        index = getattr(
            self.current_task,
            "current_step_index",
            0,
        )

        if not isinstance(
            index,
            int,
        ):
            index = 0

        if index < 0:
            index = 0

        if index >= len(steps):
            return None

        return steps[index]