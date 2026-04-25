"""Unit tests for memory_decay + SqliteMemoryStore decay integration."""

from __future__ import annotations

import math
import os
import time
from pathlib import Path

import pytest

from tools.memory.memory_decay import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    confidence_threshold,
    effective_confidence,
    half_life_seconds,
    reinforced_confidence,
)
from tools.memory.sqlite_memory_store import SqliteMemoryStore


# ======================================================================
# Pure decay math
# ======================================================================


class TestHalfLife:
    def test_protected_types_never_decay(self) -> None:
        assert math.isinf(half_life_seconds("ConstitutionalRule"))
        assert math.isinf(half_life_seconds("ArchitectureLayer"))
        assert math.isinf(half_life_seconds("ProceduralPattern"))

    def test_general_is_short_lived(self) -> None:
        assert half_life_seconds("general") == 14 * 86400

    def test_unknown_type_falls_back_to_general(self) -> None:
        assert half_life_seconds("UnknownType") == half_life_seconds("general")

    def test_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MEMORY_HALF_LIFE_OVERRIDE", "general=1.0,Foo=0.5")
        assert half_life_seconds("general") == 86400
        assert half_life_seconds("Foo") == 43200


class TestEffectiveConfidence:
    def test_fresh_memory_full_confidence(self) -> None:
        now = time.time()
        assert effective_confidence(1.0, now, "general", now=now) == pytest.approx(1.0)

    def test_protected_type_no_decay_across_a_year(self) -> None:
        past = time.time() - 365 * 86400
        now = time.time()
        got = effective_confidence(1.0, past, "ConstitutionalRule", now=now)
        assert got == pytest.approx(1.0)

    def test_one_half_life_halves_confidence(self) -> None:
        """After exactly 14 days, a 'general' memory should be at 0.5."""
        now = time.time()
        past = now - 14 * 86400
        got = effective_confidence(1.0, past, "general", now=now)
        assert got == pytest.approx(0.5, abs=1e-6)

    def test_two_half_lives_quarter(self) -> None:
        now = time.time()
        past = now - 28 * 86400
        got = effective_confidence(1.0, past, "general", now=now)
        assert got == pytest.approx(0.25, abs=1e-6)

    def test_clamps_to_unit_range(self) -> None:
        now = time.time()
        assert effective_confidence(2.0, now, "general", now=now) == 1.0
        assert effective_confidence(-0.5, now, "general", now=now) == 0.0

    def test_disabled_via_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MEMORY_DECAY_DISABLED", "1")
        now = time.time()
        past = now - 365 * 86400
        got = effective_confidence(0.8, past, "general", now=now)
        assert got == pytest.approx(0.8)


class TestConfidenceThreshold:
    def test_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MEMORY_CONFIDENCE_THRESHOLD", raising=False)
        assert confidence_threshold() == DEFAULT_CONFIDENCE_THRESHOLD

    def test_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MEMORY_CONFIDENCE_THRESHOLD", "0.5")
        assert confidence_threshold() == pytest.approx(0.5)

    def test_invalid_env_falls_back_to_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MEMORY_CONFIDENCE_THRESHOLD", "not-a-float")
        assert confidence_threshold() == DEFAULT_CONFIDENCE_THRESHOLD


class TestReinforcement:
    def test_bumps_up_from_decayed(self) -> None:
        now = time.time()
        past = now - 14 * 86400  # one half-life -> effective 0.5
        new = reinforced_confidence(1.0, past, "general", now=now, bump=0.1)
        # 0.5 (decayed) + 0.1 (bump) = 0.6
        assert new == pytest.approx(0.6, abs=1e-6)

    def test_cannot_exceed_one(self) -> None:
        now = time.time()
        new = reinforced_confidence(0.95, now, "general", now=now, bump=0.5)
        assert new == 1.0


# ======================================================================
# Store integration
# ======================================================================


@pytest.fixture
def store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> SqliteMemoryStore:
    db = tmp_path / "test_memory.sqlite"
    monkeypatch.setenv("MEMORY_DB", str(db))
    monkeypatch.delenv("MEMORY_DECAY_DISABLED", raising=False)
    monkeypatch.delenv("MEMORY_CONFIDENCE_THRESHOLD", raising=False)
    monkeypatch.delenv("MEMORY_HALF_LIFE_OVERRIDE", raising=False)
    return SqliteMemoryStore(db)


