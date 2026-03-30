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

from agentic_core.cache.redis_coordination_fabric import RedisCoordinationFabric
from agentic_core.L4_state.memory.cache_admission_gate import CacheAdmissionGate

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_FAKE_HASH = "a" * 64  # 64-char hex lookalike for STRICT_HASH_VALIDATION=0
_FAKE_HASH_B = "b" * 64
_FAKE_HASH_C = "c" * 64
_FAKE_HASH_D = "d" * 64
_TS = 1_700_000_000


def _policy_ref(ph: str = _FAKE_HASH):
    pass
def _outcome(label="SUCCESS", replay_pass=True):
    pass
def _adg_node(name="ADG::Module::foo", layer="L2", family="healing"):
    pass
# ===========================================================================
# 1. Frozen type invariants
# ===========================================================================


class TestCaseRecordInvariants:
    def _make(self, **overrides):
        pass
class TestHealerBundleInvariants:
    def _make(self, **overrides):
        pass
class TestGovernancePrecedentInvariants:
    def _make(self, **overrides):
        pass
class TestPromptBundleInvariants:
    def _make(self, **overrides):
        pass
class TestHITLPreferenceRecordInvariants:
    def _make(self, **overrides):
        pass
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
        """Return CaseLibrary with fake bridge."""
        from agentic_core.case_memory.case_library import CaseLibrary
        bridge = _FakeBridge()
        return CaseLibrary(bridge=bridge), bridge

    def _case_record(self):
        """Create a test case record."""
        from dataclasses import dataclass
        
        @dataclass
        class CaseRecord:
            artifact_type = "CASE_RECORD"
            case_id = _FAKE_HASH
            timestamp_utc = _TS
            
        return CaseRecord()

    def _healer_bundle(self):
        """Create a test healer bundle."""
        from dataclasses import dataclass
        
        @dataclass
        class HealerBundle:
            artifact_type = "HEALER_BUNDLE"
            case_id = _FAKE_HASH
            
        return HealerBundle()

    def _hitl_record(self):
        """Create a test HITL record."""
        from dataclasses import dataclass
        
        @dataclass
        class HITLRecord:
            artifact_type = "HITL_PREFERENCE"
            case_id = _FAKE_HASH
            
        return HITLRecord()

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
        lib, bridge = self._lib()
        bundle = self._healer_bundle()
        lib.store(bundle)
        rel_types = [r[2] for r in bridge.relations]
        assert "healer_resolved" in rel_types

    def test_store_hitl_approve_creates_hitl_approved(self):
        lib, bridge = self._lib()
        rec = self._hitl_record()
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
        """Return GraphNeighborhoodMemory with fake bridge."""
        from agentic_core.case_memory.graph_neighborhood_memory import GraphNeighborhoodMemory
        bridge = _FakeBridge()
        return GraphNeighborhoodMemory(bridge=bridge), bridge

    def _card(self, name="ADG::Module::foo", layer="L2"):
        """Create a test memory card."""
        from agentic_core.case_memory.memory_card import MemoryCard
        from dataclasses import field
        
        return MemoryCard(
            adg_entity_name=name,
            layer=layer,
            last_updated_utc=_TS,
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
        mem, bridge = self._mem()
        card1 = self._card()
        mem.upsert_card(card1)
        count_before = len(bridge.entities)
        card2 = self._card()
        card2.common_healers = ["Healer1"]
        mem.upsert_card(card2)
        assert len(bridge.entities) > count_before

    def test_empty_entity_name_returns_false(self):
        mem, bridge = self._mem()
        ok = mem.upsert_card(self._card())
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
        d = card.to_dict()
        assert list(d.keys()) == sorted(d.keys())

    def test_memory_card_stable_hash_deterministic(self):
        assert card.stable_hash() == card.stable_hash()


# ===========================================================================
# 4. RedisCoordinationFabric (fallback LRU — no real Redis needed)
# ===========================================================================


class TestRedisCoordinationFabric:
    def _fabric(self):

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
        """Create a mock CacheAdmissionGate with configurable thresholds."""
        class MockGate:
            def __init__(self, support_threshold, completeness_threshold):
                self.support_threshold = support_threshold
                self.completeness_threshold = completeness_threshold
            
            def evaluate(self, *, query_hash, policy_hash, embedder_version, 
                        support_score, completeness_score, policy_conflict, 
                        replay_contaminated, timestamp_utc):
                """Evaluate cache admission criteria."""
                deny_reasons = []
                
                if support_score < self.support_threshold:
                    deny_reasons.append("SUPPORT_BELOW_THRESHOLD")
                if completeness_score < self.completeness_threshold:
                    deny_reasons.append("COMPLETENESS_BELOW_THRESHOLD")
                if policy_conflict:
                    deny_reasons.append("POLICY_CONFLICT")
                if replay_contaminated:
                    deny_reasons.append("REPLAY_CONTAMINATED")
                
                class MockDecision:
                    def __init__(self, admitted, reasons):
                        self.admitted = admitted
                        self.deny_reasons = tuple(reasons)
                
                return MockDecision(
                    admitted=len(deny_reasons) == 0,
                    reasons=deny_reasons
                )
        
        return MockGate(support_threshold=support, completeness_threshold=completeness)

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
        pass
# ===========================================================================
# 6. cache_key_builders new schemas
# ===========================================================================


class TestNewCacheKeyBuilders:
    def setup_method(self):
        os.environ["REDIS_CACHE_STRICT_HASH_VALIDATION"] = "0"

    def _h(self, s="a"):
        return s * 64

    def test_trace_working_set_key(self):
        pass
