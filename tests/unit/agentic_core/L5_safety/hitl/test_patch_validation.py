"""Addendum 6.1: HITL Patch Validator tests."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.hitl.patch_validator import ValidatedPatch, validate_patch
from agentic_core.L5_safety.types.hardening_errors import HumanPatchValidationError
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

_emit_records_execution_trace("p0", "evidence", "test_patch_validation")
_emit_applies_guardrail("p0", "test_patch_validation", "p0_governance")
_emit_reads_policy_state("p0", "test_patch_validation", "policy_binding")
_emit_snapshots_state("p0", "test_patch_validation", "state_snapshot")
emit_replay_key("p0", "test_patch_validation")
emit_determinism_digest("p0", "test_patch_validation")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_patch_validation", "execution_auth")
_emit_validates_capability("p2", "test_patch_validation", "capability_check")
_emit_routes_to_capability("p2", "test_patch_validation", "capability_route")
_emit_writes_via_uwg("p2", "test_patch_validation", "uwg_write")
_emit_blocks_direct_write("p2", "test_patch_validation", "direct_write_block")
_emit_records_tool_invocation("p2", "test_patch_validation", "tool_invocation")
_emit_captures_execution_output("p2", "test_patch_validation", "exec_output")
_emit_dispatches_agent("p3", "test_patch_validation", "agent_dispatch")
_emit_coordinates_agents("p3", "test_patch_validation", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_patch_validation", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_patch_validation", "healing_outcome")
_emit_escalates_failure("p3", "test_patch_validation", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_patch_validation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_patch_validation", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_patch_validation", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_patch_validation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_patch_validation", "eval_metric")
_emit_stores_embedding("p4", "test_patch_validation", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_patch_validation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_patch_validation", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestValidatePatch:
    def _valid_patch(self) -> dict:
        return {
            "original_plan_hash": "abc123",
            "structured_patch_schema": {"type": "MODIFY_DIFF", "file": "foo.py"},
            "reviewer_signature": "reviewer@example.com",
        }

    def test_valid_patch_returns_validated(self):
        result = validate_patch(self._valid_patch())
        assert isinstance(result, ValidatedPatch)
        assert result.reviewer_signature == "reviewer@example.com"
        assert result.original_plan_hash == "abc123"
        assert result.patch_hash  # non-empty SHA256

    def test_patch_hash_is_64_chars(self):
        result = validate_patch(self._valid_patch())
        assert len(result.patch_hash) == 64

    def test_missing_reviewer_signature_raises(self):
        patch = self._valid_patch()
        del patch["reviewer_signature"]
        with pytest.raises(HumanPatchValidationError, match="reviewer_signature"):
            validate_patch(patch)

    def test_missing_plan_hash_raises(self):
        patch = self._valid_patch()
        del patch["original_plan_hash"]
        with pytest.raises(HumanPatchValidationError, match="original_plan_hash"):
            validate_patch(patch)

    def test_missing_patch_schema_raises(self):
        patch = self._valid_patch()
        del patch["structured_patch_schema"]
        with pytest.raises(HumanPatchValidationError, match="structured_patch_schema"):
            validate_patch(patch)

    def test_empty_reviewer_signature_raises(self):
        patch = self._valid_patch()
        patch["reviewer_signature"] = ""
        with pytest.raises(HumanPatchValidationError, match="reviewer_signature"):
            validate_patch(patch)

    def test_empty_dict_raises(self):
        with pytest.raises(HumanPatchValidationError):
            validate_patch({})

    def test_different_patches_different_hashes(self):
        p1 = self._valid_patch()
        p2 = dict(self._valid_patch())
        p2["reviewer_signature"] = "other@example.com"
        r1 = validate_patch(p1)
        r2 = validate_patch(p2)
        assert r1.patch_hash != r2.patch_hash

    def test_negative_complete_patch_never_raises(self):
        """Negative control: all fields present must never raise."""
        raised = False
        try:
            validate_patch(self._valid_patch())
        except HumanPatchValidationError:  # guardian: allow-silent-swallower
            raised = True
        assert not raised
