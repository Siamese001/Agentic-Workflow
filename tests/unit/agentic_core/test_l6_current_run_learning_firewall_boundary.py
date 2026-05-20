"""W10 — L6 current-run learning firewall (static contract; no runtime mutation)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agentic_core.L5_safety.runtime_gates.contracts import Disposition
from agentic_core.L5_safety.runtime_gates.g29_learning_firewall import LearningFirewallGate
from agentic_core.L5_safety.runtime_gates.contracts import GateContext
from agentic_core.runtime.contracts.future_run_promotion import FutureRunPromotionRequest
from tests.fixtures.proof_evidence.runtime_artifact_validators import (
    assert_l6_eval_no_current_run_mutation,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_g29_denies_current_run_mutation_attempt() -> None:
    gate = LearningFirewallGate()
    ctx = GateContext(
        run_id="run-w10",
        learning_signal={
            "attempts_current_run_mutation": True,
            "attempts_l4_direct_write": False,
            "run_status": "in_progress",
        },
    )
    decision = gate.evaluate(ctx)
    assert decision.disposition == Disposition.DENY
    assert decision.stop_condition_violated is True
    assert "learning_attempted_current_run_mutation" in decision.reason_codes


def test_g29_denies_l6_direct_l4_write_attempt() -> None:
    gate = LearningFirewallGate()
    ctx = GateContext(
        run_id="run-w10",
        learning_signal={
            "attempts_current_run_mutation": False,
            "attempts_l4_direct_write": True,
            "run_status": "in_progress",
        },
    )
    decision = gate.evaluate(ctx)
    assert decision.disposition == Disposition.BLOCK_COMMIT
    assert decision.stop_condition_violated is True
    assert "L6_direct_L4_write_blocked" in decision.reason_codes


def test_l6_eval_record_validator_requires_no_current_run_mutation() -> None:
    good: dict[str, Any] = {
        "is_shadow": True,
        "no_current_run_mutation_assertion": True,
        "judge_calibrated": True,
        "replay_tied": True,
        "calibration_age_days": 0,
    }
    assert_l6_eval_no_current_run_mutation(good)
    bad = dict(good)
    bad["no_current_run_mutation_assertion"] = False
    with pytest.raises(Exception, match="no_current_run_mutation"):
        assert_l6_eval_no_current_run_mutation(bad)


def test_future_run_promotion_is_post_run_only_shape() -> None:
    req = FutureRunPromotionRequest(
        promotion_request_id="pr-l6-w10",
        source_runtime_exhaust_bundle_ref="exhaust-bundle-1",
        app_id="apps_rg",
        promotion_type="exact_cache_writeback",
        target_store="r1a_exact_cache",
        target_ref="cache-key",
        policy_ref="policy-1",
        evidence_refs=("ev-1",),
        proposed_state_diff="{}",
    )
    assert req.current_run_mutation_allowed is False
    assert req.requires_uwg is True


def test_l6_shadow_eval_module_documents_post_runtime_ingest() -> None:
    ingest = REPO_ROOT / "agentic_core/L6_observability/shadow_eval/ingest.py"
    assert ingest.is_file()
    src = ingest.read_text(encoding="utf-8")
    assert "proposed_state_diff" in src or "shadow" in src.lower()
