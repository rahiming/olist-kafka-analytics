import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT / "README.md",
    ROOT / "pyproject.toml",
    ROOT / "docker-compose.yml",
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / "producer" / "producer.py",
    ROOT / "processor" / "processor.py",
    ROOT / "dashboard" / "dashboard.py",
    ROOT / "tests" / "test_producer.py",
    ROOT / "tests" / "test_processor.py",
    ROOT / "tests" / "test_dashboard.py",
]

REQUIRED_DIRS = [
    ROOT / "producer",
    ROOT / "processor",
    ROOT / "dashboard",
    ROOT / "tests",
    ROOT / "scripts",
    ROOT / ".github" / "workflows",
]

FORBIDDEN_TRACKED_PATHS = {
    ".venv",
    "output/stats.json",
}

FORBIDDEN_SUFFIXES = [
    ".csv",
    "Zone.Identifier",
]


def get_tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    errors: list[str] = []

    for path in REQUIRED_DIRS:
        if not path.is_dir():
            errors.append(f"Missing required directory: {path.relative_to(ROOT)}")

    for path in REQUIRED_FILES:
        if not path.is_file():
            errors.append(f"Missing required file: {path.relative_to(ROOT)}")

    for file_path in get_tracked_files():
        normalized = file_path.as_posix()
        if normalized in FORBIDDEN_TRACKED_PATHS:
            errors.append(f"Generated artifact should not be committed: {normalized}")
        if any(normalized.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
            errors.append(f"Forbidden tracked file detected: {normalized}")

    if errors:
        print("Repository structure check failed:")
        for error in errors:
            safe_error = error.encode("ascii", errors="backslashreplace").decode("ascii")
            print(f"- {safe_error}")
        return 1

    print("Repository structure check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
