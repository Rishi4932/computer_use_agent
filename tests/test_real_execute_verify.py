from core.agent_controller import AgentController
from intelligence.decision_engine import DecisionEngine
from intelligence.agent_executor import AgentExecutor
from intelligence.verified_executor import VerifiedActionExecutor
from intelligence.vision_reasoner import VisionReasoner
from intelligence.recovery import RecoveryEngine
from perception.screenshot import ScreenshotCapture
from perception.ocr import OCRReader
from perception.vision import VisionSystem
from perception.windows_ui_tree import WindowsUITree
from intelligence.verifier import ActionVerifier


def create_real_agent_executor():

    vision_reasoner = VisionReasoner(
        screenshot_capture=ScreenshotCapture(),
        ocr_reader=OCRReader(),
        vision_system=VisionSystem(),
        ui_tree=WindowsUITree(),
    )

    verified_executor = VerifiedActionExecutor(
        vision_reasoner=vision_reasoner,
        verifier=ActionVerifier(),
    )

    return AgentExecutor(
        verified_executor=verified_executor,
        recovery_engine=RecoveryEngine(),
    )


def execute_and_check(controller, action, expected, label):

    print(f"\n=== {label} ===")
    print("Action:", action)
    print("Expected:", expected)

    result = controller.execute_action(
        action=action,
        expected=expected,
    )

    print("\n=== RAW EXECUTION RESULT ===")
    print(result)

    assert result is not None
    assert isinstance(result, dict)

    if result["success"] is False:
        print("\n=== FAILURE DETAILS ===")

        print("Overall success:", result.get("success"))
        print("Attempts:", result.get("attempts"))
        print("Recovered:", result.get("recovered"))
        print("History:", result.get("history"))

        final_result = result.get("final_result")

        print("\nFinal result:")
        print(final_result)

        if isinstance(final_result, dict):

            print("\nAction result:")
            print(final_result.get("action_result"))

            print("\nVerification result:")
            print(final_result.get("verification"))

            print("\nScreenshot:")
            print(final_result.get("screenshot"))

            print("\nMessage:")
            print(final_result.get("message"))

    assert result["success"] is True

    final_result = result["final_result"]

    verification = final_result["verification"]

    print("Verification:", verification.success)
    print("Confidence:", verification.confidence)
    print("Reason:", verification.reason)

    assert verification.success is True

    return result

    
def test_real_multistep_notepad():

    controller = AgentController(
        decision_engine=DecisionEngine(),
        executor=create_real_agent_executor(),
    )

    # =========================================================
    # STEP 1 — TASK
    # =========================================================

    controller.submit_task(
        "Open Notepad and type: Hello from my AI computer agent"
    )

    # =========================================================
    # STEP 2 — INITIAL OBSERVATION
    # =========================================================

    observation = controller.observe()

    assert observation is not None

    print("\n=== INITIAL OBSERVATION ===")
    print(
        "Screen:",
        observation.screen_width,
        "x",
        observation.screen_height,
    )
    print("Active window:", observation.active_window)
    print("Detected elements:", len(observation.elements))

    # =========================================================
    # STEP 3 — FIRST PLAN
    # =========================================================

    controller.current_plan = {
        "goal": "Open Notepad and type text",
        "steps": [
            {
                "step_number": 1,
                "description": "Open Notepad",
                "action": "open_application",
                "parameters": {
                    "executable": "notepad.exe"
                },
                "expected_result": "Notepad is open.",
            },
            {
                "step_number": 2,
                "description": "Type text into Notepad",
                "action": "type",
                "parameters": {
                    "text": "Hello from my AI computer agent"
                },
                "expected_result": "The text appears in Notepad.",
            },
        ],
    }

    # =========================================================
    # STEP 4 — DECIDE STEP 1
    # =========================================================

    decision = controller.get_next_action(
        observation=observation
    )

    assert decision.success is True
    assert decision.action is not None

    print("\n=== DECISION — STEP 1 ===")
    print("Action:", decision.action)
    print("Reasoning:", decision.reasoning)

    # =========================================================
    # STEP 5 — EXECUTE STEP 1
    # =========================================================

    open_result = execute_and_check(
        controller=controller,
        action=decision.action,
        expected={
            "type": "text_contains",
            "text": "Notepad",
        },
        label="EXECUTE STEP 1 — OPEN NOTEPAD",
    )

    print(
        "\nNotepad opened and visually verified."
    )

    # =========================================================
    # STEP 6 — OBSERVE AGAIN
    # =========================================================

    observation_after_open = controller.observe()

    assert observation_after_open is not None

    print("\n=== OBSERVATION AFTER OPEN ===")
    print(
        "Active window:",
        observation_after_open.active_window,
    )
    print(
        "Detected elements:",
        len(observation_after_open.elements),
    )

    # =========================================================
    # STEP 7 — MOVE TO STEP 2
    # =========================================================

    controller.current_plan = {
        "goal": "Open Notepad and type text",
        "steps": [
            {
                "step_number": 2,
                "description": "Type text into Notepad",
                "action": "type",
                "parameters": {
                    "text": "Hello from my AI computer agent"
                },
                "expected_result": "The text appears in Notepad.",
            },
        ],
    }

    # =========================================================
    # STEP 8 — DECIDE STEP 2
    # =========================================================

    decision = controller.get_next_action(
        observation=observation_after_open
    )

    assert decision.success is True
    assert decision.action is not None

    print("\n=== DECISION — STEP 2 ===")
    print("Action:", decision.action)
    print("Reasoning:", decision.reasoning)

    # =========================================================
    # STEP 9 — EXECUTE STEP 2
    # =========================================================

    typed_text = "Hello from my AI computer agent"

    type_result = execute_and_check(
        controller=controller,
        action={
            "action": "type",
            "text": typed_text,
        },
        expected={
            "type": "text_contains",
            "text": typed_text,
        },
        label="EXECUTE STEP 2 — TYPE TEXT",
    )

    # =========================================================
    # STEP 10 — FINAL OBSERVATION
    # =========================================================

    final_observation = controller.observe()

    assert final_observation is not None

    print("\n=== FINAL OBSERVATION ===")
    print(
        "Active window:",
        final_observation.active_window,
    )
    print(
        "Detected elements:",
        len(final_observation.elements),
    )

    # =========================================================
    # FINAL RESULT
    # =========================================================

    print("\n========================================")
    print(" MULTI-STEP COMPUTER AGENT TEST PASSED")
    print("========================================")
    print("Step 1: Open Notepad       ✓")
    print("Step 2: Type text          ✓")
    print("Step 3: Visual verification ✓")
    print("Step 4: Final observation  ✓")
    print("----------------------------------------")
    print("Observe → Decide → Execute → Verify")
    print("========================================")