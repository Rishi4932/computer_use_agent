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