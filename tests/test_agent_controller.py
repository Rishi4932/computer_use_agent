from unittest.mock import MagicMock

from core.agent_controller import AgentController


def create_controller():
    task_manager = MagicMock()
    task_understanding = MagicMock()
    planner = MagicMock()
    decision_engine = MagicMock()
    executor = MagicMock()
    state_machine = MagicMock()

    controller = AgentController(
        task_manager=task_manager,
        task_understanding=task_understanding,
        planner=planner,
        decision_engine=decision_engine,
        executor=executor,
        state_machine=state_machine,
    )

    return (
        controller,
        task_manager,
        task_understanding,
        planner,
        decision_engine,
        executor,
        state_machine,
    )


def test_controller_initialization():
    controller, *_ = create_controller()

    assert controller is not None
    assert controller.current_task is None
    assert controller.current_plan is None
    assert controller.execution_history == []


def test_submit_task():
    (
        controller,
        task_manager,
        *_,
    ) = create_controller()

    task = MagicMock()
    task.description = "Open Notepad"

    task_manager.create_task.return_value = task

    result = controller.submit_task("Open Notepad")

    assert result == task
    assert controller.current_task == task
    assert controller.current_plan is None
    assert controller.execution_history == []

    task_manager.create_task.assert_called_once_with(
        "Open Notepad"
    )


def test_understand_task():
    (
        controller,
        _,
        task_understanding,
        *_,
    ) = create_controller()

    understanding = MagicMock()
    understanding.success = True
    understanding.task_description = "Open Notepad"
    understanding.steps = [
        {
            "description": "Open Notepad",
            "action": "open_application",
            "parameters": {
                "executable": "notepad.exe"
            },
        }
    ]

    task_understanding.understand.return_value = (
        understanding
    )

    controller.submit_task("Open Notepad")

    result = controller.understand_task()

    assert result == understanding
    assert controller.current_understanding == (
        understanding
    )

    task_understanding.understand.assert_called_once_with(
        "Open Notepad"
    )


def test_create_plan():
    (
        controller,
        _,
        task_understanding,
        planner,
        *_,
    ) = create_controller()

    understanding = MagicMock()
    understanding.success = True
    understanding.steps = [
        {
            "description": "Open Notepad",
            "action": "open_application",
            "parameters": {
                "executable": "notepad.exe"
            },
        }
    ]

    task_understanding.understand.return_value = (
        understanding
    )

    plan = MagicMock()
    planner.create_plan.return_value = plan

    controller.submit_task("Open Notepad")

    controller.understand_task()

    result = controller.create_plan()

    assert result == plan
    assert controller.current_plan == plan

    planner.create_plan.assert_called_once_with(
        "Open Notepad",
        understanding.steps,
    )


def test_create_plan_runs_understanding_automatically():
    (
        controller,
        _,
        task_understanding,
        planner,
        *_,
    ) = create_controller()

    understanding = MagicMock()
    understanding.success = True
    understanding.steps = [
        {
            "description": "Open Notepad",
            "action": "open_application",
            "parameters": {
                "executable": "notepad.exe"
            },
        }
    ]

    task_understanding.understand.return_value = (
        understanding
    )

    plan = MagicMock()
    planner.create_plan.return_value = plan

    controller.submit_task("Open Notepad")

    result = controller.create_plan()

    assert result == plan
    assert controller.current_understanding == (
        understanding
    )

    task_understanding.understand.assert_called_once_with(
        "Open Notepad"
    )

    planner.create_plan.assert_called_once_with(
        "Open Notepad",
        understanding.steps,
    )


def test_create_plan_populates_task_manager():
    (
        controller,
        task_manager,
        task_understanding,
        planner,
        *_,
    ) = create_controller()

    understanding = MagicMock()
    understanding.success = True
    understanding.steps = [
        {
            "description": "Open Notepad",
            "action": "open_application",
            "parameters": {
                "executable": "notepad.exe"
            },
        }
    ]

    task_understanding.understand.return_value = (
        understanding
    )

    plan = MagicMock()
    plan.success = True
    plan.steps = [
        {
            "step_number": 1,
            "description": "Open Notepad",
            "action": "open_application",
            "parameters": {
                "executable": "notepad.exe"
            },
            "expected_result": "Notepad is open.",
        }
    ]

    planner.create_plan.return_value = plan

    task = MagicMock()
    task.description = "Open Notepad"

    task_manager.create_task.return_value = task

    controller.submit_task("Open Notepad")

    controller.create_plan()

    task_manager.add_plan_steps.assert_called_once_with(
        task.task_id,
        plan.steps,
    )


def test_create_plan_without_task():
    controller, *_ = create_controller()

    try:
        controller.create_plan()
        assert False
    except RuntimeError as error:
        assert "No active task" in str(error)


def test_get_next_action_without_task():
    controller, *_ = create_controller()

    try:
        controller.get_next_action(
            observation={"screen": "desktop"}
        )
        assert False
    except RuntimeError as error:
        assert "No active task" in str(error)


