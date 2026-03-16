"""Tests for the Memory MCP + Redis + ADG case memory architecture.

Covers:
  - CaseRecord / HealerBundle / GovernancePrecedent / PromptBundle /
    HITLPreferenceRecord frozen invariants and deterministic serialisation
  - CaseLibrary entity/relation wiring via injected bridge
  - GraphNeighborhoodMemory card upsert and no-op dedup
  - RedisCoordinationFabric DB-2 namespace contracts (fallback LRU)
  - CacheAdmissionGate all four gates, fail-closed, stats
  - cache_key_builders new DB-2 and admission key schemas
"""

from __future__ import annotations

import os

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_case_memory_architecture")
_emit_applies_guardrail("p0", "test_case_memory_architecture", "p0_governance")
_emit_snapshots_state("p0", "test_case_memory_architecture", "state_snapshot")
emit_replay_key("p0", "test_case_memory_architecture")
emit_determinism_digest("p0", "test_case_memory_architecture")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

os.environ.setdefault("REDIS_CACHE_STRICT_HASH_VALIDATION", "0")

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_FAKE_HASH = "a" * 64  # 64-char hex lookalike for STRICT_HASH_VALIDATION=0
_FAKE_HASH_B = "b" * 64
_FAKE_HASH_C = "c" * 64
_FAKE_HASH_D = "d" * 64
_TS = 1_700_000_000


def _policy_ref(ph: str = _FAKE_HASH):
    from system_learning.types.case_memory_types import PolicyHashRef

    return PolicyHashRef(policy_hash=ph, config_version="v1.0")


def _outcome(label="SUCCESS", replay_pass=True):
    from system_learning.types.case_memory_types import OutcomeClass

    return OutcomeClass(label=label, replay_pass=replay_pass)


def _adg_node(name="ADG::Module::foo", layer="L2", family="healing"):
    from system_learning.types.case_memory_types import ADGNodeRef

    return ADGNodeRef(entity_name=name, layer=layer, relation_family=family)


# ===========================================================================
# 1. Frozen type invariants
# ===========================================================================


class TestCaseRecordInvariants:
    def _make(self, **overrides):
        from system_learning.types.case_memory_types import CaseRecord

        defaults = {
            "artifact_type": "CASE_RECORD",
            "trace_id": "trace-001",
            "plan_hash": _FAKE_HASH,
            "policy_hash_ref": _policy_ref(),
            "replay_key": "rk-001",
            "request_family": "rg_resume",
            "route_path": "PATH_A",
            "agent_set": ("AgentX",),
            "prompt_artifact_hash": _FAKE_HASH_B,
            "healer_actions": (),
            "validator_actions": (),
            "outcome": _outcome(),
            "adg_nodes": (_adg_node(),),
            "timestamp_utc": _TS,
        }
        defaults.update(overrides)
        return CaseRecord(**defaults)

    def test_happy_path_creates_record(self):
        rec = self._make()
        assert rec.artifact_type == "CASE_RECORD"
        assert rec.trace_id == "trace-001"

    def test_frozen(self):
        rec = self._make()
        with pytest.raises((AttributeError, TypeError)):
            rec.trace_id = "mutated"  # type: ignore[misc]

    def test_wrong_artifact_type_raises(self):
        with pytest.raises(ValueError):
            self._make(artifact_type="WRONG")

    def test_empty_trace_id_raises(self):
        with pytest.raises(ValueError):
            self._make(trace_id="")

    def test_empty_plan_hash_raises(self):
        with pytest.raises(ValueError):
            self._make(plan_hash="")

    def test_empty_replay_key_raises(self):
        with pytest.raises(ValueError):
            self._make(replay_key="")

    def test_to_dict_sorted_keys(self):
        rec = self._make()
        d = rec.to_dict()
        assert list(d.keys()) == sorted(d.keys())

    def test_stable_hash_deterministic(self):
        r1 = self._make()
        r2 = self._make()
        assert r1.stable_hash() == r2.stable_hash()

    def test_stable_hash_changes_with_content(self):
        r1 = self._make(route_path="PATH_A")
        r2 = self._make(route_path="PATH_D")
        assert r1.stable_hash() != r2.stable_hash()

    def test_to_json_is_deterministic(self):
        r1 = self._make()
        r2 = self._make()
        assert r1.to_json() == r2.to_json()


