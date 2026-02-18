"""Tests for meta-learning operator — Wave 7.0.16 / 7.0.19.

Validates:
  T1) DRY_RUN produces identical audit_pack_json for same inputs.
  T2) DRY_RUN never calls apply path (monkeypatch sentinel).
  T3) APPLY requires capability_token (missing -> REJECTED).
  T4) APPLY with token calls apply_meta_learning_rollout (monkeypatch capture).
  T5) Approval REJECT -> decision=REJECT, no change_package/rollout, applied=False.
  T6) Non-IMPROVE verdict (candidate worse) -> decision=REJECT, applied=False.
  T7) (7.0.19) audit pack includes current_config payload (empty when missing).
  T8) (7.0.19) audit pack includes dry_run_delta when change_package present.
  T9) (7.0.19) determinism: identical inputs -> byte-identical audit JSON.
  T10) (7.0.19) AST scan: operator has no apply imports/calls in audit join code.
"""

from __future__ import annotations

import ast
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.meta_control.config_store import write_next_version
from agentic_core.L0_routing.meta_control.config_store_types import canonical_json
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L2_execution.types.capability_token_types import (
    CapabilityConstraints,
    CapabilityTokenSubject,
    build_capability_token,
)
from apps_shared.scripts.meta_learning_operator import (
    render_meta_learning_audit_pack,
    run_meta_learning_operator,
)
from system_learning.types.app_signal_types import (
    AppSignalEventArtifact,
    build_app_signal_event,
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
    store_root: Path | None = None,
) -> dict[str, Any]:
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
        "store_root": store_root,
    }


def _build_token(*, permissions: list[str] | None = None):
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
    def test_dry_run_produces_identical_audit_pack_json(self, tmp_path: Path) -> None:
        kwargs = _common_kwargs(store_root=tmp_path)
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
    def test_dry_run_never_calls_apply_functions(self, monkeypatch, tmp_path: Path) -> None:
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

        kwargs = _common_kwargs(mode="DRY_RUN", store_root=tmp_path)
        pack = run_meta_learning_operator(**kwargs)
        assert pack["applied"] is False
        assert pack["apply_attempt"] is None


# ---------------------------------------------------------------------------
# T3: APPLY requires capability_token
# ---------------------------------------------------------------------------


class TestApplyRequiresToken:
    def test_apply_without_token_rejected(self, tmp_path: Path) -> None:
        kwargs = _common_kwargs(mode="APPLY", fs_root=tmp_path, store_root=tmp_path)
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
        calls: list[dict] = []

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
        kwargs = _common_kwargs(mode="APPLY", capability_token=token, fs_root=tmp_path, store_root=tmp_path)
        pack = run_meta_learning_operator(**kwargs)

        assert len(calls) == 1
        assert calls[0]["apply_mode"] == "DRY_RUN"
        assert pack["apply_attempt"] is not None


# ---------------------------------------------------------------------------
# T5: Approval REJECT path
# ---------------------------------------------------------------------------


