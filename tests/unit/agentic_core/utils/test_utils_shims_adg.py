"""ADG-driven tests for utility shims — fan_in=2 batch.

Covers: detection_protocol_util, project_root_util, meta_learning_storage_util.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