class TestHealerBundleInvariants:
    def _make(self, **overrides):
        from system_learning.types.case_memory_types import HealerBundle

        defaults = {
            "artifact_type": "HEALER_BUNDLE",
            "bundle_id": "bnd-001",
            "trace_id": "trace-001",
            "violation_pattern": "IMPORT_ERROR",
            "healer_id": "AutoRepairHealer",
            "healer_tier": "LOCAL_AGENT",
            "patch_hash": _FAKE_HASH_B,
            "validation_passed": True,
            "replay_validated": True,
            "policy_hash_ref": _policy_ref(),
            "adg_healer_node": _adg_node(name="ADG::Symbol::AutoRepairHealer", family="healing"),
            "adg_validator_node": None,
            "outcome": _outcome(),
            "timestamp_utc": _TS,
        }
        defaults.update(overrides)
        return HealerBundle(**defaults)

    def test_happy_path(self):
        b = self._make()
        assert b.healer_id == "AutoRepairHealer"

    def test_frozen(self):
        b = self._make()
        with pytest.raises((AttributeError, TypeError)):
            b.healer_id = "x"  # type: ignore[misc]

    def test_wrong_type_raises(self):
        with pytest.raises(ValueError):
            self._make(artifact_type="CASE_RECORD")

    def test_empty_bundle_id_raises(self):
        with pytest.raises(ValueError):
            self._make(bundle_id="")

    def test_stable_hash_deterministic(self):
        b1 = self._make()
        b2 = self._make()
        assert b1.stable_hash() == b2.stable_hash()


class TestGovernancePrecedentInvariants:
    def _make(self, **overrides):
        from system_learning.types.case_memory_types import GovernancePrecedent

        defaults = {
            "artifact_type": "GOVERNANCE_PRECEDENT",
            "precedent_id": "prec-001",
            "trace_id": "trace-001",
            "safety_issue_type": "PROMPT_INJECTION",
            "guardrail_id": "InstructionFenceGuardrail",
            "remediation_applied": "BLOCK",
            "safety_classifier_outputs": (("clf-a", 0.95), ("clf-b", 0.87)),
            "policy_hash_ref": _policy_ref(),
            "fp_fn_record": None,
            "adg_guardrail_node": _adg_node(
                name="ADG::Symbol::InstructionFenceGuardrail", layer="L5", family="guardrail"
            ),
            "timestamp_utc": _TS,
        }
        defaults.update(overrides)
        return GovernancePrecedent(**defaults)

    def test_happy_path(self):
        p = self._make()
        assert p.safety_issue_type == "PROMPT_INJECTION"

    def test_frozen(self):
        p = self._make()
        with pytest.raises((AttributeError, TypeError)):
            p.guardrail_id = "x"  # type: ignore[misc]

    def test_wrong_type_raises(self):
        with pytest.raises(ValueError):
            self._make(artifact_type="HEALER_BUNDLE")

    def test_to_dict_classifier_outputs(self):
        p = self._make()
        d = p.to_dict()
        assert d["safety_classifier_outputs"] == [["clf-a", 0.95], ["clf-b", 0.87]]

    def test_stable_hash_deterministic(self):
        p1 = self._make()
        p2 = self._make()
        assert p1.stable_hash() == p2.stable_hash()


class TestPromptBundleInvariants:
    def _make(self, **overrides):
        from system_learning.types.case_memory_types import PromptBundle

        defaults = {
            "artifact_type": "PROMPT_BUNDLE",
            "bundle_id": "pb-001",
            "trace_id": "trace-001",
            "prompt_artifact_hash": _FAKE_HASH,
            "template_manifest_hash": _FAKE_HASH_B,
            "slot_types_used": ("S0", "C0", "U0"),
            "injection_findings": (),
            "authority_violations": (),
            "outcome": _outcome(),
            "policy_hash_ref": _policy_ref(),
            "adg_prompt_node": _adg_node(name="ADG::Symbol::PromptAssembly", family="prompt_generation"),
            "timestamp_utc": _TS,
        }
        defaults.update(overrides)
        return PromptBundle(**defaults)

    def test_happy_path(self):
        b = self._make()
        assert b.slot_types_used == ("S0", "C0", "U0")

    def test_frozen(self):
        b = self._make()
        with pytest.raises((AttributeError, TypeError)):
            b.bundle_id = "x"  # type: ignore[misc]

    def test_stable_hash_changes_with_findings(self):
        b1 = self._make(injection_findings=())
        b2 = self._make(injection_findings=("injection_attempt",))
        assert b1.stable_hash() != b2.stable_hash()


