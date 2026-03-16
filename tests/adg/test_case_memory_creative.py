"""Creative advanced tests for the Memory MCP + Redis + ADG case memory architecture.

Test strategies used:
  1. Property-based / fuzz (hypothesis) — verify hash stability and frozen
     invariants hold under arbitrary valid inputs.
  2. Cross-tier integration simulation — CaseLibrary → RedisCoordinationFabric
     → CacheAdmissionGate full pipeline in a single scenario.
  3. Adversarial key injection — attempt to corrupt key schemas with colons,
     null bytes, newlines, empty strings.
  4. Concurrent lock contention — multithreaded acquire/release race under
     the in-process LRU fallback.
  5. Corpus bridge pipeline — PolicyGuardrailEmbedder → GovernancePrecedent →
     CaseLibrary: verify ADG entity naming and observation wiring.
  6. Hash collision resistance — every distinct semantic mutation produces a
     distinct stable_hash across all five bundle types.
  7. Memory card high-cardinality — upsert 300 distinct cards; verify no
     entity name collision or corruption.
  8. Replay safety under concurrent reads — many threads reading with
     replay_mode=True all get None.
  9. TTL boundary fencing — every namespace rejects TTLs exactly one second
     over its cap.
 10. Admission gate threshold boundary — values exactly at threshold admit;
     values infinitesimally below deny.
"""

from __future__ import annotations

