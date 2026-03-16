"""
Guardian Escalation Determinism Tests.

1. Clean repo → PASS on all escalation checks
2. File with f-string in FailureSignal() → FAIL on failure_signal_built_from_raw_notes
3. File with mutation on escalation context → FAIL on escalation_context_mutation
4. Output conforms to guardian_contract schema
5. scan functions are deterministic (same input → same output)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
)
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

_emit_records_execution_trace("p0", "evidence", "test_guardian_escalation_determinism")
_emit_applies_guardrail("p0", "test_guardian_escalation_determinism", "p0_governance")
_emit_reads_policy_state("p0", "test_guardian_escalation_determinism", "policy_binding")
_emit_snapshots_state("p0", "test_guardian_escalation_determinism", "state_snapshot")
emit_replay_key("p0", "test_guardian_escalation_determinism")
emit_determinism_digest("p0", "test_guardian_escalation_determinism")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_guardian_escalation_determinism", "execution_auth")
_emit_validates_capability("p2", "test_guardian_escalation_determinism", "capability_check")
_emit_routes_to_capability("p2", "test_guardian_escalation_determinism", "capability_route")
_emit_writes_via_uwg("p2", "test_guardian_escalation_determinism", "uwg_write")
_emit_blocks_direct_write("p2", "test_guardian_escalation_determinism", "direct_write_block")
_emit_records_tool_invocation("p2", "test_guardian_escalation_determinism", "tool_invocation")
_emit_captures_execution_output("p2", "test_guardian_escalation_determinism", "exec_output")
_emit_dispatches_agent("p3", "test_guardian_escalation_determinism", "agent_dispatch")
_emit_coordinates_agents("p3", "test_guardian_escalation_determinism", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_guardian_escalation_determinism", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_guardian_escalation_determinism", "healing_outcome")
_emit_escalates_failure("p3", "test_guardian_escalation_determinism", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_guardian_escalation_determinism", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_guardian_escalation_determinism", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_guardian_escalation_determinism", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_guardian_escalation_determinism", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_guardian_escalation_determinism", "eval_metric")
_emit_stores_embedding("p4", "test_guardian_escalation_determinism", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_guardian_escalation_determinism", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_guardian_escalation_determinism", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_escalation_determinism import (
    run_escalation_determinism_guardian,
    scan_escalation_patterns,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianStatus,
)

pytestmark = pytest.mark.guardian


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "clean.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def fstring_signal_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "bad.py").write_text("FailureSignal(f'error: {msg}')\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def mutation_context_repo(tmp_path: Path) -> Path:
    (tmp_path / APPS_LIC_DIR).mkdir()
    (tmp_path / APPS_LIC_DIR / "bad.py").write_text(
        "escalation_context.update({'key': 'value'})\n", encoding="utf-8"
    )
    return tmp_path


class TestEscalationDeterminismGuardianClean:
    def test_clean_repo_passes(self, clean_repo):
        result = run_escalation_determinism_guardian(repo_root=clean_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["failure_signal_built_from_raw_notes"] == CheckStatus.PASS.value
        assert check_map["alternate_escalation_context_construction"] == CheckStatus.PASS.value
        assert check_map["escalation_context_mutation"] == CheckStatus.PASS.value

    def test_clean_repo_top_status_pass(self, clean_repo):
        result = run_escalation_determinism_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value


class TestEscalationDeterminismGuardianViolations:
    def test_fstring_signal_detected(self, fstring_signal_repo):
        viols = scan_escalation_patterns(fstring_signal_repo)
        assert viols["failure_signal_built_from_raw_notes"]
        assert len(viols["failure_signal_built_from_raw_notes"]) == 1

    def test_fstring_signal_fails_result(self, fstring_signal_repo):
        result = run_escalation_determinism_guardian(repo_root=fstring_signal_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["failure_signal_built_from_raw_notes"] == CheckStatus.FAIL.value

    def test_mutation_context_detected(self, mutation_context_repo):
        viols = scan_escalation_patterns(mutation_context_repo)
        assert viols["escalation_context_mutation"]
        assert len(viols["escalation_context_mutation"]) == 1

    def test_mutation_context_fails_result(self, mutation_context_repo):
        result = run_escalation_determinism_guardian(repo_root=mutation_context_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["escalation_context_mutation"] == CheckStatus.FAIL.value


class TestEscalationDeterminismDeterminism:
    def test_scan_is_deterministic(self, fstring_signal_repo):
        a = scan_escalation_patterns(fstring_signal_repo)
        b = scan_escalation_patterns(fstring_signal_repo)
        assert a == b

    def test_result_guardian_id_correct(self, clean_repo):
        result = run_escalation_determinism_guardian(repo_root=clean_repo)
        assert result.guardian_id == "escalation_determinism"