class TestHITLPreferenceRecordInvariants:
    def _make(self, **overrides):
        from system_learning.types.case_memory_types import HITLPreferenceRecord

        defaults = {
            "artifact_type": "HITL_PREFERENCE_RECORD",
            "record_id": "hr-001",
            "trace_id": "trace-001",
            "original_plan_hash": _FAKE_HASH,
            "human_decision": "APPROVE",
            "reason_tags": ("QUALITY_OK",),
            "patch_schema_hash": None,
            "dpo_pair_id": "dpo-123",
            "downstream_outcome": _outcome(),
            "policy_hash_ref": _policy_ref(),
            "adg_hitl_node": _adg_node(name="ADG::Symbol::HITLCheckpoint", layer="L3", family="hitl"),
            "timestamp_utc": _TS,
        }
        defaults.update(overrides)
        return HITLPreferenceRecord(**defaults)

    def test_happy_path(self):
        r = self._make()
        assert r.human_decision == "APPROVE"

    def test_reject_decision(self):
        r = self._make(human_decision="REJECT")
        assert r.human_decision == "REJECT"

    def test_invalid_decision_raises(self):
        with pytest.raises(ValueError):
            self._make(human_decision="MAYBE")

    def test_empty_plan_hash_raises(self):
        with pytest.raises(ValueError):
            self._make(original_plan_hash="")

    def test_frozen(self):
        r = self._make()
        with pytest.raises((AttributeError, TypeError)):
            r.human_decision = "REJECT"  # type: ignore[misc]

    def test_stable_hash_deterministic(self):
        r1 = self._make()
        r2 = self._make()
        assert r1.stable_hash() == r2.stable_hash()


# ===========================================================================
# 2. CaseLibrary — bridge injection and entity/relation wiring
# ===========================================================================


class _FakeBridge:
    """Minimal stub for GraphMemoryBridge that records calls."""

    def __init__(self):
        self.entities: list[dict] = []
        self.relations: list[tuple[str, str, str]] = []

    def create_agent_entity(self, agent_name, agent_type=None, observations=None):
        self.entities.append({"name": agent_name, "type": agent_type, "obs": observations})
        return True

    def create_relation(self, from_e, to_e, rel_type):
        self.relations.append((from_e, to_e, rel_type))
        return True

    def search_entities(self, query):
        return []

    def get_statistics(self):
        return {}


