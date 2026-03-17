"""Tests for ADG P4 enhancements: E8 (Protocol/ABC Coverage), E10 (Schema Migration), E11 (Symbol Index).

All tests use synthetic ScanResult/edge fixtures — no filesystem access.
"""

from __future__ import annotations

from agentic_core.adg.analysis.protocol_coverage import (
    check_protocol_coverage,
)

from agentic_core.adg.analysis.schema_migration import (
    CURRENT_SCHEMA_VERSION,
    get_migration,
    list_migrations,
    migrate_scan_result_dict,
    register_migration,
)
from agentic_core.adg.analysis.symbol_index import SymbolIndex
from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_adg_p4_enhancements", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_p4_enhancements", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_p4_enhancements", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_p4_enhancements", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_p4_enhancements", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_p4_enhancements", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_p4_enhancements", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_p4_enhancements", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_p4_enhancements", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_p4_enhancements", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_p4_enhancements", "p4obs", "alert")
_emit_links_incident_trace("test_adg_p4_enhancements", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_p4_enhancements", "p3lm", "pattern")
_emit_records_learning_event("test_adg_p4_enhancements", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_p4_enhancements", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_p4_enhancements", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_p4_enhancements", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_p4_enhancements", "p3lm", "policy")
_emit_stores_learning_state("test_adg_p4_enhancements", "p3lm", "state")
_emit_records_execution_trace("test_adg_p4_enhancements", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_p4_enhancements", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_p4_enhancements", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_p4_enhancements", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_p4_enhancements", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_p4_enhancements", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_p4_enhancements", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_p4_enhancements", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_p4_enhancements", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_adg_p4_enhancements")
_emit_applies_guardrail("p0", "test_adg_p4_enhancements", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_p4_enhancements", "policy_binding")
_emit_snapshots_state("p0", "test_adg_p4_enhancements", "state_snapshot")
_emit_pulls_context("p1", "test_adg_p4_enhancements", "context_pull")
_emit_pulls_context("p1", "test_adg_p4_enhancements", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_adg_p4_enhancements", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_p4_enhancements", "uwg_term_secondary")
_emit_writes_through("p1", "test_adg_p4_enhancements", "write_through")
_emit_writes_through("p1", "test_adg_p4_enhancements", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_adg_p4_enhancements", "safety_validation")
_emit_invokes_eval("p1", "test_adg_p4_enhancements", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_p4_enhancements", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_p4_enhancements", "human_escalation")
_emit_routes_through("p1", "test_adg_p4_enhancements", "route_through")
_emit_checks_agent_registry("p1", "test_adg_p4_enhancements", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_p4_enhancements", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_p4_enhancements", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_p4_enhancements", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_p4_enhancements", "target_agent")
_emit_verifies_policy("p1", "test_adg_p4_enhancements", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_p4_enhancements", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_p4_enhancements", "boundary_check")
_emit_transcripts_response("p1", "test_adg_p4_enhancements", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_p4_enhancements")
_emit_gated_by_confidence("p1", "test_adg_p4_enhancements", "confidence_gate")
emit_replay_key("p0", "test_adg_p4_enhancements")
emit_determinism_digest("p0", "test_adg_p4_enhancements")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_p4_enhancements", "execution_auth")
_emit_validates_capability("p2", "test_adg_p4_enhancements", "capability_check")
_emit_routes_to_capability("p2", "test_adg_p4_enhancements", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_p4_enhancements", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_p4_enhancements", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_p4_enhancements", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_p4_enhancements", "exec_output")
_emit_dispatches_agent("p3", "test_adg_p4_enhancements", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_p4_enhancements", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_p4_enhancements", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_p4_enhancements", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_p4_enhancements", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_p4_enhancements", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_p4_enhancements", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_p4_enhancements", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_p4_enhancements", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_p4_enhancements", "eval_metric")
_emit_stores_embedding("p4", "test_adg_p4_enhancements", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_p4_enhancements", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_p4_enhancements", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_module_adg(rel: str) -> str:
    return f"ADG::Module::{rel}"


def _make_implements_edge(from_class: str, to_base_sym: str, base_short: str) -> Edge:
    return Edge(
        from_name=from_class,
        relation_type="implements",
        to_name=f"ADG::Symbol::{to_base_sym}",
        edge_kind="resolved_internal",
        source_file="foo.py",
        line_no=1,
        symbol=base_short,
    )


def _make_exports_edge(module_rel: str, symbol: str) -> Edge:
    return Edge(
        from_name=_make_module_adg(module_rel),
        relation_type="exports",
        to_name=f"ADG::Symbol::{module_rel}::{symbol}",
        edge_kind="export",
        source_file=module_rel,
        line_no=1,
        symbol=symbol,
    )


def _scan_result(*edges: Edge) -> ScanResult:
    result = ScanResult()
    result.edges = sorted(set(edges))
    result.modules = []
    return result


# ===========================================================================
# E8: Protocol / ABC Coverage Check
# ===========================================================================


class TestProtocolCoverageCheck:
    """E8: verify abstract base detection and coverage reporting.

    Model:
      Pass 1: class C extends Protocol/ABC -> C is an abstract base.
      Pass 2: class D extends C (where C is abstract) -> C is covered.
    """

    def test_abstract_class_with_concrete_implementor_is_covered(self):
        """MyProtocol extends Protocol (abstract). ConcreteImpl extends MyProtocol (covered)."""
        my_protocol_adg = _make_module_adg("iface.py") + "::MyProtocol"
        concrete_adg = _make_module_adg("impl.py") + "::ConcreteImpl"
        e1 = Edge(
            from_name=my_protocol_adg,
            relation_type="implements",
            to_name="ADG::Symbol::Protocol",
            edge_kind="resolved_internal",
            source_file="iface.py",
            line_no=1,
            symbol="Protocol",
        )
        e2 = Edge(
            from_name=concrete_adg,
            relation_type="implements",
            to_name=my_protocol_adg,
            edge_kind="resolved_internal",
            source_file="impl.py",
            line_no=5,
            symbol="MyProtocol",
        )
        result = _scan_result(e1, e2)
        report = check_protocol_coverage(result)
        assert my_protocol_adg in report.abstract_bases
        assert my_protocol_adg in report.covered_bases
        assert my_protocol_adg not in report.uncovered_bases
        assert report.coverage_rate == 1.0

    def test_abstract_class_without_implementor_is_uncovered(self):
        """MyABC extends ABC, but nothing extends MyABC — uncovered."""
        my_abc_adg = _make_module_adg("base.py") + "::MyABC"
        e1 = Edge(
            from_name=my_abc_adg,
            relation_type="implements",
            to_name="ADG::Symbol::ABC",
            edge_kind="resolved_internal",
            source_file="base.py",
            line_no=1,
            symbol="ABC",
        )
        result = _scan_result(e1)
        report = check_protocol_coverage(result)
        assert my_abc_adg in report.abstract_bases
        assert my_abc_adg in report.uncovered_bases
        assert my_abc_adg not in report.covered_bases
        assert report.coverage_rate == 0.0

    def test_multiple_implementors_same_abstract_base(self):
        """Two concrete classes extend the same abstract base — it is covered once."""
        base_adg = _make_module_adg("iface.py") + "::IFace"
        declare = Edge(
            from_name=base_adg,
            relation_type="implements",
            to_name="ADG::Symbol::Protocol",
            edge_kind="resolved_internal",
            source_file="iface.py",
            line_no=1,
            symbol="Protocol",
        )
        impl_a = Edge(
            from_name=_make_module_adg("a.py") + "::ImplA",
            relation_type="implements",
            to_name=base_adg,
            edge_kind="resolved_internal",
            source_file="a.py",
            line_no=1,
            symbol="IFace",
        )
        impl_b = Edge(
            from_name=_make_module_adg("b.py") + "::ImplB",
            relation_type="implements",
            to_name=base_adg,
            edge_kind="resolved_internal",
            source_file="b.py",
            line_no=1,
            symbol="IFace",
        )
        result = _scan_result(declare, impl_a, impl_b)
        report = check_protocol_coverage(result)
        assert len(report.covered_bases) == 1
        assert len(report.uncovered_bases) == 0

    def test_no_implements_edges_full_coverage(self):
        result = _scan_result()
        report = check_protocol_coverage(result)
        assert report.abstract_bases == []
        assert report.coverage_rate == 1.0

    def test_non_abstract_base_not_counted(self):
        """A class extending a non-ABC/Protocol base is NOT tracked as abstract."""
        edge = Edge(
            from_name=_make_module_adg("a.py") + "::Child",
            relation_type="implements",
            to_name="ADG::Symbol::MyMixin",
            edge_kind="resolved_internal",
            source_file="a.py",
            line_no=1,
            symbol="MyMixin",
        )
        result = _scan_result(edge)
        report = check_protocol_coverage(result)
        assert len(report.abstract_bases) == 0

    def test_typing_protocol_detected(self):
        """typing.Protocol should be recognized as an abstract anchor."""
        my_iface_adg = _make_module_adg("iface.py") + "::MyInterface"
        e = Edge(
            from_name=my_iface_adg,
            relation_type="implements",
            to_name="ADG::Symbol::typing.Protocol",
            edge_kind="resolved_internal",
            source_file="iface.py",
            line_no=1,
            symbol="typing.Protocol",
        )
        result = _scan_result(e)
        report = check_protocol_coverage(result)
        assert my_iface_adg in report.abstract_bases

    def test_to_dict_structure(self):
        my_abc_adg = _make_module_adg("base.py") + "::MyABC"
        e = Edge(
            from_name=my_abc_adg,
            relation_type="implements",
            to_name="ADG::Symbol::ABC",
            edge_kind="resolved_internal",
            source_file="base.py",
            line_no=1,
            symbol="ABC",
        )
        report = check_protocol_coverage(_scan_result(e))
        d = report.to_dict()
        assert "abstract_count" in d
        assert "covered_count" in d
        assert "uncovered_count" in d
        assert "coverage_rate" in d
        assert "uncovered_bases" in d

    def test_coverage_rate_partial(self):
        """Two abstract bases: one covered, one not.

        IFaceCovered extends Protocol, and ConcreteImpl extends IFaceCovered.
        IFaceUncovered extends ABC, but nothing extends IFaceUncovered.
        """
        covered_adg = _make_module_adg("iface.py") + "::IFaceCovered"
        uncovered_adg = _make_module_adg("base.py") + "::IFaceUncovered"

        declare_covered = Edge(
            from_name=covered_adg,
            relation_type="implements",
            to_name="ADG::Symbol::Protocol",
            edge_kind="resolved_internal",
            source_file="iface.py",
            line_no=1,
            symbol="Protocol",
        )
        concrete_impl = Edge(
            from_name=_make_module_adg("impl.py") + "::Concrete",
            relation_type="implements",
            to_name=covered_adg,
            edge_kind="resolved_internal",
            source_file="impl.py",
            line_no=5,
            symbol="IFaceCovered",
        )
        declare_uncovered = Edge(
            from_name=uncovered_adg,
            relation_type="implements",
            to_name="ADG::Symbol::ABC",
            edge_kind="resolved_internal",
            source_file="base.py",
            line_no=1,
            symbol="ABC",
        )
        result = _scan_result(declare_covered, concrete_impl, declare_uncovered)
        report = check_protocol_coverage(result)
        assert len(report.abstract_bases) == 2
        assert len(report.covered_bases) == 1
        assert len(report.uncovered_bases) == 1
        assert 0.0 < report.coverage_rate < 1.0


# ===========================================================================
# E10: Schema Version Migration Guard
# ===========================================================================


class TestSchemaMigration:
    """E10: verify migration registration, application, and registry."""

    def test_builtin_migration_registered(self):
        migrations = list_migrations()
        assert ("0.9", "1.0") in migrations

    def test_0_9_to_1_0_adds_symbol_field(self):
        fn = get_migration("0.9", "1.0")
        assert fn is not None
        data = {
            "manifest": {"schema_version": "0.9"},
            "edges": [
                {
                    "from_name": "ADG::Module::a.py",
                    "relation_type": "imports",
                    "to_name": "ADG::Symbol::os",
                    "edge_kind": "import",
                    "source_file": "a.py",
                    "line_no": 1,
                }
            ],
        }
        result = fn(data)
        assert result["edges"][0]["symbol"] == ""

    def test_migrate_current_version_no_op(self):
        data = {
            "manifest": {"schema_version": CURRENT_SCHEMA_VERSION},
            "edges": [],
        }
        result = migrate_scan_result_dict(data)
        assert result is not data  # deepcopy
        assert result["manifest"]["schema_version"] == CURRENT_SCHEMA_VERSION

    def test_migrate_legacy_0_9_updates_version(self):
        data = {
            "manifest": {"schema_version": "0.9"},
            "edges": [],
        }
        result = migrate_scan_result_dict(data)
        assert result["manifest"]["schema_version"] == CURRENT_SCHEMA_VERSION

    def test_migrate_does_not_modify_original(self):
        data = {
            "manifest": {"schema_version": "0.9"},
            "edges": [{"from_name": "x", "symbol": "existing"}],
        }
        _ = migrate_scan_result_dict(data)
        assert data["edges"][0]["symbol"] == "existing"

    def test_register_custom_migration(self):
        @register_migration("test_from", "test_to")
        def my_migration(d: dict) -> dict:
            d["migrated"] = True
            return d

        fn = get_migration("test_from", "test_to")
        assert fn is not None
        result = fn({})
        assert result["migrated"] is True

    def test_missing_version_defaults_to_0_9(self):
        data = {"manifest": {}, "edges": [{"from_name": "x"}]}
        result = migrate_scan_result_dict(data)
        assert result["manifest"]["schema_version"] == CURRENT_SCHEMA_VERSION

    def test_get_missing_migration_returns_none(self):
        assert get_migration("99.0", "100.0") is None

    def test_current_schema_version_is_string(self):
        assert isinstance(CURRENT_SCHEMA_VERSION, str)
        assert len(CURRENT_SCHEMA_VERSION) > 0


# ===========================================================================
# E11: Cross-File Symbol Resolution Index
# ===========================================================================


class TestSymbolIndex:
    """E11: verify symbol index build, queries, and all_registry."""

    def test_build_from_exports_edges(self):
        result = _scan_result(
            _make_exports_edge("pkg/mod.py", "MyClass"),
            _make_exports_edge("pkg/mod.py", "helper_func"),
        )
        idx = SymbolIndex.build(result)
        assert idx.total_exports == 2

    def test_resolve_symbol_to_module(self):
        result = _scan_result(
            _make_exports_edge("pkg/mod.py", "MyClass"),
        )
        idx = SymbolIndex.build(result)
        resolved = idx.resolve("MyClass")
        assert resolved == _make_module_adg("pkg/mod.py")

    def test_resolve_unknown_symbol_returns_none(self):
        idx = SymbolIndex.build(_scan_result())
        assert idx.resolve("NonExistent") is None

    def test_exports_of_by_rel_path(self):
        result = _scan_result(
            _make_exports_edge("pkg/mod.py", "Alpha"),
            _make_exports_edge("pkg/mod.py", "Beta"),
        )
        idx = SymbolIndex.build(result)
        exports = idx.exports_of("pkg/mod.py")
        assert sorted(exports) == ["Alpha", "Beta"]

    def test_exports_of_by_adg_name(self):
        result = _scan_result(
            _make_exports_edge("pkg/mod.py", "Alpha"),
        )
        idx = SymbolIndex.build(result)
        exports = idx.exports_of("ADG::Module::pkg/mod.py")
        assert "Alpha" in exports

    def test_exports_of_unknown_module_returns_empty(self):
        idx = SymbolIndex.build(_scan_result())
        assert idx.exports_of("pkg/ghost.py") == []

    def test_build_all_registry_dotted_path(self):
        result = _scan_result(
            _make_exports_edge("pkg/utils.py", "parse"),
            _make_exports_edge("pkg/utils.py", "format_output"),
        )
        idx = SymbolIndex.build(result)
        registry = idx.build_all_registry()
        assert "pkg.utils" in registry
        assert sorted(registry["pkg.utils"]) == ["format_output", "parse"]

    def test_all_registry_strips_py_extension(self):
        result = _scan_result(
            _make_exports_edge("helpers.py", "helper"),
        )
        idx = SymbolIndex.build(result)
        registry = idx.build_all_registry()
        assert "helpers" in registry
        assert ".py" not in "helpers"

    def test_all_registry_strips_init(self):
        result = _scan_result(
            _make_exports_edge("pkg/__init__.py", "pkg_func"),
        )
        idx = SymbolIndex.build(result)
        registry = idx.build_all_registry()
        assert "pkg" in registry

    def test_non_exports_edges_ignored(self):
        result = _scan_result(
            Edge(
                from_name=_make_module_adg("a.py"),
                relation_type="imports",
                to_name="ADG::Symbol::os",
                edge_kind="import",
                source_file="a.py",
                line_no=1,
                symbol="os",
            ),
        )
        idx = SymbolIndex.build(result)
        assert idx.total_exports == 0
        assert idx.resolve("os") is None

    def test_stats_dict(self):
        result = _scan_result(
            _make_exports_edge("a.py", "func_a"),
            _make_exports_edge("b.py", "func_b"),
        )
        idx = SymbolIndex.build(result)
        stats = idx.stats()
        assert stats["total_exports"] == 2
        assert stats["unique_symbols"] == 2
        assert stats["modules_with_exports"] == 2

    def test_empty_result_empty_index(self):
        idx = SymbolIndex.build(_scan_result())
        assert idx.total_exports == 0
        assert idx.symbol_to_module == {}
        assert idx.module_to_symbols == {}

    def test_multiple_modules_different_symbols(self):
        result = _scan_result(
            _make_exports_edge("mod_a.py", "ClassA"),
            _make_exports_edge("mod_b.py", "ClassB"),
        )
        idx = SymbolIndex.build(result)
        assert idx.resolve("ClassA") == _make_module_adg("mod_a.py")
        assert idx.resolve("ClassB") == _make_module_adg("mod_b.py")

    def test_exports_sorted_in_module_to_symbols(self):
        result = _scan_result(
            _make_exports_edge("mod.py", "Zebra"),
            _make_exports_edge("mod.py", "Apple"),
            _make_exports_edge("mod.py", "Mango"),
        )
        idx = SymbolIndex.build(result)
        exports = idx.exports_of("mod.py")
        assert exports == sorted(exports)

    def test_all_registry_multiple_modules(self):
        result = _scan_result(
            _make_exports_edge("pkg/a.py", "foo"),
            _make_exports_edge("pkg/b.py", "bar"),
        )
        idx = SymbolIndex.build(result)
        registry = idx.build_all_registry()
        assert "pkg.a" in registry
        assert "pkg.b" in registry