class TestSchemaMigration:
    def test_columns_exist_after_init(self, store: SqliteMemoryStore) -> None:
        with store.connection() as conn:
            ent_cols = {r[1] for r in conn.execute("PRAGMA table_info(entities)")}
            obs_cols = {r[1] for r in conn.execute("PRAGMA table_info(observations)")}
        assert "confidence" in ent_cols
        assert "last_reinforced" in ent_cols
        assert "confidence" in obs_cols
        assert "last_reinforced" in obs_cols

    def test_migration_is_idempotent(self, store: SqliteMemoryStore) -> None:
        # Second init on same DB should not raise
        SqliteMemoryStore(store.db_path)
        SqliteMemoryStore(store.db_path)

    def test_backfills_last_reinforced_from_legacy_rows(self, tmp_path: Path) -> None:
        """Simulate a pre-migration DB: insert entity with legacy schema,
        then open via SqliteMemoryStore and confirm last_reinforced is back-filled.
        """
        import sqlite3

        db = tmp_path / "legacy.sqlite"
        conn = sqlite3.connect(str(db))
        conn.executescript(
            """
            CREATE TABLE entities (
                name TEXT PRIMARY KEY, entity_type TEXT NOT NULL DEFAULT 'general',
                created_at REAL NOT NULL, updated_at REAL NOT NULL
            );
            CREATE TABLE observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT, entity_name TEXT NOT NULL,
                content TEXT NOT NULL, created_at REAL NOT NULL, UNIQUE(entity_name, content)
            );
            CREATE TABLE relations (
                from_entity TEXT NOT NULL, relation_type TEXT NOT NULL,
                to_entity TEXT NOT NULL, created_at REAL NOT NULL,
                PRIMARY KEY(from_entity, relation_type, to_entity)
            );
            """
        )
        ts = 1_700_000_000.0
        conn.execute(
            "INSERT INTO entities (name, entity_type, created_at, updated_at) "
            "VALUES ('Legacy', 'general', ?, ?)",
            (ts, ts),
        )
        conn.commit()
        conn.close()

        # Open via store — triggers migration.
        SqliteMemoryStore(db)

        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT confidence, last_reinforced FROM entities WHERE name='Legacy'").fetchone()
        conn.close()
        assert row[0] == pytest.approx(1.0)  # default
        assert row[1] == pytest.approx(ts)  # back-filled from updated_at


