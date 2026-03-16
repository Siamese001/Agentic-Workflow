#!/usr/bin/env python3
"""
Test Structure Auto-Fix Script

Moves misplaced test files to their correct locations based on the
Depth-3 SSOT (Single Source of Truth) requirements.

Rules:
1. Test files in tests/unit/ should be under agentic_core/, apps_rg/, apps_lic/, or apps_shared/
2. Test files in tests/integration/ should be under the same domain structure
3. Attempts to determine correct location by analyzing test content
"""

import ast
import shutil
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "fix_test_structure")
_emit_applies_guardrail("p0", "fix_test_structure", "p0_governance")
_emit_reads_policy_state("p0", "fix_test_structure", "policy_binding")
_emit_snapshots_state("p0", "fix_test_structure", "state_snapshot")
emit_replay_key("p0", "fix_test_structure")
emit_determinism_digest("p0", "fix_test_structure")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

PROJECT_ROOT = get_validated_project_root()
TESTS_ROOT = PROJECT_ROOT / TESTS_DIR


def analyze_test_imports(file_path: Path) -> str | None:
    """Analyze test file to determine which domain it belongs to based on imports."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(AGENTIC_CORE_DIR):
                        return AGENTIC_CORE_DIR
                    elif alias.name.startswith(APPS_RG_DIR):
                        return APPS_RG_DIR
                    elif alias.name.startswith(APPS_LIC_DIR):
                        return APPS_LIC_DIR
                    elif alias.name.startswith(APPS_SHARED_DIR):
                        return APPS_SHARED_DIR
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    if node.module.startswith(AGENTIC_CORE_DIR):
                        return AGENTIC_CORE_DIR
                    elif node.module.startswith(APPS_RG_DIR):
                        return APPS_RG_DIR
                    elif node.module.startswith(APPS_LIC_DIR):
                        return APPS_LIC_DIR
                    elif node.module.startswith(APPS_SHARED_DIR):
                        return APPS_SHARED_DIR
    # guardian: allow-silent-swallow
    except Exception:
        pass

    return None


def fix_test_structure():
    """Move misplaced test files to correct locations."""
    print("[AUTO-FIX] Moving misplaced test files to correct locations...")

    moved_count = 0
    error_count = 0

    # Process both unit and integration tests
    for test_type in ["unit", "integration"]:
        test_dir = TESTS_ROOT / test_type
        if not test_dir.exists():
            continue

        print(f"\n--- Processing {test_type} tests ---")

        for item in test_dir.iterdir():
            if item.is_file() and item.name.startswith("test_") and item.name.endswith(".py"):
                # Skip allowed files
                if item.name in {"__init__.py", "conftest.py"}:
                    continue

                # Determine target domain
                domain = analyze_test_imports(item)
                if not domain:
                    # Default to agentic_core if we can't determine
                    domain = AGENTIC_CORE_DIR
                    print(
                        f"  [WARNING] Could not determine domain for {item.name}, defaulting to {domain}",
                    )

                # Create target directory
                target_dir = test_dir / domain
                target_dir.mkdir(parents=True, exist_ok=True)

                # Move file
                target_path = target_dir / item.name
                try:
                    shutil.move(str(item), str(target_path))
                    print(f"  [MOVED] {item.name} -> {test_type}/{domain}/")
                    moved_count += 1
                # guardian: allow-silent-swallow
                except Exception as e:
                    print(f"  [ERROR] Could not move {item.name}: {e}")
                    error_count += 1

    print(f"\n[AUTO-FIX] Complete: {moved_count} files moved, {error_count} errors")
    return moved_count, error_count


if __name__ == "__main__":
    fix_test_structure()
