"""Tests for meta-learning operator — Wave 7.0.16.

Validates:
  T1) DRY_RUN produces identical audit_pack_json for same inputs.
  T2) DRY_RUN never calls apply path (monkeypatch sentinel).
  T3) APPLY requires capability_token (missing → REJECTED).
  T4) APPLY with token calls apply_meta_learning_rollout (monkeypatch capture).
  T5) Approval REJECT → decision=REJECT, no change_package/rollout, applied=False.
  T6) Non-IMPROVE verdict (candidate worse) → decision=REJECT, applied=False.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.types.v15_p2_types import SemanticClockSnapshot
from agentic_core.L2_execution.types.capability_token_types import (
    CapabilityConstraints,
    CapabilityTokenSubject,
    build_capability_token,
)
from agentic_core.L7_meta_learning.types.app_signal_types import (
    AppSignalEventArtifact,
    build_app_signal_event,
)
from apps_shared.scripts.meta_learning_operator import (
    render_meta_learning_audit_pack,
    run_meta_learning_operator,
)

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_events(
    values: Sequence[float],
    *,
    prefix: str = "msg",
) -> list[AppSignalEventArtifact]:
    """Build AppSignalEventArtifact list for operator tests."""
    return [
        build_app_signal_event(
            app_id="apps_rg",
            run_id="run_op",
            message_id=f"{prefix}_{i:03d}",
            metric_name="resume_message_response_rate",
            metric_value=v,
            semantic_clock=_CLOCK,
        )
        for i, v in enumerate(values)
    ]


def _baseline_sel(e: AppSignalEventArtifact) -> bool:
    return e.message_id.startswith("bl")


def _candidate_sel(e: AppSignalEventArtifact) -> bool:
    return e.message_id.startswith("cd")


def _common_kwargs(
    *,
    baseline_vals: list[float] | None = None,
    candidate_vals: list[float] | None = None,
    approval_decision: str = "APPROVE",
    mode: str = "DRY_RUN",
    capability_token: Any = None,
    fs_root: Path | None = None,
) -> dict[str, Any]:
    """Build common kwargs for run_meta_learning_operator."""
    bl = baseline_vals or [0.40, 0.42, 0.44]
    cd = candidate_vals or [0.50, 0.52, 0.54]
    events = _make_events(bl, prefix="bl") + _make_events(cd, prefix="cd")
    return {
        "app_id": "apps_rg",
        "metric_name": "resume_message_response_rate",
        "events": events,
        "baseline_selector": _baseline_sel,
        "candidate_selector": _candidate_sel,
        "proposer": "test_operator",
        "target_component": "routing_thresholds",
        "change_spec": {"threshold": 0.05},
        "evaluator": "offline_bench",
        "dataset_id": "ds_op",
        "approval_decision": approval_decision,
        "approval_rationale": "Operator test.",
        "rollout_strategy": "ALL_AT_ONCE",
        "canary_percent": None,
        "invariants": ["no_schema_changes"],
        "max_duration_minutes": 60,
        "rollback_on_invariant_fail": True,
        "policy_config_hash": None,
        "semantic_clock": _CLOCK,
        "mode": mode,
        "capability_token": capability_token,
        "fs_root": fs_root,
    }


def _build_token(*, permissions: list[str] | None = None):
    """Build a CapabilityTokenArtifact for tests."""
    return build_capability_token(
        semantic_clock=_CLOCK,
        subject=CapabilityTokenSubject(kind="agent", id="op_test"),
        issued_by="test_harness",
        permissions=permissions or ["FS:WRITE"],
        constraints=CapabilityConstraints(allowed_paths=("meta_control/state",), max_tool_calls=100),
    )


# ---------------------------------------------------------------------------
# T1: DRY_RUN determinism
# ---------------------------------------------------------------------------


class TestDryRunDeterminism:
    def test_dry_run_produces_identical_audit_pack_json(self) -> None:
        """Two DRY_RUN calls with same inputs produce byte-identical audit JSON."""
        kwargs = _common_kwargs()
        pack1 = run_meta_learning_operator(**kwargs)
        pack2 = run_meta_learning_operator(**kwargs)

        json1 = render_meta_learning_audit_pack(pack1)
        json2 = render_meta_learning_audit_pack(pack2)
        assert json1 == json2

        assert pack1["bundle_json"] == pack2["bundle_json"]
        assert pack1["applied"] is False
        assert pack1["apply_attempt"] is None
        assert pack1["mode"] == "DRY_RUN"


# ---------------------------------------------------------------------------
# T2: DRY_RUN never calls apply path
# ---------------------------------------------------------------------------


class TestDryRunNoApplyCall:
    def test_dry_run_never_calls_apply_functions(self, monkeypatch) -> None:
        """DRY_RUN must never invoke apply_meta_learning_rollout or apply_with_invariants."""

        def _explode_apply(*args, **kwargs):
            raise AssertionError("apply_meta_learning_rollout called in DRY_RUN")

        def _explode_inv(*args, **kwargs):
            raise AssertionError("apply_with_invariants called in DRY_RUN")

        monkeypatch.setattr(
            "apps_shared.scripts.meta_learning_operator.apply_meta_learning_rollout",
            _explode_apply,
        )
        monkeypatch.setattr(
            "apps_shared.scripts.meta_learning_operator.apply_with_invariants",
            _explode_inv,
        )

        kwargs = _common_kwargs(mode="DRY_RUN")
        pack = run_meta_learning_operator(**kwargs)
        assert pack["applied"] is False
        assert pack["apply_attempt"] is None


# ---------------------------------------------------------------------------
# T3: APPLY requires capability_token
# ---------------------------------------------------------------------------


class TestApplyRequiresToken:
    def test_apply_without_token_rejected(self, tmp_path: Path) -> None:
        """APPLY mode without capability_token is fail-closed REJECTED."""
        kwargs = _common_kwargs(mode="APPLY", fs_root=tmp_path)
        pack = run_meta_learning_operator(**kwargs)

        assert pack["applied"] is False
        assert pack["apply_attempt"] is not None
        assert pack["apply_attempt"].outcome == "REJECTED"
        assert "CAPABILITY_TOKEN" in pack["apply_attempt"].reject_reason


# ---------------------------------------------------------------------------
# T4: APPLY with token calls apply_meta_learning_rollout
# ---------------------------------------------------------------------------


class TestApplyCallsApply:
    def test_apply_with_token_calls_apply_function(self, monkeypatch, tmp_path: Path) -> None:
        """APPLY with valid token calls apply_meta_learning_rollout."""
        calls: list[dict] = []

        original_apply = None
        import apps_shared.scripts.meta_learning_operator as op_mod

        original_apply = op_mod.apply_meta_learning_rollout

        def _capture_apply(**kwargs):
            calls.append(kwargs)
            return original_apply(**kwargs)

        monkeypatch.setattr(
            "apps_shared.scripts.meta_learning_operator.apply_meta_learning_rollout",
            _capture_apply,
        )

        token = _build_token()
        kwargs = _common_kwargs(mode="APPLY", capability_token=token, fs_root=tmp_path)
        pack = run_meta_learning_operator(**kwargs)

        assert len(calls) == 1, "apply_meta_learning_rollout must be called exactly once"
        assert calls[0]["apply_mode"] == "DRY_RUN"
        assert pack["apply_attempt"] is not None


# ---------------------------------------------------------------------------
# T5: Approval REJECT path
# ---------------------------------------------------------------------------


class TestApprovalReject:
    def test_approval_reject_produces_no_apply(self) -> None:
        """Approval REJECT → decision=REJECT, no change_package/rollout, applied=False."""
        kwargs = _common_kwargs(approval_decision="REJECT")
        pack = run_meta_learning_operator(**kwargs)

        bundle = pack["bundle"]
        assert bundle.decision.decision == "REJECT"
        assert bundle.decision.deny_reason == "APPROVAL_REJECTED"
        assert bundle.change_package is None
        assert bundle.rollout_plan is None
        assert pack["applied"] is False
        assert pack["apply_attempt"] is None

        pack2 = run_meta_learning_operator(**kwargs)
        assert pack["bundle_json"] == pack2["bundle_json"]


# ---------------------------------------------------------------------------
# T6: Non-IMPROVE verdict (candidate worse than baseline)
# ---------------------------------------------------------------------------


class TestNonImproveVerdict:
    def test_candidate_worse_produces_reject(self) -> None:
        """Candidate < baseline → verdict=REGRESS → decision=REJECT, applied=False."""
        kwargs = _common_kwargs(
            baseline_vals=[0.80, 0.82, 0.84],
            candidate_vals=[0.70, 0.72, 0.74],
        )
        pack = run_meta_learning_operator(**kwargs)

        bundle = pack["bundle"]
        assert bundle.decision.decision == "REJECT"
        assert bundle.decision.deny_reason == "EVAL_VERDICT_NOT_IMPROVE"
        assert bundle.change_package is None
        assert bundle.rollout_plan is None
        assert pack["applied"] is False

        pack2 = run_meta_learning_operator(**kwargs)
        assert pack["bundle_json"] == pack2["bundle_json"]
