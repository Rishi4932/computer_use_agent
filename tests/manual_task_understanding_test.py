from intelligence.task_understanding import (
    TaskUnderstanding,
)


def main():

    print("=" * 60)
    print(" AI TASK UNDERSTANDING TEST")
    print("=" * 60)

    instruction = (
        "Open Chrome, visit https://example.com "
        "and read the page"
    )

    print("\nUser instruction:")
    print(instruction)

    understanding = TaskUnderstanding()

    result = understanding.understand(
        instruction
    )

    print("\nUnderstanding result:")
    print("Success:", result.success)
    print("Message:", result.message)

    print("\nTask:")
    print(result.task_description)

    print("\nGenerated steps:")

    for index, step in enumerate(
        result.steps,
        start=1,
    ):

        print(
            f"\nStep {index}: "
            f"{step['description']}"
        )

        print(
            f"  Action: {step['action']}"
        )

        print(
            f"  Parameters: "
            f"{step['parameters']}"
        )


if __name__ == "__main__":
    main()