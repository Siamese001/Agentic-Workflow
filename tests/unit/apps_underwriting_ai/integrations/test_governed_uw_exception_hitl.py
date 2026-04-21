"""Tests for the covenant-exception HITL hook on GovernedUwException (W5 P5.2).

apps_underwriting_ai is permanently exempt from GovernedAppRunner; its HITL
integration lives on the CoreAdapter boundary, exposed via
``GovernedUwException.maybe_escalate_covenant_exception``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_control.exit_controller import (
    ExitAction,
    ExitController,
)
from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerState,
    RuntimeHitlLedger,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass
from agentic_core.L5_safety.exit_control.hitl_policy import (
    ClassPolicy,
    HitlPolicy,
)
from apps_shared.integrations.runtime_hitl_integration import (
    ENV_FLAG,
    RunStateStore,
)
from apps_underwriting_ai.integrations.governed_uw_exception import (
    GovernedUwException,
)


def _make_policy() -> HitlPolicy:
    classes: dict[HitlClass, ClassPolicy] = {
        cls: ClassPolicy(
            timeout_s=60,
            fallback="DENY",
            approver_pool=f"pool_{cls.value}",
            description=cls.value,
        )
        for cls in HitlClass
    }
    return HitlPolicy(
        version=1,
        novelty_min=0.72,
        confidence_max=0.60,
        classes=classes,
        precedence=(
            HitlClass.POLICY_OVERRIDE,
            HitlClass.REGULATED,
            HitlClass.SAFETY,
            HitlClass.FINANCIAL,
            HitlClass.NOVEL_CONTEXT,
            HitlClass.LOW_CONFIDENCE,
        ),
        policy_snapshot="uw-test",
    )


@pytest.fixture
def controller(tmp_path: Path) -> ExitController:
    return ExitController(
        policy=_make_policy(),
        ledger=RuntimeHitlLedger(tmp_path / "ledger.db"),
    )


@pytest.fixture
def run_state_store(tmp_path: Path) -> RunStateStore:
    return RunStateStore(tmp_path / "uw_runstate.db")


@pytest.fixture
def uw_handler() -> GovernedUwException:
    return GovernedUwException()


# ---------------------------------------------------------------------------
# Flag gating
# ---------------------------------------------------------------------------


class TestFlagGating:
    def test_default_env_off_returns_commit_disabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
        controller: ExitController,
        uw_handler: GovernedUwException,
    ) -> None:
        monkeypatch.delenv(ENV_FLAG, raising=False)
        result = uw_handler.maybe_escalate_covenant_exception(
            request_id="req-1",
            product_type="commercial_loan",
            decision_type="covenant_exception",
            recommended_decision="review",
            confidence_score=0.4,
            review_required=True,
            controller=controller,
        )
        assert result.enabled is False
        assert result.action is ExitAction.COMMIT


# ---------------------------------------------------------------------------
# Escalation paths
# ---------------------------------------------------------------------------


class TestCovenantExceptionEscalation:
    def test_review_required_escalates_as_policy_override(
        self,
        monkeypatch: pytest.MonkeyPatch,
        controller: ExitController,
        run_state_store: RunStateStore,
        uw_handler: GovernedUwException,
    ) -> None:
        monkeypatch.setenv(ENV_FLAG, "true")
        result = uw_handler.maybe_escalate_covenant_exception(
            request_id="req-42",
            product_type="commercial_loan",
            decision_type="covenant_exception",
            recommended_decision="approve_with_condition",
            confidence_score=0.45,
            review_required=True,
            covenant_exception_reason="DSCR below 1.10",
            controller=controller,
            run_state_store=run_state_store,
        )
        assert result.action is ExitAction.ESCALATE_HITL
        assert result.enabled is True
        # review_required=True → requires_policy_override=True → highest precedence
        assert result.hitl_class == HitlClass.POLICY_OVERRIDE.value
        assert result.approver_pool == "pool_policy_override"
        assert result.ledger_id

    def test_non_review_but_regulated_escalates_as_regulated(
        self,
        monkeypatch: pytest.MonkeyPatch,
        controller: ExitController,
        run_state_store: RunStateStore,
        uw_handler: GovernedUwException,
    ) -> None:
        monkeypatch.setenv(ENV_FLAG, "true")
        result = uw_handler.maybe_escalate_covenant_exception(
            request_id="req-43",
            product_type="retail_credit",
            decision_type="credit_decision",
            recommended_decision="approve",
            confidence_score=0.85,
            review_required=False,  # no policy override
            is_regulated=True,  # but still regulated
            is_financial=True,
            controller=controller,
            run_state_store=run_state_store,
        )
        assert result.action is ExitAction.ESCALATE_HITL
        # policy_override did not match (review_required=False) → regulated wins
        assert result.hitl_class == HitlClass.REGULATED.value

    def test_checkpoint_payload_captures_business_state(
        self,
        monkeypatch: pytest.MonkeyPatch,
        controller: ExitController,
        run_state_store: RunStateStore,
        uw_handler: GovernedUwException,
    ) -> None:
        monkeypatch.setenv(ENV_FLAG, "true")
        result = uw_handler.maybe_escalate_covenant_exception(
            request_id="req-g7",
            product_type="commercial_loan",
            decision_type="covenant_exception",
            recommended_decision="approve_with_condition",
            confidence_score=0.5,
            review_required=True,
            covenant_exception_reason="LTV > 85%",
            controller=controller,
            run_state_store=run_state_store,
            extra_checkpoint={"borrower_id": "B-99", "loan_id": "L-101"},
        )
        assert result.action is ExitAction.ESCALATE_HITL
        assert result.checkpoint is not None
        assert result.checkpoint.checkpoint_kind == "covenant_exception"

        loaded = run_state_store.load(run_id="uw-req-g7", ledger_id=result.ledger_id)
        assert loaded is not None
        assert loaded.app_name == "apps_underwriting_ai"
        # Core fields
        assert loaded.payload["request_id"] == "req-g7"
        assert loaded.payload["product_type"] == "commercial_loan"
        assert loaded.payload["covenant_exception_reason"] == "LTV > 85%"
        # Extra fields merged
        assert loaded.payload["borrower_id"] == "B-99"
        assert loaded.payload["loan_id"] == "L-101"

    def test_ledger_row_binds_regulated_envelope_fields(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        uw_handler: GovernedUwException,
    ) -> None:
        monkeypatch.setenv(ENV_FLAG, "true")
        ledger = RuntimeHitlLedger(tmp_path / "audit.db")
        controller = ExitController(policy=_make_policy(), ledger=ledger)
        result = uw_handler.maybe_escalate_covenant_exception(
            request_id="req-audit",
            product_type="commercial_loan",
            decision_type="covenant_exception",
            recommended_decision="review",
            confidence_score=0.5,
            review_required=True,
            covenant_exception_reason="minimum_liquidity_breach",
            controller=controller,
        )
        assert result.action is ExitAction.ESCALATE_HITL
        rows = ledger.list_by_run("uw-req-audit")
        assert len(rows) == 1
        row = rows[0]
        assert row.state is LedgerState.PENDING
        # Envelope persisted verbatim — domain fields recoverable for audit
        assert row.envelope["is_regulated"] is True
        assert row.envelope["is_financial"] is True
        assert row.envelope["product_type"] == "commercial_loan"
        assert row.envelope["covenant_exception_reason"] == "minimum_liquidity_breach"


# ---------------------------------------------------------------------------
# Exception-record contract preservation
# ---------------------------------------------------------------------------


class TestExceptionRecordUntouched:
    def test_hitl_hook_does_not_alter_exception_record(self, uw_handler: GovernedUwException) -> None:
        # Adding a HITL hook must not reopen the blocked layers declaration.
        rec = uw_handler.get_exception_record()
        assert rec.exception_reason_code == "regulatory_domain"
        assert "L5" in rec.blocked_layers
        # Safe layers list unchanged
        assert set(rec.safe_layers) == {
            "BUS_T_telemetry",
            "conformance_metadata",
        }

    def test_compensating_controls_still_pass(self, uw_handler: GovernedUwException) -> None:
        results = uw_handler.check_compensating_controls()
        labels = {label for label, _, _ in results}
        assert "CC-UW-01 telemetry (ObservabilityAdapter)" in labels
        assert "CC-UW-03 exception record accessible" in labels
        # All four CCs must still report a pass bit (True/False); here we
        # require CC-UW-01, CC-UW-03, CC-UW-04 true — CC-UW-02 depends on
        # module import availability and is not asserted here.
        by_label = {label: passed for label, passed, _ in results}
        assert by_label["CC-UW-01 telemetry (ObservabilityAdapter)"] is True
        assert by_label["CC-UW-03 exception record accessible"] is True
        assert by_label["CC-UW-04 review cadence declared"] is True
