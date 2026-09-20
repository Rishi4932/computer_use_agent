from intelligence.task_understanding import (
    TaskUnderstanding,
)

from intelligence.planner import Planner


def main():

    print("=" * 60)
    print(" AI PLANNER TEST")
    print("=" * 60)

    instruction = (
        "Open Chrome, visit https://example.com "
        "and read the page"
    )

    print("\nUser instruction:")
    print(instruction)

    # ---------------------------------------------
    # Task Understanding
    # ---------------------------------------------

    understanding = TaskUnderstanding()

    understood = understanding.understand(
        instruction
    )

    print("\n[1] Task Understanding")

    print(
        "Success:",
        understood.success
    )

    # ---------------------------------------------
    # Planning
    # ---------------------------------------------

    planner = Planner()

    plan = planner.create_plan(
        understood.task_description,
        understood.steps,
    )

    print("\n[2] Planner")

    print(
        "Success:",
        plan.success
    )

    print(
        "Message:",
        plan.message
    )

    print("\nGoal:")
    print(plan.goal)

    print("\nExecution Plan:")

    for step in plan.steps:

        print(
            f"\nStep {step['step_number']}: "
            f"{step['description']}"
        )

        print(
            f"  Action: "
            f"{step['action']}"
        )

        print(
            f"  Parameters: "
            f"{step['parameters']}"
        )

        print(
            f"  Expected result: "
            f"{step['expected_result']}"
        )


if __name__ == "__main__":
    main()