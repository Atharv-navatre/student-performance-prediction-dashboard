"""Environment file verification for the Student Performance project."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


ENV_VARIABLES: list[str] = [
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "FLASK_DEBUG",
    "API_BASE_URL",
]


def is_placeholder(value: str) -> bool:
    """Return True when a variable is empty or still uses a placeholder value."""

    return value.strip() == "" or "your_" in value


def main() -> int:
    """Load .env, report environment readiness, and exit with the required code."""

    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        print("[ERROR] .env file not found at project root")
        return 1

    load_dotenv(dotenv_path=env_path)

    ready = 0
    missing = 0

    for variable_name in ENV_VARIABLES:
        value = os.getenv(variable_name, "")
        if is_placeholder(value):
            print(f"[MISSING]  {variable_name:<16} — placeholder not replaced yet")
            missing += 1
        else:
            print(f"[SET]      {variable_name:<16} {value}")
            ready += 1

    print("=== Environment Check ===")
    print(f"Ready    : {ready}")
    print(f"Missing  : {missing}")
    print("Note: SUPABASE vars will be filled in Phase 3.")
    print("      All other vars must show [SET] to continue.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
