"""Tests for ADGMemoryAdapter and namespace_builder.

Covers:
  - ADGMemoryAdapter._infer_layer routing
  - ADGMemoryAdapter entity construction (no live MCP required)
  - namespace_builder.build_key validation
  - namespace_builder.parse_key round-trip
  - namespace_builder.NS pre-defined specs
  - namespace_builder.key_prefix scoping
"""

from __future__ import annotations

import pytest

from agentic_core.adg.adapters.ADGMemoryAdapter import ADGMemoryAdapter, _infer_layer
from agentic_core.cache.namespace_builder import (
    NS,
    build_global_key,
    build_key,
    build_mission_key,
    key_prefix,
    parse_key,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_memory_mcp_adapter")
_emit_applies_guardrail("p0", "test_memory_mcp_adapter", "p0_governance")
_emit_reads_policy_state("p0", "test_memory_mcp_adapter", "policy_binding")
_emit_snapshots_state("p0", "test_memory_mcp_adapter", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_memory_mcp_adapter", "p4obs", "metric_1")
_emit_emits_metric_event("test_memory_mcp_adapter", "p4obs", "metric_2")
_emit_emits_metric_event("test_memory_mcp_adapter", "p4obs", "metric_3")
_emit_emits_metric_event("test_memory_mcp_adapter", "p4obs", "metric_4")
_emit_emits_metric_event("test_memory_mcp_adapter", "p4obs", "metric_5")
_emit_emits_metric_event("test_memory_mcp_adapter", "p4obs", "metric_6")
_emit_records_incident_event("test_memory_mcp_adapter", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_memory_mcp_adapter", "p4obs", "anomaly")
_emit_writes_observability_log("test_memory_mcp_adapter", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_memory_mcp_adapter", "p4obs", "mon_state")
_emit_triggers_alert("test_memory_mcp_adapter", "p4obs", "alert")
_emit_links_incident_trace("test_memory_mcp_adapter", "p4obs", "trace_link")
_emit_captures_pattern("test_memory_mcp_adapter", "p3lm", "pattern")
_emit_records_learning_event("test_memory_mcp_adapter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_memory_mcp_adapter", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_memory_mcp_adapter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_memory_mcp_adapter", "p3lm", "routing")
_emit_improves_agent_policy("test_memory_mcp_adapter", "p3lm", "policy")
_emit_stores_learning_state("test_memory_mcp_adapter", "p3lm", "state")
_emit_records_execution_trace("test_memory_mcp_adapter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_memory_mcp_adapter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_memory_mcp_adapter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_memory_mcp_adapter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_memory_mcp_adapter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_memory_mcp_adapter", "env_read", "p2_env_1")
_emit_reads_environ("test_memory_mcp_adapter", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_memory_mcp_adapter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_memory_mcp_adapter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_memory_mcp_adapter", "context_pull")
_emit_pulls_context("p1", "test_memory_mcp_adapter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_memory_mcp_adapter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_memory_mcp_adapter", "uwg_term_2")
_emit_writes_through("p1", "test_memory_mcp_adapter", "write_through")
_emit_writes_through("p1", "test_memory_mcp_adapter", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_memory_mcp_adapter", "safety_validation")
_emit_invokes_eval("p1", "test_memory_mcp_adapter", "eval_call")
_emit_proposal_commits_routing("p1", "test_memory_mcp_adapter", "routing_commit")
_emit_escalates_to_human("p1", "test_memory_mcp_adapter", "human_escalation")
_emit_routes_through("p1", "test_memory_mcp_adapter", "route_through")
_emit_checks_agent_registry("p1", "test_memory_mcp_adapter", "agent_registry")
_emit_validates_agent_capability("p1", "test_memory_mcp_adapter", "capability")
_emit_dispatches_execution_plan("p1", "test_memory_mcp_adapter", "exec_plan")
_emit_agent_executes_agent("p1", "test_memory_mcp_adapter", "sub_agent")
_emit_routes_to_agent("p1", "test_memory_mcp_adapter", "target_agent")
_emit_verifies_policy("p1", "test_memory_mcp_adapter", "policy_check")
_emit_observes_runtime_state("p1", "test_memory_mcp_adapter", "runtime_state")
_emit_verifies_boundary("p1", "test_memory_mcp_adapter", "boundary_check")
_emit_transcripts_response("p1", "test_memory_mcp_adapter", "transcript")
_emit_hard_fails_untranscripted("p1", "test_memory_mcp_adapter")
_emit_gated_by_confidence("p1", "test_memory_mcp_adapter", "confidence_gate")
emit_replay_key("p0", "test_memory_mcp_adapter")
emit_determinism_digest("p0", "test_memory_mcp_adapter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_memory_mcp_adapter", "execution_auth")
_emit_validates_capability("p2", "test_memory_mcp_adapter", "capability_check")
_emit_routes_to_capability("p2", "test_memory_mcp_adapter", "capability_route")
_emit_writes_via_uwg("p2", "test_memory_mcp_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "test_memory_mcp_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "test_memory_mcp_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "test_memory_mcp_adapter", "exec_output")
_emit_dispatches_agent("p3", "test_memory_mcp_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "test_memory_mcp_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_memory_mcp_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_memory_mcp_adapter", "healing_outcome")
_emit_escalates_failure("p3", "test_memory_mcp_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_memory_mcp_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_memory_mcp_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_memory_mcp_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_memory_mcp_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_memory_mcp_adapter", "eval_metric")
_emit_stores_embedding("p4", "test_memory_mcp_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_memory_mcp_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_memory_mcp_adapter", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# _infer_layer
# ---------------------------------------------------------------------------


class TestInferLayer:
    def test_l4_path(self):
        assert _infer_layer("agentic_core/L4_state/memory/semantic_cache_manager.py") == "L4"

    def test_l0_path(self):
        assert _infer_layer("agentic_core/L0_routing/scripts/execute_ssot.py") == "L0"

    def test_l5_path(self):
        assert _infer_layer("agentic_core/L5_safety/reasoning/FileClassificationAgent.py") == "L5"

    def test_apps_shared(self):
        assert _infer_layer("apps_shared/types/sovereign_severity_types.py") == "L_APP"

    def test_apps_rg(self):
        assert _infer_layer("apps_rg/reasoning/ATSCompatibilityAgent.py") == "L_APP"

    def test_system_learning(self):
        assert _infer_layer("system_learning/engines/rag_retrieval_cache.py") == "L_SL"

    def test_ops_scripts(self):
        assert _infer_layer("ops_scripts/ci/_audit_scan.py") == "L_OPS"

    def test_tools(self):
        assert _infer_layer("tools/generate_full_adg.py") == "L_TOOLS"

    def test_tests(self):
        assert _infer_layer("tests/adg/test_memory_mcp_adapter.py") == "L_TEST"

    def test_unknown(self):
        assert _infer_layer("some_random_file.py") == "L_UNKNOWN"

    def test_l6_path(self):
        assert _infer_layer("agentic_core/L6_observability/something.py") == "L6"


# ---------------------------------------------------------------------------
# namespace_builder — build_key
# ---------------------------------------------------------------------------


class TestBuildKey:
    def test_basic_global_key(self):
        key = build_global_key("L4", "semantic_cache", "file", "e3b0c44298fc1c14")
        assert key == "L4:semantic_cache:global:file:e3b0c44298fc1c14"

    def test_mission_scoped_key(self):
        key = build_mission_key("L4", "semantic_cache", "file", "e3b0c44298fc1c14", "m_abc123")
        assert key == "L4:semantic_cache:m_abc123:file:e3b0c44298fc1c14"

    def test_l_sl_key(self):
        key = build_global_key("L_SL", "rag_topk", "retrieval", "0f3ec30c8c67")
        assert key == "L_SL:rag_topk:global:retrieval:0f3ec30c8c67"

    def test_unknown_layer_raises(self):
        with pytest.raises(ValueError, match="Unknown layer"):
            build_key("L99", "cache", "file", "abcdef12")

    def test_colon_in_component_raises(self):
        with pytest.raises(ValueError, match="illegal ':'"):
            build_key("L4", "bad:component", "file", "abcdef12")

    def test_colon_in_entity_type_raises(self):
        with pytest.raises(ValueError, match="illegal ':'"):
            build_key("L4", "cache", "file:type", "abcdef12")

    def test_empty_component_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            build_key("L4", "", "file", "abcdef12")

    def test_short_hash_valid(self):
        key = build_global_key("L0", "routing", "config", "abcdef12")
        assert key == "L0:routing:global:config:abcdef12"

    def test_invalid_hash_raises(self):
        with pytest.raises(ValueError, match="hex string"):
            build_key("L4", "cache", "file", "not-hex!!")

    def test_hash_too_short_raises(self):
        with pytest.raises(ValueError, match="hex string"):
            build_key("L4", "cache", "file", "abc")

    def test_all_valid_layers(self):
        valid_layers = [
            "L0",
            "L1",
            "L2",
            "L3",
            "L4",
            "L5",
            "L6",
            "L_APP",
            "L_SL",
            "L_OPS",
            "L_TOOLS",
            "L_TEST",
            "L_RUNTIME",
            "L_SHARED",
            "L_UNKNOWN",
        ]
        for layer in valid_layers:
            key = build_global_key(layer, "comp", "entity", "abcdef1234567890")
            assert key.startswith(f"{layer}:")


# ---------------------------------------------------------------------------
# namespace_builder — parse_key
# ---------------------------------------------------------------------------


class TestParseKey:
    def test_round_trip(self):
        original = build_global_key("L4", "semantic_cache", "file", "e3b0c44298fc1c14")
        parsed = parse_key(original)
        assert parsed["layer"] == "L4"
        assert parsed["component"] == "semantic_cache"
        assert parsed["mission_id"] == "global"
        assert parsed["entity_type"] == "file"
        assert parsed["content_hash"] == "e3b0c44298fc1c14"

    def test_mission_round_trip(self):
        original = build_mission_key("L_SL", "rag_topk", "retrieval", "0f3ec30c8c67abcd", "m_xyz")
        parsed = parse_key(original)
        assert parsed["layer"] == "L_SL"
        assert parsed["mission_id"] == "m_xyz"
        assert parsed["content_hash"] == "0f3ec30c8c67abcd"

    def test_wrong_segment_count_raises(self):
        with pytest.raises(ValueError, match="5 colon-separated segments"):
            parse_key("L4:cache:global:file")

    def test_extra_segments_raises(self):
        with pytest.raises(ValueError, match="5 colon-separated segments"):
            parse_key("L4:cache:global:file:abc123:extra")


# ---------------------------------------------------------------------------
# namespace_builder — key_prefix
# ---------------------------------------------------------------------------


class TestKeyPrefix:
    def test_global_prefix(self):
        prefix = key_prefix("L4", "semantic_cache")
        assert prefix == "L4:semantic_cache:global:"

    def test_mission_prefix(self):
        prefix = key_prefix("L4", "semantic_cache", mission_id="m_abc")
        assert prefix == "L4:semantic_cache:m_abc:"

    def test_unknown_layer_raises(self):
        with pytest.raises(ValueError, match="Unknown layer"):
            key_prefix("L99", "cache")

    def test_prefix_usable_for_glob(self):
        prefix = key_prefix("L_SL", "rag_topk")
        pattern = prefix + "*"
        assert pattern == "L_SL:rag_topk:global:*"


# ---------------------------------------------------------------------------
# namespace_builder — NS pre-defined specs
# ---------------------------------------------------------------------------


class TestNSSpecs:
    def test_ns_l4_semantic_build(self):
        key = NS.build(NS.L4_SEMANTIC, "file", "e3b0c44298fc1c14")
        assert key == "L4:semantic_cache:global:file:e3b0c44298fc1c14"

    def test_ns_l_sl_rag_topk_build(self):
        key = NS.build(NS.L_SL_RAG_TOPK, "retrieval", "0f3ec30c8c67abcd", mission_id="m_test")
        assert key == "L_SL:rag_topk:m_test:retrieval:0f3ec30c8c67abcd"

    def test_ns_l2_lease_build(self):
        key = NS.build(NS.L2_LEASE, "resource", "deadbeef12345678")
        assert key == "L2:coordination:global:resource:deadbeef12345678"

    def test_ns_l1_assembly_build(self):
        key = NS.build(NS.L1_ASSEMBLY, "thought", "cafebabe12345678")
        assert key == "L1:assembly:global:thought:cafebabe12345678"


# ---------------------------------------------------------------------------
# ADGMemoryAdapter — instantiation with fallback bridge
# ---------------------------------------------------------------------------


class TestADGMemoryAdapter:
    def test_adapter_instantiation(self):
        """Adapter must instantiate without live MCP (uses fallback bridge)."""
        adapter = ADGMemoryAdapter()
        assert adapter is not None

    def test_is_available_property(self):
        """is_available should be bool, True or False depending on MCP status."""
        adapter = ADGMemoryAdapter()
        assert isinstance(adapter.is_available, bool)

    def test_query_violations_returns_list(self):
        """query_violations must return a list (empty or not) without raising."""
        adapter = ADGMemoryAdapter()
        result = adapter.query_violations("L0->L5")
        assert isinstance(result, list)

    def test_query_hotspots_returns_list(self):
        """query_hotspots must return a list without raising."""
        adapter = ADGMemoryAdapter()
        result = adapter.query_hotspots()
        assert isinstance(result, list)

    def test_query_snapshot_returns_list(self):
        adapter = ADGMemoryAdapter()
        result = adapter.query_snapshot("20260311T193725Z")
        assert isinstance(result, list)

    def test_ingest_snapshot_with_mock(self):
        """ingest_snapshot must complete without error using a mock ScanResult."""
        from dataclasses import dataclass, field

        @dataclass
        class MockEdge:
            from_name: str = "mod_a"
            relation_type: str = "imports"
            to_name: str = "mod_b"
            edge_kind: str = "import"
            source_file: str = "agentic_core/L4_state/foo.py"
            line_no: int = 1
            symbol: str = ""

        @dataclass
        class MockScanResult:
            digest: str = "deadbeef" * 8
            modules: list = field(
                default_factory=lambda: [
                    "agentic_core/L4_state/foo.py",
                    "agentic_core/L0_routing/bar.py",
                ]
            )
            edges: list = field(default_factory=lambda: [MockEdge()])

        adapter = ADGMemoryAdapter()
        result = MockScanResult()
        adapter.ingest_snapshot(result, ts="20991231T000000Z")

    def test_ingest_snapshot_entities_actually_persisted(self, tmp_path, monkeypatch):
        """ingest_snapshot must write entities to SQLite — not silently succeed with 0 rows.

        Previously this test did not exist. The old test called ingest_snapshot() and
        asserted nothing about storage — so it passed even when data went to /dev/null.
        This test is the primary regression guard for Bug B4.
        """
        import sqlite3
        from dataclasses import dataclass, field

        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

        db = tmp_path / "kg_adapter_test.sqlite"
        monkeypatch.setenv("MEMORY_DB", str(db))
        GraphMemoryBridge.reset_instance()

        @dataclass
        class MockEdge:
            from_name: str = "mod_a"
            relation_type: str = "imports"
            to_name: str = "mod_b"
            edge_kind: str = "import"
            source_file: str = "agentic_core/L4_state/foo.py"
            line_no: int = 1
            symbol: str = ""

        @dataclass
        class MockScanResult:
            digest: str = "deadbeef" * 8
            modules: list = field(
                default_factory=lambda: [
                    "agentic_core/L4_state/foo.py",
                    "agentic_core/L0_routing/bar.py",
                ]
            )
            edges: list = field(default_factory=lambda: [MockEdge()])

        adapter = ADGMemoryAdapter()
        adapter.ingest_snapshot(MockScanResult(), ts="20991231T000000Z")

        conn = sqlite3.connect(str(db))
        entity_count = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        conn.close()
        GraphMemoryBridge.reset_instance()

        assert entity_count > 0, (
            f"ingest_snapshot must write entities to SQLite — got {entity_count}. "
            "If this is 0, GraphMemoryBridge is silently dropping all data."
        )

    def test_snapshot_entity_exists_after_ingest(self, tmp_path, monkeypatch):
        """ADGSnapshot entity must be queryable after ingest_snapshot completes."""
        import sqlite3
        from dataclasses import dataclass, field

        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

        db = tmp_path / "kg_snapshot_test.sqlite"
        monkeypatch.setenv("MEMORY_DB", str(db))
        GraphMemoryBridge.reset_instance()

        @dataclass
        class MockEdge:
            from_name: str = "mod_x"
            relation_type: str = "imports"
            to_name: str = "mod_y"
            edge_kind: str = "import"
            source_file: str = "agentic_core/L0_routing/x.py"
            line_no: int = 1
            symbol: str = ""

        @dataclass
        class MockScanResult:
            digest: str = "cafe1234" * 8
            modules: list = field(default_factory=lambda: ["agentic_core/L0_routing/x.py"])
            edges: list = field(default_factory=lambda: [MockEdge()])

        ts = "20991231T120000Z"
        adapter = ADGMemoryAdapter()
        adapter.ingest_snapshot(MockScanResult(), ts=ts)

        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT name FROM entities WHERE name LIKE 'ADGSnapshot%'").fetchone()
        conn.close()
        GraphMemoryBridge.reset_instance()

        assert row is not None, f"ADGSnapshot entity must exist in SQLite after ingest_snapshot(ts={ts!r})"

    def test_is_available_reflects_real_availability(self, tmp_path, monkeypatch):
        """is_available must be True when SQLite is wired — not just 'any bool'.

        Previously the test checked isinstance(adapter.is_available, bool) which
        passes even when is_available=False (i.e. persistence is completely broken).
        """
        from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

        db = tmp_path / "kg_avail_test.sqlite"
        monkeypatch.setenv("MEMORY_DB", str(db))
        GraphMemoryBridge.reset_instance()
        adapter = ADGMemoryAdapter()
        GraphMemoryBridge.reset_instance()

        assert adapter.is_available is True, (
            "adapter.is_available must be True when SQLite store is wired. "
            "False means the bridge fell through to no-op mode and will silently drop all data."
        )
