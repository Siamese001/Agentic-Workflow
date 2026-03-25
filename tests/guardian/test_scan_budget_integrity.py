"""
Scan Budget Integrity Enforcement.

Verifies that the contract integrity checker correctly detects:
1. Scanning guardians that raise RuntimeError for scan caps (violation)
2. Scanning guardians that import cap constants but NOT guard_scan_budget (violation)
3. Scanning guardians that correctly use guard_scan_budget (pass)

Uses synthetic AST fixtures — no actual files created.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_scan_budget_integrity")
# REMOVED: _emit_applies_guardrail("p0", "test_scan_budget_integrity", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_scan_budget_integrity", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_scan_budget_integrity", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_scan_budget_integrity")
# REMOVED: emit_determinism_digest("p0", "test_scan_budget_integrity")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_scan_budget_integrity", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_scan_budget_integrity", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_scan_budget_integrity", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_scan_budget_integrity", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_scan_budget_integrity", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_scan_budget_integrity", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_scan_budget_integrity", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_scan_budget_integrity", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_scan_budget_integrity", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_scan_budget_integrity", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_scan_budget_integrity", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_scan_budget_integrity", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_scan_budget_integrity", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_scan_budget_integrity", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_scan_budget_integrity", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_scan_budget_integrity", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_scan_budget_integrity", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_scan_budget_integrity", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_scan_budget_integrity", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_scan_budget_integrity", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_contract_integrity import (
    _check_imports_scan_caps,
    _check_no_raise_exception_for_caps,
    _check_no_raise_runtime_error_for_caps,
    _check_uses_guard_scan_budget,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_scan_budget_integrity", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_scan_budget_integrity", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_scan_budget_integrity", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_scan_budget_integrity", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_scan_budget_integrity", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_scan_budget_integrity", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_scan_budget_integrity", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_scan_budget_integrity", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_scan_budget_integrity", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_scan_budget_integrity", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_scan_budget_integrity", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_scan_budget_integrity", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_scan_budget_integrity", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_scan_budget_integrity", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_scan_budget_integrity", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_scan_budget_integrity", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_scan_budget_integrity", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_scan_budget_integrity", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_scan_budget_integrity", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_scan_budget_integrity", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_scan_budget_integrity", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_scan_budget_integrity", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_scan_budget_integrity", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_scan_budget_integrity", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_scan_budget_integrity", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_scan_budget_integrity", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_scan_budget_integrity", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_scan_budget_integrity", "runtime_state", "p2_rt_2")
# REMOVED: _emit_escalates_to_human("p1", "test_scan_budget_integrity", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_scan_budget_integrity", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_scan_budget_integrity", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_scan_budget_integrity", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_scan_budget_integrity", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_scan_budget_integrity", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_scan_budget_integrity", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_scan_budget_integrity", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_scan_budget_integrity", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_scan_budget_integrity", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_scan_budget_integrity", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_scan_budget_integrity")
# REMOVED: _emit_gated_by_confidence("p1", "test_scan_budget_integrity", "confidence_gate")

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Synthetic source fixtures
# ---------------------------------------------------------------------------

GOOD_GUARDIAN_SOURCE = """\
from agentic_core.L0_routing.types.guardian_contract_types import (
    MAX_FILES_PER_SCAN,
    MAX_FOLDER_DEPTH,
    guard_scan_budget,
)

def scan(repo_root):
    count = 0
    for f in repo_root.rglob("*"):
        count += 1
        breach = guard_scan_budget(count)
        if breach is not None:
            return breach
    return []
"""

BAD_GUARDIAN_RAISES_RUNTIME_ERROR = """\
from agentic_core.L0_routing.types.guardian_contract_types import (
    MAX_FILES_PER_SCAN,
    MAX_FOLDER_DEPTH,
)

def scan(repo_root):
    count = 0
    for f in repo_root.rglob("*"):
        count += 1
        if count > 10000:
            raise RuntimeError("Exceeded MAX_FILES_PER_SCAN limit")
    return []
"""

BAD_GUARDIAN_NO_BUDGET_HELPER = """\
from agentic_core.L0_routing.types.guardian_contract_types import (
    MAX_FILES_PER_SCAN,
    MAX_FOLDER_DEPTH,
)

def scan(repo_root):
    count = 0
    for f in repo_root.rglob("*"):
        count += 1
        if count > MAX_FILES_PER_SCAN:
            return "too many files"
    return []
"""

NON_SCANNING_GUARDIAN_SOURCE = """\
from agentic_core.L0_routing.types.guardian_contract_types import (
    GuardianResult,
    CheckStatus,
)

def run_guardian(repo_root):
    result = GuardianResult(guardian_id="simple")
    return result
"""

BAD_GUARDIAN_RAISES_VALUE_ERROR = """\
from agentic_core.L0_routing.types.guardian_contract_types import (
    MAX_FILES_PER_SCAN,
    MAX_FOLDER_DEPTH,
)