class TestCaseLibrary:
    def _lib(self):
        from agentic_core.L4_state.memory.case_library import CaseLibrary

        bridge = _FakeBridge()
        lib = CaseLibrary(bridge=bridge)
        return lib, bridge

    def _case_record(self):
        from system_learning.types.case_memory_types import CaseRecord

        return CaseRecord(
            artifact_type="CASE_RECORD",
            trace_id="trace-001",
            plan_hash=_FAKE_HASH,
            policy_hash_ref=_policy_ref(),
            replay_key="rk-001",
            request_family="rg_resume",
            route_path="PATH_A",
            agent_set=("AgentX",),
            prompt_artifact_hash=None,
            healer_actions=(),
            validator_actions=(),
            outcome=_outcome(),
            adg_nodes=(_adg_node(),),
            timestamp_utc=_TS,
        )

    def test_store_case_record_creates_entity(self):
        lib, bridge = self._lib()
        rec = self._case_record()
        ok = lib.store(rec)
        assert ok is True
        entity_names = [e["name"] for e in bridge.entities]
        assert any("CASE_RECORD" in n for n in entity_names)

    def test_store_creates_lineage_relation(self):
        lib, bridge = self._lib()
        lib.store(self._case_record())
        rel_types = [r[2] for r in bridge.relations]
        assert "lineage_of" in rel_types

    def test_store_creates_policy_relation(self):
        lib, bridge = self._lib()
        lib.store(self._case_record())
        rel_types = [r[2] for r in bridge.relations]
        assert "governed_by_policy" in rel_types

    def test_store_creates_adg_node_relation(self):
        lib, bridge = self._lib()
        lib.store(self._case_record())
        rel_types = [r[2] for r in bridge.relations]
        assert "sourced_from_adg_node" in rel_types

    def test_store_healer_bundle_creates_healer_resolved(self):
        from system_learning.types.case_memory_types import HealerBundle

        lib, bridge = self._lib()
        bundle = HealerBundle(
            artifact_type="HEALER_BUNDLE",
            bundle_id="bnd-001",
            trace_id="trace-001",
            violation_pattern="IMPORT_ERROR",
            healer_id="AutoRepairHealer",
            healer_tier="LOCAL_AGENT",
            patch_hash=None,
            validation_passed=True,
            replay_validated=False,
            policy_hash_ref=_policy_ref(),
            adg_healer_node=_adg_node(name="ADG::Symbol::AutoRepairHealer", family="healing"),
            adg_validator_node=None,
            outcome=_outcome(),
            timestamp_utc=_TS,
        )
        lib.store(bundle)
        rel_types = [r[2] for r in bridge.relations]
        assert "healer_resolved" in rel_types

    def test_store_hitl_approve_creates_hitl_approved(self):
        from system_learning.types.case_memory_types import HITLPreferenceRecord

        lib, bridge = self._lib()
        rec = HITLPreferenceRecord(
            artifact_type="HITL_PREFERENCE_RECORD",
            record_id="hr-001",
            trace_id="trace-001",
            original_plan_hash=_FAKE_HASH,
            human_decision="APPROVE",
            reason_tags=(),
            patch_schema_hash=None,
            dpo_pair_id=None,
            downstream_outcome=None,
            policy_hash_ref=_policy_ref(),
            adg_hitl_node=_adg_node(name="ADG::Symbol::HITL", layer="L3", family="hitl"),
            timestamp_utc=_TS,
        )
        lib.store(rec)
        rel_types = [r[2] for r in bridge.relations]
        assert "hitl_approved" in rel_types

    def test_store_unknown_type_returns_false(self):
        lib, bridge = self._lib()

        class _Fake:
            artifact_type = "UNKNOWN_TYPE"

        assert lib.store(_Fake()) is False  # type: ignore[arg-type]


# ===========================================================================
# 3. GraphNeighborhoodMemory
# ===========================================================================


