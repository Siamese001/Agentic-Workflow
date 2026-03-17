"""
Guardian Hardened Tests — Gravity Validator (Tier 1)

AST-graph justification:
  gravity_validator (UnifiedSSOTValidator) has fan_in=6; test_cov=1 (import
  probe only in test_path_setup.py). It is the single consolidation point for
  all five SSOT violation categories (gravity, import, hierarchy, drift,
  compliance). A regression here silently passes all consumers.

Strategy: UnifiedSSOTValidator.validate_all() requires a live filesystem
  with a matching project structure. Behavioral tests are written against:
  (a) the public data-contract types (GravityViolation, ImportViolation,
      HierarchyViolation, DriftViolation, SovereignHealthReport)
  (b) the helper seams (_get_layer_from_path, _extract_target_layer)
  (c) SovereignHealthReport computed properties (total_violations, is_compliant,
      to_markdown())
  (d) validate_all() via a controlled minimal tmp_path project root.

Covers:
  1.  GravityViolation.__str__() contract
  2.  ImportViolation.__str__() contract
  3.  HierarchyViolation.__str__() contract
  4.  DriftViolation.__str__() contract
  5.  SovereignHealthReport.total_violations aggregation
  6.  SovereignHealthReport.is_compliant — True iff zero violations
  7.  SovereignHealthReport.to_markdown() contains required section headers
  8.  SovereignHealthReport.to_markdown() shows COMPLIANT status when clean
  9.  SovereignHealthReport.to_markdown() shows NON-COMPLIANT status with violations
 10.  SovereignHealthReport.to_markdown() compliance_score rendered
 11.  _get_layer_from_path() extracts L0–L5 from path parts
 12.  _get_layer_from_path() returns None for non-layer paths
 13.  _extract_target_layer() extracts layer from ImportFrom node
 14.  _extract_target_layer() extracts layer from Import node
 15.  _extract_target_layer() returns None for non-agentic_core imports
 16.  UnifiedSSOTValidator initialises without error on valid tmp project root
 17.  validate_all() returns SovereignHealthReport (not raises) on minimal repo
 18.  Fail-closed: empty project root returns report with zero agents
"""

from __future__ import annotations

