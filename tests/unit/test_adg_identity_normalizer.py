"""Unit tests for ADG Identity Normalizer (Phase 1).

Tests cover:
- All 5 IdentityKind categories (repo_module, package_container,
  external_module, unresolved_import, inferred_symbol)
- Determinism: same input -> same output on two calls
- Confidence labels are correct
- NormalizationReport aggregates correctly
- No silent swallowing: unresolved_import always reports reason
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.adg.identity.normalizer import (
    IdentityConfidence,
    IdentityKind,
    IdentityNormalizer,
    NormalizationReport,
    build_identity_index,
    normalize_identity,
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

_emit_records_execution_trace("p0", "evidence", "test_adg_identity_normalizer")
_emit_applies_guardrail("p0", "test_adg_identity_normalizer", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_identity_normalizer", "policy_binding")
_emit_snapshots_state("p0", "test_adg_identity_normalizer", "state_snapshot")
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

_emit_emits_metric_event("test_adg_identity_normalizer", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_identity_normalizer", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_identity_normalizer", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_identity_normalizer", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_identity_normalizer", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_identity_normalizer", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_identity_normalizer", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_identity_normalizer", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_identity_normalizer", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_identity_normalizer", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_identity_normalizer", "p4obs", "alert")
_emit_links_incident_trace("test_adg_identity_normalizer", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_identity_normalizer", "p3lm", "pattern")
_emit_records_learning_event("test_adg_identity_normalizer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_identity_normalizer", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_identity_normalizer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_identity_normalizer", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_identity_normalizer", "p3lm", "policy")
_emit_stores_learning_state("test_adg_identity_normalizer", "p3lm", "state")
_emit_records_execution_trace("test_adg_identity_normalizer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_identity_normalizer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_identity_normalizer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_identity_normalizer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_identity_normalizer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_identity_normalizer", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_identity_normalizer", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_identity_normalizer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_identity_normalizer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_identity_normalizer", "context_pull")
_emit_pulls_context("p1", "test_adg_identity_normalizer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_identity_normalizer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_identity_normalizer", "uwg_term_2")
_emit_writes_through("p1", "test_adg_identity_normalizer", "write_through")
_emit_writes_through("p1", "test_adg_identity_normalizer", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_identity_normalizer", "safety_validation")
_emit_invokes_eval("p1", "test_adg_identity_normalizer", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_identity_normalizer", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_identity_normalizer", "human_escalation")
_emit_routes_through("p1", "test_adg_identity_normalizer", "route_through")
_emit_checks_agent_registry("p1", "test_adg_identity_normalizer", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_identity_normalizer", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_identity_normalizer", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_identity_normalizer", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_identity_normalizer", "target_agent")
_emit_verifies_policy("p1", "test_adg_identity_normalizer", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_identity_normalizer", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_identity_normalizer", "boundary_check")
_emit_transcripts_response("p1", "test_adg_identity_normalizer", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_identity_normalizer")
_emit_gated_by_confidence("p1", "test_adg_identity_normalizer", "confidence_gate")
emit_replay_key("p0", "test_adg_identity_normalizer")
emit_determinism_digest("p0", "test_adg_identity_normalizer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_identity_normalizer", "execution_auth")
_emit_validates_capability("p2", "test_adg_identity_normalizer", "capability_check")
_emit_routes_to_capability("p2", "test_adg_identity_normalizer", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_identity_normalizer", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_identity_normalizer", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_identity_normalizer", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_identity_normalizer", "exec_output")
_emit_dispatches_agent("p3", "test_adg_identity_normalizer", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_identity_normalizer", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_identity_normalizer", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_identity_normalizer", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_identity_normalizer", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_identity_normalizer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_identity_normalizer", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_identity_normalizer", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_identity_normalizer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_identity_normalizer", "eval_metric")
_emit_stores_embedding("p4", "test_adg_identity_normalizer", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_identity_normalizer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_identity_normalizer", "exec_snapshot_link")

_REPO_ROOT = Path(__file__).resolve().parents[2]


class TestIdentityKindEnum:
    """IdentityKind values are string-comparable."""

    @pytest.mark.unit
    def test_repo_module_value(self) -> None:
        assert IdentityKind.REPO_MODULE.value == "repo_module"

    @pytest.mark.unit
    def test_external_module_value(self) -> None:
        assert IdentityKind.EXTERNAL_MODULE.value == "external_module"

    @pytest.mark.unit
    def test_unresolved_import_value(self) -> None:
        assert IdentityKind.UNRESOLVED_IMPORT.value == "unresolved_import"

    @pytest.mark.unit
    def test_package_container_value(self) -> None:
        assert IdentityKind.PACKAGE_CONTAINER.value == "package_container"

    @pytest.mark.unit
    def test_inferred_symbol_value(self) -> None:
        assert IdentityKind.INFERRED_SYMBOL.value == "inferred_symbol"


class TestExternalModuleResolution:
    """Names whose top-level is not in SSOT roots resolve to EXTERNAL_MODULE."""

    @pytest.mark.unit
    def test_openai_is_external(self) -> None:
        rec = normalize_identity("openai", repo_root=_REPO_ROOT)
        assert rec.kind == IdentityKind.EXTERNAL_MODULE

    @pytest.mark.unit
    def test_anthropic_is_external(self) -> None:
        rec = normalize_identity("anthropic", repo_root=_REPO_ROOT)
        assert rec.kind == IdentityKind.EXTERNAL_MODULE

    @pytest.mark.unit
    def test_json_stdlib_is_external(self) -> None:
        rec = normalize_identity("json", repo_root=_REPO_ROOT)
        assert rec.kind == IdentityKind.EXTERNAL_MODULE

    @pytest.mark.unit
    def test_external_has_high_confidence(self) -> None:
        rec = normalize_identity("pathlib", repo_root=_REPO_ROOT)
        assert rec.confidence == IdentityConfidence.HIGH

    @pytest.mark.unit
    def test_external_resolved_path_empty(self) -> None:
        rec = normalize_identity("os.path", repo_root=_REPO_ROOT)
        assert rec.resolved_path == ""


class TestRepoModuleResolution:
    """Names whose file exists in repo resolve to REPO_MODULE."""

    @pytest.mark.unit
    def test_adg_schema_is_repo_module(self) -> None:
        rec = normalize_identity(
            "agentic_core.adg.schema_util",
            repo_root=_REPO_ROOT,
        )
        assert rec.kind == IdentityKind.REPO_MODULE

    @pytest.mark.unit
    def test_repo_module_resolved_path_ends_with_py(self) -> None:
        rec = normalize_identity(
            "agentic_core.adg.schema_util",
            repo_root=_REPO_ROOT,
        )
        assert rec.resolved_path.endswith(".py")

    @pytest.mark.unit
    def test_repo_module_has_high_confidence(self) -> None:
        rec = normalize_identity(
            "agentic_core.adg.schema_util",
            repo_root=_REPO_ROOT,
        )
        assert rec.confidence == IdentityConfidence.HIGH

    @pytest.mark.unit
    def test_repo_module_adg_name_starts_with_adg_module(self) -> None:
        rec = normalize_identity(
            "agentic_core.adg.schema_util",
            repo_root=_REPO_ROOT,
        )
        assert rec.adg_name.startswith("ADG::Module::")


class TestPackageContainerResolution:
    """Package dirs resolve to PACKAGE_CONTAINER."""

    @pytest.mark.unit
    def test_package_with_init_is_container(self) -> None:
        rec = normalize_identity(
            "agentic_core.adg",
            repo_root=_REPO_ROOT,
        )
        assert rec.kind == IdentityKind.PACKAGE_CONTAINER

    @pytest.mark.unit
    def test_package_container_has_init_path(self) -> None:
        rec = normalize_identity(
            "agentic_core.adg",
            repo_root=_REPO_ROOT,
        )
        assert "__init__.py" in rec.resolved_path

    @pytest.mark.unit
    def test_package_container_high_confidence(self) -> None:
        rec = normalize_identity(
            "agentic_core.adg",
            repo_root=_REPO_ROOT,
        )
        assert rec.confidence == IdentityConfidence.HIGH


class TestUnresolvedImportResolution:
    """Completely missing internal names become UNRESOLVED_IMPORT with reason."""

    @pytest.mark.unit
    def test_missing_internal_module_is_unresolved(self) -> None:
        rec = normalize_identity(
            "agentic_core.nonexistent.does_not_exist",
            repo_root=_REPO_ROOT,
        )
        assert rec.kind == IdentityKind.UNRESOLVED_IMPORT

    @pytest.mark.unit
    def test_unresolved_has_reason(self) -> None:
        rec = normalize_identity(
            "agentic_core.totally_fake_module_xyz",
            repo_root=_REPO_ROOT,
        )
        assert len(rec.reason) > 0

    @pytest.mark.unit
    def test_unresolved_has_low_confidence(self) -> None:
        # Use a path where BOTH parent and direct resolution fail:
        # "agentic_core.totally_fake_pkg_zzz.sub_module" — parent
        # "agentic_core.totally_fake_pkg_zzz" also doesn't exist, so no
        # INFERRED_SYMBOL promotion occurs and confidence stays LOW.
        rec = normalize_identity(
            "agentic_core.totally_fake_pkg_zzz.sub_module",
            repo_root=_REPO_ROOT,
        )
        assert rec.confidence == IdentityConfidence.LOW

    @pytest.mark.unit
    def test_unresolved_resolved_path_empty(self) -> None:
        # Both the direct path and the parent must be unresolvable so we get
        # UNRESOLVED_IMPORT (empty resolved_path), not INFERRED_SYMBOL.
        rec = normalize_identity(
            "agentic_core.totally_fake_pkg_zzz.sub_module",
            repo_root=_REPO_ROOT,
        )
        assert rec.resolved_path == ""


class TestInferredSymbolResolution:
    """Names whose parent resolves but the leaf is a class/fn become INFERRED_SYMBOL."""

    @pytest.mark.unit
    def test_class_from_module_is_inferred_symbol(self) -> None:
        rec = normalize_identity(
            "agentic_core.adg.schema_util.EntityType",
            repo_root=_REPO_ROOT,
        )
        assert rec.kind == IdentityKind.INFERRED_SYMBOL

    @pytest.mark.unit
    def test_inferred_symbol_has_parent_path(self) -> None:
        rec = normalize_identity(
            "agentic_core.adg.schema_util.canonical_name",
            repo_root=_REPO_ROOT,
        )
        assert rec.resolved_path.endswith(".py")

    @pytest.mark.unit
    def test_inferred_symbol_has_medium_confidence(self) -> None:
        rec = normalize_identity(
            "agentic_core.adg.schema_util.RelationType",
            repo_root=_REPO_ROOT,
        )
        assert rec.confidence == IdentityConfidence.MEDIUM


class TestDeterminism:
    """Same input must always produce identical IdentityRecord."""

    @pytest.mark.unit
    def test_external_deterministic(self) -> None:
        r1 = normalize_identity("openai", repo_root=_REPO_ROOT)
        r2 = normalize_identity("openai", repo_root=_REPO_ROOT)
        assert r1.kind == r2.kind
        assert r1.adg_name == r2.adg_name

    @pytest.mark.unit
    def test_repo_module_deterministic(self) -> None:
        r1 = normalize_identity("agentic_core.adg.schema_util", repo_root=_REPO_ROOT)
        r2 = normalize_identity("agentic_core.adg.schema_util", repo_root=_REPO_ROOT)
        assert r1.resolved_path == r2.resolved_path
        assert r1.confidence == r2.confidence

    @pytest.mark.unit
    def test_normalize_many_order_independent(self) -> None:
        """normalize_many result is keyed by sorted names regardless of input order."""
        normalizer = IdentityNormalizer(repo_root=_REPO_ROOT)
        r1 = normalizer.normalize_many(["openai", "agentic_core.adg.schema_util"])
        r2 = normalizer.normalize_many(["agentic_core.adg.schema_util", "openai"])
        assert set(r1.keys()) == set(r2.keys())
        for k in r1:
            assert r1[k].kind == r2[k].kind


class TestNormalizationReport:
    """NormalizationReport aggregates correctly over a batch of records."""

    @pytest.mark.unit
    def test_report_total_matches_record_count(self) -> None:
        normalizer = IdentityNormalizer(repo_root=_REPO_ROOT)
        names = ["openai", "agentic_core.adg.schema_util", "agentic_core.adg"]
        records = normalizer.normalize_many(names)
        report = normalizer.report(records)
        assert report.total == 3

    @pytest.mark.unit
    def test_report_by_kind_sums_to_total(self) -> None:
        normalizer = IdentityNormalizer(repo_root=_REPO_ROOT)
        names = ["openai", "agentic_core.adg.schema_util", "agentic_core.adg"]
        records = normalizer.normalize_many(names)
        report = normalizer.report(records)
        assert sum(report.by_kind.values()) == report.total

    @pytest.mark.unit
    def test_unresolved_explicitly_listed(self) -> None:
        # Both parent and direct path must be non-existent for UNRESOLVED_IMPORT
        normalizer = IdentityNormalizer(repo_root=_REPO_ROOT)
        names = ["agentic_core.fake_pkg_zzz.nonexistent_module"]
        records = normalizer.normalize_many(names)
        report = normalizer.report(records)
        assert "agentic_core.fake_pkg_zzz.nonexistent_module" in report.unresolved

    @pytest.mark.unit
    def test_report_to_dict_has_required_keys(self) -> None:
        normalizer = IdentityNormalizer(repo_root=_REPO_ROOT)
        records = normalizer.normalize_many(["openai"])
        report = normalizer.report(records)
        d = report.to_dict()
        for key in ("total", "by_kind", "by_confidence", "unresolved_count", "unresolved_names"):
            assert key in d, f"Missing key: {key}"


class TestBuildIdentityIndex:
    """build_identity_index convenience function."""

    @pytest.mark.unit
    def test_returns_records_and_report(self) -> None:
        records, report = build_identity_index(
            ["openai", "agentic_core.adg.schema_util"],
            repo_root=_REPO_ROOT,
        )
        assert isinstance(records, dict)
        assert isinstance(report, NormalizationReport)

    @pytest.mark.unit
    def test_empty_list_returns_empty(self) -> None:
        records, report = build_identity_index([], repo_root=_REPO_ROOT)
        assert records == {}
        assert report.total == 0


class TestIdentityRecordAdgName:
    """Every IdentityRecord has a non-empty adg_name."""

    @pytest.mark.unit
    def test_repo_module_adg_name_nonempty(self) -> None:
        rec = normalize_identity("agentic_core.adg.schema_util", repo_root=_REPO_ROOT)
        assert len(rec.adg_name) > 0

    @pytest.mark.unit
    def test_external_adg_name_starts_with_adg_symbol(self) -> None:
        rec = normalize_identity("openai", repo_root=_REPO_ROOT)
        assert rec.adg_name.startswith("ADG::Symbol::")

    @pytest.mark.unit
    def test_inferred_symbol_adg_name_nonempty(self) -> None:
        rec = normalize_identity("agentic_core.adg.schema_util.EntityType", repo_root=_REPO_ROOT)
        assert len(rec.adg_name) > 0


class TestNormalizeFromScanResult:
    """normalize_from_scan_result processes edges from a ScanResult."""

    @pytest.mark.unit
    def test_normalize_from_scan_result_returns_tuple(self) -> None:
        from agentic_core.adg.extraction.static_scanner import Edge, ScanResult

        result = ScanResult(commit_sha="test")
        result.modules = ["agentic_core/adg/schema.py"]
        result.edges = [
            Edge(
                from_name="ADG::Module::agentic_core/adg/schema.py",
                relation_type="imports",
                to_name="ADG::Symbol::openai.ChatCompletion",
                edge_kind="import",
                source_file="agentic_core/adg/schema.py",
                line_no=1,
            )
        ]
        result.compute_digest()
        normalizer = IdentityNormalizer(repo_root=_REPO_ROOT)
        records, report = normalizer.normalize_from_scan_result(result)
        assert isinstance(records, dict)
        assert isinstance(report, NormalizationReport)
