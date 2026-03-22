"""
Phase F: Guardian Self-Integrity Tests.

Tests the Guardian-of-Guardians (run_guardian_contract_integrity.py).
Verifies:
1. Real guardian scripts pass integrity check
2. Synthetic non-compliant script is caught
3. AST-based checks are accurate
4. Schema compliance of integrity result
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
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

_emit_records_execution_trace("p0", "evidence", "test_guardian_self_integrity")
_emit_applies_guardrail("p0", "test_guardian_self_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_guardian_self_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_guardian_self_integrity", "state_snapshot")
emit_replay_key("p0", "test_guardian_self_integrity")
emit_determinism_digest("p0", "test_guardian_self_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_guardian_self_integrity", "execution_auth")
_emit_validates_capability("p2", "test_guardian_self_integrity", "capability_check")
_emit_routes_to_capability("p2", "test_guardian_self_integrity", "capability_route")
_emit_writes_via_uwg("p2", "test_guardian_self_integrity", "uwg_write")
_emit_blocks_direct_write("p2", "test_guardian_self_integrity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_guardian_self_integrity", "tool_invocation")
_emit_captures_execution_output("p2", "test_guardian_self_integrity", "exec_output")
_emit_dispatches_agent("p3", "test_guardian_self_integrity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_guardian_self_integrity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_guardian_self_integrity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_guardian_self_integrity", "healing_outcome")
_emit_escalates_failure("p3", "test_guardian_self_integrity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_guardian_self_integrity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_guardian_self_integrity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_guardian_self_integrity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_guardian_self_integrity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_guardian_self_integrity", "eval_metric")
_emit_stores_embedding("p4", "test_guardian_self_integrity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_guardian_self_integrity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_guardian_self_integrity", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import ast

from agentic_core.L0_routing.scripts.run_guardian_contract_integrity import (
    _check_imports_contract,
    _check_imports_normalize,
    _check_no_raw_json_dumps,
    _check_returns_guardian_result,
    run_contract_integrity_guardian,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianStatus,
    check_schema_compatibility,
    validate_no_absolute_paths,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_links_incident_trace,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)

_emit_emits_metric_event("test_guardian_self_integrity", "p4obs", "metric_1")
_emit_emits_metric_event("test_guardian_self_integrity", "p4obs", "metric_2")
_emit_emits_metric_event("test_guardian_self_integrity", "p4obs", "metric_3")
_emit_emits_metric_event("test_guardian_self_integrity", "p4obs", "metric_4")
_emit_emits_metric_event("test_guardian_self_integrity", "p4obs", "metric_5")
_emit_emits_metric_event("test_guardian_self_integrity", "p4obs", "metric_6")
_emit_records_incident_event("test_guardian_self_integrity", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_guardian_self_integrity", "p4obs", "anomaly")
_emit_writes_observability_log("test_guardian_self_integrity", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_guardian_self_integrity", "p4obs", "mon_state")
_emit_triggers_alert("test_guardian_self_integrity", "p4obs", "alert")
_emit_links_incident_trace("test_guardian_self_integrity", "p4obs", "trace_link")
_emit_captures_pattern("test_guardian_self_integrity", "p3lm", "pattern")
_emit_records_learning_event("test_guardian_self_integrity", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_guardian_self_integrity", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_guardian_self_integrity", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_guardian_self_integrity", "p3lm", "routing")
_emit_improves_agent_policy("test_guardian_self_integrity", "p3lm", "policy")
_emit_stores_learning_state("test_guardian_self_integrity", "p3lm", "state")
_emit_records_execution_trace("test_guardian_self_integrity", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_guardian_self_integrity", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_guardian_self_integrity", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_guardian_self_integrity", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_guardian_self_integrity", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_guardian_self_integrity", "env_read", "p2_env_1")
_emit_reads_environ("test_guardian_self_integrity", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_guardian_self_integrity", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_guardian_self_integrity", "runtime_state", "p2_rt_2")
_emit_escalates_to_human("p1", "test_guardian_self_integrity", "human_escalation")
_emit_routes_through("p1", "test_guardian_self_integrity", "route_through")
_emit_checks_agent_registry("p1", "test_guardian_self_integrity", "agent_registry")
_emit_validates_agent_capability("p1", "test_guardian_self_integrity", "capability")
_emit_dispatches_execution_plan("p1", "test_guardian_self_integrity", "exec_plan")
_emit_agent_executes_agent("p1", "test_guardian_self_integrity", "sub_agent")
_emit_routes_to_agent("p1", "test_guardian_self_integrity", "target_agent")
_emit_verifies_policy("p1", "test_guardian_self_integrity", "policy_check")
_emit_observes_runtime_state("p1", "test_guardian_self_integrity", "runtime_state")
_emit_verifies_boundary("p1", "test_guardian_self_integrity", "boundary_check")
_emit_transcripts_response("p1", "test_guardian_self_integrity", "transcript")
_emit_hard_fails_untranscripted("p1", "test_guardian_self_integrity")
_emit_gated_by_confidence("p1", "test_guardian_self_integrity", "confidence_gate")

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Fixtures: synthetic scripts
# ---------------------------------------------------------------------------

COMPLIANT_SCRIPT = '''
"""Compliant guardian."""
from agentic_core.L0_routing.types.guardian_contract_types import (
    GuardianResult,
    normalize_repo_path,
)

def run_guardian_example(repo_root=None) -> GuardianResult:
    return GuardianResult(guardian_id="example")
'''

NON_COMPLIANT_SCRIPT = '''
"""Non-compliant guardian — raw dict emission."""
import json

def run_guardian_bad(repo_root=None) -> dict:
    return {"status": "PASS"}
'''


# ---------------------------------------------------------------------------
# 1. AST check unit tests
# ---------------------------------------------------------------------------


class TestASTChecks:
    def test_compliant_imports_contract(self):
        tree = ast.parse(COMPLIANT_SCRIPT)
        assert _check_imports_contract(tree) is True

    def test_non_compliant_missing_contract(self):
        tree = ast.parse(NON_COMPLIANT_SCRIPT)
        assert _check_imports_contract(tree) is False

    def test_compliant_imports_normalize(self):
        tree = ast.parse(COMPLIANT_SCRIPT)
        assert _check_imports_normalize(tree) is True

    def test_non_compliant_missing_normalize(self):
        tree = ast.parse(NON_COMPLIANT_SCRIPT)
        assert _check_imports_normalize(tree) is False

    def test_compliant_returns_guardian_result(self):
        tree = ast.parse(COMPLIANT_SCRIPT)
        assert _check_returns_guardian_result(tree) is True

    def test_non_compliant_returns_dict(self):
        tree = ast.parse(NON_COMPLIANT_SCRIPT)
        assert _check_returns_guardian_result(tree) is False

    def test_raw_json_dumps_detected(self):
        script_with_dumps = """
