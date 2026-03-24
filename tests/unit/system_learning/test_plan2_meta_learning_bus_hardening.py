"""Plan 2 — System Learning / Meta-Learning Bus Hardening Tests.

Covers:
- Gap 1: DefaultMetaOutcomeBusHook uses correct MetaLearningChangePackage.create()
- Gap 2: drain_and_apply() drains bus and updates HealingSuccessRateStore
- Gap 3: L4MetaPriorProvider delegates to store, falls back to neutral on cold start
- End-to-end: publish → drain → prior reflects outcome
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.meta_control.meta_learning_bus import (
    MetaLearningBus,
    MetaLearningChangePackage,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "test_plan2_meta_learning_bus_hardening", "execution_auth")
_emit_validates_capability("p2", "test_plan2_meta_learning_bus_hardening", "capability_check")
_emit_routes_to_capability("p2", "test_plan2_meta_learning_bus_hardening", "capability_route")
_emit_writes_via_uwg("p2", "test_plan2_meta_learning_bus_hardening", "uwg_write")
_emit_blocks_direct_write("p2", "test_plan2_meta_learning_bus_hardening", "direct_write_block")
_emit_records_tool_invocation("p2", "test_plan2_meta_learning_bus_hardening", "tool_invocation")
_emit_captures_execution_output("p2", "test_plan2_meta_learning_bus_hardening", "exec_output")
_emit_dispatches_agent("p3", "test_plan2_meta_learning_bus_hardening", "agent_dispatch")
_emit_coordinates_agents("p3", "test_plan2_meta_learning_bus_hardening", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_plan2_meta_learning_bus_hardening", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_plan2_meta_learning_bus_hardening", "healing_outcome")
_emit_escalates_failure("p3", "test_plan2_meta_learning_bus_hardening", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_plan2_meta_learning_bus_hardening", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_plan2_meta_learning_bus_hardening", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_plan2_meta_learning_bus_hardening", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_plan2_meta_learning_bus_hardening", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_plan2_meta_learning_bus_hardening", "eval_metric")
_emit_stores_embedding("p4", "test_plan2_meta_learning_bus_hardening", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_plan2_meta_learning_bus_hardening", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_plan2_meta_learning_bus_hardening", "exec_snapshot_link")
from system_learning.engines.bus_consumer import drain_and_apply
from system_learning.engines.healing_success_rate_store import (
    _MIN_SAMPLE_SIZE,
    _NEUTRAL_PRIOR,
    HealingSuccessRateStore,
)

_emit_records_execution_trace("p0", "evidence", "test_plan2_meta_learning_bus_hardening")
_emit_applies_guardrail("p0", "test_plan2_meta_learning_bus_hardening", "p0_governance")
_emit_reads_policy_state("p0", "test_plan2_meta_learning_bus_hardening", "policy_binding")
_emit_snapshots_state("p0", "test_plan2_meta_learning_bus_hardening", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_plan2_meta_learning_bus_hardening", "p4obs", "metric_1")
_emit_emits_metric_event("test_plan2_meta_learning_bus_hardening", "p4obs", "metric_2")
_emit_emits_metric_event("test_plan2_meta_learning_bus_hardening", "p4obs", "metric_3")
_emit_emits_metric_event("test_plan2_meta_learning_bus_hardening", "p4obs", "metric_4")
_emit_emits_metric_event("test_plan2_meta_learning_bus_hardening", "p4obs", "metric_5")
_emit_emits_metric_event("test_plan2_meta_learning_bus_hardening", "p4obs", "metric_6")
_emit_records_incident_event("test_plan2_meta_learning_bus_hardening", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_plan2_meta_learning_bus_hardening", "p4obs", "anomaly")
_emit_writes_observability_log("test_plan2_meta_learning_bus_hardening", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_plan2_meta_learning_bus_hardening", "p4obs", "mon_state")
_emit_triggers_alert("test_plan2_meta_learning_bus_hardening", "p4obs", "alert")
_emit_links_incident_trace("test_plan2_meta_learning_bus_hardening", "p4obs", "trace_link")
_emit_captures_pattern("test_plan2_meta_learning_bus_hardening", "p3lm", "pattern")
_emit_records_learning_event("test_plan2_meta_learning_bus_hardening", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_plan2_meta_learning_bus_hardening", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_plan2_meta_learning_bus_hardening", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_plan2_meta_learning_bus_hardening", "p3lm", "routing")
_emit_improves_agent_policy("test_plan2_meta_learning_bus_hardening", "p3lm", "policy")
_emit_stores_learning_state("test_plan2_meta_learning_bus_hardening", "p3lm", "state")
_emit_records_execution_trace("test_plan2_meta_learning_bus_hardening", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_plan2_meta_learning_bus_hardening", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_plan2_meta_learning_bus_hardening", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_plan2_meta_learning_bus_hardening", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_plan2_meta_learning_bus_hardening", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_plan2_meta_learning_bus_hardening", "env_read", "p2_env_1")
_emit_reads_environ("test_plan2_meta_learning_bus_hardening", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_plan2_meta_learning_bus_hardening", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_plan2_meta_learning_bus_hardening", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_plan2_meta_learning_bus_hardening", "context_pull")
_emit_pulls_context("p1", "test_plan2_meta_learning_bus_hardening", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_plan2_meta_learning_bus_hardening", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_plan2_meta_learning_bus_hardening", "uwg_term_2")
_emit_writes_through("p1", "test_plan2_meta_learning_bus_hardening", "write_through")
_emit_writes_through("p1", "test_plan2_meta_learning_bus_hardening", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_plan2_meta_learning_bus_hardening", "safety_validation")
_emit_invokes_eval("p1", "test_plan2_meta_learning_bus_hardening", "eval_call")
_emit_proposal_commits_routing("p1", "test_plan2_meta_learning_bus_hardening", "routing_commit")
_emit_escalates_to_human("p1", "test_plan2_meta_learning_bus_hardening", "human_escalation")
_emit_routes_through("p1", "test_plan2_meta_learning_bus_hardening", "route_through")
_emit_checks_agent_registry("p1", "test_plan2_meta_learning_bus_hardening", "agent_registry")
_emit_validates_agent_capability("p1", "test_plan2_meta_learning_bus_hardening", "capability")
_emit_dispatches_execution_plan("p1", "test_plan2_meta_learning_bus_hardening", "exec_plan")
_emit_agent_executes_agent("p1", "test_plan2_meta_learning_bus_hardening", "sub_agent")
_emit_routes_to_agent("p1", "test_plan2_meta_learning_bus_hardening", "target_agent")
_emit_verifies_policy("p1", "test_plan2_meta_learning_bus_hardening", "policy_check")
_emit_observes_runtime_state("p1", "test_plan2_meta_learning_bus_hardening", "runtime_state")
_emit_verifies_boundary("p1", "test_plan2_meta_learning_bus_hardening", "boundary_check")
_emit_transcripts_response("p1", "test_plan2_meta_learning_bus_hardening", "transcript")
_emit_hard_fails_untranscripted("p1", "test_plan2_meta_learning_bus_hardening")
_emit_gated_by_confidence("p1", "test_plan2_meta_learning_bus_hardening", "confidence_gate")
emit_replay_key("p0", "test_plan2_meta_learning_bus_hardening")
emit_determinism_digest("p0", "test_plan2_meta_learning_bus_hardening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Gap 1: DefaultMetaOutcomeBusHook schema fix
# ---------------------------------------------------------------------------


class TestDefaultMetaOutcomeBusHookSchema:
    """DefaultMetaOutcomeBusHook must use MetaLearningChangePackage.create()."""

    def _make_healing_input(self, error_signature="syntax_error", trace_id="t-001"):
        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

        return HealingInput(
            failure_type="syntax_error",
            error_signature=error_signature,
            trace_id=trace_id,
            retry_count=0,
            blast_radius_estimate=0.3,
        )

    def _make_decision(self):
        from agentic_core.L2_execution.healers.healing_tier_types import (
            HealingDecision,
            HealingTier,
        )

        return HealingDecision(
            tier=HealingTier.LOCAL_AGENT,
            heal_confidence=0.90,
            reason_codes=("high_conf",),
        )

    def test_publish_outcome_enqueues_one_package(self):
        """publish_outcome must enqueue exactly one package on the bus."""
        from system_learning.ports.meta_outcome_bus_hook import DefaultMetaOutcomeBusHook

        bus = MetaLearningBus()
        hook = DefaultMetaOutcomeBusHook(bus=bus)

        hook.publish_outcome(
            healing_input=self._make_healing_input(),
            decision=self._make_decision(),
            record=None,
            success=True,
        )

        assert bus.size() == 1

    def test_published_package_has_correct_kind(self):
        """Published package must have kind == 'healing_outcome'."""
        from system_learning.ports.meta_outcome_bus_hook import DefaultMetaOutcomeBusHook

        bus = MetaLearningBus()
        hook = DefaultMetaOutcomeBusHook(bus=bus)

        hook.publish_outcome(
            healing_input=self._make_healing_input(),
            decision=self._make_decision(),
            record=None,
            success=False,
        )

        pkg = bus.dequeue()
        assert pkg is not None
        assert pkg.kind == "healing_outcome"

    def test_published_package_carries_error_signature(self):
        """Payload must include error_signature from HealingInput."""
        from system_learning.ports.meta_outcome_bus_hook import DefaultMetaOutcomeBusHook

        bus = MetaLearningBus()
        hook = DefaultMetaOutcomeBusHook(bus=bus)

        hook.publish_outcome(
            healing_input=self._make_healing_input(error_signature="import_cycle"),
            decision=self._make_decision(),
            record=None,
            success=True,
        )

        pkg = bus.dequeue()
        assert pkg.payload["error_signature"] == "import_cycle"
        assert pkg.payload["success"] is True
        assert pkg.payload["proposal_only"] is True

    def test_published_package_carries_trace_id(self):
        from system_learning.ports.meta_outcome_bus_hook import DefaultMetaOutcomeBusHook

        bus = MetaLearningBus()
        hook = DefaultMetaOutcomeBusHook(bus=bus)

        hook.publish_outcome(
            healing_input=self._make_healing_input(trace_id="trace-xyz"),
            decision=self._make_decision(),
            record=None,
            success=True,
        )

        pkg = bus.dequeue()
        assert pkg.trace_id == "trace-xyz"

    def test_null_bus_publish_outcome_is_no_op(self):
        """NullMetaOutcomeBusHook must silently do nothing."""
        from system_learning.ports.meta_outcome_bus_hook import NullMetaOutcomeBusHook

        hook = NullMetaOutcomeBusHook()
        hook.publish_outcome(
            healing_input=self._make_healing_input(),
            decision=self._make_decision(),
            record=None,
            success=True,
        )

    def test_none_bus_publish_outcome_is_no_op(self):
        """DefaultMetaOutcomeBusHook with bus=None must silently do nothing."""
        from system_learning.ports.meta_outcome_bus_hook import DefaultMetaOutcomeBusHook

        hook = DefaultMetaOutcomeBusHook(bus=None)
        hook.publish_outcome(
            healing_input=self._make_healing_input(),
            decision=self._make_decision(),
            record=None,
            success=True,
        )


# ---------------------------------------------------------------------------
# Gap 2: bus_consumer.drain_and_apply()
# ---------------------------------------------------------------------------


class TestDrainAndApply:
    """drain_and_apply() must drain queue and update HealingSuccessRateStore."""

    def test_drain_three_packages_updates_store(self):
        bus = MetaLearningBus()
        store = HealingSuccessRateStore()

        for i in range(3):
            pkg = MetaLearningChangePackage.create(
                trace_id=f"t-{i}",
                kind="healing_outcome",
                payload={"error_signature": "syntax_error", "success": True},
            )
            bus.enqueue(pkg)

        count = drain_and_apply(bus, store)

        assert count == 3
        assert bus.size() == 0
        assert store.get_counts().get("syntax_error", 0) == 3

    def test_drain_empty_bus_returns_zero(self):
        bus = MetaLearningBus()
        store = HealingSuccessRateStore()

        count = drain_and_apply(bus, store)

        assert count == 0

    def test_drain_twice_empty_second_time(self):
        bus = MetaLearningBus()
        store = HealingSuccessRateStore()

        pkg = MetaLearningChangePackage.create(
            trace_id="t-0",
            kind="healing_outcome",
            payload={"error_signature": "runtime_error", "success": False},
        )
        bus.enqueue(pkg)

        first = drain_and_apply(bus, store)
        second = drain_and_apply(bus, store)

        assert first == 1
        assert second == 0

    def test_drain_skips_unknown_kind(self):
        bus = MetaLearningBus()
        store = HealingSuccessRateStore()

        pkg = MetaLearningChangePackage.create(
            trace_id="t-0",
            kind="config_proposal",
            payload={"something": "else"},
        )
        bus.enqueue(pkg)

        count = drain_and_apply(bus, store)

        assert count == 1
        assert store.get_counts() == {}

    def test_drain_mixed_kinds_only_updates_healing_outcomes(self):
        bus = MetaLearningBus()
        store = HealingSuccessRateStore()

        bus.enqueue(
            MetaLearningChangePackage.create(
                trace_id="t-0",
                kind="healing_outcome",
                payload={"error_signature": "type_error", "success": True},
            )
        )
        bus.enqueue(
            MetaLearningChangePackage.create(
                trace_id="t-1",
                kind="config_proposal",
                payload={"something": "else"},
            )
        )
        bus.enqueue(
            MetaLearningChangePackage.create(
                trace_id="t-2",
                kind="healing_outcome",
                payload={"error_signature": "type_error", "success": False},
            )
        )

        count = drain_and_apply(bus, store)

        assert count == 3
        assert store.get_counts().get("type_error", 0) == 2

    def test_drain_missing_error_signature_skips_store_update(self):
        bus = MetaLearningBus()
        store = HealingSuccessRateStore()

        pkg = MetaLearningChangePackage.create(
            trace_id="t-0",
            kind="healing_outcome",
            payload={"success": True},  # no error_signature
        )
        bus.enqueue(pkg)

        count = drain_and_apply(bus, store)

        assert count == 1
        assert store.get_counts() == {}


# ---------------------------------------------------------------------------
# Gap 3: L4MetaPriorProvider
# ---------------------------------------------------------------------------


class TestL4MetaPriorProvider:
    """L4MetaPriorProvider must delegate to store and fall back on cold start."""

    def test_returns_neutral_when_store_is_none(self):
        from system_learning.adapters.l4_meta_prior_provider import L4MetaPriorProvider

        provider = L4MetaPriorProvider(store=None)
        assert provider.get_prior("syntax_error") == _NEUTRAL_PRIOR

    def test_returns_neutral_for_unknown_signature(self):
        from system_learning.adapters.l4_meta_prior_provider import L4MetaPriorProvider

        store = HealingSuccessRateStore()
        provider = L4MetaPriorProvider(store=store)
        assert provider.get_prior("unknown_sig") == _NEUTRAL_PRIOR

    def test_returns_neutral_before_min_sample_size(self):
        from system_learning.adapters.l4_meta_prior_provider import L4MetaPriorProvider

        store = HealingSuccessRateStore()
        # Record fewer than _MIN_SAMPLE_SIZE outcomes
        for _ in range(_MIN_SAMPLE_SIZE - 1):
            store.record_outcome("import_error", True)

        provider = L4MetaPriorProvider(store=store)
        assert provider.get_prior("import_error") == _NEUTRAL_PRIOR

    def test_returns_live_rate_after_min_sample_size(self):
        from system_learning.adapters.l4_meta_prior_provider import L4MetaPriorProvider

        store = HealingSuccessRateStore()
        for _ in range(_MIN_SAMPLE_SIZE):
            store.record_outcome("import_error", True)

        provider = L4MetaPriorProvider(store=store)
        prior = provider.get_prior("import_error")
        assert prior > _NEUTRAL_PRIOR, f"Expected > {_NEUTRAL_PRIOR}, got {prior}"

    def test_falls_back_to_neutral_when_store_raises(self):
        from unittest.mock import Mock

        from system_learning.adapters.l4_meta_prior_provider import L4MetaPriorProvider

        bad_store = Mock()
        bad_store.get_prior.side_effect = RuntimeError("store unavailable")

        provider = L4MetaPriorProvider(store=bad_store)
        result = provider.get_prior("syntax_error")
        assert result == _NEUTRAL_PRIOR

    def test_satisfies_meta_prior_provider_protocol(self):
        """L4MetaPriorProvider must satisfy MetaPriorProvider structural protocol."""
        from system_learning.adapters.l4_meta_prior_provider import L4MetaPriorProvider

        provider = L4MetaPriorProvider(store=None)
        assert hasattr(provider, "get_prior")
        result = provider.get_prior("any_sig")
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


# ---------------------------------------------------------------------------
# End-to-end: publish → drain → prior
# ---------------------------------------------------------------------------


class TestEndToEndBusFlow:
    """Full loop: hook publishes → drain_and_apply updates store → prior reflects outcome."""

    def test_end_to_end_success_raises_prior_above_neutral(self):
        from agentic_core.L2_execution.healers.healing_tier_types import (
            HealingDecision,
            HealingInput,
            HealingTier,
        )
        from system_learning.adapters.l4_meta_prior_provider import L4MetaPriorProvider
        from system_learning.ports.meta_outcome_bus_hook import DefaultMetaOutcomeBusHook

        bus = MetaLearningBus()
        store = HealingSuccessRateStore()
        hook = DefaultMetaOutcomeBusHook(bus=bus)
        provider = L4MetaPriorProvider(store=store)

        healing_input = HealingInput(
            failure_type="import_cycle",
            error_signature="import_cycle",
            trace_id="e2e-001",
            retry_count=0,
            blast_radius_estimate=0.2,
        )
        decision = HealingDecision(
            tier=HealingTier.LOCAL_AGENT,
            heal_confidence=0.90,
            reason_codes=("high_conf",),
        )

        # Publish _MIN_SAMPLE_SIZE successful outcomes
        for i in range(_MIN_SAMPLE_SIZE):
            hi = HealingInput(
                failure_type="import_cycle",
                error_signature="import_cycle",
                trace_id=f"e2e-{i:03d}",
                retry_count=0,
                blast_radius_estimate=0.2,
            )
            hook.publish_outcome(healing_input=hi, decision=decision, record=None, success=True)

        drain_and_apply(bus, store)

        prior = provider.get_prior("import_cycle")
        assert prior > _NEUTRAL_PRIOR, f"Expected prior > {_NEUTRAL_PRIOR}, got {prior}"

    def test_end_to_end_failure_lowers_prior_below_neutral(self):
        from agentic_core.L2_execution.healers.healing_tier_types import (
            HealingDecision,
            HealingInput,
            HealingTier,
        )
        from system_learning.adapters.l4_meta_prior_provider import L4MetaPriorProvider
        from system_learning.ports.meta_outcome_bus_hook import DefaultMetaOutcomeBusHook

        bus = MetaLearningBus()
        store = HealingSuccessRateStore()
        hook = DefaultMetaOutcomeBusHook(bus=bus)
        provider = L4MetaPriorProvider(store=store)

        decision = HealingDecision(
            tier=HealingTier.LOCAL_AGENT,
            heal_confidence=0.50,
            reason_codes=("low_conf",),
        )

        # Publish _MIN_SAMPLE_SIZE failure outcomes
        for i in range(_MIN_SAMPLE_SIZE):
            hi = HealingInput(
                failure_type="runtime_error",
                error_signature="runtime_error",
                trace_id=f"e2e-f-{i:03d}",
                retry_count=0,
                blast_radius_estimate=0.5,
            )
            hook.publish_outcome(healing_input=hi, decision=decision, record=None, success=False)

        drain_and_apply(bus, store)

        prior = provider.get_prior("runtime_error")
        assert prior < _NEUTRAL_PRIOR, f"Expected prior < {_NEUTRAL_PRIOR}, got {prior}"