def scan(repo_root):
    count = 0
    for f in repo_root.rglob("*"):
        count += 1
        if count > 10000:
            raise ValueError("MAX_FILES_PER_SCAN exceeded")
    return []
"""

BAD_GUARDIAN_RAISES_CUSTOM_EXCEPTION = """\
from agentic_core.L0_routing.types.guardian_contract_types import (
    MAX_FILES_PER_SCAN,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
# REMOVED: _emit_pulls_context("p1", "test_scan_budget_integrity", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_scan_budget_integrity", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_scan_budget_integrity", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_scan_budget_integrity", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_scan_budget_integrity", "write_through")
# REMOVED: _emit_writes_through("p1", "test_scan_budget_integrity", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_scan_budget_integrity", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_scan_budget_integrity", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_scan_budget_integrity", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_scan_budget_integrity", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_scan_budget_integrity", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_scan_budget_integrity", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_scan_budget_integrity", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_scan_budget_integrity", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_scan_budget_integrity", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_scan_budget_integrity", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_scan_budget_integrity", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_scan_budget_integrity", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_scan_budget_integrity", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_scan_budget_integrity", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_scan_budget_integrity")
# REMOVED: _emit_gated_by_confidence("p1", "test_scan_budget_integrity", "confidence_gate")

def scan(repo_root):
    count = 0
    for f in repo_root.rglob("*"):
        count += 1
        if count > 10000:
            raise ScanBudgetError("Breached MAX_FILES_PER_SCAN")
    return []
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestScanCapImportDetection:
    """AST correctly identifies guardians that import scan cap constants."""

    def test_detects_scan_cap_imports(self):
        tree = ast.parse(GOOD_GUARDIAN_SOURCE)
        assert _check_imports_scan_caps(tree) is True

    def test_non_scanning_guardian_has_no_caps(self):
        tree = ast.parse(NON_SCANNING_GUARDIAN_SOURCE)
        assert _check_imports_scan_caps(tree) is False


class TestGuardScanBudgetUsage:
    """AST correctly identifies guard_scan_budget import."""

    def test_detects_guard_scan_budget_import(self):
        tree = ast.parse(GOOD_GUARDIAN_SOURCE)
        assert _check_uses_guard_scan_budget(tree) is True

    def test_missing_guard_scan_budget_detected(self):
        tree = ast.parse(BAD_GUARDIAN_NO_BUDGET_HELPER)
        assert _check_uses_guard_scan_budget(tree) is False


class TestRuntimeErrorForCapsDetection:
    """AST correctly flags raise RuntimeError mentioning scan cap names."""

    def test_detects_raise_runtime_error_with_cap_name(self):
    """Test detects_raise_runtime_error_with_cap_name runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute detects_raise_runtime_error_with_cap_name
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions


class TestAnyExceptionForCapsDetection:
    """Broadened check flags any raise <Exception> mentioning scan cap names."""

    def test_detects_value_error_with_cap_name(self):
        tree = ast.parse(BAD_GUARDIAN_RAISES_VALUE_ERROR)
        violations = _check_no_raise_exception_for_caps(tree)
        assert len(violations) > 0, "Should detect ValueError mentioning MAX_FILES_PER_SCAN"
        assert violations[0][1] == "ValueError"

    def test_detects_custom_exception_with_cap_name(self):
        tree = ast.parse(BAD_GUARDIAN_RAISES_CUSTOM_EXCEPTION)
        violations = _check_no_raise_exception_for_caps(tree)
        assert len(violations) > 0, "Should detect ScanBudgetError mentioning MAX_FILES_PER_SCAN"
        assert violations[0][1] == "ScanBudgetError"

    def test_detects_runtime_error_with_cap_name(self):
    """Test detects_runtime_error_with_cap_name runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute detects_runtime_error_with_cap_name
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        assert violations == []


class TestEndToEndIntegrityPattern:
    """Full pattern: scanning guardian → must import guard_scan_budget, must not raise RuntimeError."""

    def test_good_guardian_passes_all_checks(self):
        tree = ast.parse(GOOD_GUARDIAN_SOURCE)
        assert _check_imports_scan_caps(tree) is True
        assert _check_uses_guard_scan_budget(tree) is True
        assert _check_no_raise_runtime_error_for_caps(tree) == []

    def test_bad_guardian_raising_error_fails(self):
        tree = ast.parse(BAD_GUARDIAN_RAISES_RUNTIME_ERROR)
        assert _check_imports_scan_caps(tree) is True
        assert _check_no_raise_runtime_error_for_caps(tree) != []

    def test_bad_guardian_missing_helper_fails(self):
        tree = ast.parse(BAD_GUARDIAN_NO_BUDGET_HELPER)
        assert _check_imports_scan_caps(tree) is True
        assert _check_uses_guard_scan_budget(tree) is False
