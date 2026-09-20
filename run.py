from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def create_required_directories():
    directories = [
        PROJECT_ROOT / "data",
        PROJECT_ROOT / "data" / "screenshots",
        PROJECT_ROOT / "data" / "logs",
        PROJECT_ROOT / "data" / "database",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def main():
    create_required_directories()

    print("=" * 60)
    print(" COMPUTER USE AI AGENT")
    print("=" * 60)
    print()
    print("Project initialized successfully.")
    print(f"Project directory: {PROJECT_ROOT}")
    print()
    print("Next stage: Windows computer control")
    print()


if __name__ == "__main__":
    main()