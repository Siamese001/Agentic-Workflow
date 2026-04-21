"""Tests for the HITL hook in GovernedAppRunner.run_governed_core (W5).

Focuses on the _maybe_escalate_hitl wiring and threading of fields into
GovernedAppRunRecord. The shared-base pipeline itself is covered elsewhere —
these tests call the hook directly and exercise the record contract.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_control.exit_controller import (
    ExitAction,
    ExitController,
)
from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    RuntimeHitlLedger,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass
from agentic_core.L5_safety.exit_control.hitl_policy import (
    ClassPolicy,
    HitlPolicy,
)
from apps_shared.integrations.governed_app_runner import (
    GovernedAppRunner,
    GovernedAppRunRecord,
)
from apps_shared.integrations.runtime_hitl_integration import (
    ENV_FLAG,
    HitlResult,
    RunStateStore,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


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
        policy_snapshot="test",
    )


class _LicLikeRunner(GovernedAppRunner):
    APP_NAME = "apps_lic"
    CAPABILITY_TOKEN = "apps_lic.governed_e2e.v1"
    ROUTING_TARGET = "lic_campaign_assembly"
    ROUTING_KEYWORDS = ["campaign"]
    HITL_ENABLED = True


class _DisabledRunner(GovernedAppRunner):
    APP_NAME = "apps_disabled"
    CAPABILITY_TOKEN = "apps_disabled.v1"
    ROUTING_TARGET = "disabled_target"
    ROUTING_KEYWORDS = ["x"]
    HITL_ENABLED = False


@pytest.fixture
def policy() -> HitlPolicy:
    return _make_policy()


@pytest.fixture
def controller(policy: HitlPolicy, tmp_path: Path) -> ExitController:
    return ExitController(
        policy=policy,
        ledger=RuntimeHitlLedger(tmp_path / "ledger.db"),
    )


@pytest.fixture
def run_state_store(tmp_path: Path) -> RunStateStore:
    return RunStateStore(tmp_path / "runstate.db")


# ---------------------------------------------------------------------------
# Class attribute contract
# ---------------------------------------------------------------------------


class TestClassAttributeContract:
    def test_default_runner_hitl_disabled(self) -> None:
        assert GovernedAppRunner.HITL_ENABLED is False

    def test_subclass_can_opt_in(self) -> None:
        assert _LicLikeRunner.HITL_ENABLED is True

    def test_subclass_can_opt_out(self) -> None:
        assert _DisabledRunner.HITL_ENABLED is False


# ---------------------------------------------------------------------------
# _maybe_escalate_hitl wiring
# ---------------------------------------------------------------------------


class TestMaybeEscalateHitlHook:
    def test_flag_off_returns_commit_disabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
        controller: ExitController,
    ) -> None:
        monkeypatch.delenv(ENV_FLAG, raising=False)
        runner = _LicLikeRunner(collection="lic_docs")
        runner._hitl_controller = controller  # type: ignore[assignment]
        result = runner._maybe_escalate_hitl(  # pylint: disable=protected-access
            run_id="r",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=1,
            support_coverage=0.9,
            disposition="strong_support",
        )
        assert isinstance(result, HitlResult)
        assert result.enabled is False
        assert result.action is ExitAction.COMMIT

    def test_runner_disabled_always_commit(
        self,
        monkeypatch: pytest.MonkeyPatch,
        controller: ExitController,
    ) -> None:
        monkeypatch.setenv(ENV_FLAG, "true")
        runner = _DisabledRunner()
        runner._hitl_controller = controller  # type: ignore[assignment]
        result = runner._maybe_escalate_hitl(  # pylint: disable=protected-access
            run_id="r",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=1,
            support_coverage=0.9,
            disposition="s",
        )
        assert result.enabled is False
        assert result.action is ExitAction.COMMIT

    def test_escalate_with_policy_override_writes_checkpoint(
        self,
        monkeypatch: pytest.MonkeyPatch,
        controller: ExitController,
        run_state_store: RunStateStore,
    ) -> None:
        monkeypatch.setenv(ENV_FLAG, "true")
        runner = _LicLikeRunner(collection="lic_docs")
        runner._hitl_controller = controller  # type: ignore[assignment]
        runner._hitl_run_state_store = run_state_store  # type: ignore[assignment]
        # Pass policy_overrides via subclass hook — simulate apps_lic
        # compliance-mode tagging a regulated envelope.
        result = runner._maybe_escalate_hitl(  # pylint: disable=protected-access
            run_id="lic-run-1",
            query="outreach campaign regulated",
            gate_disposition="allow",
            grounded=True,
            citation_count=1,
            support_coverage=0.9,
            disposition="strong_support",
            policy_overrides={"is_regulated": True},
        )
        assert result.action is ExitAction.ESCALATE_HITL
        assert result.enabled is True
        assert result.hitl_class == HitlClass.REGULATED.value
        assert result.ledger_id
        # G7 checkpoint written
        assert result.checkpoint is not None
        loaded = run_state_store.load(run_id="lic-run-1", ledger_id=result.ledger_id)
        assert loaded is not None
        assert loaded.payload["app_name"] == "apps_lic"
        assert loaded.payload["query"] == "outreach campaign regulated"
        assert loaded.payload["collection"] == "lic_docs"
        assert loaded.checkpoint_kind == "pre_uwg"

    def test_commit_path_no_ledger_no_checkpoint(
        self,
        monkeypatch: pytest.MonkeyPatch,
        controller: ExitController,
        run_state_store: RunStateStore,
    ) -> None:
        monkeypatch.setenv(ENV_FLAG, "true")
        runner = _LicLikeRunner()
        runner._hitl_controller = controller  # type: ignore[assignment]
        runner._hitl_run_state_store = run_state_store  # type: ignore[assignment]
        result = runner._maybe_escalate_hitl(  # pylint: disable=protected-access
            run_id="r",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=5,
            support_coverage=0.95,
            disposition="strong_support",
        )
        assert result.action is ExitAction.COMMIT
        assert result.ledger_id == ""
        assert result.checkpoint is None


# ---------------------------------------------------------------------------
# GovernedAppRunRecord backward compatibility
# ---------------------------------------------------------------------------


class TestGovernedAppRunRecordBackwardCompat:
    def test_record_constructible_without_hitl_fields(self) -> None:
        # Existing callers (pre-W5) must not break — HITL fields have defaults.
        rec = GovernedAppRunRecord(
            run_id="r",
            app_name="a",
            query="q",
            l1_sub_queries=(),
            l1_fallback=False,
            l0_intent="",
            l0_target="",
            l0_confidence=0.0,
            l0_fallback=False,
            c0_raw_count=0,
            c0_shaped_count=0,
            c0_collection="c",
            disposition="d",
            gate_disposition="g",
            grounded=False,
            citation_count=0,
            support_coverage=0.0,
            l6_ingested=False,
            l2_executed=False,
            error="",
        )
        assert rec.hitl_action == "none"
        assert rec.hitl_class == ""
        assert rec.hitl_ledger_id == ""
        assert rec.hitl_enabled is False

    def test_record_accepts_hitl_fields_when_provided(self) -> None:
        rec = GovernedAppRunRecord(
            run_id="r",
            app_name="a",
            query="q",
            l1_sub_queries=(),
            l1_fallback=False,
            l0_intent="",
            l0_target="",
            l0_confidence=0.0,
            l0_fallback=False,
            c0_raw_count=0,
            c0_shaped_count=0,
            c0_collection="c",
            disposition="d",
            gate_disposition="g",
            grounded=False,
            citation_count=0,
            support_coverage=0.0,
            l6_ingested=False,
            l2_executed=False,
            error="",
            hitl_action="escalate_hitl",
            hitl_class="financial",
            hitl_ledger_id="abc123",
            hitl_enabled=True,
        )
        assert rec.hitl_action == "escalate_hitl"
        assert rec.hitl_class == "financial"
        assert rec.hitl_ledger_id == "abc123"
        assert rec.hitl_enabled is True


# ---------------------------------------------------------------------------
# App-record threading sanity
# ---------------------------------------------------------------------------


class TestAppRecordThreading:
    def test_lic_record_has_hitl_fields(self) -> None:
        from apps_lic.integrations.governed_lic_run import (  # noqa: PLC0415
            GovernedLicE2ERunRecord,
            GovernedLicRun,
        )

        # Class flag enabled per P5.1
        assert GovernedLicRun.HITL_ENABLED is True

        rec = GovernedLicE2ERunRecord(
            run_id="r",
            app_name="apps_lic",
            query="q",
            l1_sub_queries=(),
            l1_fallback=False,
            l0_intent="",
            l0_target="",
            l0_confidence=0.0,
            l0_fallback=False,
            c0_raw_count=0,
            c0_shaped_count=0,
            c0_collection="c",
            disposition="d",
            gate_disposition="g",
            grounded=False,
            citation_count=0,
            support_coverage=0.0,
            l6_ingested=False,
            l2_executed=False,
            error="",
            campaign_id="camp-1",
            target_audience="aud",
            compliance_level="standard",
        )
        # Defaults
        assert rec.hitl_action == "none"
        assert rec.hitl_enabled is False

    def test_exec_record_has_hitl_fields(self) -> None:
        from apps_exec.integrations.governed_exec_run import (  # noqa: PLC0415
            GovernedExecE2ERunRecord,
            GovernedExecRun,
        )

        assert GovernedExecRun.HITL_ENABLED is True

        rec = GovernedExecE2ERunRecord(
            run_id="r",
            audience="board",
            emphasis_areas=(),
            query="q",
            l1_sub_queries=(),
            l1_fallback=False,
            l0_intent="",
            l0_target="",
            l0_confidence=0.0,
            l0_fallback=False,
            c0_raw_count=0,
            c0_shaped_count=0,
            c0_collection="c",
            disposition="d",
            gate_disposition="g",
            grounded=False,
            citation_count=0,
            support_coverage=0.0,
            l6_ingested=False,
            l2_executed=False,
            error="",
        )
        assert rec.hitl_action == "none"
        assert rec.hitl_enabled is False
