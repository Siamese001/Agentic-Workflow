"""W9 — Intended E2 validation entrypoint shape (docs/tests only; no E2 refactor)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L2_execution.orchestration.l2_phase_pipeline import L2PhasePipeline
from agentic_core.L2_execution.types.l2_v3_receipts import (
    DeterminismBundle,
    LineageRoot,
    ValidationOutcome,
    ValidationReceipt,
)

REPO_ROOT = Path(__file__).resolve().parents[4]

E2_KEEP_CORE_MODULES: tuple[str, ...] = (
    "agentic_core.L2_execution.orchestration.l2_phase_pipeline",
    "agentic_core.L2_execution.enforcement.e2_validate_before_execute",
    "agentic_core.L2_execution.enforcement.e2_agent_gate",
    "agentic_core.L2_execution.enforcement.boundary_validator",
    "agentic_core.L2_execution.reasoning.authority_validator",
)

VALIDATION_ORCHESTRATOR_MODULE = (
    "agentic_core.L2_execution.reasoning.validation_orchestrator"
)


def _repo_py_files_importing(module_suffix: str) -> list[str]:
    """Static import scan — not runtime reachability proof."""
    hits: list[str] = []
    for root in (REPO_ROOT / "agentic_core", REPO_ROOT / "apps_rg", REPO_ROOT / "tests"):
        if not root.is_dir():
            continue
        for py in root.rglob("*.py"):
            if "__pycache__" in py.parts:
                continue
            try:
                tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module == module_suffix:
                    hits.append(py.relative_to(REPO_ROOT).as_posix())
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == module_suffix:
                            hits.append(py.relative_to(REPO_ROOT).as_posix())
    return sorted(set(hits))


def test_l2_phase_pipeline_documents_e2_validation_receipt() -> None:
    src = Path(L2PhasePipeline.__module__.replace(".", "/") + ".py")
    # Resolve via package path under repo
    pipeline_path = REPO_ROOT / "agentic_core" / "L2_execution" / "orchestration" / "l2_phase_pipeline.py"
    text = pipeline_path.read_text(encoding="utf-8")
    assert "E2 VALID" in text
    assert "ValidationReceipt" in text


def test_validation_receipt_type_is_sealed_e2_artifact() -> None:
    det = DeterminismBundle(
        blueprint_hash="bp-w9",
        policy_hash="pol-w9",
        prompt_hash="prompt-w9",
        input_hash="input-w9",
        replay_key="replay-w9",
        attempt_seed="seed-w9",
    )
    lin = LineageRoot(
        parent_route_id="route-w9",
        parent_plan_id="plan-w9",
        parent_step_id="step-w9",
    )
    rid = ValidationReceipt.new_id()
    receipt = ValidationReceipt(
        validation_packet_id=rid,
        prep_receipt_id="prep-test",
        outcome=ValidationOutcome.PASS,
        determinism=det,
        lineage=lin,
        rules_passed=("rule_a",),
    )
    assert receipt.validation_packet_id == rid
    assert receipt.is_approved()


def test_e2_supplemental_modules_are_importable() -> None:
    for mod in E2_KEEP_CORE_MODULES[1:]:
        __import__(mod)


def test_validation_orchestrator_has_no_python_importers_outside_self() -> None:
    importers = _repo_py_files_importing(VALIDATION_ORCHESTRATOR_MODULE)
    importers = [p for p in importers if "validation_orchestrator.py" not in p]
    assert importers == [], (
        "validation_orchestrator has non-self importers — reclassify before RETIRE:\n"
        + "\n".join(importers)
    )


def test_w9_decision_documented() -> None:
    """KEEP_CORE: l2_phase_pipeline E2; QUARANTINE_UNTIL_REVIEW: validation_orchestrator."""
    assert VALIDATION_ORCHESTRATOR_MODULE.endswith("validation_orchestrator")
    assert "l2_phase_pipeline" in E2_KEEP_CORE_MODULES[0]
