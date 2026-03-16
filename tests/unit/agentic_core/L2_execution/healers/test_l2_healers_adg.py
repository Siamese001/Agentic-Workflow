"""ADG-driven tests for L2 execution healers — fan_in=1.

Covers: architecture_governor_healer, file_classification_healer,
        filesystem_ssot_healer, gravity_leak_healer.
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

_emit_records_execution_trace("p0", "evidence", "test_l2_healers_adg")
_emit_applies_guardrail("p0", "test_l2_healers_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_l2_healers_adg", "policy_binding")
_emit_snapshots_state("p0", "test_l2_healers_adg", "state_snapshot")
emit_replay_key("p0", "test_l2_healers_adg")
emit_determinism_digest("p0", "test_l2_healers_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_l2_healers_adg", "execution_auth")
_emit_validates_capability("p2", "test_l2_healers_adg", "capability_check")
_emit_routes_to_capability("p2", "test_l2_healers_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_l2_healers_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_l2_healers_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_l2_healers_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_l2_healers_adg", "exec_output")
_emit_dispatches_agent("p3", "test_l2_healers_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_l2_healers_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_l2_healers_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_l2_healers_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_l2_healers_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_l2_healers_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_l2_healers_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_l2_healers_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_l2_healers_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_l2_healers_adg", "eval_metric")
_emit_stores_embedding("p4", "test_l2_healers_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_l2_healers_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_l2_healers_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# architecture_governor_healer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.healers.architecture_governor_healer import (
    CHECK_ID as ARCH_CHECK_ID,
)
from agentic_core.L2_execution.healers.architecture_governor_healer import (
    heal_architecture_governance,
)
from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus


class TestArchitectureGovernorHealer:
    def test_check_id_string(self):
        assert isinstance(ARCH_CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_architecture_governance)

    def test_no_violations_returns_healed(self):
        result = heal_architecture_governance(
            {"violations_count": 0}, apply=False
        )
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_violations_returns_result(self):
        result = heal_architecture_governance(
            {"violations_count": 3, "territory": "agentic_core"},
            apply=False,
        )
        assert isinstance(result, HealCheckResult)
        assert result.status != HealStatus.HEALED

    def test_check_id_matches(self):
        result = heal_architecture_governance({"violations_count": 0})
        assert result.check_id == ARCH_CHECK_ID


# ---------------------------------------------------------------------------
# file_classification_healer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.healers.file_classification_healer import (
    CHECK_ID as FILE_CLASS_CHECK_ID,
)
from agentic_core.L2_execution.healers.file_classification_healer import (
    heal_file_classification,
)


class TestFileClassificationHealer:
    def test_check_id_string(self):
        assert isinstance(FILE_CLASS_CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_file_classification)

    def test_no_violations_returns_healed(self):
        result = heal_file_classification(
            {"violations_count": 0}, apply=False
        )
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_violations_returns_result(self):
        result = heal_file_classification(
            {"violations_count": 2, "territory": "agentic_core"},
            apply=False,
        )
        assert isinstance(result, HealCheckResult)

    def test_check_id_matches(self):
        result = heal_file_classification({"violations_count": 0})
        assert result.check_id == FILE_CLASS_CHECK_ID


# ---------------------------------------------------------------------------
# filesystem_ssot_healer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.healers.filesystem_ssot_healer import (
    CHECK_ID as FS_CHECK_ID,
)
from agentic_core.L2_execution.healers.filesystem_ssot_healer import (
    heal_filesystem_ssot_drift,
)


class TestFilesystemSSOTHealer:
    def test_check_id_string(self):
        assert isinstance(FS_CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_filesystem_ssot_drift)

    def test_no_evidence_returns_healed(self):
        result = heal_filesystem_ssot_drift({"evidence": {}}, apply=False)
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_forbidden_folders(self):
        result = heal_filesystem_ssot_drift(
            {"evidence": {"forbidden_folders": ["bad_folder"]}},
            apply=False,
        )
        assert isinstance(result, HealCheckResult)

    def test_check_id_matches(self):
        result = heal_filesystem_ssot_drift({"evidence": {}})
        assert result.check_id == FS_CHECK_ID


# ---------------------------------------------------------------------------
# gravity_leak_healer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.healers.gravity_leak_healer import (
    CHECK_ID as GRAVITY_CHECK_ID,
)
from agentic_core.L2_execution.healers.gravity_leak_healer import (
    heal_gravity_violations,
)


class TestGravityLeakHealer:
    def test_check_id_string(self):
        assert isinstance(GRAVITY_CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_gravity_violations)

    def test_no_violations_returns_healed(self):
        result = heal_gravity_violations(
            {"violations_count": 0, "evidence": {}}, apply=False
        )
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_violations_returns_result(self):
        result = heal_gravity_violations(
            {
                "violations_count": 1,
                "evidence": {"violations": [{"file": "foo.py", "import": "L5.bar"}]},
            },
            apply=False,
        )
        assert isinstance(result, HealCheckResult)

    def test_check_id_matches(self):
        result = heal_gravity_violations({"violations_count": 0, "evidence": {}})
        assert result.check_id == GRAVITY_CHECK_ID
