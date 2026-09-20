from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class TaskStep:
    step_id: str
    description: str
    status: str = "pending"
    action: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class Task:
    task_id: str
    description: str
    status: str = "created"
    steps: List[TaskStep] = field(default_factory=list)
    current_step_index: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def create_task(self, description: str) -> Task:
        task_id = str(uuid4())

        task = Task(
            task_id=task_id,
            description=description,
        )

        self.tasks[task_id] = task

        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def add_step(
        self,
        task_id: str,
        description: str,
        action: Optional[Dict[str, Any]] = None,
    ) -> TaskStep:

        task = self.get_task(task_id)

        if task is None:
            raise ValueError(
                f"Task not found: {task_id}"
            )

        step = TaskStep(
            step_id=str(uuid4()),
            description=description,
            action=action,
        )

        task.steps.append(step)

        return step

    def get_current_step(
        self,
        task_id: str,
    ) -> Optional[TaskStep]:

        task = self.get_task(task_id)

        if task is None:
            raise ValueError(
                f"Task not found: {task_id}"
            )

        if task.current_step_index >= len(task.steps):
            return None

        return task.steps[
            task.current_step_index
        ]

    def start_task(self, task_id: str):
        task = self.get_task(task_id)

        if task is None:
            raise ValueError(
                f"Task not found: {task_id}"
            )

        task.status = "running"

        if task.steps:
            task.steps[0].status = "running"

        return task

    def complete_current_step(
        self,
        task_id: str,
        result: Optional[Dict[str, Any]] = None,
    ):

        task = self.get_task(task_id)

        if task is None:
            raise ValueError(
                f"Task not found: {task_id}"
            )

        step = self.get_current_step(task_id)

        if step is None:
            return task

        step.status = "completed"
        step.result = result

        task.current_step_index += 1

        if task.current_step_index < len(task.steps):
            task.steps[
                task.current_step_index
            ].status = "running"

        else:
            task.status = "completed"
            task.completed_at = datetime.now()

        return task

    def fail_current_step(
        self,
        task_id: str,
        error: str,
    ):

        task = self.get_task(task_id)

        if task is None:
            raise ValueError(
                f"Task not found: {task_id}"
            )

        step = self.get_current_step(task_id)

        if step is not None:
            step.status = "failed"
            step.error = error

        task.status = "failed"

        return task

    def get_progress(
        self,
        task_id: str,
    ) -> Dict[str, Any]:

        task = self.get_task(task_id)

        if task is None:
            raise ValueError(
                f"Task not found: {task_id}"
            )

        total = len(task.steps)

        completed = sum(
            1
            for step in task.steps
            if step.status == "completed"
        )

        percentage = (
            (completed / total) * 100
            if total > 0
            else 0
        )

        return {
            "task_id": task.task_id,
            "status": task.status,
            "completed_steps": completed,
            "total_steps": total,
            "percentage": percentage,
        }