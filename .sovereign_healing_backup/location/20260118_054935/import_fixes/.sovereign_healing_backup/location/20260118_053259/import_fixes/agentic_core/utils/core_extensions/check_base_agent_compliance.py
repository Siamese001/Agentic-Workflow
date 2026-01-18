#!/usr/bin/env python3
"""
Pre-commit hook script for Phase 5 base class compliance enforcement.

Purpose: Git pre-commit hook to block commits if any agent does not inherit
         from the correct layer-specific base class (Phase 5 enforcement).

Usage:
- Place in .git/hooks/pre-commit (or symlink)
- Or integrate via pre-commit framework (recommended)

Requires: Python 3.8+, ast module (standard library)
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately


import ast
import sys
from pathlib import Path

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

# Layer to expected base class mapping (SSOT - update if layers change)
LAYER_BASE_MAP = {
    "L0": "MaintenanceBaseAgent",
    "L1": "L1CognitionBaseAgent",
    "L2": "L2ExecutionBaseAgent",
    "L3": "L3OrchestrationBaseAgent",
    "L4": "L4StateBaseAgent",
    "L5": "L5SafetyBaseAgent",
}

# Root project path - adjust if hook runs from different cwd
PROJECT_ROOT = Path(__file__).parent.parent.parent

def detect_layer(file_path: Path) -> str:
    """Detect layer from file path (L0-L5)."""
    relative = file_path.relative_to(PROJECT_ROOT)
    parts = relative.parts
    for part in parts:
        if part.startswith("L") and part[1:].isdigit() and len(part) == 2:
            return part
    return "UNKNOWN"

def get_base_names(node: ast.ClassDef) -> list:
    """Extract base class names from ClassDef node."""
    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(base.attr)
    return bases

def check_file(file_path: Path) -> tuple:
    """Check single file for proper base class inheritance."""
    layer = detect_layer(file_path)
    if layer == "UNKNOWN" or layer not in LAYER_BASE_MAP:
        return True, "Skip non-agent file"
    
    expected_base = LAYER_BASE_MAP[layer]
    
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"Parse error: {e}"
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
            bases = get_base_names(node)
            if expected_base not in bases:
                return False, f"{file_path}: {node.name} missing {expected_base} (found {bases})"
    
    return True, "OK"

def main() -> int:
    """Pre-commit entrypoint - check staged Python files."""
    from subprocess import check_output
    
    # Get staged .py files
    try:
        staged = check_output(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]).decode().strip().splitlines()
    except Exception:
        print("Error: Not a git repo or no staged files")
        return 1
    
    python_files = [Path(p) for p in staged if p.endswith(".py") and AGENTIC_CORE_DIR in p]
    
    failures = []
    for file_path in python_files:
        ok, msg = check_file(PROJECT_ROOT / file_path)
        if not ok:
            failures.append(msg)
    
    if failures:
        print("\n❌ BASE CLASS COMPLIANCE FAILED (Phase 5 enforcement)\n")
        for failure in failures:
            print(f"   {failure}")
        print("\nFix: Ensure agent inherits from correct layer base (see LAYER_BASE_MAP)")
        return 1
    
    print("✓ All staged agents comply with base class hierarchy")
    return 0

if __name__ == "__main__":
    sys.exit(main())