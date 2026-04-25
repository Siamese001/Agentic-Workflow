"""Tests for P2 (Jaccard dedup, access-counter) and P3 (consolidation CLI)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from tools.memory.memory_consolidation import (
    ConsolidationPlan,
    apply_plan,
    build_plan,
)
from tools.memory.memory_decay import (
    JACCARD_DEDUP_THRESHOLD,
    jaccard_similarity,
    jaccard_threshold,
)
from tools.memory.sqlite_memory_store import SqliteMemoryStore


@pytest.fixture
def store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> SqliteMemoryStore:
    db = tmp_path / "test_memory.sqlite"
    monkeypatch.setenv("MEMORY_DB", str(db))
    monkeypatch.delenv("MEMORY_JACCARD_THRESHOLD", raising=False)
    monkeypatch.delenv("MEMORY_DECAY_DISABLED", raising=False)
    return SqliteMemoryStore(db)


# ======================================================================
# Jaccard similarity pure math
# ======================================================================


class TestJaccard:
    def test_identical_strings(self) -> None:
        assert jaccard_similarity("hello world foo", "hello world foo") == 1.0

    def test_completely_disjoint(self) -> None:
        assert jaccard_similarity("apple banana cherry", "dog elephant frog") == 0.0

    def test_empty_returns_zero(self) -> None:
        assert jaccard_similarity("", "hello world") == 0.0
        assert jaccard_similarity("hello world", "") == 0.0
        assert jaccard_similarity("", "") == 0.0

    def test_case_insensitive(self) -> None:
        assert jaccard_similarity("Hello World", "hello world") == 1.0

    def test_word_order_irrelevant(self) -> None:
        assert jaccard_similarity("foo bar baz", "baz bar foo") == 1.0

    def test_short_tokens_filtered(self) -> None:
        # "is" and "a" under 3 chars are dropped, so these are identical on content words
        sim = jaccard_similarity("this is a test", "test this")
        assert sim == pytest.approx(1.0)

    def test_partial_overlap(self) -> None:
        # {hello, world, foo} vs {hello, world, bar}: inter=2, union=4 -> 0.5
        sim = jaccard_similarity("hello world foo", "hello world bar")
        assert sim == pytest.approx(0.5)

    def test_default_threshold_constant(self) -> None:
        assert JACCARD_DEDUP_THRESHOLD == 0.60

    def test_threshold_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MEMORY_JACCARD_THRESHOLD", "0.75")
        assert jaccard_threshold() == pytest.approx(0.75)


# ======================================================================
# Jaccard dedup on write
# ======================================================================


class TestJaccardDedup:
    def test_exact_duplicate_reinforces(self, store: SqliteMemoryStore) -> None:
        store.create_entities(
            [{"name": "A", "entityType": "general", "observations": ["the quick brown fox jumps"]}]
        )
        store.add_observations([{"entityName": "A", "contents": ["the quick brown fox jumps"]}])
        with store.connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM observations WHERE entity_name='A'").fetchone()[0]
        assert count == 1

    def test_near_duplicate_reinforces_not_inserts(self, store: SqliteMemoryStore) -> None:
        """Re-phrased observation with high token overlap should reinforce."""
        store.create_entities(
            [
                {
                    "name": "A",
                    "entityType": "general",
                    "observations": ["fixed the cache lookup bug in replay key"],
                }
            ]
        )
        # Same 6 content tokens (fixed cache lookup bug replay key) plus one new — Jaccard ~0.857 >= 0.60
        store.add_observations(
            [{"entityName": "A", "contents": ["fixed cache lookup bug replay key yesterday"]}]
        )
        with store.connection() as conn:
            rows = conn.execute("SELECT content FROM observations WHERE entity_name='A'").fetchall()
        assert len(rows) == 1, f"expected 1 obs after near-dup merge, got {[r[0] for r in rows]}"

    def test_genuinely_different_observation_inserts(self, store: SqliteMemoryStore) -> None:
        store.create_entities(
            [{"name": "A", "entityType": "general", "observations": ["fixed cache lookup bug"]}]
        )
        store.add_observations([{"entityName": "A", "contents": ["added unit test for decay function"]}])
        with store.connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM observations WHERE entity_name='A'").fetchone()[0]
        assert count == 2

    def test_near_duplicate_bumps_confidence(self, store: SqliteMemoryStore) -> None:
        store.create_entities(
            [{"name": "A", "entityType": "general", "observations": ["shared alpha beta gamma delta"]}]
        )
        # Age it so a bump has room to grow
        past = time.time() - 10 * 86400
        with store.connection() as conn:
            conn.execute("UPDATE observations SET last_reinforced = ? WHERE entity_name='A'", (past,))
            before = conn.execute("SELECT confidence FROM observations WHERE entity_name='A'").fetchone()[0]
        store.add_observations([{"entityName": "A", "contents": ["shared alpha beta gamma delta epsilon"]}])
        with store.connection() as conn:
            after_rows = conn.execute(
                "SELECT confidence, last_reinforced FROM observations WHERE entity_name='A'"
            ).fetchall()
        # Still one row (merged); confidence reflects reinforcement.
        assert len(after_rows) == 1
        assert after_rows[0][0] > before * 0.5  # reinforced > pure decay

    def test_threshold_override_prevents_merge(
        self, store: SqliteMemoryStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Raising Jaccard threshold to 0.95 treats moderate overlap as new."""
        monkeypatch.setenv("MEMORY_JACCARD_THRESHOLD", "0.95")
        store.create_entities([{"name": "A", "entityType": "general", "observations": ["hello world"]}])
        # Jaccard ~0.5 (< 0.95) -> inserts
        store.add_observations([{"entityName": "A", "contents": ["hello universe"]}])
        with store.connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM observations WHERE entity_name='A'").fetchone()[0]
        assert count == 2


