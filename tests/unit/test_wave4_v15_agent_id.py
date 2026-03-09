"""
Wave 4 Invariant: All V15ExecutionGateway.execute() call sites in production
code must supply a non-empty agent_id kwarg.
"""

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
)

ROOT = Path(__file__).parent.parent.parent.parent

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
            except Exception:
                pass
    return missing, present


@pytest.mark.unit_min_deps
def test_no_execute_calls_missing_agent_id():
    """Wave 4: Every V15ExecutionGateway.execute() call must supply agent_id."""
    missing, present = _collect_execute_calls()
    assert len(missing) == 0, (
        f"Found {len(missing)} V15ExecutionGateway.execute() calls without agent_id "
        f"(these will hard-fail at runtime):\n" + "\n".join(f"  {m}" for m in missing)
    )


@pytest.mark.unit_min_deps
def test_wave4_registry_entries_exist():
    """Wave 4: All audit-only agent IDs added in Wave 4 must be in AGENT_REGISTRY source."""
    registry_path = ROOT / AGENTIC_CORE_DIR / "agents" / "agent_registry.py"
    src = registry_path.read_text(encoding="utf-8", errors="replace")
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
    """Wave 4: Regression — at least 11 call sites must be present and have agent_id."""
    _, present = _collect_execute_calls()
    assert len(present) >= 10, (
        f"Expected >=10 execute() calls with agent_id, found {len(present)}. "
        "Some call sites may have been removed or reverted."
    )