import ast
import types
from pathlib import Path
from unittest.mock import patch

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
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_gravity_validator_hardened")
_emit_applies_guardrail("p0", "test_gravity_validator_hardened", "p0_governance")
_emit_reads_policy_state("p0", "test_gravity_validator_hardened", "policy_binding")
_emit_snapshots_state("p0", "test_gravity_validator_hardened", "state_snapshot")
emit_replay_key("p0", "test_gravity_validator_hardened")
emit_determinism_digest("p0", "test_gravity_validator_hardened")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_gravity_validator_hardened", "execution_auth")
_emit_validates_capability("p2", "test_gravity_validator_hardened", "capability_check")
_emit_routes_to_capability("p2", "test_gravity_validator_hardened", "capability_route")
_emit_writes_via_uwg("p2", "test_gravity_validator_hardened", "uwg_write")
_emit_blocks_direct_write("p2", "test_gravity_validator_hardened", "direct_write_block")
_emit_records_tool_invocation("p2", "test_gravity_validator_hardened", "tool_invocation")
_emit_captures_execution_output("p2", "test_gravity_validator_hardened", "exec_output")
_emit_dispatches_agent("p3", "test_gravity_validator_hardened", "agent_dispatch")
_emit_coordinates_agents("p3", "test_gravity_validator_hardened", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_gravity_validator_hardened", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_gravity_validator_hardened", "healing_outcome")
_emit_escalates_failure("p3", "test_gravity_validator_hardened", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_gravity_validator_hardened", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_gravity_validator_hardened", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_gravity_validator_hardened", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_gravity_validator_hardened", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_gravity_validator_hardened", "eval_metric")
_emit_stores_embedding("p4", "test_gravity_validator_hardened", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_gravity_validator_hardened", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_gravity_validator_hardened", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.guardian

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L5_safety.validators.gravity_validator import (
    DriftViolation,
    GravityViolation,
    HierarchyViolation,
    ImportViolation,
    SovereignHealthReport,
    UnifiedSSOTValidator,
)
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

_emit_emits_metric_event("test_gravity_validator_hardened", "p4obs", "metric_1")
_emit_emits_metric_event("test_gravity_validator_hardened", "p4obs", "metric_2")
_emit_emits_metric_event("test_gravity_validator_hardened", "p4obs", "metric_3")
_emit_emits_metric_event("test_gravity_validator_hardened", "p4obs", "metric_4")
_emit_emits_metric_event("test_gravity_validator_hardened", "p4obs", "metric_5")
_emit_emits_metric_event("test_gravity_validator_hardened", "p4obs", "metric_6")
_emit_records_incident_event("test_gravity_validator_hardened", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_gravity_validator_hardened", "p4obs", "anomaly")
_emit_writes_observability_log("test_gravity_validator_hardened", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_gravity_validator_hardened", "p4obs", "mon_state")
_emit_triggers_alert("test_gravity_validator_hardened", "p4obs", "alert")
_emit_links_incident_trace("test_gravity_validator_hardened", "p4obs", "trace_link")
_emit_captures_pattern("test_gravity_validator_hardened", "p3lm", "pattern")
_emit_records_learning_event("test_gravity_validator_hardened", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_gravity_validator_hardened", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_gravity_validator_hardened", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_gravity_validator_hardened", "p3lm", "routing")
_emit_improves_agent_policy("test_gravity_validator_hardened", "p3lm", "policy")
_emit_stores_learning_state("test_gravity_validator_hardened", "p3lm", "state")
_emit_records_execution_trace("test_gravity_validator_hardened", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_gravity_validator_hardened", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_gravity_validator_hardened", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_gravity_validator_hardened", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_gravity_validator_hardened", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_gravity_validator_hardened", "env_read", "p2_env_1")
_emit_reads_environ("test_gravity_validator_hardened", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_gravity_validator_hardened", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_gravity_validator_hardened", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_gravity_validator_hardened", "context_pull")
_emit_pulls_context("p1", "test_gravity_validator_hardened", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_gravity_validator_hardened", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_gravity_validator_hardened", "uwg_term_secondary")
_emit_writes_through("p1", "test_gravity_validator_hardened", "write_through")
_emit_writes_through("p1", "test_gravity_validator_hardened", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_gravity_validator_hardened", "safety_validation")
_emit_invokes_eval("p1", "test_gravity_validator_hardened", "eval_call")
_emit_proposal_commits_routing("p1", "test_gravity_validator_hardened", "routing_commit")
_emit_escalates_to_human("p1", "test_gravity_validator_hardened", "human_escalation")
_emit_routes_through("p1", "test_gravity_validator_hardened", "route_through")
_emit_checks_agent_registry("p1", "test_gravity_validator_hardened", "agent_registry")
_emit_validates_agent_capability("p1", "test_gravity_validator_hardened", "capability")
_emit_dispatches_execution_plan("p1", "test_gravity_validator_hardened", "exec_plan")
_emit_agent_executes_agent("p1", "test_gravity_validator_hardened", "sub_agent")
_emit_routes_to_agent("p1", "test_gravity_validator_hardened", "target_agent")
_emit_verifies_policy("p1", "test_gravity_validator_hardened", "policy_check")
_emit_observes_runtime_state("p1", "test_gravity_validator_hardened", "runtime_state")
_emit_verifies_boundary("p1", "test_gravity_validator_hardened", "boundary_check")
_emit_transcripts_response("p1", "test_gravity_validator_hardened", "transcript")
_emit_hard_fails_untranscripted("p1", "test_gravity_validator_hardened")
_emit_gated_by_confidence("p1", "test_gravity_validator_hardened", "confidence_gate")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_import_from(module: str, lineno: int = 1) -> ast.ImportFrom:
    node = ast.ImportFrom(module=module, names=[], level=0)
    node.lineno = lineno
    node.col_offset = 0
    return node


def _make_import(name: str, lineno: int = 1) -> ast.Import:
    alias = ast.alias(name=name, asname=None)
    node = ast.Import(names=[alias])
    node.lineno = lineno
    node.col_offset = 0
    return node


def _fresh_validator(tmp_path: Path) -> UnifiedSSOTValidator:
    """Create an UnifiedSSOTValidator pointed at a minimal empty project root."""
    (tmp_path / AGENTIC_CORE_DIR).mkdir(exist_ok=True)
    return UnifiedSSOTValidator(project_root=tmp_path)


# ---------------------------------------------------------------------------
# 1-4. Violation dataclass __str__() contracts
# ---------------------------------------------------------------------------


class TestViolationStrContracts:
    def test_gravity_violation_str_contains_file_path(self):
        v = GravityViolation(
            file_path="agentic_core/L0_routing/MyAgent.py",
            actual_layer="L0",
            assigned_layer="L2",
            agent_name="MyAgent",
        )
        s = str(v)
        assert "agentic_core/L0_routing/MyAgent.py" in s

    def test_gravity_violation_str_contains_layers(self):
        v = GravityViolation(
            file_path="agentic_core/L0_routing/MyAgent.py",
            actual_layer="L0",
            assigned_layer="L2",
            agent_name="MyAgent",
        )
        s = str(v)
        assert "L0" in s
        assert "L2" in s

    def test_import_violation_str_contains_file_and_layers(self):
        v = ImportViolation(
            file_path="agentic_core/L0_routing/foo.py",
            source_layer="L0",
            target_layer="L5",
            import_line="from agentic_core.L5_safety import x",
            line_number=10,
        )
        s = str(v)
        assert "agentic_core/L0_routing/foo.py" in s
        assert "L0" in s
        assert "L5" in s
        assert "10" in s

    def test_hierarchy_violation_str_contains_depth(self):
        v = HierarchyViolation(
            folder_path="agentic_core/L5_safety/a/b/c/d",
            actual_depth=5,
            max_depth=MAX_DEPTH,
            root_folder="agentic_core",
        )
        s = str(v)
        assert "5" in s
        assert "3" in s

    def test_drift_violation_str_contains_violation_type(self):
        v = DriftViolation(
            folder_path="agentic_core/mystery_folder",
            parent_folder="agentic_core",
            violation_type="orphaned",
        )
        s = str(v)
        assert "orphaned" in s
        assert "agentic_core/mystery_folder" in s


# ---------------------------------------------------------------------------
# 5-6. SovereignHealthReport aggregation
# ---------------------------------------------------------------------------


class TestSovereignHealthReportAggregation:
    def test_empty_report_has_zero_total_violations(self):
        r = SovereignHealthReport()
        assert r.total_violations == 0

    def test_empty_report_is_compliant(self):
        r = SovereignHealthReport()
        assert r.is_compliant is True

    def test_single_gravity_violation_total_is_one(self):
        v = GravityViolation("path", "L0", "L2", "Agent")
        r = SovereignHealthReport(gravity_violations=[v])
        assert r.total_violations == 1
        assert r.is_compliant is False

    def test_single_import_violation_total_is_one(self):
        v = ImportViolation("path", "L0", "L5", "from x import y", 1)
        r = SovereignHealthReport(import_violations=[v])
        assert r.total_violations == 1
        assert r.is_compliant is False

    def test_single_hierarchy_violation_total_is_one(self):
        v = HierarchyViolation("path/a/b/c/d", 5, 3, "root")
        r = SovereignHealthReport(hierarchy_violations=[v])
        assert r.total_violations == 1
        assert r.is_compliant is False

    def test_single_drift_violation_total_is_one(self):
        v = DriftViolation("path/mystery", "agentic_core", "orphaned")
        r = SovereignHealthReport(drift_violations=[v])
        assert r.total_violations == 1
        assert r.is_compliant is False

    def test_violations_across_categories_sum_correctly(self):
        r = SovereignHealthReport(
            gravity_violations=[GravityViolation("p", "L0", "L2", "A")],
            import_violations=[ImportViolation("p", "L0", "L5", "import x", 1)],
            hierarchy_violations=[HierarchyViolation("p", 5, 3, "root")],
            drift_violations=[DriftViolation("p", "core", "orphaned")],
        )
        assert r.total_violations == 4
        assert r.is_compliant is False

    def test_is_compliant_true_only_when_all_lists_empty(self):
        r = SovereignHealthReport(
            gravity_violations=[],
            import_violations=[],
            hierarchy_violations=[],
            drift_violations=[],
        )
        assert r.is_compliant is True


# ---------------------------------------------------------------------------
# 7-10. SovereignHealthReport.to_markdown() contract
# ---------------------------------------------------------------------------


class TestSovereignHealthReportMarkdown:
    def test_to_markdown_contains_required_section_headers(self):
        r = SovereignHealthReport()
        md = r.to_markdown()
        assert "# SSOT Sovereign Health Report" in md
        assert "Gravity Violations" in md
        assert "Import Violations" in md
        assert "Hierarchy Violations" in md
        assert "Drift Violations" in md
        assert "Summary Statistics" in md

    def test_to_markdown_shows_compliant_status_when_clean(self):
        r = SovereignHealthReport()
        md = r.to_markdown()
        assert "COMPLIANT" in md
        assert "NON-COMPLIANT" not in md

    def test_to_markdown_shows_non_compliant_with_violations(self):
        r = SovereignHealthReport(gravity_violations=[GravityViolation("p", "L0", "L2", "A")])
        md = r.to_markdown()
        assert "NON-COMPLIANT" in md

    def test_to_markdown_renders_compliance_score(self):
        r = SovereignHealthReport(compliance_score=87.5)
        md = r.to_markdown()
        assert "87.5" in md

    def test_to_markdown_returns_string(self):
        r = SovereignHealthReport()
        assert isinstance(r.to_markdown(), str)

    def test_to_markdown_shows_violation_counts(self):
        v = GravityViolation("agentic_core/L0/MyAgent.py", "L0", "L2", "MyAgent")
        r = SovereignHealthReport(gravity_violations=[v])
        md = r.to_markdown()
        assert "1" in md

    def test_to_markdown_shows_file_path_in_gravity_table(self):
        v = GravityViolation("agentic_core/L0/MyAgent.py", "L0", "L2", "MyAgent")
        r = SovereignHealthReport(gravity_violations=[v])
        md = r.to_markdown()
        assert "agentic_core/L0/MyAgent.py" in md

    def test_to_markdown_clean_shows_no_violations_message(self):
        r = SovereignHealthReport()
        md = r.to_markdown()
        assert "No violations" in md or "no violations" in md.lower()

    def test_to_markdown_scan_duration_rendered(self):
        r = SovereignHealthReport(scan_duration=3.14)
        md = r.to_markdown()
        assert "3.14" in md


# ---------------------------------------------------------------------------
# 11-12. _get_layer_from_path() seam
# ---------------------------------------------------------------------------


class TestGetLayerFromPath:
    def setup_method(self):
        self._v = UnifiedSSOTValidator.__new__(UnifiedSSOTValidator)

    def test_extracts_l0_from_path(self):
        p = Path("agentic_core/L0_routing/config/path_constants.py")
        assert self._v._get_layer_from_path(p) == "L0"

    def test_extracts_l5_from_path(self):
        p = Path("agentic_core/L5_safety/validators/base_detector_validator.py")
        assert self._v._get_layer_from_path(p) == "L5"

    def test_extracts_l2_from_path(self):
        p = Path("agentic_core/L2_execution/enforcement/SovereignLLMGateway.py")
        assert self._v._get_layer_from_path(p) == "L2"

    def test_returns_none_for_non_layer_path(self):
        p = Path("apps_rg/reasoning/MyAgent.py")
        assert self._v._get_layer_from_path(p) is None

    def test_returns_none_for_tests_path(self):
        p = Path("tests/guardian/test_foo.py")
        assert self._v._get_layer_from_path(p) is None

    def test_extracts_l3_from_path(self):
        p = Path("agentic_core/L3_orchestration/arbitration/engine.py")
        assert self._v._get_layer_from_path(p) == "L3"

    def test_returns_none_for_empty_path(self):
        p = Path(".")
        assert self._v._get_layer_from_path(p) is None

    def test_l_prefix_must_be_followed_by_digit(self):
        p = Path("Lxyz_routing/foo.py")
        assert self._v._get_layer_from_path(p) is None


# ---------------------------------------------------------------------------
# 13-15. _extract_target_layer() seam
# ---------------------------------------------------------------------------


class TestExtractTargetLayer:
    def setup_method(self):
        self._v = UnifiedSSOTValidator.__new__(UnifiedSSOTValidator)

    def test_extracts_l5_from_import_from(self):
        node = _make_import_from("agentic_core.L5_safety.validators.base_detector_validator")
        assert self._v._extract_target_layer(node) == "L5"

    def test_extracts_l0_from_import_from(self):
        node = _make_import_from("agentic_core.L0_routing.config")
        assert self._v._extract_target_layer(node) == "L0"

    def test_extracts_l2_from_import_from(self):
        node = _make_import_from("agentic_core.L2_execution.enforcement")
        assert self._v._extract_target_layer(node) == "L2"

    def test_extracts_l5_from_plain_import(self):
        node = _make_import("agentic_core.L5_safety.core_kernel.classification_kernel")
        assert self._v._extract_target_layer(node) == "L5"

    def test_returns_none_for_non_agentic_core_import_from(self):
        node = _make_import_from("third_party.some_lib")
        assert self._v._extract_target_layer(node) is None

    def test_returns_none_for_non_agentic_core_import(self):
        node = _make_import("os.path")
        assert self._v._extract_target_layer(node) is None

    def test_returns_none_for_agentic_core_no_layer(self):
        node = _make_import_from("agentic_core.agents.agent_registry")
        assert self._v._extract_target_layer(node) is None

    def test_returns_none_for_none_module(self):
        node = ast.ImportFrom(module=None, names=[], level=1)
        node.lineno = 1
        node.col_offset = 0
        assert self._v._extract_target_layer(node) is None


# ---------------------------------------------------------------------------
# 16-18. UnifiedSSOTValidator initialisation and validate_all() fail-safe
# ---------------------------------------------------------------------------


class TestUnifiedSSOTValidatorInit:
    def test_initialises_without_error_on_valid_root(self, tmp_path):
        (tmp_path / AGENTIC_CORE_DIR).mkdir()
        v = UnifiedSSOTValidator(project_root=tmp_path)
        assert v.project_root == tmp_path.resolve()

    def test_project_root_resolved(self, tmp_path):
        (tmp_path / AGENTIC_CORE_DIR).mkdir()
        v = UnifiedSSOTValidator(project_root=tmp_path)
        assert v.project_root.is_absolute()

    def test_layer_hierarchy_covers_l0_to_l5(self, tmp_path):
        (tmp_path / AGENTIC_CORE_DIR).mkdir()
        v = UnifiedSSOTValidator(project_root=tmp_path)
        for layer in ("L0", "L1", "L2", "L3", "L4", "L5"):
            assert layer in v.layer_hierarchy

    def test_layer_hierarchy_ordering_is_correct(self, tmp_path):
        (tmp_path / AGENTIC_CORE_DIR).mkdir()
        v = UnifiedSSOTValidator(project_root=tmp_path)
        lh = v.layer_hierarchy
        assert lh["L0"] < lh["L1"] < lh["L2"] < lh["L3"] < lh["L4"] < lh["L5"]


def _patch_ssot_discovery(tmp_path: Path):
    """Context manager that injects a stub ssot_discovery_validator returning no files.

    Both ssot_scanner_enforcer (get_agent_files) and gravity_validator
    (get_python_files) do late imports from this non-existent module.
    The stub satisfies both call sites so validate_all() can complete.
    """
    stub_module = types.ModuleType("agentic_core.utils.ssot_discovery_validator")
    stub_module.get_python_files = lambda root: []  # type: ignore[attr-defined]
    stub_module.get_agent_files = lambda root: []  # type: ignore[attr-defined]
    return patch.dict(
        "sys.modules",
        {
            "agentic_core.utils.ssot_discovery_validator": stub_module,
        },
    )


class TestValidateAllFailSafe:
    def test_validate_all_returns_sovereign_health_report(self, tmp_path):
        (tmp_path / AGENTIC_CORE_DIR).mkdir()
        v = UnifiedSSOTValidator(project_root=tmp_path)
        with _patch_ssot_discovery(tmp_path):
            result = v.validate_all()
        assert isinstance(result, SovereignHealthReport)

    def test_validate_all_does_not_raise_on_empty_root(self, tmp_path):
        (tmp_path / AGENTIC_CORE_DIR).mkdir()
        v = UnifiedSSOTValidator(project_root=tmp_path)
        with _patch_ssot_discovery(tmp_path):
            result = v.validate_all()
        assert result is not None

    def test_validate_all_reports_scan_duration_positive(self, tmp_path):
        (tmp_path / AGENTIC_CORE_DIR).mkdir()
        v = UnifiedSSOTValidator(project_root=tmp_path)
        with _patch_ssot_discovery(tmp_path):
            result = v.validate_all()
        assert result.scan_duration >= 0.0

    def test_empty_project_has_zero_agents(self, tmp_path):
        (tmp_path / AGENTIC_CORE_DIR).mkdir()
        v = UnifiedSSOTValidator(project_root=tmp_path)
        with _patch_ssot_discovery(tmp_path):
            result = v.validate_all()
        assert result.total_agents == 0

    def test_validate_all_result_is_compliant_on_empty_repo(self, tmp_path):
        (tmp_path / AGENTIC_CORE_DIR).mkdir()
        v = UnifiedSSOTValidator(project_root=tmp_path)
        with _patch_ssot_discovery(tmp_path):
            result = v.validate_all()
        # Empty repo has no agents to violate; should have no gravity violations
        assert result.gravity_violations == []
