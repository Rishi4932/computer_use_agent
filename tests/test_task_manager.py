from core.task_manager import TaskManager


def test_create_task():
    manager = TaskManager()

    task = manager.create_task(
        "Open Chrome and visit example.com"
    )

    assert task.description == (
        "Open Chrome and visit example.com"
    )

    assert task.status == "created"
    assert task.task_id is not None


def test_add_steps():
    manager = TaskManager()

    task = manager.create_task(
        "Open website"
    )

    manager.add_step(
        task.task_id,
        "Open browser",
        {
            "action": "browser_start"
        },
    )

    manager.add_step(
        task.task_id,
        "Open website",
        {
            "action": "browser_open_url",
            "url": "https://example.com",
        },
    )

    assert len(task.steps) == 2
    assert task.steps[0].description == "Open browser"
    assert task.steps[1].description == "Open website"


def test_complete_steps():
    manager = TaskManager()

    task = manager.create_task(
        "Test task"
    )

    manager.add_step(
        task.task_id,
        "Step one",
    )

    manager.add_step(
        task.task_id,
        "Step two",
    )

    manager.start_task(
        task.task_id
    )

    assert task.status == "running"
    assert task.steps[0].status == "running"

    manager.complete_current_step(
        task.task_id,
        {
            "success": True
        },
    )

    assert task.steps[0].status == "completed"
    assert task.steps[1].status == "running"

    manager.complete_current_step(
        task.task_id,
        {
            "success": True
        },
    )

    assert task.status == "completed"
    assert task.steps[1].status == "completed"


def test_task_progress():
    manager = TaskManager()

    task = manager.create_task(
        "Progress test"
    )

    manager.add_step(
        task.task_id,
        "Step one",
    )

    manager.add_step(
        task.task_id,
        "Step two",
    )

    manager.start_task(
        task.task_id
    )

    manager.complete_current_step(
        task.task_id
    )

    progress = manager.get_progress(
        task.task_id
    )

    assert progress["completed_steps"] == 1
    assert progress["total_steps"] == 2
    assert progress["percentage"] == 50.0


def test_add_plan_steps():
    manager = TaskManager()

    task = manager.create_task(
        "Open Chrome and visit example.com"
    )

    plan_steps = [
        {
            "step_number": 1,
            "description": "Open the browser",
            "action": "browser_start",
            "parameters": {},
            "expected_result": (
                "A browser window is open."
            ),
        },
        {
            "step_number": 2,
            "description": "Open the website",
            "action": "browser_open_url",
            "parameters": {
                "url": "https://example.com",
            },
            "expected_result": (
                "The requested webpage is loaded."
            ),
        },
    ]

    created_steps = manager.add_plan_steps(
        task.task_id,
        plan_steps,
    )

    assert len(created_steps) == 2
    assert len(task.steps) == 2

    assert task.steps[0].description == (
        "Open the browser"
    )

    assert task.steps[0].action["action"] == (
        "browser_start"
    )

    assert task.steps[0].action["parameters"] == {}

    assert task.steps[0].action["expected_result"] == (
        "A browser window is open."
    )

    assert task.steps[1].action["action"] == (
        "browser_open_url"
    )

    assert task.steps[1].action["parameters"]["url"] == (
        "https://example.com"
    )


def test_add_plan_steps_with_uia_actions():
    manager = TaskManager()

    task = manager.create_task(
        "Use a native Windows control"
    )

    plan_steps = [
        {
            "step_number": 1,
            "description": "Invoke the Settings button",
            "action": "uia_invoke_control",
            "parameters": {
                "window_title": "Untitled - Notepad",
                "control_type": "Button",
                "auto_id": "SettingsButton",
            },
            "expected_result": (
                "The requested native Windows UI control "
                "is invoked."
            ),
        },
    ]

    created_steps = manager.add_plan_steps(
        task.task_id,
        plan_steps,
    )

    assert len(created_steps) == 1
    assert len(task.steps) == 1

    step = task.steps[0]

    assert step.description == (
        "Invoke the Settings button"
    )

    assert step.action["action"] == (
        "uia_invoke_control"
    )

    assert step.action["parameters"]["window_title"] == (
        "Untitled - Notepad"
    )

    assert step.action["parameters"]["control_type"] == (
        "Button"
    )

    assert step.action["parameters"]["auto_id"] == (
        "SettingsButton"
    )

    assert step.action["expected_result"] == (
        "The requested native Windows UI control "
        "is invoked."
    )