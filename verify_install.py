"""Dependency verification script for the project requirements."""

from __future__ import annotations

from importlib import import_module
from importlib.metadata import PackageNotFoundError, version as package_version
from typing import Final


PACKAGE_SPECS: Final[list[tuple[str, str, str | None]]] = [
    ("pandas", "pandas", "__version__"),
    ("numpy", "numpy", "__version__"),
    ("sklearn", "scikit-learn", "__version__"),
    ("xgboost", "xgboost", "__version__"),
    ("joblib", "joblib", "__version__"),
    ("matplotlib", "matplotlib", "__version__"),
    ("seaborn", "seaborn", "__version__"),
    ("plotly", "plotly", "__version__"),
    ("streamlit", "streamlit", "__version__"),
    ("scipy", "scipy", "__version__"),
    ("supabase", "supabase", "__version__"),
    ("flask", "flask", "__version__"),
    ("flask_cors", "flask-cors", "__version__"),
    ("dotenv", "python-dotenv", "__version__"),
    ("requests", "requests", "__version__"),
    ("reportlab", "reportlab", "__version__"),
    ("pytest", "pytest", "__version__"),
]


def resolve_version(module: object, pip_name: str, version_attr: str | None) -> str:
    """Resolve a package version from the module or package metadata."""

    if version_attr:
        module_version = getattr(module, version_attr, None)
        if isinstance(module_version, str) and module_version.strip():
            return module_version

    try:
        return package_version(pip_name)
    except PackageNotFoundError:
        return "unknown"


def verify_package(import_name: str, pip_name: str, version_attr: str | None) -> tuple[bool, str]:
    """Import a package and return its verification status and version text."""

    try:
        module = import_module(import_name)
    except ImportError:
        return False, f"[FAIL] {import_name:<14} — not installed (run: pip install {pip_name})"

    version_text = resolve_version(module, pip_name, version_attr)
    return True, f"[OK]   {import_name:<14} {version_text}"


def main() -> int:
    """Verify that every required dependency is importable."""

    passed = 0
    failed = 0

    for import_name, pip_name, version_attr in PACKAGE_SPECS:
        is_installed, message = verify_package(import_name, pip_name, version_attr)
        print(message)
        if is_installed:
            passed += 1
        else:
            failed += 1

    print("=== Install Verification ===")
    print(f"Passed : {passed}")
    print(f"Failed : {failed}")
    if failed == 0:
        print("Result : ALL DEPENDENCIES READY")
        return 0

    print(f"Result : {failed} PACKAGES MISSING — install them before continuing")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