class TestGraphNeighborhoodMemory:
    def _mem(self):
        from agentic_core.L4_state.memory.graph_neighborhood_memory import (
            GraphNeighborhoodMemory,
        )

        bridge = _FakeBridge()
        return GraphNeighborhoodMemory(bridge=bridge), bridge

    def _card(self, name="ADG::Module::foo", layer="L2"):
        from agentic_core.L4_state.memory.graph_neighborhood_memory import MemoryCard

        return MemoryCard(
            adg_entity_name=name,
            layer=layer,
            territory="L2_execution",
            relation_families={"healing"},
            timestamp_utc=_TS,
        )

    def test_upsert_stores_entity(self):
        mem, bridge = self._mem()
        ok = mem.upsert_card(self._card())
        assert ok is True
        names = [e["name"] for e in bridge.entities]
        assert "ADG::Module::foo" in names

    def test_upsert_same_card_twice_is_noop(self):
        mem, bridge = self._mem()
        card = self._card()
        mem.upsert_card(card)
        count_before = len(bridge.entities)
        mem.upsert_card(card)
        assert len(bridge.entities) == count_before

    def test_upsert_changed_card_writes_again(self):
        from agentic_core.L4_state.memory.graph_neighborhood_memory import MemoryCard

        mem, bridge = self._mem()
        card = self._card()
        mem.upsert_card(card)
        count_before = len(bridge.entities)
        card2 = MemoryCard(
            adg_entity_name="ADG::Module::foo",
            layer="L2",
            territory="L2_execution",
            relation_families={"healing", "guardrail"},
            timestamp_utc=_TS + 1,
        )
        mem.upsert_card(card2)
        assert len(bridge.entities) > count_before

    def test_empty_entity_name_returns_false(self):
        from agentic_core.L4_state.memory.graph_neighborhood_memory import MemoryCard

        mem, bridge = self._mem()
        card = MemoryCard(adg_entity_name="", layer="L2", timestamp_utc=_TS)
        assert mem.upsert_card(card) is False

    def test_record_failure_adds_family(self):
        mem, bridge = self._mem()
        ok = mem.record_failure(
            adg_entity_name="ADG::Module::foo",
            failure_family="POLICY_VIOLATION",
            layer="L2",
            timestamp_utc=_TS,
        )
        assert ok is True
        card = mem.get_card("ADG::Module::foo")
        assert "POLICY_VIOLATION" in card.common_failure_families

    def test_record_healer_success_adds_healer(self):
        mem, bridge = self._mem()
        mem.record_healer_success(
            adg_entity_name="ADG::Module::foo",
            healer_id="AutoRepairHealer",
            layer="L2",
            timestamp_utc=_TS,
        )
        card = mem.get_card("ADG::Module::foo")
        assert "AutoRepairHealer" in card.common_healers

    def test_record_policy_touchpoint(self):
        mem, bridge = self._mem()
        mem.record_policy_touchpoint(
            adg_entity_name="ADG::Module::foo",
            policy_hash=_FAKE_HASH,
            layer="L2",
            timestamp_utc=_TS,
        )
        card = mem.get_card("ADG::Module::foo")
        assert _FAKE_HASH in card.policy_touchpoints

    def test_memory_card_to_dict_sorted(self):
        from agentic_core.L4_state.memory.graph_neighborhood_memory import MemoryCard

        card = MemoryCard(
            adg_entity_name="ADG::Module::foo",
            layer="L4",
            territory="L4_state",
            relation_families={"routing", "healing"},
            replay_sensitive=True,
            timestamp_utc=_TS,
        )
        d = card.to_dict()
        assert list(d.keys()) == sorted(d.keys())

    def test_memory_card_stable_hash_deterministic(self):
        from agentic_core.L4_state.memory.graph_neighborhood_memory import MemoryCard

        card = MemoryCard(
            adg_entity_name="ADG::Module::foo",
            layer="L4",
            timestamp_utc=_TS,
        )
        assert card.stable_hash() == card.stable_hash()


# ===========================================================================
# 4. RedisCoordinationFabric (fallback LRU — no real Redis needed)
# ===========================================================================


class TestRedisCoordinationFabric:
    def _fabric(self):
        from agentic_core.cache.redis_coordination_fabric import (
            RedisCoordinationFabric,
        )

        return RedisCoordinationFabric(redis_url="redis://localhost:19999")

    def test_trace_working_set_roundtrip(self):
        fab = self._fabric()
        fab.set_trace_working_set(
            trace_id_hash=_FAKE_HASH,
            state={"path": "PATH_A", "budget": 10},
        )
        result = fab.get_trace_working_set(_FAKE_HASH)
        assert result is not None
        assert result["path"] == "PATH_A"

    def test_trace_working_set_replay_mode_returns_none(self):
        fab = self._fabric()
        fab.set_trace_working_set(trace_id_hash=_FAKE_HASH, state={"x": 1})
        assert fab.get_trace_working_set(_FAKE_HASH, replay_mode=True) is None

    def test_trace_working_set_ttl_cap(self):
        fab = self._fabric()
        with pytest.raises(ValueError, match="trace working set TTL"):
            fab.set_trace_working_set(trace_id_hash=_FAKE_HASH, state={}, ttl_seconds=9999)

    def test_team_lock_acquire_and_release(self):
        fab = self._fabric()
        acquired = fab.acquire_team_lock(
            resource_hash=_FAKE_HASH,
            holder_id="AgentX",
            semantic_clock_tick=1,
        )
        assert acquired is True
        assert fab.is_team_locked(_FAKE_HASH) is True
        released = fab.release_team_lock(_FAKE_HASH, "AgentX", semantic_clock_tick=1)
        assert released is True

    def test_team_lock_duplicate_returns_false(self):
        fab = self._fabric()
        fab.acquire_team_lock(_FAKE_HASH_B, "AgentX", semantic_clock_tick=1)
        second = fab.acquire_team_lock(_FAKE_HASH_B, "AgentY", semantic_clock_tick=2)
        assert second is False

    def test_team_lock_ttl_cap(self):
        fab = self._fabric()
        with pytest.raises(ValueError, match="team lock TTL"):
            fab.acquire_team_lock(_FAKE_HASH, "A", semantic_clock_tick=1, ttl_seconds=9999)

    def test_route_context_roundtrip(self):
        fab = self._fabric()
        fab.set_route_context(_FAKE_HASH_C, {"path": "PATH_B", "score": 0.9})
        r = fab.get_route_context(_FAKE_HASH_C)
        assert r["score"] == 0.9

    def test_route_context_replay_mode(self):
        fab = self._fabric()
        fab.set_route_context(_FAKE_HASH_C, {"x": 1})
        assert fab.get_route_context(_FAKE_HASH_C, replay_mode=True) is None

    def test_replay_fragment_roundtrip(self):
        fab = self._fabric()
        fab.set_replay_fragment(_FAKE_HASH_D, {"steps": [1, 2, 3]})
        r = fab.get_replay_fragment(_FAKE_HASH_D)
        assert r["steps"] == [1, 2, 3]

    def test_replay_fragment_replay_mode_bypassed(self):
        fab = self._fabric()
        fab.set_replay_fragment(_FAKE_HASH_D, {"steps": [1]})
        assert fab.get_replay_fragment(_FAKE_HASH_D, replay_mode=True) is None

    def test_novelty_cluster_roundtrip(self):
        fab = self._fabric()
        fab.set_novelty_cluster(_FAKE_HASH, {"family": "IMPORT_ERROR", "count": 5})
        r = fab.get_novelty_cluster(_FAKE_HASH)
        assert r["family"] == "IMPORT_ERROR"

    def test_novelty_cluster_ttl_cap(self):
        fab = self._fabric()
        with pytest.raises(ValueError, match="novelty cluster TTL"):
            fab.set_novelty_cluster(_FAKE_HASH, {}, ttl_seconds=99999)

    def test_delete_trace_working_set(self):
        fab = self._fabric()
        fab.set_trace_working_set(_FAKE_HASH, {"x": 1})
        fab.delete_trace_working_set(_FAKE_HASH)
        assert fab.get_trace_working_set(_FAKE_HASH) is None

    def test_get_stats_returns_dict(self):
        fab = self._fabric()
        stats = fab.get_stats()
        assert isinstance(stats, dict)


