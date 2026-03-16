"""Unit tests for tools/memory/sqlite_memory_store.py.

SqliteMemoryStore is the shared SSOT for all knowledge_graph.sqlite writes.
It must be thoroughly tested because both the MCP server and GraphMemoryBridge
depend on it for persistence correctness.
"""
from __future__ import annotations

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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_authorize_and_execute("p2", "test_sqlite_memory_store", "execution_auth")
_emit_validates_capability("p2", "test_sqlite_memory_store", "capability_check")
_emit_routes_to_capability("p2", "test_sqlite_memory_store", "capability_route")
_emit_writes_via_uwg("p2", "test_sqlite_memory_store", "uwg_write")
_emit_blocks_direct_write("p2", "test_sqlite_memory_store", "direct_write_block")
_emit_records_tool_invocation("p2", "test_sqlite_memory_store", "tool_invocation")
_emit_captures_execution_output("p2", "test_sqlite_memory_store", "exec_output")
_emit_dispatches_agent("p3", "test_sqlite_memory_store", "agent_dispatch")
_emit_coordinates_agents("p3", "test_sqlite_memory_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_sqlite_memory_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_sqlite_memory_store", "healing_outcome")
_emit_escalates_failure("p3", "test_sqlite_memory_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_sqlite_memory_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_sqlite_memory_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_sqlite_memory_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_sqlite_memory_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_sqlite_memory_store", "eval_metric")
_emit_stores_embedding("p4", "test_sqlite_memory_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_sqlite_memory_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_sqlite_memory_store", "exec_snapshot_link")
from tools.memory.sqlite_memory_store import SqliteMemoryStore