class TestReadTimeFilter:
    def test_fresh_entity_visible(self, store: SqliteMemoryStore) -> None:
        store.create_entities([{"name": "A", "entityType": "general", "observations": ["obs1"]}])
        e = store.load_entity("A")
        assert e is not None
        assert e["effectiveConfidence"] == pytest.approx(1.0, abs=1e-4)

    def test_old_general_entity_hidden_below_threshold(
        self, store: SqliteMemoryStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Manually stamp a 'general' entity 60 days old — should be below 0.3 threshold."""
        store.create_entities([{"name": "Stale", "entityType": "general", "observations": []}])
        past = time.time() - 60 * 86400
        with store.connection() as conn:
            conn.execute("UPDATE entities SET last_reinforced = ? WHERE name='Stale'", (past,))
        # 60 days with 14-day half-life: 0.5 ** (60/14) = ~0.0504 < 0.3
        assert store.load_entity("Stale") is None

    def test_old_protected_entity_still_visible(self, store: SqliteMemoryStore) -> None:
        """Protected types never decay — an ancient ConstitutionalRule is still returned."""
        store.create_entities([{"name": "Rule", "entityType": "ConstitutionalRule", "observations": ["r"]}])
        ancient = time.time() - 365 * 86400
        with store.connection() as conn:
            conn.execute("UPDATE entities SET last_reinforced = ? WHERE name='Rule'", (ancient,))
        e = store.load_entity("Rule")
        assert e is not None
        assert e["effectiveConfidence"] == pytest.approx(1.0)

    def test_include_low_confidence_bypass(self, store: SqliteMemoryStore) -> None:
        store.create_entities([{"name": "Stale", "entityType": "general", "observations": []}])
        past = time.time() - 60 * 86400
        with store.connection() as conn:
            conn.execute("UPDATE entities SET last_reinforced = ? WHERE name='Stale'", (past,))
        assert store.load_entity("Stale", include_low_confidence=True) is not None

    def test_read_graph_hides_and_drops_dangling_relations(self, store: SqliteMemoryStore) -> None:
        store.create_entities(
            [
                {"name": "Fresh", "entityType": "general", "observations": []},
                {"name": "Stale", "entityType": "general", "observations": []},
            ]
        )
        store.create_relations([{"from": "Fresh", "to": "Stale", "relationType": "references"}])
        past = time.time() - 60 * 86400
        with store.connection() as conn:
            conn.execute("UPDATE entities SET last_reinforced = ? WHERE name='Stale'", (past,))
        g = store.read_graph()
        names = {e["name"] for e in g["entities"]}
        assert "Fresh" in names
        assert "Stale" not in names
        # Relation to hidden entity is dropped
        assert g["relations"] == []


class TestStoreReinforcement:
    def test_reinforcing_bumps_stored_confidence(self, store: SqliteMemoryStore) -> None:
        """A single reinforce of a very-stale entity does NOT cross the
        threshold in one call (by design — matches Memento). But it DOES
        raise stored confidence above the decayed floor. Repeated reinforces
        eventually bring it back into the active surface."""
        store.create_entities([{"name": "A", "entityType": "general", "observations": []}])
        past = time.time() - 60 * 86400  # ~4 half-lives -> ~0.05
        with store.connection() as conn:
            conn.execute("UPDATE entities SET last_reinforced = ? WHERE name='A'", (past,))
            before = conn.execute("SELECT confidence FROM entities WHERE name='A'").fetchone()[0]

        assert store.load_entity("A") is None  # hidden below threshold

        assert store.reinforce("A") is True

        with store.connection() as conn:
            after = conn.execute("SELECT confidence FROM entities WHERE name='A'").fetchone()[0]
        # Stored confidence was decayed-then-bumped: 0.05 + 0.10 = 0.15
        assert after < before  # below original stored value
        assert after > 0.10  # but above the decayed floor

        # Entity is still below threshold after one reinforce
        assert store.load_entity("A") is None
        # But readable with bypass
        assert store.load_entity("A", include_low_confidence=True) is not None

        # Two more reinforces push it over the threshold (0.15 -> 0.25 -> 0.35)
        store.reinforce("A")
        store.reinforce("A")
        e = store.load_entity("A")
        assert e is not None
        assert e["effectiveConfidence"] > 0.30

    def test_duplicate_observation_reinforces(self, store: SqliteMemoryStore) -> None:
        store.create_entities([{"name": "A", "entityType": "general", "observations": ["obs-v1"]}])
        # Age it
        past = time.time() - 10 * 86400
        with store.connection() as conn:
            conn.execute("UPDATE observations SET last_reinforced = ? WHERE content='obs-v1'", (past,))
            before = conn.execute(
                "SELECT last_reinforced FROM observations WHERE content='obs-v1'"
            ).fetchone()[0]
        # Re-adding same observation should reinforce, not insert duplicate
        store.add_observations([{"entityName": "A", "contents": ["obs-v1"]}])
        with store.connection() as conn:
            after = conn.execute(
                "SELECT last_reinforced FROM observations WHERE content='obs-v1'"
            ).fetchone()[0]
            count = conn.execute("SELECT COUNT(*) FROM observations WHERE content='obs-v1'").fetchone()[0]
        assert count == 1
        assert after > before


class TestBackCompat:
    """Existing callers must keep working with default args."""

    def test_search_nodes_signature_back_compat(self, store: SqliteMemoryStore) -> None:
        store.create_entities([{"name": "hello", "entityType": "general", "observations": []}])
        # Old call signature — query only
        r = store.search_nodes("hello")
        assert len(r) == 1

    def test_get_stats_still_works(self, store: SqliteMemoryStore) -> None:
        store.create_entities([{"name": "a", "entityType": "general", "observations": []}])
        s = store.get_stats()
        assert s["total_entities"] == 1
