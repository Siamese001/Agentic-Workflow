"""Unit tests for apps_shared.integrations.runtime_hitl_integration (W5).

Covers:

- Envelope builder defaults and overrides
- RunStateStore round-trip (G7 checkpoint)
- Feature-flag gating (env + per-runner)
- maybe_escalate_hitl: flag-off, COMMIT, ESCALATE with checkpoint, DENY
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
    HitlResult,
    RunStateStore,
    build_exit_envelope,
    is_hitl_enabled,
    maybe_escalate_hitl,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_policy() -> HitlPolicy:
    """Build a hermetic HitlPolicy covering every class."""
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
        policy_snapshot="test-snap",
    )


@pytest.fixture
def policy() -> HitlPolicy:
    return _make_policy()


@pytest.fixture
def ledger(tmp_path: Path) -> RuntimeHitlLedger:
    return RuntimeHitlLedger(tmp_path / "ledger.db")


@pytest.fixture
def controller(policy: HitlPolicy, ledger: RuntimeHitlLedger) -> ExitController:
    return ExitController(policy=policy, ledger=ledger)


@pytest.fixture
def run_state_store(tmp_path: Path) -> RunStateStore:
    return RunStateStore(tmp_path / "run_state.db")


@pytest.fixture
def hitl_enabled_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_FLAG, "true")


@pytest.fixture
def hitl_disabled_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_FLAG, raising=False)


# ---------------------------------------------------------------------------
# build_exit_envelope
# ---------------------------------------------------------------------------


class TestBuildExitEnvelope:
    def test_defaults_map_support_coverage_to_confidence(self) -> None:
        env = build_exit_envelope(
            app_name="apps_lic",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=3,
            support_coverage=0.55,
            disposition="weak_support",
        )
        assert env["confidence_score"] == pytest.approx(0.55)
        assert env["novelty_score"] == 0.0
        assert env["is_financial"] is False
        assert env["is_regulated"] is False
        assert env["is_safety_impacting"] is False
        assert env["requires_policy_override"] is False
        assert env["deny"] is False
        assert env["app_name"] == "apps_lic"
        assert env["citation_count"] == 3

    def test_zero_citations_sets_novelty_to_one(self) -> None:
        env = build_exit_envelope(
            app_name="apps_exec",
            query="q",
            gate_disposition="allow",
            grounded=False,
            citation_count=0,
            support_coverage=0.0,
            disposition="unknown",
        )
        assert env["novelty_score"] == 1.0

    def test_support_coverage_clamped_to_unit_interval(self) -> None:
        above = build_exit_envelope(
            app_name="a",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=1,
            support_coverage=1.5,
            disposition="d",
        )
        below = build_exit_envelope(
            app_name="a",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=1,
            support_coverage=-0.2,
            disposition="d",
        )
        assert above["confidence_score"] == 1.0
        assert below["confidence_score"] == 0.0

    def test_block_disposition_triggers_policy_override(self) -> None:
        env = build_exit_envelope(
            app_name="a",
            query="q",
            gate_disposition="block",
            grounded=False,
            citation_count=1,
            support_coverage=0.5,
            disposition="weak_support",
        )
        assert env["requires_policy_override"] is True

    def test_overrides_win_over_defaults(self) -> None:
        env = build_exit_envelope(
            app_name="a",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=5,
            support_coverage=0.9,
            disposition="strong_support",
            policy_overrides={
                "is_regulated": True,
                "is_financial": True,
                "custom_field": "x",
            },
        )
        assert env["is_regulated"] is True
        assert env["is_financial"] is True
        assert env["custom_field"] == "x"


# ---------------------------------------------------------------------------
# is_hitl_enabled / feature flag gating
# ---------------------------------------------------------------------------


class TestFeatureFlagGating:
    def test_both_on_is_enabled(self, hitl_enabled_env: None) -> None:
        assert is_hitl_enabled(runner_flag=True) is True

    def test_env_off_per_runner_on_is_disabled(self, hitl_disabled_env: None) -> None:
        assert is_hitl_enabled(runner_flag=True) is False

    def test_env_on_runner_off_is_disabled(self, hitl_enabled_env: None) -> None:
        assert is_hitl_enabled(runner_flag=False) is False

    @pytest.mark.parametrize("val", ["1", "true", "TRUE", "yes", "on", "On"])
    def test_env_truthy_forms(self, monkeypatch: pytest.MonkeyPatch, val: str) -> None:
        monkeypatch.setenv(ENV_FLAG, val)
        assert is_hitl_enabled(runner_flag=True) is True

    @pytest.mark.parametrize("val", ["0", "false", "", "no", "off", "nonsense"])
    def test_env_falsy_forms(self, monkeypatch: pytest.MonkeyPatch, val: str) -> None:
        monkeypatch.setenv(ENV_FLAG, val)
        assert is_hitl_enabled(runner_flag=True) is False


# ---------------------------------------------------------------------------
# RunStateStore — G7 checkpoint round-trip
# ---------------------------------------------------------------------------


class TestRunStateStore:
    def test_checkpoint_then_load_round_trip(self, run_state_store: RunStateStore) -> None:
        cp = run_state_store.checkpoint(
            run_id="run-1",
            ledger_id="ledger-1",
            app_name="apps_lic",
            checkpoint_kind="pre_uwg",
            payload={"query": "q", "citations": 3},
        )
        assert cp.run_id == "run-1"
        assert cp.ledger_id == "ledger-1"
        assert cp.payload == {"query": "q", "citations": 3}
        assert cp.created_at > 0.0

        loaded = run_state_store.load(run_id="run-1", ledger_id="ledger-1")
        assert loaded is not None
        assert loaded.payload == {"query": "q", "citations": 3}
        assert loaded.checkpoint_kind == "pre_uwg"

    def test_load_missing_returns_none(self, run_state_store: RunStateStore) -> None:
        assert run_state_store.load(run_id="nope", ledger_id="nope") is None

    def test_checkpoint_replaces_on_same_key(self, run_state_store: RunStateStore) -> None:
        run_state_store.checkpoint(
            run_id="r",
            ledger_id="l",
            app_name="a",
            checkpoint_kind="k",
            payload={"v": 1},
        )
        run_state_store.checkpoint(
            run_id="r",
            ledger_id="l",
            app_name="a",
            checkpoint_kind="k",
            payload={"v": 2},
        )
        loaded = run_state_store.load(run_id="r", ledger_id="l")
        assert loaded is not None
        assert loaded.payload == {"v": 2}

    def test_list_by_app(self, run_state_store: RunStateStore) -> None:
        run_state_store.checkpoint(
            run_id="r1",
            ledger_id="l1",
            app_name="apps_lic",
            checkpoint_kind="k",
            payload={},
        )
        run_state_store.checkpoint(
            run_id="r2",
            ledger_id="l2",
            app_name="apps_lic",
            checkpoint_kind="k",
            payload={},
        )
        run_state_store.checkpoint(
            run_id="r3",
            ledger_id="l3",
            app_name="apps_exec",
            checkpoint_kind="k",
            payload={},
        )
        lic = run_state_store.list_by_app("apps_lic")
        assert len(lic) == 2
        assert {cp.run_id for cp in lic} == {"r1", "r2"}

    def test_non_serializable_payload_raises(self, run_state_store: RunStateStore) -> None:
        with pytest.raises(ValueError, match="JSON-serializable"):
            run_state_store.checkpoint(
                run_id="r",
                ledger_id="l",
                app_name="a",
                checkpoint_kind="k",
                payload={"bad": {1, 2, 3}},  # sets aren't JSON-serializable
            )

    def test_context_manager_closes(self, tmp_path: Path) -> None:
        path = tmp_path / "cm.db"
        with RunStateStore(path) as store:
            store.checkpoint(
                run_id="r",
                ledger_id="l",
                app_name="a",
                checkpoint_kind="k",
                payload={},
            )
        # Re-open and verify persistence across close/open
        store2 = RunStateStore(path)
        try:
            assert store2.load(run_id="r", ledger_id="l") is not None
        finally:
            store2.close()


# ---------------------------------------------------------------------------
# maybe_escalate_hitl — integration helper
# ---------------------------------------------------------------------------


class TestMaybeEscalateHitl:
    def test_flag_off_returns_commit_no_side_effects(
        self,
        hitl_disabled_env: None,
        controller: ExitController,
        run_state_store: RunStateStore,
        ledger: RuntimeHitlLedger,
    ) -> None:
        env = build_exit_envelope(
            app_name="apps_lic",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=3,
            support_coverage=0.9,
            disposition="strong_support",
            policy_overrides={"is_financial": True},  # would escalate if on
        )
        result = maybe_escalate_hitl(
            app_name="apps_lic",
            run_id="r",
            trace_id="r",
            envelope=env,
            runner_flag=True,
            controller=controller,
            run_state_store=run_state_store,
            checkpoint_payload={"x": 1},
        )
        assert result.action is ExitAction.COMMIT
        assert result.enabled is False
        assert result.ledger_id == ""
        # no ledger row, no checkpoint
        assert ledger.list_by_run("r") == []
        assert run_state_store.load(run_id="r", ledger_id="") is None

    def test_runner_flag_off_also_returns_commit(
        self,
        hitl_enabled_env: None,
        controller: ExitController,
    ) -> None:
        env = build_exit_envelope(
            app_name="a",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=1,
            support_coverage=0.9,
            disposition="s",
        )
        result = maybe_escalate_hitl(
            app_name="a",
            run_id="r",
            trace_id="r",
            envelope=env,
            runner_flag=False,
            controller=controller,
        )
        assert result.enabled is False
        assert result.action is ExitAction.COMMIT

    def test_commit_path_no_escalation(
        self,
        hitl_enabled_env: None,
        controller: ExitController,
        ledger: RuntimeHitlLedger,
    ) -> None:
        # High confidence, cited, no regulatory flags → no match → COMMIT
        env = build_exit_envelope(
            app_name="apps_lic",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=5,
            support_coverage=0.95,
            disposition="strong_support",
        )
        result = maybe_escalate_hitl(
            app_name="apps_lic",
            run_id="r",
            trace_id="r",
            envelope=env,
            runner_flag=True,
            controller=controller,
        )
        assert result.action is ExitAction.COMMIT
        assert result.enabled is True
        assert result.ledger_id == ""
        assert ledger.list_by_run("r") == []

    def test_deny_envelope_short_circuits(
        self,
        hitl_enabled_env: None,
        controller: ExitController,
        ledger: RuntimeHitlLedger,
    ) -> None:
        env = build_exit_envelope(
            app_name="a",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=1,
            support_coverage=0.9,
            disposition="s",
        )
        env["deny"] = True
        env["deny_reason"] = "blocklist"
        result = maybe_escalate_hitl(
            app_name="a",
            run_id="r",
            trace_id="r",
            envelope=env,
            runner_flag=True,
            controller=controller,
        )
        assert result.action is ExitAction.DENY
        assert result.deny_reason == "blocklist"
        assert result.enabled is True
        assert ledger.list_by_run("r") == []  # deny does not write

    def test_escalate_writes_ledger_and_checkpoint(
        self,
        hitl_enabled_env: None,
        controller: ExitController,
        run_state_store: RunStateStore,
        ledger: RuntimeHitlLedger,
    ) -> None:
        env = build_exit_envelope(
            app_name="apps_lic",
            query="loan_q",
            gate_disposition="allow",
            grounded=True,
            citation_count=1,
            support_coverage=0.9,
            disposition="strong_support",
            policy_overrides={"is_financial": True},
        )
        result = maybe_escalate_hitl(
            app_name="apps_lic",
            run_id="run-escalate",
            trace_id="run-escalate",
            envelope=env,
            runner_flag=True,
            controller=controller,
            run_state_store=run_state_store,
            checkpoint_kind="pre_uwg",
            checkpoint_payload={"query": "loan_q", "stage": "awaiting_uwg"},
        )
        assert result.action is ExitAction.ESCALATE_HITL
        assert result.enabled is True
        assert result.hitl_class == HitlClass.FINANCIAL.value
        assert result.ledger_id
        assert result.approver_pool == "pool_financial"
        assert result.timeout_s == 60
        assert result.fallback == "DENY"
        # ledger row persisted
        rows = ledger.list_by_run("run-escalate")
        assert len(rows) == 1
        assert rows[0].state is LedgerState.PENDING
        assert rows[0].hitl_class is HitlClass.FINANCIAL
        # checkpoint written (G7)
        assert result.checkpoint is not None
        assert result.checkpoint.checkpoint_kind == "pre_uwg"
        loaded = run_state_store.load(run_id="run-escalate", ledger_id=result.ledger_id)
        assert loaded is not None
        assert loaded.payload["query"] == "loan_q"
        assert loaded.payload["stage"] == "awaiting_uwg"

    def test_escalate_without_checkpoint_payload_skips_checkpoint(
        self,
        hitl_enabled_env: None,
        controller: ExitController,
        run_state_store: RunStateStore,
    ) -> None:
        env = build_exit_envelope(
            app_name="a",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=1,
            support_coverage=0.9,
            disposition="s",
            policy_overrides={"is_regulated": True},
        )
        result = maybe_escalate_hitl(
            app_name="a",
            run_id="r",
            trace_id="r",
            envelope=env,
            runner_flag=True,
            controller=controller,
            run_state_store=run_state_store,
            checkpoint_payload=None,
        )
        assert result.action is ExitAction.ESCALATE_HITL
        assert result.checkpoint is None
        assert run_state_store.load(run_id="r", ledger_id=result.ledger_id) is None

    def test_classify_type_error_returns_commit(
        self,
        hitl_enabled_env: None,
        controller: ExitController,
    ) -> None:
        # Passing a non-Mapping envelope triggers TypeError inside classify_exit
        # → helper catches and returns enabled=True, COMMIT (fail-open on the
        #   classification step but not on side effects).
        result = maybe_escalate_hitl(
            app_name="a",
            run_id="r",
            trace_id="r",
            envelope="not-a-mapping",  # type: ignore[arg-type]
            runner_flag=True,
            controller=controller,
        )
        assert result.action is ExitAction.COMMIT
        assert result.enabled is True

    def test_builds_default_controller_when_none_supplied(
        self,
        hitl_enabled_env: None,
        policy: HitlPolicy,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Force the helper to construct its own ledger by pointing the default
        # path at tmp_path. We still pass policy to avoid disk YAML read.
        env = build_exit_envelope(
            app_name="a",
            query="q",
            gate_disposition="allow",
            grounded=True,
            citation_count=1,
            support_coverage=0.9,
            disposition="s",
            policy_overrides={"is_safety_impacting": True},
        )
        # Redirect default ledger path into tmp_path via monkeypatch.
        import apps_shared.integrations.runtime_hitl_integration as mod  # noqa: PLC0415

        monkeypatch.setattr(mod, "DEFAULT_LEDGER_PATH", tmp_path / "def.db")
        result = maybe_escalate_hitl(
            app_name="a",
            run_id="r",
            trace_id="r",
            envelope=env,
            runner_flag=True,
            controller=None,
            policy=policy,
            ledger=None,
        )
        assert result.action is ExitAction.ESCALATE_HITL
        assert result.hitl_class == HitlClass.SAFETY.value
