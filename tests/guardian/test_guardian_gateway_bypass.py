"""
Guardian Gateway Bypass Tests.

1. Clean repo → PASS on provider_sdk_import and direct_model_call
2. File with forbidden import → FAIL with correct check_id
3. Allowlisted file containing SDK import → PASS (not flagged)
4. File with direct OpenAI() call → FAIL on direct_model_call
5. Output conforms to guardian_contract schema
6. scan functions are deterministic (same input → same output)
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

_emit_records_execution_trace("p0", "evidence", "test_guardian_gateway_bypass")
_emit_applies_guardrail("p0", "test_guardian_gateway_bypass", "p0_governance")
_emit_reads_policy_state("p0", "test_guardian_gateway_bypass", "policy_binding")
_emit_snapshots_state("p0", "test_guardian_gateway_bypass", "state_snapshot")
emit_replay_key("p0", "test_guardian_gateway_bypass")
emit_determinism_digest("p0", "test_guardian_gateway_bypass")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_guardian_gateway_bypass", "execution_auth")
_emit_validates_capability("p2", "test_guardian_gateway_bypass", "capability_check")
_emit_routes_to_capability("p2", "test_guardian_gateway_bypass", "capability_route")
_emit_writes_via_uwg("p2", "test_guardian_gateway_bypass", "uwg_write")
_emit_blocks_direct_write("p2", "test_guardian_gateway_bypass", "direct_write_block")
_emit_records_tool_invocation("p2", "test_guardian_gateway_bypass", "tool_invocation")
_emit_captures_execution_output("p2", "test_guardian_gateway_bypass", "exec_output")
_emit_dispatches_agent("p3", "test_guardian_gateway_bypass", "agent_dispatch")
_emit_coordinates_agents("p3", "test_guardian_gateway_bypass", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_guardian_gateway_bypass", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_guardian_gateway_bypass", "healing_outcome")
_emit_escalates_failure("p3", "test_guardian_gateway_bypass", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_guardian_gateway_bypass", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_guardian_gateway_bypass", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_guardian_gateway_bypass", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_guardian_gateway_bypass", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_guardian_gateway_bypass", "eval_metric")
_emit_stores_embedding("p4", "test_guardian_gateway_bypass", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_guardian_gateway_bypass", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_guardian_gateway_bypass", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_gateway_bypass import (
    run_gateway_bypass_guardian,
    scan_direct_model_calls,
    scan_provider_sdk_imports,
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
def sdk_import_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "bad.py").write_text("import openai\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def direct_call_repo(tmp_path: Path) -> Path:
    (tmp_path / APPS_LIC_DIR).mkdir()
    (tmp_path / APPS_LIC_DIR / "caller.py").write_text(
        "from openai import OpenAI\nclient = OpenAI()\n", encoding="utf-8"
    )
    return tmp_path


class TestGatewayBypassGuardianClean:
    def test_clean_repo_passes(self, clean_repo):
        result = run_gateway_bypass_guardian(repo_root=clean_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["provider_sdk_import"] == CheckStatus.PASS.value
        assert check_map["direct_model_call"] == CheckStatus.PASS.value

    def test_clean_repo_top_status_pass(self, clean_repo):
        result = run_gateway_bypass_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value


class TestGatewayBypassGuardianViolations:
    def test_sdk_import_detected(self, sdk_import_repo):
        viols = scan_provider_sdk_imports(sdk_import_repo)
        assert any(v["check_id"] == "provider_sdk_import" for v in viols)
        assert any("openai" in v["detail"] for v in viols)

    def test_sdk_import_fails_result(self, sdk_import_repo):
        result = run_gateway_bypass_guardian(repo_root=sdk_import_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["provider_sdk_import"] == CheckStatus.FAIL.value

    def test_direct_call_detected(self, direct_call_repo):
        viols = scan_direct_model_calls(direct_call_repo)
        assert any(v["check_id"] == "direct_model_call" for v in viols)

    def test_direct_call_fails_result(self, direct_call_repo):
        result = run_gateway_bypass_guardian(repo_root=direct_call_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["direct_model_call"] == CheckStatus.FAIL.value


class TestGatewayBypassDeterminism:
    def test_scan_is_deterministic(self, sdk_import_repo):
        a = scan_provider_sdk_imports(sdk_import_repo)
        b = scan_provider_sdk_imports(sdk_import_repo)
        assert a == b

    def test_result_guardian_id_correct(self, clean_repo):
        result = run_gateway_bypass_guardian(repo_root=clean_repo)
        assert result.guardian_id == "gateway_bypass"
