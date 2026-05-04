"""W7 HITL sentinel — X3B disposition and HITLReviewPacket structure.

Verifies:
1. HITLReviewPacket is the ONLY carrier of human decision into Exit (static).
2. runtime_author_gate.freeze() returns a HITLReviewPacket (in-process).
3. HITLReviewPacket fields match the X3B mapping spec (freeze_reason, input_manifest_hash,
   decision, l5_receipt present after freeze).
4. Trigger policy YAML declares all 6 required trigger kinds.
5. RuntimeAuthorGate does NOT directly call Exit V6 (decision of Exit hand-off is the caller's).

Plan: apps-rg-canonical-wireup-c8a4f2 W7 sentinel.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
TRIGGER_POLICY = REPO_ROOT / "apps_rg" / "config" / "hitl_trigger_policy.yaml"
GATE_FILE = REPO_ROOT / "apps_rg" / "hitl" / "runtime_author_gate.py"
REQUIRED_TRIGGER_KINDS = {
    "MISSING_BRIEF",
    "STALE_BRIEF",
    "UNSUPPORTED_CLAIM",
    "LOW_CONFIDENCE",
    "RELEASE_APPROVAL",
    "CACHE_PROMOTION",
}


@pytest.mark.governance
def test_apps_rg_hitl_trigger_policy_declares_all_six_triggers() -> None:
    """hitl_trigger_policy.yaml must declare all 6 trigger kinds."""
    assert TRIGGER_POLICY.exists(), f"hitl_trigger_policy.yaml missing: {TRIGGER_POLICY}"
    doc = yaml.safe_load(TRIGGER_POLICY.read_text(encoding="utf-8"))
    declared = {t["trigger_kind"] for t in doc.get("triggers", [])}
    missing = REQUIRED_TRIGGER_KINDS - declared
    assert not missing, (
        f"hitl_trigger_policy.yaml is missing trigger kinds: {missing}. "
        "All 6 HITL triggers must be declared."
    )


@pytest.mark.governance
def test_apps_rg_hitl_review_packet_is_exit_carrier() -> None:
    """HITLReviewPacket is the declared X3B carrier (static source check)."""
    assert GATE_FILE.exists(), f"runtime_author_gate.py missing: {GATE_FILE}"
    src = GATE_FILE.read_text(encoding="utf-8")
    assert "HITLReviewPacket(" in src, (
        "runtime_author_gate.py must construct a HITLReviewPacket as the Exit X3B carrier."
    )
    # Must NOT call Exit pipeline directly
    forbidden = ["ExitEvalPipeline(", "exit_eval_pipeline.run(", "pipeline.run("]
    found = [f for f in forbidden if f in src]
    assert not found, (
        f"runtime_author_gate.py must NOT call Exit V6 directly: {found}. "
        "Exit hand-off is the caller's responsibility."
    )


@pytest.mark.governance
def test_apps_rg_hitl_freeze_returns_review_packet(tmp_path: Path) -> None:
    """RuntimeAuthorGate.freeze() returns a HITLReviewPacket (in-process)."""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from apps_rg.hitl.hitl_schemas import (
        BoundedOption,
        HITLReviewPacket,
        HumanReviewDecision,
        make_decision_request,
    )
    from apps_rg.hitl.runtime_author_gate import RuntimeAuthorGate

    request = make_decision_request(
        trigger_kind="LOW_CONFIDENCE",
        run_id="run-x3b-test",
        input_manifest_hash="deadbeef01",
        recommendations=["Low confidence — review before release"],
        confidence_score=0.42,
        evidence_refs=[],
        bounded_options=[
            BoundedOption("APPROVE_RELEASE", "Approve", "ALLOW", is_recommended=False),
            BoundedOption("REJECT_RELEASE", "Reject", "DENY", is_recommended=True),
        ],
        replay_key="rk-x3b-test",
    )

    gate = RuntimeAuthorGate(run_dir=tmp_path)

    # Monkeypatch: replace _input to avoid TTY hang and inject a valid choice
    chosen_option_id = "REJECT_RELEASE"

    def _fake_input(_prompt: str = "") -> str:
        return chosen_option_id

    import apps_rg.hitl.cli_hitl_adapter as adapter_mod
    with patch.object(adapter_mod, "_input", side_effect=_fake_input):
        # Also patch sys.stdin.isatty to return True
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            result = gate.freeze(request)

    assert isinstance(result, HITLReviewPacket), (
        f"freeze() must return HITLReviewPacket, got {type(result)}"
    )
    assert result.freeze_reason == "LOW_CONFIDENCE"
    assert result.input_manifest_hash == "deadbeef01"
    assert isinstance(result.decision, HumanReviewDecision)
    assert result.decision.chosen_option_id == chosen_option_id
    assert result.decision.verify_hash(), "decision_hash must verify after freeze()"
    assert result.l5_receipt is not None, "l5_receipt must be attached after freeze()"


@pytest.mark.governance
def test_apps_rg_hitl_schemas_module_has_all_required_types() -> None:
    """hitl_schemas.py must export all required W7 dataclasses."""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from apps_rg.hitl import hitl_schemas
    required = [
        "RuntimeAuthorGateDecisionRequest",
        "BoundedOption",
        "HumanReviewDecision",
        "HITLReviewPacket",
        "L5ReClearanceReceipt",
        "TRIGGER_KINDS",
    ]
    missing = [r for r in required if not hasattr(hitl_schemas, r)]
    assert not missing, f"hitl_schemas.py is missing: {missing}"