import json
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
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
_emit_pulls_context("p1", "test_guardian_self_integrity", "context_pull")
_emit_pulls_context("p1", "test_guardian_self_integrity", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_guardian_self_integrity", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_guardian_self_integrity", "uwg_term_secondary")
_emit_writes_through("p1", "test_guardian_self_integrity", "write_through")
_emit_writes_through("p1", "test_guardian_self_integrity", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_guardian_self_integrity", "safety_validation")
_emit_invokes_eval("p1", "test_guardian_self_integrity", "eval_call")
_emit_proposal_commits_routing("p1", "test_guardian_self_integrity", "routing_commit")
_emit_escalates_to_human("p1", "test_guardian_self_integrity", "human_escalation")
_emit_routes_through("p1", "test_guardian_self_integrity", "route_through")
_emit_checks_agent_registry("p1", "test_guardian_self_integrity", "agent_registry")
_emit_validates_agent_capability("p1", "test_guardian_self_integrity", "capability")
_emit_dispatches_execution_plan("p1", "test_guardian_self_integrity", "exec_plan")
_emit_agent_executes_agent("p1", "test_guardian_self_integrity", "sub_agent")
_emit_routes_to_agent("p1", "test_guardian_self_integrity", "target_agent")
_emit_verifies_policy("p1", "test_guardian_self_integrity", "policy_check")
_emit_observes_runtime_state("p1", "test_guardian_self_integrity", "runtime_state")
_emit_verifies_boundary("p1", "test_guardian_self_integrity", "boundary_check")
_emit_transcripts_response("p1", "test_guardian_self_integrity", "transcript")
_emit_hard_fails_untranscripted("p1", "test_guardian_self_integrity")
_emit_gated_by_confidence("p1", "test_guardian_self_integrity", "confidence_gate")
def bad():
    return json.dumps({"key": "val"})
"""
        tree = ast.parse(script_with_dumps)
        lines = _check_no_raw_json_dumps(tree)
        assert len(lines) > 0

    def test_no_raw_json_dumps_in_compliant(self):
        tree = ast.parse(COMPLIANT_SCRIPT)
        lines = _check_no_raw_json_dumps(tree)
        assert lines == []


# ---------------------------------------------------------------------------
# 2. Real repo integrity check
# ---------------------------------------------------------------------------


class TestRealRepoIntegrity:
    def test_real_guardians_pass(self):
        """All real guardian scripts must pass the integrity checker."""
        result = run_contract_integrity_guardian()
        failed_checks = [c for c in result.checks if c.status == CheckStatus.FAIL.value]
        assert not failed_checks, (
            f"Real guardian scripts have integrity violations: "
            f"{[c.check_id + ': ' + c.details for c in failed_checks]}"
        )

    def test_real_result_is_pass(self):
        result = run_contract_integrity_guardian()
        assert result.status == GuardianStatus.PASS.value, (
            f"Integrity guardian status: {result.status}, summary: {result.summary}"
        )

    def test_scripts_found(self):
        result = run_contract_integrity_guardian()
        assert result.metrics["scripts_checked"] >= 2, (
            "Should find at least 2 guardian scripts (hygiene + manifest)"
        )


# ---------------------------------------------------------------------------
# 3. Synthetic non-compliant script detected
# ---------------------------------------------------------------------------


class TestSyntheticViolation:
    def test_non_compliant_detected(self, tmp_path: Path):
        """A synthetic non-compliant script should be caught."""
        # Create a fake repo with a non-compliant guardian script
        scripts_dir = tmp_path / L0_ROUTING_DIR / "scripts"
        scripts_dir.mkdir(parents=True)
        bad_script = scripts_dir / "run_guardian_fake.py"
        bad_script.write_text(NON_COMPLIANT_SCRIPT, encoding="utf-8")

        result = run_contract_integrity_guardian(repo_root=tmp_path)
        assert result.status == GuardianStatus.FAIL.value
        assert result.metrics["violations_found"] > 0


# ---------------------------------------------------------------------------
# 4. Schema compliance of integrity result
# ---------------------------------------------------------------------------


class TestSchemaCompliance:
    def test_no_absolute_paths(self):
        result = run_contract_integrity_guardian()
        violations = validate_no_absolute_paths(result.to_dict())
        assert violations == [], f"Absolute paths: {violations}"

    def test_schema_compatible(self):
        result = run_contract_integrity_guardian()
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"Schema drift: {errors}"

    def test_guardian_id_stable(self):
        result = run_contract_integrity_guardian()
        assert result.guardian_id == "contract_integrity"