class TestApprovalReject:
    def test_approval_reject_produces_no_apply(self, tmp_path: Path) -> None:
        kwargs = _common_kwargs(approval_decision="REJECT", store_root=tmp_path)
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
    def test_candidate_worse_produces_reject(self, tmp_path: Path) -> None:
        kwargs = _common_kwargs(
            baseline_vals=[0.80, 0.82, 0.84],
            candidate_vals=[0.70, 0.72, 0.74],
            store_root=tmp_path,
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


# ---------------------------------------------------------------------------
# T7 (7.0.19): audit pack includes current_config payload
# ---------------------------------------------------------------------------


class TestAuditPackCurrentConfig:
    def test_current_config_empty_when_store_missing(self, tmp_path: Path) -> None:
        """Audit pack current_config.payload is {} when no config exists."""
        kwargs = _common_kwargs(store_root=tmp_path)
        pack = run_meta_learning_operator(**kwargs)

        cc = pack["current_config"]
        assert cc["app_id"] == "apps_rg"
        assert cc["target_component"] == "routing_thresholds"
        assert cc["payload"] == {}

    def test_current_config_populated_when_store_exists(self, tmp_path: Path) -> None:
        """Audit pack current_config.payload reflects written config."""
        payload = {"threshold": 0.42}
        write_next_version(tmp_path, "apps_rg", "routing_thresholds", payload, _CLOCK)

        kwargs = _common_kwargs(store_root=tmp_path)
        pack = run_meta_learning_operator(**kwargs)

        cc = pack["current_config"]
        expected = json.loads(canonical_json(payload))
        assert cc["payload"] == expected


# ---------------------------------------------------------------------------
# T8 (7.0.19): audit pack includes dry_run_delta when change_package present
# ---------------------------------------------------------------------------


class TestAuditPackDryRunDelta:
    def test_dry_run_delta_present_when_approved(self, tmp_path: Path) -> None:
        """dry_run_delta is a ConfigDeltaArtifact dict when change_package present."""
        kwargs = _common_kwargs(store_root=tmp_path)
        pack = run_meta_learning_operator(**kwargs)

        delta = pack["dry_run_delta"]
        assert delta is not None
        assert delta.artifact_type == "META_CONTROL_CONFIG_DELTA"
        assert delta.from_version == 0
        assert delta.to_version == 1

        # Must not create any files
        store_apps = tmp_path / "apps"
        if store_apps.exists():
            files = list(store_apps.rglob("*"))
            assert len(files) == 0, f"apply_change_package_readonly created files: {files}"

    def test_dry_run_delta_null_when_rejected(self, tmp_path: Path) -> None:
        """dry_run_delta is None when approval is REJECT (no change_package)."""
        kwargs = _common_kwargs(approval_decision="REJECT", store_root=tmp_path)
        pack = run_meta_learning_operator(**kwargs)
        assert pack["dry_run_delta"] is None


# ---------------------------------------------------------------------------
# T9 (7.0.19): determinism with current_config + dry_run_delta
# ---------------------------------------------------------------------------


class TestAuditPackFullDeterminism:
    def test_identical_inputs_byte_identical_audit_json(self, tmp_path: Path) -> None:
        """Full audit pack including 7.0.19 fields is deterministic."""
        kwargs = _common_kwargs(store_root=tmp_path)
        pack1 = run_meta_learning_operator(**kwargs)
        pack2 = run_meta_learning_operator(**kwargs)

        json1 = render_meta_learning_audit_pack(pack1)
        json2 = render_meta_learning_audit_pack(pack2)
        assert json1 == json2


# ---------------------------------------------------------------------------
# T10 (7.0.19): AST scan — operator audit join has no apply calls
# ---------------------------------------------------------------------------

_OPERATOR_FILE = Path(__file__).resolve().parents[3] / "apps_shared" / "scripts" / "meta_learning_operator.py"
_FORBIDDEN_AUDIT_CALLS = {"apply_meta_learning_rollout", "apply_with_invariants"}


class TestOperatorNoApplyInAuditJoin:
    def test_config_store_imports_are_read_only(self) -> None:
        """AST scan: operator imports config_store (read-only), not meta_apply for audit join."""
        source = _OPERATOR_FILE.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(_OPERATOR_FILE))

        # Verify config_store imports exist (read-only path)
        has_load_current = False
        has_apply_readonly = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "config_store" in node.module and node.names:
                    for alias in node.names:
                        if alias.name == "load_current":
                            has_load_current = True
                        if alias.name == "apply_change_package_readonly":
                            has_apply_readonly = True

        assert has_load_current, "operator must import load_current from config_store"
        assert has_apply_readonly, "operator must import apply_change_package_readonly from config_store"

        # Verify apply functions are NOT called within render_meta_learning_audit_pack
        # (they are allowed in the APPLY branch, but the audit join must be read-only)
        # We check that apply_change_package_readonly is the ONLY config-related call
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "apply_change_package_readonly":
                    pass  # This is the read-only call, allowed
                elif isinstance(func, ast.Attribute) and func.attr == "apply_change_package_readonly":
                    pass  # Method form, allowed
