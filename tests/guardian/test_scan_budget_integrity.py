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

_emit_records_execution_trace("p0", "evidence", "test_scan_budget_integrity")
_emit_applies_guardrail("p0", "test_scan_budget_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_scan_budget_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_scan_budget_integrity", "state_snapshot")
emit_replay_key("p0", "test_scan_budget_integrity")
emit_determinism_digest("p0", "test_scan_budget_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_scan_budget_integrity", "execution_auth")
_emit_validates_capability("p2", "test_scan_budget_integrity", "capability_check")
_emit_routes_to_capability("p2", "test_scan_budget_integrity", "capability_route")
_emit_writes_via_uwg("p2", "test_scan_budget_integrity", "uwg_write")
_emit_blocks_direct_write("p2", "test_scan_budget_integrity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_scan_budget_integrity", "tool_invocation")
_emit_captures_execution_output("p2", "test_scan_budget_integrity", "exec_output")
_emit_dispatches_agent("p3", "test_scan_budget_integrity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_scan_budget_integrity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_scan_budget_integrity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_scan_budget_integrity", "healing_outcome")
_emit_escalates_failure("p3", "test_scan_budget_integrity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_scan_budget_integrity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_scan_budget_integrity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_scan_budget_integrity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_scan_budget_integrity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_scan_budget_integrity", "eval_metric")
_emit_stores_embedding("p4", "test_scan_budget_integrity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_scan_budget_integrity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_scan_budget_integrity", "exec_snapshot_link")

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
        tree = ast.parse(BAD_GUARDIAN_RAISES_RUNTIME_ERROR)
        violations = _check_no_raise_runtime_error_for_caps(tree)
        assert len(violations) > 0, "Should detect RuntimeError mentioning MAX_FILES_PER_SCAN"

    def test_no_false_positive_on_correct_guardian(self):
        tree = ast.parse(GOOD_GUARDIAN_SOURCE)
        violations = _check_no_raise_runtime_error_for_caps(tree)
        assert violations == [], f"Good guardian should have no violations: {violations}"

    def test_no_false_positive_on_non_scanning_guardian(self):
        tree = ast.parse(NON_SCANNING_GUARDIAN_SOURCE)
        violations = _check_no_raise_runtime_error_for_caps(tree)
        assert violations == []


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
        tree = ast.parse(BAD_GUARDIAN_RAISES_RUNTIME_ERROR)
        violations = _check_no_raise_exception_for_caps(tree)
        assert len(violations) > 0
        assert violations[0][1] == "RuntimeError"

    def test_no_false_positive_on_correct_guardian(self):
        tree = ast.parse(GOOD_GUARDIAN_SOURCE)
        violations = _check_no_raise_exception_for_caps(tree)
        assert violations == []

    def test_no_false_positive_on_non_scanning_guardian(self):
        tree = ast.parse(NON_SCANNING_GUARDIAN_SOURCE)
        violations = _check_no_raise_exception_for_caps(tree)
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
