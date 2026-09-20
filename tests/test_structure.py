from pathlib import Path


def test_project_structure():
    root = Path(__file__).resolve().parents[1]

    required_directories = [
        "core",
        "intelligence",
        "perception",
        "execution",
        "voice",
        "safety",
        "memory",
        "evaluation",
        "backend",
    ]

    for directory in required_directories:
        assert (root / directory).exists()


def test_data_directories():
    root = Path(__file__).resolve().parents[1]

    assert (root / "data").exists()
    assert (root / "data" / "screenshots").exists()
    assert (root / "data" / "logs").exists()
    assert (root / "data" / "database").exists()