# ===========================================================================
# 5. CacheAdmissionGate
# ===========================================================================


class TestCacheAdmissionGate:
    def _gate(self, support=0.6, completeness=0.5):
        from agentic_core.L4_state.memory.cache_admission_gate import CacheAdmissionGate

        return CacheAdmissionGate(
            support_threshold=support,
            completeness_threshold=completeness,
        )

    def _eval(self, gate, *, support=0.8, completeness=0.7, policy_conflict=False, replay=False):
        return gate.evaluate(
            query_hash=_FAKE_HASH,
            policy_hash=_FAKE_HASH_B,
            embedder_version="bge-m3-v1",
            support_score=support,
            completeness_score=completeness,
            policy_conflict=policy_conflict,
            replay_contaminated=replay,
            timestamp_utc=_TS,
        )

    def test_all_gates_pass(self):
        g = self._gate()
        d = self._eval(g)
        assert d.admitted is True
        assert d.deny_reasons == ()

    def test_support_below_threshold(self):
        g = self._gate(support=0.8)
        d = self._eval(g, support=0.5)
        assert d.admitted is False
        assert "SUPPORT_BELOW_THRESHOLD" in d.deny_reasons

    def test_completeness_below_threshold(self):
        g = self._gate(completeness=0.9)
        d = self._eval(g, completeness=0.3)
        assert d.admitted is False
        assert "COMPLETENESS_BELOW_THRESHOLD" in d.deny_reasons

    def test_policy_conflict_denies(self):
        g = self._gate()
        d = self._eval(g, policy_conflict=True)
        assert d.admitted is False
        assert "POLICY_CONFLICT" in d.deny_reasons

    def test_replay_contaminated_denies(self):
        g = self._gate()
        d = self._eval(g, replay=True)
        assert d.admitted is False
        assert "REPLAY_CONTAMINATED" in d.deny_reasons

    def test_multiple_deny_reasons(self):
        g = self._gate(support=1.0, completeness=1.0)
        d = self._eval(g, support=0.0, completeness=0.0, policy_conflict=True, replay=True)
        assert len(d.deny_reasons) == 4

    def test_decision_is_frozen(self):
        from agentic_core.L4_state.memory.cache_admission_gate import CacheAdmissionDecision

        g = self._gate()
        d = self._eval(g)
        assert isinstance(d, CacheAdmissionDecision)
        with pytest.raises((AttributeError, TypeError)):
            d.admitted = False  # type: ignore[misc]

    def test_decision_to_dict_sorted(self):
        g = self._gate()
        d = self._eval(g)
        dd = d.to_dict()
        assert list(dd.keys()) == sorted(dd.keys())

    def test_stable_hash_deterministic(self):
        g = self._gate()
        d1 = self._eval(g)
        d2 = self._eval(g)
        assert d1.stable_hash() == d2.stable_hash()

    def test_invalid_threshold_raises(self):
        from agentic_core.L4_state.memory.cache_admission_gate import CacheAdmissionGate

        with pytest.raises(ValueError):
            CacheAdmissionGate(support_threshold=1.5)
        with pytest.raises(ValueError):
            CacheAdmissionGate(completeness_threshold=-0.1)

    def test_stats_admitted_counted(self):
        g = self._gate()
        self._eval(g)
        stats = g.get_stats()
        assert stats["admitted"] == 1

    def test_stats_deny_reasons_counted(self):
        g = self._gate(support=1.0)
        self._eval(g, support=0.0)
        stats = g.get_stats()
        assert stats["denied_support"] == 1

    def test_admit_rate_calculation(self):
        g = self._gate()
        self._eval(g)  # admitted
        self._eval(g, support=0.0)  # denied
        stats = g.get_stats()
        assert stats["admit_rate"] == pytest.approx(0.5, abs=1e-6)


