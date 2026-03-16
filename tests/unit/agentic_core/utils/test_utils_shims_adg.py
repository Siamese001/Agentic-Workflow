"""ADG-driven tests for utility shims — fan_in=2 batch.

Covers: detection_protocol_util, project_root_util, meta_learning_storage_util.
"""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_utils_shims_adg")
_emit_applies_guardrail("p0", "test_utils_shims_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_utils_shims_adg", "policy_binding")
_emit_snapshots_state("p0", "test_utils_shims_adg", "state_snapshot")
emit_replay_key("p0", "test_utils_shims_adg")
emit_determinism_digest("p0", "test_utils_shims_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_utils_shims_adg", "execution_auth")
_emit_validates_capability("p2", "test_utils_shims_adg", "capability_check")
_emit_routes_to_capability("p2", "test_utils_shims_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_utils_shims_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_utils_shims_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_utils_shims_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_utils_shims_adg", "exec_output")
_emit_dispatches_agent("p3", "test_utils_shims_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_utils_shims_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_utils_shims_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_utils_shims_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_utils_shims_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_utils_shims_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_utils_shims_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_utils_shims_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_utils_shims_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_utils_shims_adg", "eval_metric")
_emit_stores_embedding("p4", "test_utils_shims_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_utils_shims_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_utils_shims_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# detection_protocol_util
# ---------------------------------------------------------------------------
from agentic_core.utils.detection_protocol_util import (
    DetectionRequest,
    DetectionResult,
    DetectionSignalProtocol,
    Severity,
    __all__,
)


class TestDetectionProtocolShim:
    def test_all_list_complete(self):
        for name in ("DetectionRequest", "DetectionResult", "Severity"):
            assert name in __all__

    def test_detection_request_importable(self):
        assert callable(DetectionRequest)

    def test_detection_result_importable(self):
        assert callable(DetectionResult)

    def test_severity_importable(self):
        assert callable(Severity)

    def test_identity_matches_canonical(self):
        from agentic_core.runtime.config.detection_config import DetectionRequest as canon
        assert DetectionRequest is canon


class TestDetectionSignalProtocol:
    def test_importable(self):
        assert callable(DetectionSignalProtocol)

    def test_detect_method_raises_not_implemented(self):
        protocol = DetectionSignalProtocol()
        req = DetectionRequest(file_path="dummy.py", detection_type="test")
        with pytest.raises(NotImplementedError):
            protocol.detect(req)

    def test_is_protocol_class(self):
        assert hasattr(DetectionSignalProtocol, "detect")


# ---------------------------------------------------------------------------
# project_root_util
# ---------------------------------------------------------------------------
from agentic_core.utils.project_root_util import get_project_root, get_project_root_safe


class TestGetProjectRoot:
    def test_returns_path_from_repo(self):
        root = get_project_root(Path(__file__))
        assert isinstance(root, Path)

    def test_root_contains_git(self):
        root = get_project_root(Path(__file__))
        assert (root / ".git").exists()

    def test_root_contains_agentic_core(self):
        root = get_project_root(Path(__file__))
        assert (root / "agentic_core").exists()

    def test_raises_runtime_error_for_no_git(self):
        with pytest.raises(RuntimeError):
            get_project_root(Path("/nonexistent_xyz_abc/foo"))


class TestGetProjectRootSafe:
    def test_returns_path_from_repo(self):
        root = get_project_root_safe(Path(__file__))
        assert isinstance(root, Path)

    def test_safe_version_does_not_raise_for_repo_path(self):
        root = get_project_root_safe(Path(__file__))
        assert isinstance(root, Path)


# ---------------------------------------------------------------------------
# meta_learning_storage_util
# ---------------------------------------------------------------------------
from agentic_core.utils.meta_learning_storage_util import MetaLearningStorage


class TestMetaLearningStorage:
    def test_importable(self):
        assert callable(MetaLearningStorage)

    def test_lobotomized_starts_false(self):
        assert MetaLearningStorage._lobotomized is False

    def test_memory_starts_none(self):
        assert MetaLearningStorage._memory is None

    def test_graph_bridge_starts_none(self):
        assert MetaLearningStorage._graph_bridge is None

    def test_ensure_memory_connection_method_exists(self):
        assert callable(MetaLearningStorage.ensure_memory_connection)

    def test_ensure_memory_connection_when_lobotomized(self):
        original = MetaLearningStorage._lobotomized
        try:
            MetaLearningStorage._lobotomized = True
            MetaLearningStorage.ensure_memory_connection("test_agent")
        finally:
            MetaLearningStorage._lobotomized = original
