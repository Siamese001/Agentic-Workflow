"""
Dry-run the FileClassificationAgent to preview what file movements
the LCD+ remediation logic would perform.

Usage:
    python ops_scripts/run_lcd_dry_run.py
"""

from pathlib import Path

from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
    FileClassificationAgent,
)


def main():
    repo_root = Path(__file__).resolve().parent.parent
    agent = FileClassificationAgent(
        project_root=repo_root / "agentic_core",
        dry_run=True,
        validate_only=True,
    )
    result = agent.run()

    violations = result.get("violations", [])
    moves = result.get("moves", [])
    renames = result.get("renames", [])

    print(f"\n=== LCD+ Dry-Run Results ===")
    print(f"Violations found: {len(violations)}")
    print(f"Moves proposed:   {len(moves)}")
    print(f"Renames proposed: {len(renames)}")

    if moves:
        print(f"\n--- Proposed Moves ---")
        for m in moves[:50]:
            print(f"  {m}")

    if renames:
        print(f"\n--- Proposed Renames ---")
        for r in renames[:50]:
            print(f"  {r}")

    if violations:
        print(f"\n--- Violations ---")
        for v in violations[:50]:
            print(f"  {v}")


if __name__ == "__main__":
    main()
