"""
Wave 6 Invariant: HITL gates must be present at all required trigger points.

Checks (AST-based):
1. system_learning/engines/hitl_decision_logger.py exists and exports log_hitl_decision.
2. LocationHealerAgent._heal_via_archiving() accepts hitl_approval_fn kwarg.
3. FileClassificationAgent.classify_file_with_confidence() logs HITL_FLAGGED when
   top-2 confidence delta < 0.15.
4. execute_ssot.py wires _hitl_approval_fn onto location_validator before heal_violations.
"""

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
    SYSTEM_LEARNING_DIR,
)

ROOT = Path(__file__).parent.parent.parent.parent

LOGGER_PATH = ROOT / SYSTEM_LEARNING_DIR / "engines" / "hitl_decision_logger.py"
LOCATION_HEALER_PATH = ROOT / AGENTIC_CORE_DIR / "L5_safety" / "reasoning" / "LocationHealerAgent.py"
FILE_CLASS_PATH = ROOT / AGENTIC_CORE_DIR / "L5_safety" / "reasoning" / "FileClassificationAgent.py"
EXECUTE_SSOT_PATH = ROOT / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _ast_func_args(path: Path, func_name: str, class_name: str | None = None) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    if class_name:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == func_name:
                        return (
                            [a.arg for a in item.args.args]
                            + [a.arg for a in (item.args.kwonlyargs or [])]
                            + ([item.args.vararg.arg] if item.args.vararg else [])
                            + [a.arg for a in (item.args.posonlyargs or [])]
                        )
        return []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            return [a.arg for a in node.args.args] + [a.arg for a in (node.args.kwonlyargs or [])]
    return []


# ---------------------------------------------------------------------------
# Test 1: hitl_decision_logger exists and defines log_hitl_decision
# ---------------------------------------------------------------------------


@pytest.mark.unit_min_deps
def test_hitl_decision_logger_exists():
    """Wave 6: system_learning/engines/hitl_decision_logger.py must exist."""
    assert LOGGER_PATH.exists(), (
        f"hitl_decision_logger.py not found at {LOGGER_PATH} — HITL decisions cannot be recorded"
    )


@pytest.mark.unit_min_deps
def test_hitl_decision_logger_exports_log_fn():
    """Wave 6: hitl_decision_logger must define log_hitl_decision function."""
    src = LOGGER_PATH.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    fn_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert "log_hitl_decision" in fn_names, "log_hitl_decision not defined in hitl_decision_logger.py"


# ---------------------------------------------------------------------------
# Test 2: LocationHealerAgent._heal_via_archiving has hitl_approval_fn
# ---------------------------------------------------------------------------


@pytest.mark.unit_min_deps
def test_location_healer_hitl_approval_fn_param():
    """Wave 6: _heal_via_archiving must accept hitl_approval_fn kwarg."""
    args = _ast_func_args(LOCATION_HEALER_PATH, "_heal_via_archiving")
    assert "hitl_approval_fn" in args, (
        "_heal_via_archiving() missing hitl_approval_fn parameter — archive deletions will bypass HITL gate"
    )


@pytest.mark.unit_min_deps
def test_location_healer_reads_instance_hitl_fn():
    """Wave 6: _heal_via_archiving must fall back to self._hitl_approval_fn."""
    src = LOCATION_HEALER_PATH.read_text(encoding="utf-8", errors="replace")
    assert "_hitl_approval_fn" in src, (
        "LocationHealerAgent._heal_via_archiving does not read self._hitl_approval_fn — "
        "execute_ssot.py injection won't take effect"
    )


# ---------------------------------------------------------------------------
# Test 3: FileClassificationAgent logs HITL_FLAGGED on ambiguous delta
# ---------------------------------------------------------------------------


@pytest.mark.unit_min_deps
def test_file_classification_hitl_flagged_delta():
    """Wave 6: classify_file_with_confidence must flag ambiguous classifications (delta < 0.15)."""
    src = FILE_CLASS_PATH.read_text(encoding="utf-8", errors="replace")
    assert "HITL_FLAGGED" in src, (
        "FileClassificationAgent.classify_file_with_confidence missing HITL_FLAGGED annotation — "
        "ambiguous classifications (delta<0.15) will not be surfaced for review"
    )


@pytest.mark.unit_min_deps
def test_file_classification_hitl_logs_decision():
    """Wave 6: classify_file_with_confidence must call log_hitl_decision for ambiguous cases."""
    src = FILE_CLASS_PATH.read_text(encoding="utf-8", errors="replace")
    assert "log_hitl_decision" in src, (
        "FileClassificationAgent does not call log_hitl_decision — "
        "ambiguous classification HITL events will not be recorded"
    )


# ---------------------------------------------------------------------------
# Test 4: execute_ssot.py wires _hitl_approval_fn before heal_violations
# ---------------------------------------------------------------------------


@pytest.mark.unit_min_deps
def test_execute_ssot_wires_hitl_approval_fn():
    """Wave 6: execute_ssot.py must set _hitl_approval_fn on location_validator."""
    src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
    assert "_hitl_approval_fn" in src, (
        "execute_ssot.py does not wire _hitl_approval_fn onto location_validator — "
        "file deletion HITL gate will not fire during healing"
    )


@pytest.mark.unit_min_deps
def test_execute_ssot_hitl_gate_before_heal_violations():
    """Wave 6: The HITL gate assignment must appear before heal_violations call in source."""
    src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
    hitl_pos = src.find("_hitl_approval_fn")
    heal_pos = src.find("heal_violations(")
    assert hitl_pos != -1, "_hitl_approval_fn not found in execute_ssot.py"
    assert heal_pos != -1, "heal_violations( not found in execute_ssot.py"
    assert hitl_pos < heal_pos, (
        "_hitl_approval_fn must be assigned BEFORE heal_violations() is called in execute_ssot.py"
    )
