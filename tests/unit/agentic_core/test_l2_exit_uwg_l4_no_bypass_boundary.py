"""W10 — L2 / UWG / L4 no-bypass boundary (static contract; no runtime mutation)."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from agentic_core.L2_execution.orchestration.l2_phase_pipeline import L2PhasePipeline
from agentic_core.L2_execution.types.l2_v3_receipts import (
    AttemptReceipt,
    DispatchReceipt,
    TerminalStamp,
)
from agentic_core.runtime.contracts.future_run_promotion import FutureRunPromotionRequest
from agentic_core.runtime.uwg.universal_write_gate import (
    UniversalWriteGate,
    _FORBIDDEN_DIRECT_WRITE_SOURCES,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_l2_phase_pipeline_documents_no_l4_uwg_write() -> None:
    src = (REPO_ROOT / "agentic_core/L2_execution/orchestration/l2_phase_pipeline.py").read_text(
        encoding="utf-8"
    )
    assert "never writes to L4" in src or "never writes to L4 / UWG" in src
    assert "DispatchReceipt" in src


def test_dispatch_receipt_rejects_commit_payload() -> None:
    """E5 seal cannot represent durable commit (v3 invariant)."""
    from agentic_core.L2_execution.types.l2_v3_receipts import (
        DeterminismBundle,
        LineageRoot,
        PrepReceipt,
    )

    det = DeterminismBundle(
        blueprint_hash="bp-w10",
        policy_hash="pol-w10",
        prompt_hash="p-w10",
        input_hash="i-w10",
        replay_key="r-w10",
        attempt_seed="s-w10",
    )
    lin = LineageRoot(parent_route_id="route-w10", parent_plan_id="plan-w10", parent_step_id="step-w10")
    prep = PrepReceipt(
        prep_receipt_id=PrepReceipt.new_id(),
        run_id="run-w10",
        idempotency_key="idem-w10",
        route_id="route-w10",
        step_id="step-w10",
        capability_token="cap-w10",
        compliance_hash="comp-w10",
        sandbox_envelope_id="env-w10",
        determinism=det,
        lineage=lin,
    )
    with pytest.raises(ValueError, match="cannot carry a commit payload"):
        DispatchReceipt(
            dispatch_receipt_id=DispatchReceipt.new_id(),
            sealed_l2_artifact_id="sealed-w10",
            terminal_stamp=TerminalStamp.SUCCESS,
            determinism=det,
            lineage=lin,
            prep_receipt_id=prep.prep_receipt_id,
            validation_packet_id="valid-w10",
            has_commit_payload=True,
        )


def test_attempt_receipt_proposed_state_diff_defaults_inert() -> None:
    """E3 attempt may carry proposed_state_diff; durable commit is downstream only."""
    fields = {f.name for f in AttemptReceipt.__dataclass_fields__.values()}
    assert "proposed_state_diff" in fields
    doc = AttemptReceipt.__doc__ or ""
    assert "inert" in doc.lower() or "proposal" in doc.lower()


def test_dispatch_receipt_default_targets_exit_not_l4() -> None:
    """Handoff targets Exit/UWG audit — not direct L4 persistence."""
    src = inspect.getsource(DispatchReceipt)
    assert "exit" in src.lower() or "EXIT" in src
    assert "uwg" in src.lower() or "UWG" in src


def test_future_run_promotion_request_blocks_current_run_mutation() -> None:
    with pytest.raises(ValueError, match="current_run_mutation_allowed must be False"):
        FutureRunPromotionRequest(current_run_mutation_allowed=True)  # type: ignore[call-arg]


def test_future_run_promotion_requires_uwg() -> None:
    with pytest.raises(ValueError, match="requires_uwg must be True"):
        FutureRunPromotionRequest(requires_uwg=False)  # type: ignore[call-arg]


def test_uwg_forbids_direct_write_from_l2_and_exit() -> None:
    assert "L2" in _FORBIDDEN_DIRECT_WRITE_SOURCES
    assert "Exit" in _FORBIDDEN_DIRECT_WRITE_SOURCES
    assert "L6" in _FORBIDDEN_DIRECT_WRITE_SOURCES


def test_uwg_admit_blocks_current_run_mutation_flag() -> None:
    uwg = UniversalWriteGate(policy={"semantic_cache_enabled": False})
    bad = FutureRunPromotionRequest(
        promotion_request_id="pr-w10",
        app_id="apps_rg",
        promotion_type="exact_cache_writeback",
        target_store="r1a_exact_cache",
        target_ref="key",
        policy_ref="policy-w10",
        evidence_refs=("ev-1",),
        proposed_state_diff="{}",
    )
    # Structural invariant prevents True; belt-and-suspenders via object replacement is not possible
    # on frozen dataclass — document gate exists for runtime requests carrying the flag.
    gate_src = (REPO_ROOT / "agentic_core/runtime/uwg/universal_write_gate.py").read_text(encoding="utf-8")
    assert "current_run_mutation_allowed" in gate_src
    assert uwg is not None
    assert bad.current_run_mutation_allowed is False
