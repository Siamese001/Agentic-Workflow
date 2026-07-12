"""Focused tests for the deterministic SVP documentation review gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import svp_docs_review as mod  # noqa: E402


def _x1d(decision: str = "ALLOW") -> dict[str, object]:
    return {
        "schema_version": "svp_docs_x1d/v1",
        "decision": decision,
        "blocking_findings": [],
    }


def test_audit_with_material_change_is_plan_only() -> None:
    receipt = mod._x3_disposition(
        run_id="run-1",
        mode="audit",
        phase="pre",
        x2_decision="ALLOW",
        x1d=_x1d(),
        changed=["README.md"],
        approval_receipt=None,
        prior_x2="NOT_RUN",
        implementation_change=False,
    )

    assert receipt["decision"] == "PLAN_ONLY"
    assert receipt["publication_authorized"] is False
    assert receipt["publication_handoff"] is None


def test_clean_audit_is_noop() -> None:
    receipt = mod._x3_disposition(
        run_id="run-2",
        mode="audit",
        phase="pre",
        x2_decision="ALLOW",
        x1d=_x1d(),
        changed=[],
        approval_receipt=None,
        prior_x2="NOT_RUN",
        implementation_change=False,
    )

    assert receipt["decision"] == "NOOP"
    assert receipt["publication_authorized"] is False


def test_post_edit_allow_hands_off_to_pr_publisher(tmp_path: Path) -> None:
    approval = tmp_path / "approval.json"
    approval.write_text(
        json.dumps(
            {
                "schema_version": "svp_docs_approval/v1",
                "status": "APPROVED",
                "plan_id": "svp-docs-gate-hardening-7c4e2a",
                "approved_by": "test",
                "approved_at": "2026-07-12T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )

    receipt = mod._x3_disposition(
        run_id="run-3",
        mode="edit",
        phase="post",
        x2_decision="ALLOW",
        x1d=_x1d("WARN"),
        changed=["README.md"],
        approval_receipt=approval,
        prior_x2="ALLOW",
        implementation_change=False,
    )

    assert receipt["decision"] == "ALLOW_TO_PR"
    assert receipt["publication_authorized"] is True
    assert receipt["publication_handoff"] == "on-demand-pr-main-publisher"


def test_high_severity_x1d_finding_blocks() -> None:
    x1d = _x1d()
    x1d["blocking_findings"] = [{"severity": "high"}]

    receipt = mod._x3_disposition(
        run_id="run-4",
        mode="edit",
        phase="post",
        x2_decision="ALLOW",
        x1d=x1d,
        changed=["README.md"],
        approval_receipt=None,
        prior_x2="ALLOW",
        implementation_change=False,
    )

    assert receipt["decision"] == "BLOCK"


def test_docs_only_scope_blocks_runtime_code() -> None:
    gate = mod._docs_only_gate(["README.md", "agentic_core/runtime.py"], implementation_change=False)

    assert gate.status == "FAIL"
    assert "agentic_core/runtime.py" in gate.evidence


def test_docs_only_scope_is_not_applicable_for_gate_implementation() -> None:
    gate = mod._docs_only_gate(["scripts/governance/svp_docs_review.py"], implementation_change=True)

    assert gate.status == "NOT_APPLICABLE"


def test_shallow_schema_requires_fields_and_const() -> None:
    schema = {
        "required": ["schema_version", "decision"],
        "properties": {
            "schema_version": {"const": "svp_docs_x3/v1"},
            "decision": {"enum": ["ALLOW_TO_PR", "BLOCK"]},
        },
    }

    assert mod._validate_shallow_schema(schema, {"schema_version": "svp_docs_x3/v1", "decision": "BLOCK"}) == []
    errors = mod._validate_shallow_schema(schema, {"schema_version": "wrong"})
    assert any("missing required field decision" in error for error in errors)
    assert any("expected 'svp_docs_x3/v1'" in error for error in errors)


def test_x2_gate_order_is_complete() -> None:
    assert len(mod.X2_GATE_IDS) == 18
    assert mod.X2_GATE_IDS[0] == "x2_toml_parse"
    assert mod.X2_GATE_IDS[-1] == "x2_no_absolute_unproven_language"