_emit_records_execution_trace("p0", "evidence", "test_sqlite_memory_store")
_emit_applies_guardrail("p0", "test_sqlite_memory_store", "p0_governance")
_emit_reads_policy_state("p0", "test_sqlite_memory_store", "policy_binding")
_emit_snapshots_state("p0", "test_sqlite_memory_store", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_sqlite_memory_store", "p4obs", "metric_1")
_emit_emits_metric_event("test_sqlite_memory_store", "p4obs", "metric_2")
_emit_emits_metric_event("test_sqlite_memory_store", "p4obs", "metric_3")
_emit_emits_metric_event("test_sqlite_memory_store", "p4obs", "metric_4")
_emit_emits_metric_event("test_sqlite_memory_store", "p4obs", "metric_5")
_emit_emits_metric_event("test_sqlite_memory_store", "p4obs", "metric_6")
_emit_records_incident_event("test_sqlite_memory_store", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_sqlite_memory_store", "p4obs", "anomaly")
_emit_writes_observability_log("test_sqlite_memory_store", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_sqlite_memory_store", "p4obs", "mon_state")
_emit_triggers_alert("test_sqlite_memory_store", "p4obs", "alert")
_emit_links_incident_trace("test_sqlite_memory_store", "p4obs", "trace_link")
_emit_captures_pattern("test_sqlite_memory_store", "p3lm", "pattern")
_emit_records_learning_event("test_sqlite_memory_store", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_sqlite_memory_store", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_sqlite_memory_store", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_sqlite_memory_store", "p3lm", "routing")
_emit_improves_agent_policy("test_sqlite_memory_store", "p3lm", "policy")
_emit_stores_learning_state("test_sqlite_memory_store", "p3lm", "state")
_emit_records_execution_trace("test_sqlite_memory_store", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_sqlite_memory_store", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_sqlite_memory_store", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_sqlite_memory_store", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_sqlite_memory_store", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_sqlite_memory_store", "env_read", "p2_env_1")
_emit_reads_environ("test_sqlite_memory_store", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_sqlite_memory_store", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_sqlite_memory_store", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_sqlite_memory_store", "context_pull")
_emit_pulls_context("p1", "test_sqlite_memory_store", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_sqlite_memory_store", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_sqlite_memory_store", "uwg_term_2")
_emit_writes_through("p1", "test_sqlite_memory_store", "write_through")
_emit_writes_through("p1", "test_sqlite_memory_store", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_sqlite_memory_store", "safety_validation")
_emit_invokes_eval("p1", "test_sqlite_memory_store", "eval_call")
_emit_proposal_commits_routing("p1", "test_sqlite_memory_store", "routing_commit")
emit_replay_key("p0", "test_sqlite_memory_store")
emit_determinism_digest("p0", "test_sqlite_memory_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@pytest.fixture()
def store(tmp_path):
    """Fresh SqliteMemoryStore backed by a temp file."""
    return SqliteMemoryStore(tmp_path / "test_kg.sqlite")


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class TestSchema:
    def test_tables_created_on_init(self, store):
        with store.connection() as conn:
            tables = {
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
        assert {"entities", "observations", "relations"}.issubset(tables)

    def test_idempotent_init(self, tmp_path):
        """Constructing SqliteMemoryStore twice on the same db must not raise."""
        db = tmp_path / "idempotent.sqlite"
        SqliteMemoryStore(db)
        SqliteMemoryStore(db)


# ---------------------------------------------------------------------------
# create_entities
# ---------------------------------------------------------------------------

class TestCreateEntities:
    def test_single_entity_created(self, store):
        result = store.create_entities([{"name": "A", "entityType": "Agent"}])
        assert result["created"] == ["A"]
        assert result["skipped_existing"] == []

    def test_duplicate_entity_skipped(self, store):
        store.create_entities([{"name": "A", "entityType": "Agent"}])
        result = store.create_entities([{"name": "A", "entityType": "Agent"}])
        assert result["skipped_existing"] == ["A"]
        assert result["created"] == []

    def test_observations_stored_with_entity(self, store):
        store.create_entities([{"name": "B", "entityType": "Agent", "observations": ["obs1", "obs2"]}])
        with store.connection() as conn:
            obs = [r[0] for r in conn.execute(
                "SELECT content FROM observations WHERE entity_name='B'"
            ).fetchall()]
        assert set(obs) == {"obs1", "obs2"}

    def test_blank_name_skipped(self, store):
        result = store.create_entities([{"name": "", "entityType": "X"}])
        assert result["created"] == []

    def test_multiple_entities(self, store):
        entities = [{"name": f"E{i}", "entityType": "T"} for i in range(10)]
        result = store.create_entities(entities)
        assert len(result["created"]) == 10

    def test_entity_count_in_db(self, store):
        store.create_entities([{"name": "X"}, {"name": "Y"}, {"name": "Z"}])
        with store.connection() as conn:
            n = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        assert n == 3


# ---------------------------------------------------------------------------
# add_observations
# ---------------------------------------------------------------------------

class TestAddObservations:
    def test_adds_to_existing_entity(self, store):
        store.create_entities([{"name": "E", "entityType": "A"}])
        result = store.add_observations([{"entityName": "E", "contents": ["o1", "o2"]}])
        assert result["added_observations"]["E"] == 2

    def test_creates_entity_if_missing(self, store):
        store.add_observations([{"entityName": "Ghost", "contents": ["obs"]}])
        entity = store.load_entity("Ghost")
        assert entity is not None
        assert "obs" in entity["observations"]

    def test_duplicate_observation_not_doubled(self, store):
        store.create_entities([{"name": "D", "entityType": "A"}])
        store.add_observations([{"entityName": "D", "contents": ["dup"]}])
        store.add_observations([{"entityName": "D", "contents": ["dup"]}])
        with store.connection() as conn:
            n = conn.execute(
                "SELECT COUNT(*) FROM observations WHERE entity_name='D' AND content='dup'"
            ).fetchone()[0]
        assert n == 1

    def test_blank_entity_name_skipped(self, store):
        result = store.add_observations([{"entityName": "", "contents": ["x"]}])
        assert result["added_observations"] == {}


# ---------------------------------------------------------------------------
# create_relations
# ---------------------------------------------------------------------------

class TestCreateRelations:
    def test_relation_created(self, store):
        store.create_entities([{"name": "F"}, {"name": "G"}])
        result = store.create_relations([{"from": "F", "to": "G", "relationType": "USES"}])
        assert len(result["created_relations"]) == 1
        assert result["created_relations"][0]["relationType"] == "USES"

    def test_auto_creates_missing_entities(self, store):
        store.create_relations([{"from": "NewA", "to": "NewB", "relationType": "R"}])
        assert store.load_entity("NewA") is not None
        assert store.load_entity("NewB") is not None

    def test_duplicate_relation_not_duplicated(self, store):
        store.create_entities([{"name": "H"}, {"name": "I"}])
        store.create_relations([{"from": "H", "to": "I", "relationType": "X"}])
        store.create_relations([{"from": "H", "to": "I", "relationType": "X"}])
        with store.connection() as conn:
            n = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
        assert n == 1

    def test_blank_from_or_to_skipped(self, store):
        result = store.create_relations([{"from": "", "to": "Z", "relationType": "R"}])
        assert result["created_relations"] == []


# ---------------------------------------------------------------------------
# search_nodes
# ---------------------------------------------------------------------------

class TestSearchNodes:
    def test_finds_by_name(self, store):
        store.create_entities([{"name": "UniqueXYZ", "entityType": "A"}])
        results = store.search_nodes("UniqueXYZ")
        assert any(e["name"] == "UniqueXYZ" for e in results)

    def test_finds_by_observation(self, store):
        store.create_entities([{"name": "M", "entityType": "A", "observations": ["special_token_999"]}])
        results = store.search_nodes("special_token_999")
        assert len(results) > 0

    def test_returns_empty_for_no_match(self, store):
        results = store.search_nodes("zzz_nonexistent_zzz")
        assert results == []

    def test_case_insensitive(self, store):
        store.create_entities([{"name": "CamelCase", "entityType": "A"}])
        results = store.search_nodes("camelcase")
        assert any(e["name"] == "CamelCase" for e in results)


# ---------------------------------------------------------------------------
# open_nodes / load_entity
# ---------------------------------------------------------------------------

class TestOpenNodes:
    def test_load_existing_entity(self, store):
        store.create_entities([{"name": "L", "entityType": "T", "observations": ["o"]}])
        entity = store.load_entity("L")
        assert entity is not None
        assert entity["name"] == "L"
        assert "o" in entity["observations"]

    def test_load_missing_entity_returns_none(self, store):
        assert store.load_entity("DoesNotExist") is None

    def test_open_nodes_batch(self, store):
        store.create_entities([{"name": "P"}, {"name": "Q"}])
        result = store.open_nodes(["P", "Q", "Missing"])
        assert len(result["entities"]) == 2
        assert "Missing" in result["not_found"]


# ---------------------------------------------------------------------------
# delete operations
# ---------------------------------------------------------------------------

class TestDeleteOperations:
    def test_delete_entity_removes_it(self, store):
        store.create_entities([{"name": "Del"}])
        store.delete_entities(["Del"])
        assert store.load_entity("Del") is None

    def test_delete_cascades_observations(self, store):
        store.create_entities([{"name": "Cascade", "observations": ["o1"]}])
        store.delete_entities(["Cascade"])
        with store.connection() as conn:
            n = conn.execute(
                "SELECT COUNT(*) FROM observations WHERE entity_name='Cascade'"
            ).fetchone()[0]
        assert n == 0

    def test_delete_not_found(self, store):
        result = store.delete_entities(["NeverExisted"])
        assert "NeverExisted" in result["not_found"]

    def test_delete_observation(self, store):
        store.create_entities([{"name": "W", "observations": ["keep", "remove"]}])
        store.delete_observations([{"entityName": "W", "observations": ["remove"]}])
        entity = store.load_entity("W")
        assert "remove" not in entity["observations"]
        assert "keep" in entity["observations"]

    def test_delete_relation(self, store):
        store.create_entities([{"name": "R1"}, {"name": "R2"}])
        store.create_relations([{"from": "R1", "to": "R2", "relationType": "LINK"}])
        store.delete_relations([{"from": "R1", "to": "R2", "relationType": "LINK"}])
        with store.connection() as conn:
            n = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
        assert n == 0


# ---------------------------------------------------------------------------
# get_stats
# ---------------------------------------------------------------------------

class TestGetStats:
    def test_stats_reflect_actual_counts(self, store):
        store.create_entities([
            {"name": "S1", "entityType": "T1", "observations": ["a", "b"]},
            {"name": "S2", "entityType": "T2"},
        ])
        store.create_relations([{"from": "S1", "to": "S2", "relationType": "R"}])
        stats = store.get_stats()
        assert stats["total_entities"] == 2
        assert stats["total_observations"] == 2
        assert stats["total_relations"] == 1
        assert "T1" in stats["by_entity_type"]

    def test_stats_empty_store(self, store):
        stats = store.get_stats()
        assert stats["total_entities"] == 0
        assert stats["total_observations"] == 0
        assert stats["total_relations"] == 0


# ---------------------------------------------------------------------------
# cleanup_stale
# ---------------------------------------------------------------------------

class TestCleanupStale:
    def test_stale_entity_removed(self, store):
        import time
        store.create_entities([{"name": "Old"}, {"name": "Fresh"}])
        with store.connection() as conn:
            old_time = time.time() - (40 * 86400)
            conn.execute("UPDATE entities SET updated_at=? WHERE name='Old'", (old_time,))
        result = store.cleanup_stale(older_than_days=30)
        assert "Old" in result["deleted_names"]
        assert store.load_entity("Old") is None
        assert store.load_entity("Fresh") is not None

    def test_protected_types_not_deleted(self, store):
        import time
        store.create_entities([
            {"name": "Protected", "entityType": "ArchitectureLayer"},
            {"name": "Stale", "entityType": "general"},
        ])
        with store.connection() as conn:
            old_time = time.time() - (40 * 86400)
            conn.execute("UPDATE entities SET updated_at=?", (old_time,))
        result = store.cleanup_stale(
            older_than_days=30, protected_types=("ArchitectureLayer",)
        )
        assert "Protected" not in result["deleted_names"]
        assert store.load_entity("Protected") is not None


# ---------------------------------------------------------------------------
# upsert_entity / insert_relation / add_observation helpers
# ---------------------------------------------------------------------------

class TestHelperMethods:
    def test_upsert_entity_creates_then_updates(self, store):
        store.upsert_entity("U", "TypeA", ["obs1"])
        store.upsert_entity("U", "TypeA", ["obs2"])
        entity = store.load_entity("U")
        assert set(entity["observations"]) == {"obs1", "obs2"}

    def test_add_observation_returns_true_on_insert(self, store):
        store.upsert_entity("V", "T")
        assert store.add_observation("V", "new") is True

    def test_add_observation_returns_false_on_duplicate(self, store):
        store.upsert_entity("W2", "T")
        store.add_observation("W2", "dup")
        assert store.add_observation("W2", "dup") is False

    def test_insert_relation_returns_true(self, store):
        store.upsert_entity("N1", "T")
        store.upsert_entity("N2", "T")
        assert store.insert_relation("N1", "LINK", "N2") is True

    def test_insert_relation_returns_false_on_duplicate(self, store):
        store.upsert_entity("N3", "T")
        store.upsert_entity("N4", "T")
        store.insert_relation("N3", "LINK", "N4")
        assert store.insert_relation("N3", "LINK", "N4") is False

    def test_get_entities_by_type(self, store):
        store.create_entities([
            {"name": "AL1", "entityType": "ArchitectureLayer"},
            {"name": "AL2", "entityType": "ArchitectureLayer"},
            {"name": "Other", "entityType": "general"},
        ])
        result = store.get_entities_by_type(("ArchitectureLayer",))
        names = [e["name"] for e in result]
        assert "AL1" in names
        assert "AL2" in names
        assert "Other" not in names
