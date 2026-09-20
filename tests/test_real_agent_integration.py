from core.agent_controller import AgentController
from intelligence.decision_engine import DecisionEngine


def test_real_observe_pipeline():
    controller = AgentController(
        decision_engine=DecisionEngine()
    )

    observation = controller.observe()

    assert observation is not None
    assert hasattr(observation, "elements")
    assert hasattr(observation, "screen_width")
    assert hasattr(observation, "screen_height")

    print("\n=== REAL OBSERVATION ===")
    print("Screen:", observation.screen_width, "x", observation.screen_height)
    print("Active window:", observation.active_window)
    print("Detected elements:", len(observation.elements))


def test_real_observe_to_decide_pipeline():
    controller = AgentController(
        decision_engine=DecisionEngine()
    )

    controller.submit_task("Open Notepad")

    observation = controller.observe()

    assert observation is not None

    # Create a simple test plan manually.
    # We are deliberately not executing it yet.
    controller.current_plan = {
        "goal": "Open Notepad",
        "steps": [
            {
                "step_number": 1,
                "description": "Open Notepad",
                "action": "open_application",
                "parameters": {
                    "executable": "notepad.exe"
                },
                "expected_result": "Notepad is open.",
            }
        ],
    }

    decision = controller.get_next_action(
        observation=observation
    )

    assert decision is not None
    assert decision.success is True
    assert decision.action is not None

    print("\n=== REAL DECISION ===")
    print("Action:", decision.action)
    print("Reasoning:", decision.reasoning)