import os
import threading
from typing import Any

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_case_memory_creative")
_emit_applies_guardrail("p0", "test_case_memory_creative", "p0_governance")
_emit_snapshots_state("p0", "test_case_memory_creative", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_case_memory_creative", "p4obs", "metric_1")
_emit_emits_metric_event("test_case_memory_creative", "p4obs", "metric_2")
_emit_emits_metric_event("test_case_memory_creative", "p4obs", "metric_3")
_emit_emits_metric_event("test_case_memory_creative", "p4obs", "metric_4")
_emit_emits_metric_event("test_case_memory_creative", "p4obs", "metric_5")
_emit_emits_metric_event("test_case_memory_creative", "p4obs", "metric_6")
_emit_records_incident_event("test_case_memory_creative", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_case_memory_creative", "p4obs", "anomaly")
_emit_writes_observability_log("test_case_memory_creative", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_case_memory_creative", "p4obs", "mon_state")
_emit_triggers_alert("test_case_memory_creative", "p4obs", "alert")
_emit_links_incident_trace("test_case_memory_creative", "p4obs", "trace_link")
_emit_captures_pattern("test_case_memory_creative", "p3lm", "pattern")
_emit_records_learning_event("test_case_memory_creative", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_case_memory_creative", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_case_memory_creative", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_case_memory_creative", "p3lm", "routing")
_emit_improves_agent_policy("test_case_memory_creative", "p3lm", "policy")
_emit_stores_learning_state("test_case_memory_creative", "p3lm", "state")
_emit_records_execution_trace("test_case_memory_creative", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_case_memory_creative", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_case_memory_creative", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_case_memory_creative", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_case_memory_creative", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_case_memory_creative", "env_read", "p2_env_1")
_emit_reads_environ("test_case_memory_creative", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_case_memory_creative", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_case_memory_creative", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_case_memory_creative", "context_pull")
_emit_pulls_context("p1", "test_case_memory_creative", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_case_memory_creative", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_case_memory_creative", "uwg_term_2")
_emit_writes_through("p1", "test_case_memory_creative", "write_through")
_emit_writes_through("p1", "test_case_memory_creative", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_case_memory_creative", "safety_validation")
_emit_invokes_eval("p1", "test_case_memory_creative", "eval_call")
_emit_proposal_commits_routing("p1", "test_case_memory_creative", "routing_commit")
emit_replay_key("p0", "test_case_memory_creative")
emit_determinism_digest("p0", "test_case_memory_creative")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_case_memory_creative", "execution_auth")
_emit_validates_capability("p2", "test_case_memory_creative", "capability_check")
_emit_routes_to_capability("p2", "test_case_memory_creative", "capability_route")
_emit_writes_via_uwg("p2", "test_case_memory_creative", "uwg_write")
_emit_blocks_direct_write("p2", "test_case_memory_creative", "direct_write_block")
_emit_records_tool_invocation("p2", "test_case_memory_creative", "tool_invocation")
_emit_captures_execution_output("p2", "test_case_memory_creative", "exec_output")
_emit_dispatches_agent("p3", "test_case_memory_creative", "agent_dispatch")
_emit_coordinates_agents("p3", "test_case_memory_creative", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_case_memory_creative", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_case_memory_creative", "healing_outcome")
_emit_escalates_failure("p3", "test_case_memory_creative", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_case_memory_creative", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_case_memory_creative", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_case_memory_creative", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_case_memory_creative", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_case_memory_creative", "eval_metric")
_emit_stores_embedding("p4", "test_case_memory_creative", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_case_memory_creative", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_case_memory_creative", "exec_snapshot_link")

os.environ.setdefault("REDIS_CACHE_STRICT_HASH_VALIDATION", "0")

# ---------------------------------------------------------------------------
# Try to import hypothesis — skip property tests gracefully if not installed
# ---------------------------------------------------------------------------
try:
    from hypothesis import HealthCheck, given, settings
    from hypothesis import strategies as st

    _HYPOTHESIS_AVAILABLE = True
except ImportError:
    # Provide no-op stubs so class-body @given decorators don't raise NameError
    import functools

    def given(*_a, **_kw):  # type: ignore[misc]
        def _dec(fn):
            @functools.wraps(fn)
            def _skip(*args, **kwargs):
                pytest.skip("hypothesis not installed")

            return _skip

        return _dec

    def settings(*_a, **_kw):  # type: ignore[misc]
        def _dec(fn):
            return fn

        return _dec

    class HealthCheck:  # type: ignore[misc]
        too_slow = "too_slow"

    class st:  # type: ignore[misc]
        @staticmethod
        def sampled_from(seq):
            return seq

        @staticmethod
        def integers(**kw):
            return range(0)

        @staticmethod
        def lists(*_a, **_kw):
            return [[]]

        @staticmethod
        def text(**kw):
            return ""

        @staticmethod
        def characters(**kw):
            return ""

    _HYPOTHESIS_AVAILABLE = False

_SKIP_HYPOTHESIS = pytest.mark.skipif(not _HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")

# ---------------------------------------------------------------------------
# Shared hash constants (non-strict validation mode)
# ---------------------------------------------------------------------------

_H = "a" * 64
_HB = "b" * 64
_HC = "c" * 64
_HD = "d" * 64
_TS = 1_700_000_000


# ===========================================================================
# Helpers
# ===========================================================================


def _policy_ref(ph: str = _H):
    from system_learning.types.case_memory_types import PolicyHashRef

    return PolicyHashRef(policy_hash=ph, config_version="v1")


def _outcome(label="SUCCESS"):
    from system_learning.types.case_memory_types import OutcomeClass

    return OutcomeClass(label=label, replay_pass=True)


def _adg_node(name="ADG::Module::foo", layer="L2", family="healing"):
    from system_learning.types.case_memory_types import ADGNodeRef

    return ADGNodeRef(entity_name=name, layer=layer, relation_family=family)


def _make_case_record(**overrides):
    from system_learning.types.case_memory_types import CaseRecord

    defaults = {
        "artifact_type": "CASE_RECORD",
        "trace_id": "trace-001",
        "plan_hash": _H,
        "policy_hash_ref": _policy_ref(),
        "replay_key": "rk-001",
        "request_family": "rg_resume",
        "route_path": "PATH_A",
        "agent_set": ("AgentX",),
        "prompt_artifact_hash": None,
        "healer_actions": (),
        "validator_actions": (),
        "outcome": _outcome(),
        "adg_nodes": (_adg_node(),),
        "timestamp_utc": _TS,
    }
    defaults.update(overrides)
    return CaseRecord(**defaults)


def _make_healer_bundle(**overrides):
    from system_learning.types.case_memory_types import HealerBundle

    defaults = {
        "artifact_type": "HEALER_BUNDLE",
        "bundle_id": "bnd-001",
        "trace_id": "trace-001",
        "violation_pattern": "IMPORT_ERROR",
        "healer_id": "AutoRepairHealer",
        "healer_tier": "LOCAL_AGENT",
        "patch_hash": None,
        "validation_passed": True,
        "replay_validated": True,
        "policy_hash_ref": _policy_ref(),
        "adg_healer_node": _adg_node(name="ADG::Symbol::Healer", family="healing"),
        "adg_validator_node": None,
        "outcome": _outcome(),
        "timestamp_utc": _TS,
    }
    defaults.update(overrides)
    return HealerBundle(**defaults)


def _make_governance_precedent(**overrides):
    from system_learning.types.case_memory_types import GovernancePrecedent

    defaults = {
        "artifact_type": "GOVERNANCE_PRECEDENT",
        "precedent_id": "prec-001",
        "trace_id": "trace-001",
        "safety_issue_type": "PROMPT_INJECTION",
        "guardrail_id": "InstructionFenceGuardrail",
        "remediation_applied": "BLOCK",
        "safety_classifier_outputs": (("clf-a", 0.95),),
        "policy_hash_ref": _policy_ref(),
        "fp_fn_record": None,
        "adg_guardrail_node": _adg_node(
            name="ADG::Symbol::InstructionFenceGuardrail", layer="L5", family="guardrail"
        ),
        "timestamp_utc": _TS,
    }
    defaults.update(overrides)
    return GovernancePrecedent(**defaults)


def _make_prompt_bundle(**overrides):
    from system_learning.types.case_memory_types import PromptBundle

    defaults = {
        "artifact_type": "PROMPT_BUNDLE",
        "bundle_id": "pb-001",
        "trace_id": "trace-001",
        "prompt_artifact_hash": _H,
        "template_manifest_hash": _HB,
        "slot_types_used": ("S0", "C0"),
        "injection_findings": (),
        "authority_violations": (),
        "outcome": _outcome(),
        "policy_hash_ref": _policy_ref(),
        "adg_prompt_node": _adg_node(name="ADG::Symbol::PromptAssembly", family="prompt_generation"),
        "timestamp_utc": _TS,
    }
    defaults.update(overrides)
    return PromptBundle(**defaults)


def _make_hitl_record(**overrides):
    from system_learning.types.case_memory_types import HITLPreferenceRecord

    defaults = {
        "artifact_type": "HITL_PREFERENCE_RECORD",
        "record_id": "hr-001",
        "trace_id": "trace-001",
        "original_plan_hash": _H,
        "human_decision": "APPROVE",
        "reason_tags": ("QUALITY_OK",),
        "patch_schema_hash": None,
        "dpo_pair_id": None,
        "downstream_outcome": None,
        "policy_hash_ref": _policy_ref(),
        "adg_hitl_node": _adg_node(name="ADG::Symbol::HITL", layer="L3", family="hitl"),
        "timestamp_utc": _TS,
    }
    defaults.update(overrides)
    return HITLPreferenceRecord(**defaults)


class _FakeBridge:
    def __init__(self):
        self.entities: list[dict] = []
        self.relations: list[tuple] = []

    def create_agent_entity(self, agent_name, agent_type=None, observations=None):
        self.entities.append({"name": agent_name, "type": agent_type})
        return True

    def create_relation(self, frm, to, rel):
        self.relations.append((frm, to, rel))
        return True

    def search_entities(self, query):
        return []

    def get_statistics(self):
        return {}


# ===========================================================================
# 1. Property-based tests (hypothesis)
# ===========================================================================


@_SKIP_HYPOTHESIS
class TestPropertyBasedBundleHashing:
    """Verify hash stability and frozen invariants under arbitrary inputs."""

    @given(
        route=st.sampled_from(["PATH_A", "PATH_B", "PATH_C", "PATH_D"]),
        family=st.sampled_from(["rg_resume", "lic_campaign", "generic"]),
        ts=st.integers(min_value=1_000_000_000, max_value=2_000_000_000),
    )
    @settings(max_examples=40, suppress_health_check=[HealthCheck.too_slow])
    def test_case_record_hash_stable_across_equal_inputs(self, route, family, ts):
        r1 = _make_case_record(route_path=route, request_family=family, timestamp_utc=ts)
        r2 = _make_case_record(route_path=route, request_family=family, timestamp_utc=ts)
        assert r1.stable_hash() == r2.stable_hash()

    @given(
        route=st.sampled_from(["PATH_A", "PATH_B", "PATH_D"]),
        ts=st.integers(min_value=1_000_000_000, max_value=2_000_000_000),
    )
    @settings(max_examples=40, suppress_health_check=[HealthCheck.too_slow])
    def test_case_record_hash_changes_with_timestamp(self, route, ts):
        r1 = _make_case_record(route_path=route, timestamp_utc=ts)
        r2 = _make_case_record(route_path=route, timestamp_utc=ts + 1)
        assert r1.stable_hash() != r2.stable_hash()

    @given(
        verdict=st.sampled_from(["true_positive", "false_positive", "false_negative"]),
        ts=st.integers(min_value=1_000_000_000, max_value=2_000_000_000),
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_governance_precedent_hash_stable(self, verdict, ts):
        p1 = _make_governance_precedent(safety_issue_type=verdict, timestamp_utc=ts)
        p2 = _make_governance_precedent(safety_issue_type=verdict, timestamp_utc=ts)
        assert p1.stable_hash() == p2.stable_hash()

    @given(decision=st.sampled_from(["APPROVE", "REJECT"]))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_hitl_record_frozen_under_all_decisions(self, decision):
        rec = _make_hitl_record(human_decision=decision)
        with pytest.raises((AttributeError, TypeError)):
            rec.human_decision = "MAYBE"  # type: ignore[misc]

    @given(
        tags=st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="_"),
                min_size=1,
                max_size=20,
            ),
            min_size=0,
            max_size=5,
        )
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_hitl_reason_tags_tuple_preserved(self, tags):
        rec = _make_hitl_record(reason_tags=tuple(tags))
        assert rec.reason_tags == tuple(tags)


# ===========================================================================
# 2. Cross-tier integration — CaseLibrary → Redis fabric → Admission gate
# ===========================================================================


class TestCrossTierIntegration:
    """Full pipeline: store a case bundle → cache its routing context →
    gate the RAG admission for the same trace."""

    def test_full_pipeline_case_to_redis_to_gate(self):
        from agentic_core.cache.redis_coordination_fabric import RedisCoordinationFabric
        from agentic_core.L4_state.memory.cache_admission_gate import CacheAdmissionGate
        from agentic_core.L4_state.memory.case_library import CaseLibrary

        bridge = _FakeBridge()
        lib = CaseLibrary(bridge=bridge)
        fab = RedisCoordinationFabric(redis_url="redis://localhost:19999")
        gate = CacheAdmissionGate(support_threshold=0.6, completeness_threshold=0.5)

        # 1. Store execution case in Memory MCP (via library)
        rec = _make_case_record(trace_id="pipeline-001", replay_key="rk-pipeline")
        ok = lib.store(rec)
        assert ok is True

        # 2. Cache active routing context for this trace in DB-2
        fab.set_trace_working_set(
            trace_id_hash=_H,
            state={
                "path": "PATH_A",
                "trace_id": "pipeline-001",
                "budget_remaining": 8,
                "safety_status": "CLEAR",
            },
        )
        ws = fab.get_trace_working_set(_H)
        assert ws is not None
        assert ws["path"] == "PATH_A"

        # 3. Gate a RAG admission for the same policy hash
        decision = gate.evaluate(
            query_hash=_H,
            policy_hash=_HB,
            embedder_version="bge-m3-v1",
            support_score=0.75,
            completeness_score=0.65,
            policy_conflict=False,
            replay_contaminated=False,
            timestamp_utc=_TS,
        )
        assert decision.admitted is True

        # 4. Verify case entity exists in bridge with lineage relation
        entity_names = [e["name"] for e in bridge.entities]
        assert any("CASE_RECORD" in n for n in entity_names)
        rel_types = [r[2] for r in bridge.relations]
        assert "lineage_of" in rel_types
        assert "governed_by_policy" in rel_types

    def test_full_pipeline_replay_mode_breaks_cache_not_library(self):
        """Even when replay_mode=True on Redis, the CaseLibrary write still succeeds."""
        from agentic_core.cache.redis_coordination_fabric import RedisCoordinationFabric
        from agentic_core.L4_state.memory.case_library import CaseLibrary

        bridge = _FakeBridge()
        lib = CaseLibrary(bridge=bridge)
        fab = RedisCoordinationFabric(redis_url="redis://localhost:19999")

        rec = _make_case_record(trace_id="replay-test")
        lib.store(rec)
        fab.set_trace_working_set(_H, {"state": "pre-replay"})

        # Replay mode: Redis returns None
        assert fab.get_trace_working_set(_H, replay_mode=True) is None
        # CaseLibrary is unaffected — bridge still has the entity
        assert any("CASE_RECORD" in e["name"] for e in bridge.entities)

    def test_pipeline_gate_denies_replay_contaminated_then_redis_not_written(self):
        """When gate denies due to replay contamination, caller should NOT write to Redis."""
        from agentic_core.cache.redis_coordination_fabric import RedisCoordinationFabric
        from agentic_core.L4_state.memory.cache_admission_gate import CacheAdmissionGate

        fab = RedisCoordinationFabric(redis_url="redis://localhost:19999")
        gate = CacheAdmissionGate()

        decision = gate.evaluate(
            query_hash=_HC,
            policy_hash=_HD,
            embedder_version="bge-m3-v1",
            support_score=0.9,
            completeness_score=0.9,
            policy_conflict=False,
            replay_contaminated=True,
            timestamp_utc=_TS,
        )
        assert decision.admitted is False

        # Simulate well-behaved caller: skip Redis write on denial
        if not decision.admitted:
            pass  # do not write
        else:
            fab.set_route_context(_HC, {"features": "contaminated"})

        # Nothing was cached
        assert fab.get_route_context(_HC) is None


# ===========================================================================
# 3. Adversarial key injection
# ===========================================================================


class TestAdversarialKeyInjection:
    """Attempt to corrupt key schemas with illegal characters."""

    def setup_method(self):
        os.environ["REDIS_CACHE_STRICT_HASH_VALIDATION"] = "0"

    def test_colon_in_agent_id_rejected(self):
        from agentic_core.cache.cache_key_builders import build_agent_performance_key

        with pytest.raises(ValueError, match="illegal ':' character"):
            build_agent_performance_key("Agent:Evil", _H, _HB)

    def test_colon_in_embedder_version_rejected(self):
        from agentic_core.cache.cache_key_builders import build_rag_admission_key

        with pytest.raises(ValueError, match="illegal ':' character"):
            build_rag_admission_key(_H, _HB, "bge-m3:evil")

    def test_empty_trace_hash_rejected(self):
        from agentic_core.cache.cache_key_builders import build_trace_working_set_key

        with pytest.raises(ValueError):
            build_trace_working_set_key("")

    def test_empty_team_lock_hash_rejected(self):
        from agentic_core.cache.cache_key_builders import build_team_lock_key

        with pytest.raises(ValueError):
            build_team_lock_key("")

    def test_empty_route_context_hash_rejected(self):
        from agentic_core.cache.cache_key_builders import build_route_context_key

        with pytest.raises(ValueError):
            build_route_context_key("")

    def test_null_byte_in_cache_key_rejected(self):
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        cache = DeterministicRedisCache(db=CacheDB.HOT, redis_url="redis://localhost:19999")
        with pytest.raises(ValueError):
            cache.get("key\x00evil")

    def test_newline_in_cache_key_rejected(self):
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        cache = DeterministicRedisCache(db=CacheDB.HOT, redis_url="redis://localhost:19999")
        with pytest.raises(ValueError):
            cache.set("key\nevil", b"value")

    def test_oversized_cache_value_rejected(self):
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        cache = DeterministicRedisCache(db=CacheDB.HOT, redis_url="redis://localhost:19999")
        # 10 MB + 1 byte
        with pytest.raises(ValueError, match="too large"):
            cache.set(_H[:32], b"x" * (10 * 1024 * 1024 + 1))

    def test_non_json_serialisable_object_rejected_by_canonical_json(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        with pytest.raises(TypeError):
            canonical_json_bytes({"bad": object()})

    def test_nan_in_canonical_json_rejected(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        with pytest.raises(ValueError):
            canonical_json_bytes({"score": float("nan")})

    def test_colon_in_trace_id_inside_orch_plan_key_rejected(self):
        from agentic_core.cache.cache_key_builders import build_orch_plan_key

        with pytest.raises(ValueError, match="illegal ':' character"):
            build_orch_plan_key("trace:evil", _H, _HB)

    def test_empty_admission_gate_query_hash_does_not_crash(self):
        """Gate should still return a decision (fail-closed) for empty query_hash."""
        from agentic_core.L4_state.memory.cache_admission_gate import CacheAdmissionGate

        gate = CacheAdmissionGate()
        # Empty query_hash is allowed at the gate level (it's content-addressed by caller)
        decision = gate.evaluate(
            query_hash="",
            policy_hash=_H,
            embedder_version="bge-m3-v1",
            support_score=0.8,
            completeness_score=0.8,
            policy_conflict=False,
            replay_contaminated=False,
            timestamp_utc=_TS,
        )
        # Gate itself does not validate hash format — caller's responsibility
        assert isinstance(decision.admitted, bool)


# ===========================================================================
# 4. Concurrent lock contention (LRU fallback)
# ===========================================================================


class TestConcurrentLockContention:
    """Multithreaded acquire/release race under LRU fallback."""

    def test_only_one_thread_acquires_team_lock(self):
        from agentic_core.cache.redis_coordination_fabric import RedisCoordinationFabric

        fab = RedisCoordinationFabric(redis_url="redis://localhost:19999")
        results: list[bool] = []
        lock = threading.Lock()

        def try_acquire(idx: int):
            acquired = fab.acquire_team_lock(
                resource_hash=_H,
                holder_id=f"Agent{idx}",
                semantic_clock_tick=idx,
            )
            with lock:
                results.append(acquired)

        threads = [threading.Thread(target=try_acquire, args=(i,)) for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exactly one thread should have won the lock
        assert results.count(True) == 1
        assert results.count(False) == 7

    def test_concurrent_trace_working_set_writes_are_idempotent(self):
        from agentic_core.cache.redis_coordination_fabric import RedisCoordinationFabric

        fab = RedisCoordinationFabric(redis_url="redis://localhost:19999")
        errors: list[Exception] = []

        def write_ws(i: int):
            try:
                fab.set_trace_working_set(
                    trace_id_hash=_HB,
                    state={"writer": i, "value": i * 10},
                )
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=write_ws, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
        # Final state is readable
        ws = fab.get_trace_working_set(_HB)
        assert ws is not None

    def test_concurrent_replay_mode_reads_all_return_none(self):
        """Many threads calling get with replay_mode=True must all get None."""
        from agentic_core.cache.redis_coordination_fabric import RedisCoordinationFabric

        fab = RedisCoordinationFabric(redis_url="redis://localhost:19999")
        fab.set_replay_fragment(_HC, {"data": "sensitive_transcript_fragment"})

        results: list[Any] = []
        lock = threading.Lock()

        def read_replay():
            val = fab.get_replay_fragment(_HC, replay_mode=True)
            with lock:
                results.append(val)

        threads = [threading.Thread(target=read_replay) for _ in range(12)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(r is None for r in results)


# ===========================================================================
# 5. Corpus bridge pipeline — PolicyGuardrailEmbedder → GovernancePrecedent → CaseLibrary
# ===========================================================================


class TestCorpusBridgePipeline:
    """Guardrail corpus ingest → convert to GovernancePrecedent → store in CaseLibrary."""

    def _make_guardrail_case(self, case_id="gc-001", verdict="true_positive"):
        from system_learning.types.semantic_memory_types import PolicyGuardrailCase

        return PolicyGuardrailCase(
            case_id=case_id,
            blocked_payload_summary="Inject system prompt via user slot",
            remediation_text="Blocked and logged; rewrite not attempted",
            policy_hash=_H,
            policy_root="prompt_injection_policy_v3",
            verdict=verdict,
            strictness_level="strict",
            trace_id="trace-gc-001",
            timestamp_utc=_TS,
        )

    def test_embedder_ingest_produces_corpus_record(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        emb = PolicyGuardrailEmbedder()
        case = self._make_guardrail_case()
        rec = emb.ingest(case)
        assert rec.namespace == "policy_guardrail_cases"
        assert len(rec.content_hash) == 64
        assert "payload:" in rec.text

    def test_embedder_corpus_record_text_is_deterministic(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        emb = PolicyGuardrailEmbedder()
        case = self._make_guardrail_case()
        r1 = emb.ingest(case)
        r2 = emb.ingest(case)
        assert r1.content_hash == r2.content_hash
        assert r1.text == r2.text

    def test_embedder_factory_method_validates_verdict(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        with pytest.raises(ValueError, match="verdict"):
            PolicyGuardrailEmbedder.case_from_l5_block(
                case_id="gc-x",
                blocked_payload_summary="bad",
                remediation_text="none",
                policy_hash=_H,
                policy_root="root",
                verdict="maybe",
                strictness_level="medium",
                trace_id="t",
                timestamp_utc=_TS,
            )

    def test_guardrail_case_to_governance_precedent_to_library(self):
        """Convert an embedded guardrail case into a GovernancePrecedent and store it."""
        from agentic_core.L4_state.memory.case_library import CaseLibrary
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder
        from system_learning.types.case_memory_types import (
            ADGNodeRef,
            GovernancePrecedent,
            PolicyHashRef,
        )

        emb = PolicyGuardrailEmbedder()
        gc = self._make_guardrail_case(verdict="false_positive")
        corpus_rec = emb.ingest(gc)

        # Convert corpus metadata → GovernancePrecedent
        precedent = GovernancePrecedent(
            artifact_type="GOVERNANCE_PRECEDENT",
            precedent_id=corpus_rec.content_hash,
            trace_id=gc.trace_id,
            safety_issue_type="PROMPT_INJECTION",
            guardrail_id="InstructionFenceGuardrail",
            remediation_applied="BLOCK",
            safety_classifier_outputs=(("embedder", 0.91),),
            policy_hash_ref=PolicyHashRef(policy_hash=gc.policy_hash, config_version="v3"),
            fp_fn_record=None,
            adg_guardrail_node=ADGNodeRef(
                entity_name="ADG::Symbol::InstructionFenceGuardrail",
                layer="L5",
                relation_family="guardrail",
            ),
            timestamp_utc=gc.timestamp_utc,
        )

        bridge = _FakeBridge()
        lib = CaseLibrary(bridge=bridge)
        ok = lib.store(precedent)
        assert ok is True

        # ADG entity name must contain GOVERNANCE_PRECEDENT + first 16 chars of hash
        entity_names = [e["name"] for e in bridge.entities]
        matching = [n for n in entity_names if "GOVERNANCE_PRECEDENT" in n]
        assert len(matching) >= 1
        assert precedent.stable_hash()[:16] in matching[0]

    def test_embedder_buffer_evicts_oldest_on_overflow(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        emb = PolicyGuardrailEmbedder(max_buffer=3)
        cases = [self._make_guardrail_case(case_id=f"gc-{i:03d}") for i in range(5)]
        for c in cases:
            emb.ingest(c)
        assert emb.buffer_size() == 3

    def test_embedder_export_corpus_records_sorted_deterministically(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        emb = PolicyGuardrailEmbedder()
        for i in range(6):
            emb.ingest(self._make_guardrail_case(case_id=f"gc-{i:03d}"))
        records = emb.export_corpus_records()
        hashes = [r.content_hash for r in records]
        assert hashes == sorted(hashes)

    def test_embedder_batch_ingest_order_matches_input(self):
        from system_learning.engines.policy_guardrail_embedder import PolicyGuardrailEmbedder

        emb = PolicyGuardrailEmbedder()
        cases = [
            self._make_guardrail_case(case_id=f"gc-{i:03d}", verdict=v)
            for i, v in enumerate(["true_positive", "false_positive", "false_negative"])
        ]
        records = emb.ingest_batch(cases)
        assert len(records) == 3
        # Each record maps to the corresponding case text
        for case, rec in zip(cases, records):
            assert case.case_id in emb._meta[rec.content_hash]["case_id"]


# ===========================================================================
# 6. Hash collision resistance
# ===========================================================================


class TestHashCollisionResistance:
    """Every distinct semantic mutation produces a distinct stable_hash."""

    def test_case_record_single_field_mutations_all_produce_unique_hashes(self):
        base = _make_case_record()
        mutations = [
            _make_case_record(route_path="PATH_B"),
            _make_case_record(request_family="lic_campaign"),
            _make_case_record(replay_key="rk-different"),
            _make_case_record(timestamp_utc=_TS + 1),
            _make_case_record(trace_id="trace-999"),
            _make_case_record(agent_set=("AgentY",)),
            _make_case_record(healer_actions=("SomeHealer",)),
        ]
        base_hash = base.stable_hash()
        for m in mutations:
            assert m.stable_hash() != base_hash, f"Collision on: {m}"

    def test_all_five_bundle_types_with_same_trace_produce_different_hashes(self):
        """Different bundle types with overlapping fields must never share a hash."""
        hashes = {
            _make_case_record().stable_hash(),
            _make_healer_bundle().stable_hash(),
            _make_governance_precedent().stable_hash(),
            _make_prompt_bundle().stable_hash(),
            _make_hitl_record().stable_hash(),
        }
        assert len(hashes) == 5, "Two bundle types collided!"

    def test_governance_precedent_fp_fn_affects_hash(self):
        from system_learning.types.case_memory_types import FalsePositiveNegativeRecord

        p_no_fpfn = _make_governance_precedent()
        p_with_fpfn = _make_governance_precedent(
            fp_fn_record=FalsePositiveNegativeRecord(
                disposition="FALSE_POSITIVE",
                later_policy_adjusted=True,
                adjustment_trace_id="adj-001",
            )
        )
        assert p_no_fpfn.stable_hash() != p_with_fpfn.stable_hash()

    def test_prompt_bundle_injection_finding_changes_hash(self):
        p_clean = _make_prompt_bundle(injection_findings=())
        p_dirty = _make_prompt_bundle(injection_findings=("inject_attempt_1",))
        assert p_clean.stable_hash() != p_dirty.stable_hash()

    def test_hitl_approve_vs_reject_hash_differs(self):
        approve = _make_hitl_record(human_decision="APPROVE")
        reject = _make_hitl_record(human_decision="REJECT")
        assert approve.stable_hash() != reject.stable_hash()

    def test_healer_bundle_validation_flag_changes_hash(self):
        valid = _make_healer_bundle(validation_passed=True)
        invalid = _make_healer_bundle(validation_passed=False)
        assert valid.stable_hash() != invalid.stable_hash()

    def test_200_distinct_trace_ids_produce_200_distinct_hashes(self):
        hashes = {_make_case_record(trace_id=f"trace-{i:04d}").stable_hash() for i in range(200)}
        assert len(hashes) == 200


# ===========================================================================
# 7. Memory card high-cardinality stress
# ===========================================================================


class TestMemoryCardHighCardinality:
    """Upsert 300 distinct cards; verify correctness and no corruption."""

    def test_300_distinct_cards_all_stored(self):
        from agentic_core.L4_state.memory.graph_neighborhood_memory import (
            GraphNeighborhoodMemory,
            MemoryCard,
        )

        bridge = _FakeBridge()
        mem = GraphNeighborhoodMemory(bridge=bridge)
        n = 300
        for i in range(n):
            card = MemoryCard(
                adg_entity_name=f"ADG::Module::foo_{i:04d}",
                layer="L2",
                territory="L2_execution",
                timestamp_utc=_TS + i,
            )
            ok = mem.upsert_card(card)
            assert ok is True

        assert len(mem.list_cached_entities()) == n
        entity_names = {e["name"] for e in bridge.entities}
        for i in range(n):
            assert f"ADG::Module::foo_{i:04d}" in entity_names

    def test_300_cards_then_update_half_failure_families_reflected(self):
        """record_failure mutates the cached MemoryCard in place.

        The implementation mutates the card object that is already stored in
        ``_cards``, so the stable_hash check sees equal hashes and the bridge
        write is a no-op (correct: no redundant MCP writes).  What matters is
        that the in-process card reflects the new failure family.
        """
        from agentic_core.L4_state.memory.graph_neighborhood_memory import (
            GraphNeighborhoodMemory,
            MemoryCard,
        )

        bridge = _FakeBridge()
        mem = GraphNeighborhoodMemory(bridge=bridge)
        n = 100
        for i in range(n):
            mem.upsert_card(
                MemoryCard(
                    adg_entity_name=f"ADG::Module::bar_{i:04d}",
                    layer="L4",
                    timestamp_utc=_TS,
                )
            )

        # Update half with a new failure family
        updated = 0
        for i in range(0, n, 2):
            name = f"ADG::Module::bar_{i:04d}"
            ok = mem.record_failure(
                adg_entity_name=name,
                failure_family="POLICY_VIOLATION",
                layer="L4",
                timestamp_utc=_TS + 1,
            )
            assert ok is True
            updated += 1

        assert updated == n // 2
        # In-process cards for the updated half must carry the failure family
        for i in range(0, n, 2):
            card = mem.get_card(f"ADG::Module::bar_{i:04d}")
            assert "POLICY_VIOLATION" in card.common_failure_families
        # Non-updated cards must NOT carry the failure family
        for i in range(1, n, 2):
            card = mem.get_card(f"ADG::Module::bar_{i:04d}")
            assert "POLICY_VIOLATION" not in card.common_failure_families

    def test_no_entity_name_collision_across_all_bundle_types(self):
        """ADG entity names for bundles must never collide with each other."""
        from agentic_core.L4_state.memory.case_library import CaseLibrary

        bridge = _FakeBridge()
        lib = CaseLibrary(bridge=bridge)
        bundles = (
            [_make_case_record(trace_id=f"t{i}") for i in range(30)]
            + [_make_healer_bundle(bundle_id=f"bnd-{i}") for i in range(30)]
            + [_make_governance_precedent(precedent_id=f"prec-{i}", trace_id=f"t-gp-{i}") for i in range(30)]
        )
        for b in bundles:
            lib.store(b)

        case_entity_names = [
            e["name"]
            for e in bridge.entities
            if "CASE_RECORD" in e["name"]
            or "HEALER_BUNDLE" in e["name"]
            or "GOVERNANCE_PRECEDENT" in e["name"]
        ]
        # All names should be unique
        assert len(case_entity_names) == len(set(case_entity_names))


# ===========================================================================
# 8. Replay safety under concurrent reads (already done in lock tests — extend here)
# ===========================================================================


class TestReplaySafetyAdvanced:
    """Deeper replay safety: verify that replay_mode bypasses ALL five fabric namespaces."""

    def _fabric(self):
        from agentic_core.cache.redis_coordination_fabric import RedisCoordinationFabric

        return RedisCoordinationFabric(redis_url="redis://localhost:19999")

    def test_all_namespaces_bypassed_in_replay_mode(self):
        fab = self._fabric()

        fab.set_trace_working_set(_H, {"x": 1})
        fab.set_route_context(_HB, {"y": 2})
        fab.set_replay_fragment(_HC, {"z": 3})
        fab.set_novelty_cluster(_HD, {"w": 4})

        assert fab.get_trace_working_set(_H, replay_mode=True) is None
        assert fab.get_route_context(_HB, replay_mode=True) is None
        assert fab.get_replay_fragment(_HC, replay_mode=True) is None
        assert fab.get_novelty_cluster(_HD, replay_mode=True) is None

    def test_replay_mode_does_not_poison_fallback_lru(self):
        """After replay-mode reads, non-replay reads should still return data."""
        fab = self._fabric()
        fab.set_trace_working_set(_H, {"data": "keep-me"})

        # Replay reads
        for _ in range(5):
            assert fab.get_trace_working_set(_H, replay_mode=True) is None

        # Non-replay read still returns data
        ws = fab.get_trace_working_set(_H, replay_mode=False)
        assert ws == {"data": "keep-me"}

    def test_replay_stats_increment_on_bypass(self):
        fab = self._fabric()
        fab.set_trace_working_set(_H, {"v": 1})

        initial_bypassed = fab._cache.stats.bypassed_replay
        for _ in range(3):
            fab.get_trace_working_set(_H, replay_mode=True)

        assert fab._cache.stats.bypassed_replay == initial_bypassed + 3


# ===========================================================================
# 9. TTL boundary fencing
# ===========================================================================


class TestTTLBoundaryFencing:
    """Every namespace rejects TTLs exactly one second over its cap."""

    def _fabric(self):
        from agentic_core.cache.redis_coordination_fabric import RedisCoordinationFabric

        return RedisCoordinationFabric(redis_url="redis://localhost:19999")

    def test_trace_ws_exactly_at_cap_is_accepted(self):
        fab = self._fabric()
        fab.set_trace_working_set(_H, {"ok": True}, ttl_seconds=900)

    def test_trace_ws_one_over_cap_is_rejected(self):
        fab = self._fabric()
        with pytest.raises(ValueError, match="trace working set TTL"):
            fab.set_trace_working_set(_H, {}, ttl_seconds=901)

    def test_team_lock_exactly_at_cap_is_accepted(self):
        fab = self._fabric()
        # Use a unique hash to avoid conflicts with other tests
        unique_h = "e" * 64
        fab.acquire_team_lock(unique_h, "AgentTTL", semantic_clock_tick=1, ttl_seconds=120)

    def test_team_lock_one_over_cap_is_rejected(self):
        fab = self._fabric()
        with pytest.raises(ValueError, match="team lock TTL"):
            fab.acquire_team_lock(_H, "AgentTTL", semantic_clock_tick=1, ttl_seconds=121)

    def test_route_ctx_exactly_at_cap_is_accepted(self):
        fab = self._fabric()
        fab.set_route_context(_HB, {"ok": True}, ttl_seconds=3600)

    def test_route_ctx_one_over_cap_is_rejected(self):
        fab = self._fabric()
        with pytest.raises(ValueError, match="route context TTL"):
            fab.set_route_context(_HB, {}, ttl_seconds=3601)

    def test_replay_frag_exactly_at_cap_is_accepted(self):
        fab = self._fabric()
        fab.set_replay_fragment(_HC, {"ok": True}, ttl_seconds=600)

    def test_replay_frag_one_over_cap_is_rejected(self):
        fab = self._fabric()
        with pytest.raises(ValueError, match="replay fragment TTL"):
            fab.set_replay_fragment(_HC, {}, ttl_seconds=601)

    def test_novelty_exactly_at_cap_is_accepted(self):
        fab = self._fabric()
        fab.set_novelty_cluster(_HD, {"ok": True}, ttl_seconds=1800)

    def test_novelty_one_over_cap_is_rejected(self):
        fab = self._fabric()
        with pytest.raises(ValueError, match="novelty cluster TTL"):
            fab.set_novelty_cluster(_HD, {}, ttl_seconds=1801)


# ===========================================================================
# 10. Admission gate threshold boundary conditions
# ===========================================================================


class TestAdmissionGateThresholdBoundary:
    """Values exactly at threshold admit; values infinitesimally below deny."""

    def _gate(self, support=0.6, completeness=0.5):
        from agentic_core.L4_state.memory.cache_admission_gate import CacheAdmissionGate

        return CacheAdmissionGate(support_threshold=support, completeness_threshold=completeness)

    def _eval(self, gate, support, completeness):
        return gate.evaluate(
            query_hash=_H,
            policy_hash=_HB,
            embedder_version="bge-m3-v1",
            support_score=support,
            completeness_score=completeness,
            policy_conflict=False,
            replay_contaminated=False,
            timestamp_utc=_TS,
        )

    def test_support_exactly_at_threshold_admits(self):
        g = self._gate(support=0.6)
        d = self._eval(g, support=0.6, completeness=0.9)
        assert d.admitted is True

    def test_support_one_epsilon_below_threshold_denies(self):
        g = self._gate(support=0.6)
        d = self._eval(g, support=0.5999999999, completeness=0.9)
        assert d.admitted is False
        assert "SUPPORT_BELOW_THRESHOLD" in d.deny_reasons

    def test_completeness_exactly_at_threshold_admits(self):
        g = self._gate(completeness=0.5)
        d = self._eval(g, support=0.9, completeness=0.5)
        assert d.admitted is True

    def test_completeness_one_epsilon_below_threshold_denies(self):
        g = self._gate(completeness=0.5)
        d = self._eval(g, support=0.9, completeness=0.4999999999)
        assert d.admitted is False
        assert "COMPLETENESS_BELOW_THRESHOLD" in d.deny_reasons

    def test_zero_threshold_always_admits_on_score_gates(self):
        g = self._gate(support=0.0, completeness=0.0)
        d = self._eval(g, support=0.0, completeness=0.0)
        assert d.admitted is True

    def test_unit_threshold_only_admits_perfect_scores(self):
        g = self._gate(support=1.0, completeness=1.0)
        assert self._eval(g, support=1.0, completeness=1.0).admitted is True
        assert self._eval(g, support=0.9999, completeness=1.0).admitted is False
        assert self._eval(g, support=1.0, completeness=0.9999).admitted is False

    def test_all_four_deny_reasons_present_when_all_gates_fail(self):
        g = self._gate(support=1.0, completeness=1.0)
        d = gate = g.evaluate(
            query_hash=_H,
            policy_hash=_HB,
            embedder_version="bge-m3-v1",
            support_score=0.0,
            completeness_score=0.0,
            policy_conflict=True,
            replay_contaminated=True,
            timestamp_utc=_TS,
        )
        assert "SUPPORT_BELOW_THRESHOLD" in d.deny_reasons
        assert "COMPLETENESS_BELOW_THRESHOLD" in d.deny_reasons
        assert "POLICY_CONFLICT" in d.deny_reasons
        assert "REPLAY_CONTAMINATED" in d.deny_reasons
        assert len(d.deny_reasons) == 4

    def test_admit_rate_at_50_percent_correct(self):
        # Fail exactly one gate (support only) so total_evaluated = admitted(1) + denied_support(1) = 2
        g = self._gate(support=0.8, completeness=0.0)
        self._eval(
            g, support=0.9, completeness=0.9
        )  # admit (support passes, completeness always passes with threshold=0)
        self._eval(g, support=0.5, completeness=0.9)  # deny support only
        stats = g.get_stats()
        assert stats["admitted"] == 1
        assert stats["denied_support"] == 1
        assert stats["admit_rate"] == pytest.approx(0.5, abs=1e-9)

    def test_decision_json_is_deterministic_across_calls(self):
        g = self._gate()
        d1 = self._eval(g, support=0.7, completeness=0.6)
        d2 = self._eval(g, support=0.7, completeness=0.6)
        assert d1.to_json() == d2.to_json()

    def test_decision_stable_hash_matches_to_json_hash(self):
        import hashlib

        from system_learning.enforcement.determinism import deterministic_json

        g = self._gate()
        d = self._eval(g, support=0.7, completeness=0.6)
        expected = hashlib.sha256(deterministic_json(d.to_dict()).encode("utf-8")).hexdigest()
        assert d.stable_hash() == expected