# ======================================================================
# Access counter
# ======================================================================


class TestAccessCounter:
    def test_load_entity_increments(self, store: SqliteMemoryStore) -> None:
        store.create_entities([{"name": "A", "entityType": "general", "observations": []}])
        for _ in range(3):
            assert store.load_entity("A") is not None
        with store.connection() as conn:
            ac = conn.execute("SELECT access_count FROM entities WHERE name='A'").fetchone()[0]
        assert ac == 3

    def test_access_count_column_present(self, store: SqliteMemoryStore) -> None:
        with store.connection() as conn:
            ent_cols = {r[1] for r in conn.execute("PRAGMA table_info(entities)")}
            obs_cols = {r[1] for r in conn.execute("PRAGMA table_info(observations)")}
        assert "access_count" in ent_cols
        assert "access_count" in obs_cols


# ======================================================================
# top_entities ranking
# ======================================================================


class TestTopEntities:
    def test_frequently_accessed_ranks_higher(self, store: SqliteMemoryStore) -> None:
        store.create_entities(
            [
                {"name": "Hot", "entityType": "general", "observations": []},
                {"name": "Cold", "entityType": "general", "observations": []},
            ]
        )
        # Access Hot 10 times; Cold once.
        for _ in range(10):
            store.load_entity("Hot")
        store.load_entity("Cold")
        top = store.top_entities(limit=5)
        names = [e["name"] for e in top]
        assert names.index("Hot") < names.index("Cold")

    def test_limit_respected(self, store: SqliteMemoryStore) -> None:
        for i in range(10):
            store.create_entities([{"name": f"E{i}", "entityType": "general", "observations": []}])
        assert len(store.top_entities(limit=3)) == 3

    def test_type_filter(self, store: SqliteMemoryStore) -> None:
        store.create_entities(
            [
                {"name": "R1", "entityType": "ConstitutionalRule", "observations": []},
                {"name": "G1", "entityType": "general", "observations": []},
            ]
        )
        top = store.top_entities(limit=10, entity_types=("ConstitutionalRule",))
        names = [e["name"] for e in top]
        assert names == ["R1"]


# ======================================================================
# Consolidation CLI / plan builder
# ======================================================================


class TestConsolidation:
    def test_dry_run_plan_is_a_dataclass(self, store: SqliteMemoryStore) -> None:
        store.create_entities([{"name": "A", "entityType": "general", "observations": ["x"]}])
        plan = build_plan(store)
        assert isinstance(plan, ConsolidationPlan)

    def test_plan_does_not_mutate_db(self, store: SqliteMemoryStore) -> None:
        store.create_entities([{"name": "A", "entityType": "general", "observations": ["x", "y", "z"]}])
        with store.connection() as conn:
            before = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        build_plan(store)
        with store.connection() as conn:
            after = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        assert before == after

    def test_merges_near_duplicate_observations(
        self, store: SqliteMemoryStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """With Jaccard dedup ON at the WRITE level, we need to bypass it
        here to seed a polluted DB for consolidation to repair."""
        # Set write-time dedup to a level that won't catch these pairs,
        # simulating a pre-dedup legacy DB.
        monkeypatch.setenv("MEMORY_JACCARD_THRESHOLD", "0.99")
        store.create_entities(
            [
                {
                    "name": "A",
                    "entityType": "general",
                    "observations": [
                        "fixed the cache bug",
                        "fixed cache bug yesterday",
                        "completely unrelated note",
                    ],
                }
            ]
        )
        # Build plan at merge_threshold=0.50 so the two near-dups cluster.
        plan = build_plan(store, merge_threshold=0.50)
        assert len(plan.merge_groups) == 1
        assert len(plan.merge_groups[0]) == 2

        result = apply_plan(store, plan)
        assert result["merged_observations"] == 1

        with store.connection() as conn:
            remaining = conn.execute("SELECT COUNT(*) FROM observations WHERE entity_name='A'").fetchone()[0]
        assert remaining == 2  # 3 - 1 merged

    def test_prunes_low_confidence_entity(self, store: SqliteMemoryStore) -> None:
        store.create_entities([{"name": "Stale", "entityType": "general", "observations": []}])
        # Age it heavily: ~100 days with 14-day half-life -> effective ~0.007
        past = time.time() - 100 * 86400
        with store.connection() as conn:
            conn.execute("UPDATE entities SET last_reinforced = ? WHERE name='Stale'", (past,))
        plan = build_plan(store, prune_floor=0.05)
        assert "Stale" in plan.prune_entity_names

        apply_plan(store, plan)
        with store.connection() as conn:
            still = conn.execute("SELECT COUNT(*) FROM entities WHERE name='Stale'").fetchone()[0]
        assert still == 0

    def test_protected_types_never_pruned(self, store: SqliteMemoryStore) -> None:
        store.create_entities([{"name": "Rule", "entityType": "ConstitutionalRule", "observations": []}])
        # Force absurd age — doesn't matter, protected types have inf half-life
        past = time.time() - 10000 * 86400
        with store.connection() as conn:
            conn.execute(
                "UPDATE entities SET confidence = 0.001, last_reinforced = ? WHERE name='Rule'",
                (past,),
            )
        plan = build_plan(store, prune_floor=0.5)
        assert "Rule" not in plan.prune_entity_names

    def test_idempotent(self, store: SqliteMemoryStore) -> None:
        store.create_entities([{"name": "A", "entityType": "general", "observations": ["x", "y"]}])
        plan1 = build_plan(store)
        apply_plan(store, plan1)
        plan2 = build_plan(store)
        # Second run should find no new merge groups and no prunes
        assert plan2.merge_groups == []
        assert plan2.prune_observation_ids == []
        assert plan2.prune_entity_names == []
