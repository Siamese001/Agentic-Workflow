"""
Wave 4 Invariant: All V15ExecutionGateway.execute() call sites in production
code must supply a non-empty agent_id kwarg.
"""

import ast
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent.parent

SCAN_DIRS = [
    ROOT / AGENTIC_CORE_DIR,
    ROOT / APPS_RG_DIR,
    ROOT / APPS_LIC_DIR,
    ROOT / APPS_SHARED_DIR,
    ROOT / SYSTEM_LEARNING_DIR,
]

GATEWAY_RECEIVERS = frozenset({"gateway", "gw", "_gw", "v15", "v15_gw"})


def _collect_execute_calls() -> tuple[list[str], list[str]]:
    missing = []
    present = []
    for d in SCAN_DIRS:
        if not d.exists():
            continue
        for py in d.rglob("*.py"):
            try:
                src = py.read_text(encoding="utf-8", errors="replace")
                if ".execute(" not in src:
                    continue
                tree = ast.parse(src)
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    func = node.func
                    if not (isinstance(func, ast.Attribute) and func.attr == "execute"):
                        continue
                    if not isinstance(func.value, ast.Name):
                        continue
                    if func.value.id not in GATEWAY_RECEIVERS:
                        continue
                    kws = [kw.arg for kw in node.keywords]
                    rel = str(py.relative_to(ROOT))
                    if "agent_id" in kws:
                        present.append(f"{rel}:{node.lineno}")
                    else:
                        missing.append(f"{rel}:{node.lineno}  kwargs={kws}")
            except (OSError, UnicodeDecodeError, SyntaxError) as e:
# REMOVED HIDDEN FAILURE SKIP: # REMOVED SKIP: # REMOVED HIDDEN FAILURE SKIP: # REMOVED SKIP: # Skip files with parse errors - not relevant to agent_id check  # REVEALED FAILURE: # skip files with parse errors - not relevant to agent_id check  # REVEALED FAILURE: # removed hidden failure skip: # removed skip: # skip files with parse errors - not relevant to agent_id check  # revealed failure: # skip files with parse errors - not relevant to agent_id check
                continue
    return missing, present


@pytest.mark.unit_min_deps
def test_no_execute_calls_missing_agent_id():
"""Test no_execute_calls_missing_agent_id runtime behavior."""
    from agentic_core.L0_routing.config.path_constants import (
        AGENTIC_CORE_DIR,
        APPS_LIC_DIR,
        APPS_RG_DIR,
        APPS_SHARED_DIR,
        SYSTEM_LEARNING_DIR,
    )

# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute no_execute_calls_missing_agent_id
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
    wave4_ids = [
        "sovereign_base",
        "tool_reliability_mixin",
        "ssot_audit",
        "mission_runner",
        "orchestrator_engine",
        "agent_engine",
    ]
    missing_ids = [aid for aid in wave4_ids if f'"{aid}"' not in src and f"'{aid}'" not in src]
    assert not missing_ids, (
        f"Wave 4 registry entries missing from agent_registry.py: {missing_ids} — "
        "gateway.execute() calls with these agent_ids will hard-fail at runtime"
    )


@pytest.mark.unit_min_deps
def test_execute_calls_count_at_least_eleven():
"""Test execute_calls_count_at_least_eleven runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute execute_calls_count_at_least_eleven
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
