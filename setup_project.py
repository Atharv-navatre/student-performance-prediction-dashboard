"""Project scaffold creator for the Student Performance Dashboard."""

from __future__ import annotations

from pathlib import Path


DIRECTORIES: tuple[Path, ...] = (
    Path("data/raw"),
    Path("data/processed"),
    Path("ml"),
    Path("database"),
    Path("api"),
    Path("dashboard"),
    Path("dashboard/pages"),
    Path("dashboard/components"),
    Path("exports"),
    Path("tests"),
    Path("ml/saved_models"),
)

PACKAGE_DIRECTORIES: tuple[Path, ...] = (
    Path("ml"),
    Path("database"),
    Path("api"),
    Path("dashboard"),
    Path("tests"),
)


def collect_existing_paths(root: Path) -> set[Path]:
    """Return all paths that already exist beneath the project root."""

    return {path.resolve() for path in root.rglob("*")}


def ensure_directories(root: Path) -> None:
    """Create the required project directories if they do not already exist."""

    for directory in DIRECTORIES:
        (root / directory).mkdir(parents=True, exist_ok=True)


def ensure_init_files(root: Path) -> None:
    """Create package initializer files with the required single-line comment."""

    for package_dir in PACKAGE_DIRECTORIES:
        init_file = root / package_dir / "__init__.py"
        init_file.write_text(
            f"# {package_dir.name} package\n",
            encoding="utf-8",
        )


def iter_project_paths(root: Path) -> list[Path]:
    """Return a sorted list of every file and directory in the project tree."""

    return sorted(
        root.rglob("*"),
        key=lambda path: (path.relative_to(root).as_posix().count("/"), path.relative_to(root).as_posix()),
    )


def print_status_report(root: Path, existing_paths: set[Path]) -> None:
    """Print the current project tree with CREATED or EXISTS status labels."""

    for path in iter_project_paths(root):
        status = "[EXISTS]" if path.resolve() in existing_paths else "[CREATED]"
        relative_path = path.relative_to(root).as_posix()
        print(f"{status} {relative_path}")


def main() -> None:
    """Create the required scaffold and print a full status report."""

    project_root = Path(__file__).resolve().parent
    existing_paths = collect_existing_paths(project_root)

    ensure_directories(project_root)
    ensure_init_files(project_root)
    print_status_report(project_root, existing_paths)
    print("=== Phase 1 Step 1 Complete ===")


if __name__ == "__main__":
    main()
