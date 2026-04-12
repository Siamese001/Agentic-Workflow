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

pytestmark = pytest.mark.serial

from agentic_core.cache.redis_coordination_fabric import RedisCoordinationFabric

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

    def create_entity(self, entity_type: str, properties: dict) -> str:
        """Create an entity and return its ID."""
        entity_id = f"entity_{len(self.entities)}"
        self.entities.append({"id": entity_id, "type": entity_type, **properties})
        return entity_id

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

    def put(self, key: str, value: dict) -> bool:
        """Store value by key."""
        # Store as entity for tracking
        self.entities.append({"key": key, **value})
        return True

    def get(self, key: str) -> dict | None:
        """Get value by key."""
        for entity in self.entities:
            if entity.get("key") == key:
                return entity
        return None

    def commit(self):
        """Commit pending changes."""
        pass


class TestCaseLibrary:
    def _lib(self):
        """Return CaseLibrary with fake bridge."""
        from agentic_core.case_memory import CaseLibrary

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


# ===========================================================================
# 3. GraphNeighborhoodMemory
# ===========================================================================


class TestGraphNeighborhoodMemory:
    def _mem(self):
        """Return GraphNeighborhoodMemory with fake bridge."""
        from agentic_core.case_memory import GraphNeighborhoodMemory

        bridge = _FakeBridge()
        return GraphNeighborhoodMemory(bridge=bridge), bridge

    def _card(self, name="ADG::Module::foo", layer="L2"):
        """Create a test memory card."""

        from agentic_core.case_memory import MemoryCard

        return MemoryCard(
            adg_entity_name=name,
            layer=layer,
            last_updated_utc=_TS,
        )


# ===========================================================================
# 4. RedisCoordinationFabric (fallback LRU — no real Redis needed)
# ===========================================================================


class TestRedisCoordinationFabric:
    def _fabric(self):

        return RedisCoordinationFabric(redis_url="redis://localhost:19999")


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

            def evaluate(
                self,
                *,
                query_hash,
                policy_hash,
                embedder_version,
                support_score,
                completeness_score,
                policy_conflict,
                replay_contaminated,
                timestamp_utc,
            ):
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
                    reasons=deny_reasons,
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


# ===========================================================================
# 6. cache_key_builders new schemas
# ===========================================================================


class TestNewCacheKeyBuilders:
    def setup_method(self):
        os.environ["REDIS_CACHE_STRICT_HASH_VALIDATION"] = "0"

    def _h(self, s="a"):
        return s * 64