# ===========================================================================
# 6. cache_key_builders new schemas
# ===========================================================================


class TestNewCacheKeyBuilders:
    def setup_method(self):
        os.environ["REDIS_CACHE_STRICT_HASH_VALIDATION"] = "0"

    def _h(self, s="a"):
        return s * 64

    def test_trace_working_set_key(self):
        from agentic_core.cache.cache_key_builders import build_trace_working_set_key

        k = build_trace_working_set_key(self._h())
        assert k.startswith("trace_ws:")

    def test_team_lock_key(self):
        from agentic_core.cache.cache_key_builders import build_team_lock_key

        k = build_team_lock_key(self._h())
        assert k.startswith("team_lock:")

    def test_route_context_key(self):
        from agentic_core.cache.cache_key_builders import build_route_context_key

        k = build_route_context_key(self._h())
        assert k.startswith("route_ctx:")

    def test_replay_fragment_key(self):
        from agentic_core.cache.cache_key_builders import build_replay_fragment_key

        k = build_replay_fragment_key(self._h())
        assert k.startswith("replay_frag:")

    def test_novelty_cluster_key(self):
        from agentic_core.cache.cache_key_builders import build_novelty_cluster_key

        k = build_novelty_cluster_key(self._h())
        assert k.startswith("novelty:")

    def test_rag_admission_key(self):
        from agentic_core.cache.cache_key_builders import build_rag_admission_key

        k = build_rag_admission_key(self._h("a"), self._h("b"), "bge-m3-v1")
        assert k.startswith("rag_admit:")
        assert "bge-m3-v1" in k

    def test_agent_performance_key(self):
        from agentic_core.cache.cache_key_builders import build_agent_performance_key

        k = build_agent_performance_key("AutoRepairHealer", self._h("b"), self._h("c"))
        assert k.startswith("agent_perf:")
        assert "AutoRepairHealer" in k

    def test_agent_performance_key_rejects_colon_in_agent_id(self):
        from agentic_core.cache.cache_key_builders import build_agent_performance_key

        with pytest.raises(ValueError):
            build_agent_performance_key("Agent:Bad", self._h("b"), self._h("c"))

    def test_key_stability(self):
        from agentic_core.cache.cache_key_builders import build_trace_working_set_key

        k1 = build_trace_working_set_key(self._h())
        k2 = build_trace_working_set_key(self._h())
        assert k1 == k2

    def test_key_uniqueness_by_hash(self):
        from agentic_core.cache.cache_key_builders import build_trace_working_set_key

        k1 = build_trace_working_set_key(self._h("a"))
        k2 = build_trace_working_set_key(self._h("b"))
        assert k1 != k2
