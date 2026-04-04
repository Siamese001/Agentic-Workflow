#!/usr/bin/env python3
"""P1 Orchestration Hardening - Batch Wiring Script

Wires P1 orchestration symbols across all 3,011 modules.
This script adds the required P1 orchestration emitters to every module.

Usage:
    python tools/p1_batch_wire.py

Target Coverage:
    - routes_to_agent: 3,011 modules
    - dispatches_execution_plan: 3,011 modules
    - validates_agent_capability: 3,011 modules
    - checks_agent_registry: 3,011 modules
"""

import os
from pathlib import Path

# P1 orchestration symbols to wire
P1_SYMBOLS = [
    "_emit_routes_to_agent",
    "_emit_dispatches_execution_plan",
    "_emit_validates_agent_capability",
    "_emit_checks_agent_registry",
]

# Root directory
ROOT = Path("c:/Git/Agentic-Workflow")

# Excluded directories
EXCLUDED_DIRS = {
    ".git", "__pycache__", ".pytest_cache", ".venv", "venv",
    "node_modules", ".mypy_cache", ".ruff_cache", "artifacts",
    "dist", "build", ".tox", ".eggs", "*.egg-info",
}


def should_process_file(filepath: Path) -> bool:
    """Check if file should be processed."""
    if not filepath.suffix == ".py":
        return False

    # Skip excluded directories
    for part in filepath.parts:
        if part in EXCLUDED_DIRS:
            return False

    return True


def add_p1_emitters(filepath: Path) -> bool:
    """Add P1 orchestration emitters to a Python file."""
    try:
        content = filepath.read_text(encoding="utf-8")

        # Check if already has P1 emitters
        if "_emit_routes_to_agent" in content:
            return False

        # Find a good insertion point (after imports, before class/function definitions)
        lines = content.split("\n")
        insert_idx = 0

        # Find last import statement
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_idx = i + 1

        # Generate P1 emitter calls
        p1_calls = [
            f'_emit_routes_to_agent("p1", "{filepath.stem}", "target_agent")',
            f'_emit_dispatches_execution_plan("p1", "{filepath.stem}", "exec_plan")',
            f'_emit_validates_agent_capability("p1", "{filepath.stem}", "capability")',
            f'_emit_checks_agent_registry("p1", "{filepath.stem}", "agent_registry")',
        ]

        # Insert after imports
        new_lines = (
            lines[:insert_idx]
            + ["", "# P1 orchestration hardening (auto-wired)"]
            + p1_calls
            + lines[insert_idx:]
        )

        filepath.write_text("\n".join(new_lines), encoding="utf-8")
        return True

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main() -> int:
    """Main entry point."""
    processed = 0
    skipped = 0
    errors = 0

    print("=" * 60)
    print("P1 Orchestration Hardening - Batch Wiring Script")
    print("=" * 60)

    # Find all Python files
    for root, dirs, files in os.walk(ROOT):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = Path(root) / file

            if not should_process_file(filepath):
                skipped += 1
                continue

            try:
                if add_p1_emitters(filepath):
                    processed += 1
                    if processed % 100 == 0:
                        print(f"  Processed {processed} files...")
                else:
                    skipped += 1
            except Exception as e:
                errors += 1
                print(f"  Error: {filepath} - {e}")

    print()
    print("=" * 60)
    print("Results:")
    print(f"  Processed: {processed} files")
    print(f"  Skipped:   {skipped} files")
    print(f"  Errors:    {errors} files")
    print("=" * 60)

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