def test_get_next_action_without_plan():
    (
        controller,
        task_manager,
        *_,
    ) = create_controller()

    task = MagicMock()
    task.description = "Open Notepad"

    task_manager.create_task.return_value = task

    controller.submit_task("Open Notepad")

    try:
        controller.get_next_action(
            observation={"screen": "desktop"}
        )
        assert False
    except RuntimeError as error:
        assert "No active plan" in str(error)


def test_get_next_action():
    (
        controller,
        task_manager,
        task_understanding,
        planner,
        decision_engine,
        *_,
    ) = create_controller()

    task = MagicMock()
    task.description = "Open Notepad"

    task_manager.create_task.return_value = task

    understanding = MagicMock()
    understanding.success = True
    understanding.steps = [
        {
            "description": "Open Notepad",
            "action": "open_application",
            "parameters": {
                "executable": "notepad.exe"
            },
        }
    ]

    task_understanding.understand.return_value = (
        understanding
    )

    plan = MagicMock()
    plan.steps = [
        {
            "step_number": 1,
            "description": "Open Notepad",
            "action": "open_application",
            "parameters": {
                "executable": "notepad.exe"
            },
            "expected_result": "Notepad is open.",
        }
    ]

    planner.create_plan.return_value = plan

    decision = MagicMock()

    decision_engine.choose_action.return_value = decision

    controller.submit_task("Open Notepad")
    controller.create_plan()

    result = controller.get_next_action(
        observation={
            "screen": "desktop"
        }
    )

    assert result == decision

    decision_engine.choose_action.assert_called_once()


def test_execute_action():
    (
        controller,
        _,
        _,
        _,
        _,
        executor,
        _,
    ) = create_controller()

    action = {
        "action": "click",
        "x": 100,
        "y": 200,
    }

    expected = {
        "type": "present",
        "text": "Success",
    }

    execution_result = {
        "success": True,
        "message": "Verified",
    }

    executor.execute.return_value = execution_result

    result = controller.execute_action(
        action,
        expected,
    )

    assert result == execution_result

    executor.execute.assert_called_once_with(
        action=action,
        expected=expected,
    )

    assert len(controller.execution_history) == 1


def test_run_step():
    (
        controller,
        task_manager,
        task_understanding,
        planner,
        decision_engine,
        executor,
        _,
    ) = create_controller()

    task = MagicMock()
    task.description = "Open Notepad"

    task_manager.create_task.return_value = task

    understanding = MagicMock()
    understanding.success = True
    understanding.steps = [
        {
            "description": "Open Notepad",
            "action": "open_application",
            "parameters": {
                "executable": "notepad.exe"
            },
        }
    ]

    task_understanding.understand.return_value = (
        understanding
    )

    plan = MagicMock()
    plan.steps = [
        {
            "step_number": 1,
            "description": "Open Notepad",
            "action": "open_application",
            "parameters": {
                "executable": "notepad.exe"
            },
            "expected_result": "Notepad is open.",
        }
    ]

    planner.create_plan.return_value = plan

    decision = MagicMock()

    decision.action = {
        "action": "click",
        "x": 100,
        "y": 200,
    }

    decision.expected = {
        "type": "present",
        "text": "Success",
    }

    decision_engine.choose_action.return_value = decision

    execution_result = {
        "success": True,
        "message": "Verified",
    }

    executor.execute.return_value = execution_result

    controller.submit_task("Open Notepad")
    controller.create_plan()

    result = controller.run_step()

    assert result["result"] == execution_result
    assert result["action"] == decision.action
    assert result["expected"] == decision.expected
    assert result["decision"] == decision

    decision_engine.choose_action.assert_called_once()

    executor.execute.assert_called_once_with(
        action=decision.action,
        expected=decision.expected,
    )


def test_get_execution_history():
    (
        controller,
        _,
        _,
        _,
        _,
        executor,
        _,
    ) = create_controller()

    execution_result = {
        "success": True,
        "message": "Verified",
    }

    executor.execute.return_value = execution_result

    action = {
        "action": "click",
        "x": 100,
        "y": 200,
    }

    expected = {
        "type": "present",
        "text": "Success",
    }

    controller.execute_action(
        action,
        expected,
    )

    history = controller.get_execution_history()

    assert len(history) == 1


def test_reset():
    (
        controller,
        task_manager,
        _,
        planner,
        _,
        _,
        _,
    ) = create_controller()

    task = MagicMock()
    task.description = "Open Notepad"

    task_manager.create_task.return_value = task

    plan = MagicMock()
    planner.create_plan.return_value = plan

    controller.submit_task("Open Notepad")

    controller.current_plan = plan

    controller.execution_history.append(
        {
            "action": "test"
        }
    )

    controller.reset()

    assert controller.current_task is None
    assert controller.current_plan is None
    assert controller.execution_history == []