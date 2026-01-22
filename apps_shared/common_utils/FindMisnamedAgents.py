#!/usr/bin/env python3
"""
[DEPRECATED] Find files containing agent classes that don't follow *Agent.py naming.

Use scripts/full_agent_discovery.py as the canonical AST scan.
This script performs its own AST scan which may conflict with the SSOT.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

import warnings

warnings.warn(
    "find_misnamed_agents.py is DEPRECATED. Use full_agent_discovery.py instead.",
    DeprecationWarning,
    stacklevel=2,
)
import ast

    AGENTIC_CORE_DIR,
)

PROJECT_ROOT = Path(__file__).parent.parent

AGENT_SUFFIXES = {
    "Agent",
    "Handler",
    "Manager",
    "Controller",
    "Executor",
    "Validator",
    "Orchestrator",
    "Governor",
    "Enforcer",
    "Analyzer",
    "Sentinel",
}

EXCLUDE = {"Mixin", "Base", "Abstract", "Protocol"}


def has_agent_class(path: Path) -> list:
    """Return agent class names in file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except:
        return []

    agents = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if any(p in node.name for p in EXCLUDE):
                continue
            if any(node.name.endswith(s) for s in AGENT_SUFFIXES):
                agents.append(node.name)
    return agents


# Scan directories
scan_dirs = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]
misnamed = []
properly_named = 0

for d in scan_dirs:
    dir_path = PROJECT_ROOT / d
    if not dir_path.exists():
        continue
    for py_file in get_python_files(dir_path):
        if "__pycache__" in str(py_file):
            continue

        agents = has_agent_class(py_file)
        if agents:
            if "Agent" in py_file.name:
                properly_named += 1
            else:
                misnamed.append((py_file.relative_to(PROJECT_ROOT), agents))

print(f"Properly named (*Agent.py with agent classes): {properly_named}")
print(f"Misnamed (contains agents but no 'Agent' in filename): {len(misnamed)}")
print(f"\n{'=' * 60}")
print("FILES NEEDING RENAME:")
print(f"{'=' * 60}\n")

for path, classes in sorted(misnamed)[:50]:  # Show first 50
    print(f"{path}")
    print(f"  Classes: {', '.join(classes)}")
    print()

if len(misnamed) > 50:
    print(f"... and {len(misnamed) - 50} more files")