"""W7 HITL sentinel — L5 re-clearance receipt source is human_review (not sovereign).

Verifies:
1. L5ReClearanceReceipt.gate_verdict_dict["grader_type"] == "human_calibrated".
2. The receipt is NOT produced with "sovereign" or "policy_rule" grader type.
3. binding_hash = sha256(decision_id + policy_hash) is correct.
4. RuntimeAuthorGate._l5_re_clear stamps HUMAN_CALIBRATED on gate_verdict_dict.
5. L5ReClearanceReceipt.compute_binding_hash is deterministic.

Plan: apps-rg-canonical-wireup-c8a4f2 W7 sentinel.
"""
from __future__ import annotations

import hashlib
import sys
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.governance
def test_apps_rg_l5_receipt_binding_hash_deterministic() -> None:
    """L5ReClearanceReceipt.compute_binding_hash is sha256(decision_id + policy_hash)."""
    from apps_rg.hitl.hitl_schemas import L5ReClearanceReceipt

    decision_id = "dec-test-001"
    policy_hash = "policyhash-abc123"
    result = L5ReClearanceReceipt.compute_binding_hash(decision_id, policy_hash)
    expected = hashlib.sha256((decision_id + policy_hash).encode()).hexdigest()
    assert result == expected


@pytest.mark.governance
def test_apps_rg_l5_receipt_binding_hash_changes_with_decision_id() -> None:
    """Different decision_id yields different binding_hash."""
    from apps_rg.hitl.hitl_schemas import L5ReClearanceReceipt

    h1 = L5ReClearanceReceipt.compute_binding_hash("d1", "ph")
    h2 = L5ReClearanceReceipt.compute_binding_hash("d2", "ph")
    assert h1 != h2


@pytest.mark.governance
def test_apps_rg_hitl_freeze_stamps_human_calibrated_on_receipt(tmp_path: Path) -> None:
    """After RuntimeAuthorGate.freeze(), l5_receipt.gate_verdict_dict["grader_type"]
    must be 'human_calibrated' — not sovereign."""
    from apps_rg.hitl.hitl_schemas import BoundedOption, make_decision_request
    from apps_rg.hitl.runtime_author_gate import RuntimeAuthorGate
    import apps_rg.hitl.cli_hitl_adapter as adapter_mod

    request = make_decision_request(
        trigger_kind="RELEASE_APPROVAL",
        run_id="run-l5-test",
        input_manifest_hash="l5hashtest",
        recommendations=["Release approval required"],
        confidence_score=0.88,
        evidence_refs=[],
        bounded_options=[
            BoundedOption("APPROVE", "Approve", "ALLOW", is_recommended=True),
            BoundedOption("REJECT", "Reject", "DENY", is_recommended=False),
        ],
        replay_key="rk-l5-test",
    )

    gate = RuntimeAuthorGate(run_dir=tmp_path)

    with patch.object(adapter_mod, "_input", return_value="APPROVE"):
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            result = gate.freeze(request)

    receipt = result.l5_receipt
    assert receipt is not None
    grader = receipt.gate_verdict_dict.get("grader_type", "")
    assert grader == "human_calibrated", (
        f"L5 re-clearance receipt must use grader_type='human_calibrated' "
        f"(not sovereign), got {grader!r}"
    )
    # Must NOT be sovereign
    assert grader != "policy_rule", "HITL re-clearance is not sovereign policy"


@pytest.mark.governance
def test_apps_rg_l5_receipt_has_required_fields(tmp_path: Path) -> None:
    """L5ReClearanceReceipt must have receipt_id, decision_id, cleared_at, policy_hash, binding_hash."""
    from apps_rg.hitl.hitl_schemas import BoundedOption, make_decision_request
    from apps_rg.hitl.runtime_author_gate import RuntimeAuthorGate
    import apps_rg.hitl.cli_hitl_adapter as adapter_mod

    request = make_decision_request(
        trigger_kind="CACHE_PROMOTION",
        run_id="run-receipt-test",
        input_manifest_hash="rcpt-hash",
        recommendations=[],
        confidence_score=0.95,
        evidence_refs=[],
        bounded_options=[
            BoundedOption("APPROVE_PROMOTION", "Approve", "L4 write via UWG", is_recommended=True),
            BoundedOption("SKIP_PROMOTION", "Skip", "No write", is_recommended=False),
        ],
        replay_key="rk-rcpt-test",
    )
    gate = RuntimeAuthorGate(run_dir=tmp_path)

    with patch.object(adapter_mod, "_input", return_value="APPROVE_PROMOTION"):
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            result = gate.freeze(request)

    receipt = result.l5_receipt
    assert receipt is not None
    for field in ("receipt_id", "decision_id", "cleared_at", "policy_hash", "binding_hash"):
        assert getattr(receipt, field, None), (
            f"L5ReClearanceReceipt missing or empty field: {field!r}"
        )
