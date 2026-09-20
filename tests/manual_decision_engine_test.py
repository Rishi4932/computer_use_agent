from intelligence.task_understanding import (
    TaskUnderstanding,
)

from intelligence.planner import Planner

from intelligence.decision_engine import (
    DecisionEngine,
)


def main():

    print("=" * 60)
    print(" AI DECISION ENGINE TEST")
    print("=" * 60)

    instruction = (
        "Open Chrome, visit https://example.com "
        "and read the page"
    )

    print("\nUser instruction:")
    print(instruction)

    # ---------------------------------------------------------
    # Task Understanding
    # ---------------------------------------------------------

    understanding = TaskUnderstanding()

    understood = understanding.understand(
        instruction
    )

    print("\n[1] Task Understanding:")
    print(
        "Success:",
        understood.success
    )

    # ---------------------------------------------------------
    # Planner
    # ---------------------------------------------------------

    planner = Planner()

    plan = planner.create_plan(
        understood.task_description,
        understood.steps,
    )

    print("\n[2] Planner:")
    print(
        "Success:",
        plan.success
    )

    # ---------------------------------------------------------
    # Decision Engine
    # ---------------------------------------------------------

    engine = DecisionEngine()

    history = []

    computer_state = {
        "browser_open": False,
        "current_url": None,
    }

    print("\n[3] Decision Engine:")

    for step in plan.steps:

        print(
            f"\nStep {step['step_number']}: "
            f"{step['description']}"
        )

        result = engine.choose_action(
            task=plan.goal,
            current_step=step,
            computer_state=computer_state,
            history=history,
        )

        print(
            "Decision success:",
            result.success,
        )

        print(
            "Reasoning:",
            result.reasoning,
        )

        print(
            "Selected action:",
            result.action,
        )

        if result.success:

            history.append({
                "action": result.action,
                "success": True,
            })


if __name__ == "__main__":
    main()