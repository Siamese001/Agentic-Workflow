"""ADG-driven tests for agentic_core/interfaces/determinism_types.py — fan_in=11.

Re-export shim contract tests: all __all__ symbols must be importable from
the interfaces path, have correct types, and match canonical values.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestDeterminismTypesReExports:
    """All __all__ members must be importable from the shim path."""

    def test_all_exports_present(self):
        import agentic_core.interfaces.determinism_types as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"

    def test_fix_constraint_importable(self):
        from agentic_core.interfaces.determinism_types import FixConstraint
        assert FixConstraint is not None

    def test_surgical_manifest_importable(self):
        from agentic_core.interfaces.determinism_types import SurgicalManifest
        assert callable(SurgicalManifest)

    def test_semantic_clock_importable(self):
        from agentic_core.interfaces.determinism_types import SemanticClock
        assert callable(SemanticClock)

    def test_semantic_clock_snapshot_importable(self):
        from agentic_core.interfaces.determinism_types import SemanticClockSnapshot
        assert callable(SemanticClockSnapshot)

    def test_validate_semantic_clock_callable(self):
        from agentic_core.interfaces.determinism_types import validate_semantic_clock
        assert callable(validate_semantic_clock)

    def test_forbidden_input_patterns_is_sequence(self):
        from agentic_core.interfaces.determinism_types import FORBIDDEN_INPUT_PATTERNS
        assert hasattr(FORBIDDEN_INPUT_PATTERNS, '__iter__')

    def test_wall_clock_forbidden_callables_is_sequence(self):
        from agentic_core.interfaces.determinism_types import WALL_CLOCK_FORBIDDEN_CALLABLES
        assert hasattr(WALL_CLOCK_FORBIDDEN_CALLABLES, '__iter__')

    def test_memory_confidence_threshold_is_numeric(self):
        from agentic_core.interfaces.determinism_types import MEMORY_CONFIDENCE_THRESHOLD
        assert isinstance(MEMORY_CONFIDENCE_THRESHOLD, (int, float))
        assert 0.0 <= MEMORY_CONFIDENCE_THRESHOLD <= 1.0

    def test_trace_buffer_velocity_threshold_is_numeric(self):
        from agentic_core.interfaces.determinism_types import TRACE_BUFFER_VELOCITY_THRESHOLD
        assert isinstance(TRACE_BUFFER_VELOCITY_THRESHOLD, (int, float))

    def test_trajectory_reuse_constraint_importable(self):
        from agentic_core.interfaces.determinism_types import TrajectoryReuseConstraint
        assert TrajectoryReuseConstraint is not None

    def test_state_commit_invalid_is_exception(self):
        from agentic_core.interfaces.determinism_types import StateCommitInvalid
        assert issubclass(StateCommitInvalid, Exception)

    def test_memory_hypostate_importable(self):
        from agentic_core.interfaces.determinism_types import MemoryHypostate
        assert MemoryHypostate is not None

    def test_episodic_memory_query_result_importable(self):
        from agentic_core.interfaces.determinism_types import EpisodicMemoryQueryResult
        assert EpisodicMemoryQueryResult is not None

    def test_episodic_semantic_link_importable(self):
        from agentic_core.interfaces.determinism_types import EpisodicSemanticLink
        assert EpisodicSemanticLink is not None

    def test_knowledge_supervisor_result_importable(self):
        from agentic_core.interfaces.determinism_types import KnowledgeSupervisorResult
        assert KnowledgeSupervisorResult is not None

    def test_canonical_ast_result_importable(self):
        from agentic_core.interfaces.determinism_types import CanonicalASTResult
        assert CanonicalASTResult is not None

    def test_forensic_trace_buffer_importable(self):
        from agentic_core.interfaces.determinism_types import ForensicTraceBuffer
        assert ForensicTraceBuffer is not None

    def test_boundary_snapshot_artifact_importable(self):
        from agentic_core.interfaces.determinism_types import BoundarySnapshotArtifact
        assert BoundarySnapshotArtifact is not None


class TestDeterminismTypesShimIdentity:
    """Shim re-exports must be identical to canonical source."""

    def test_fix_constraint_same_object(self):
        from agentic_core.interfaces.determinism_types import FixConstraint as shim
        from agentic_core.L0_routing.types.determinism_types import FixConstraint as canon
        assert shim is canon

    def test_surgical_manifest_same_object(self):
        from agentic_core.interfaces.determinism_types import SurgicalManifest as shim
        from agentic_core.L0_routing.types.determinism_types import SurgicalManifest as canon
        assert shim is canon

    def test_validate_semantic_clock_same_object(self):
        from agentic_core.interfaces.determinism_types import validate_semantic_clock as shim
        from agentic_core.L0_routing.types.determinism_types import validate_semantic_clock as canon
        assert shim is canon
