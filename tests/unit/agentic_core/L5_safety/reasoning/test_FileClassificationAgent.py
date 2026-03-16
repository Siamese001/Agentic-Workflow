#!/usr/bin/env python3
"""
Test suite for FileClassificationAgent.
"""

import textwrap
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

_emit_records_execution_trace("p0", "evidence", "test_FileClassificationAgent")
_emit_applies_guardrail("p0", "test_FileClassificationAgent", "p0_governance")
_emit_reads_policy_state("p0", "test_FileClassificationAgent", "policy_binding")
_emit_snapshots_state("p0", "test_FileClassificationAgent", "state_snapshot")
emit_replay_key("p0", "test_FileClassificationAgent")
emit_determinism_digest("p0", "test_FileClassificationAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_FileClassificationAgent", "execution_auth")
_emit_validates_capability("p2", "test_FileClassificationAgent", "capability_check")
_emit_routes_to_capability("p2", "test_FileClassificationAgent", "capability_route")
_emit_writes_via_uwg("p2", "test_FileClassificationAgent", "uwg_write")
_emit_blocks_direct_write("p2", "test_FileClassificationAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "test_FileClassificationAgent", "tool_invocation")
_emit_captures_execution_output("p2", "test_FileClassificationAgent", "exec_output")
_emit_dispatches_agent("p3", "test_FileClassificationAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "test_FileClassificationAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_FileClassificationAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_FileClassificationAgent", "healing_outcome")
_emit_escalates_failure("p3", "test_FileClassificationAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_FileClassificationAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_FileClassificationAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_FileClassificationAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_FileClassificationAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_FileClassificationAgent", "eval_metric")
_emit_stores_embedding("p4", "test_FileClassificationAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_FileClassificationAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_FileClassificationAgent", "exec_snapshot_link")


def test_fileclassificationagent_basic_functionality():
    """Test basic functionality of FileClassificationAgent."""
    # TODO: Implement actual test based on module functionality
    pytest.skip("TODO: Implement actual test based on module functionality")


def test_fileclassificationagent_edge_cases():
    """Test edge cases for FileClassificationAgent."""
    # TODO: Test edge cases and boundary conditions
    pytest.skip("TODO: Implement actual test based on module functionality")


def test_fileclassificationagent_error_scenarios():
    """Test error scenarios for FileClassificationAgent."""
    # TODO: Test error handling and failure modes
    pytest.skip("TODO: Implement actual test based on module functionality")


# ---------------------------------------------------------------------------
# Semantic duplicate detection tests (RCA: IBlackboardLeaseVerifier duplication)
# ---------------------------------------------------------------------------


@pytest.fixture
def fca_instance(tmp_path):
    """Create a minimal FileClassificationAgent scoped to tmp_path."""
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
        FileClassificationAgent,
    )

    return FileClassificationAgent(
        project_root=tmp_path,
        dry_run=True,
        validate_only=True,
    )


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


class TestSemanticDuplicateDetection:
    """Tests for _detect_semantic_duplicates — the fix for the
    IBlackboardLeaseVerifier / IBlackboardLeaseVerifierProtocol duplication."""

    def test_detects_pascal_vs_snake_same_class(self, fca_instance, tmp_path):
        """Two files in same dir with normalised-equivalent primary class → flagged."""
        d = tmp_path / "interfaces"
        f1 = _write(
            d / "IFooProtocol.py",
            """\
            from typing import Protocol
            class IFoo(Protocol):
                def bar(self) -> None: ...
            """,
        )
        f2 = _write(
            d / "IFoo.py",
            """\
            from typing import Protocol
            class foo(Protocol):
                def bar(self) -> None: ...
            """,
        )
        violations = fca_instance._detect_semantic_duplicates([f1, f2])
        assert len(violations) == 1
        assert violations[0]["type"] == "SEMANTIC_DUPLICATE"

    def test_no_false_positive_different_classes(self, fca_instance, tmp_path):
        """Two files in same dir with genuinely different primary classes → NOT flagged."""
        d = tmp_path / "interfaces"
        f1 = _write(
            d / "IAlpha.py",
            """\
            from typing import Protocol
            class IAlpha(Protocol):
                def run(self) -> None: ...
            """,
        )
        f2 = _write(
            d / "IBeta.py",
            """\
            from typing import Protocol
            class IBeta(Protocol):
                def run(self) -> None: ...
            """,
        )
        violations = fca_instance._detect_semantic_duplicates([f1, f2])
        assert len(violations) == 0

    def test_no_false_positive_different_directories(self, fca_instance, tmp_path):
        """Same class name in different directories → NOT flagged (cross-dir is
        handled by the existing exact-filename duplicate detector)."""
        d1 = tmp_path / "interfaces"
        d2 = tmp_path / "types"
        f1 = _write(
            d1 / "IFooProtocol.py",
            """\
            from typing import Protocol
            class IFoo(Protocol):
                def bar(self) -> None: ...
            """,
        )
        f2 = _write(
            d2 / "IFoo.py",
            """\
            from typing import Protocol
            class IFoo(Protocol):
                def bar(self) -> None: ...
            """,
        )
        violations = fca_instance._detect_semantic_duplicates([f1, f2])
        assert len(violations) == 0

    def test_canonical_prefers_more_importers(self, fca_instance, tmp_path):
        """The file referenced by more other files wins canonical status."""
        d = tmp_path / "interfaces"
        canonical = _write(
            d / "IBarProtocol.py",
            """\
            from typing import Protocol
            class IBar(Protocol):
                def baz(self) -> None: ...
            """,
        )
        duplicate = _write(
            d / "IBar.py",
            """\
            from typing import Protocol
            class bar(Protocol):
                def baz(self) -> None: ...
            """,
        )
        # A consumer that imports only the canonical
        consumer = _write(
            tmp_path / "consumer.py",
            """\
            from interfaces.IBarProtocol import IBar
            """,
        )
        violations = fca_instance._detect_semantic_duplicates([canonical, duplicate, consumer])
        assert len(violations) == 1
        v = violations[0]
        assert v["canonical_path"] == str(canonical)
        assert v["duplicate_path"] == str(duplicate)

    def test_blackboard_regression(self, tmp_path, fca_instance):
        """Regression: the exact scenario that created the original duplication."""
        d = tmp_path / "interfaces"
        protocol = _write(
            d / "IBlackboardLeaseVerifierProtocol.py",
            """\
            from typing import Protocol
            class IBlackboardLeaseVerifier(Protocol):
                def verify(self) -> bool: ...
            """,
        )
        bad_copy = _write(
            d / "IBlackboardLeaseVerifier.py",
            """\
            from typing import Protocol
            class blackboard_lease_verifier(Protocol):
                def verify(self) -> bool: ...
            """,
        )
        violations = fca_instance._detect_semantic_duplicates([protocol, bad_copy])
        assert len(violations) == 1
        assert violations[0]["type"] == "SEMANTIC_DUPLICATE"
        # The Protocol version should win (more importers or shorter name)

    def test_skips_test_files(self, fca_instance, tmp_path):
        """Test files (test_*.py) should be excluded from semantic duplicate detection."""
        d = tmp_path / "interfaces"
        f1 = _write(
            d / "IFoo.py",
            """\
            class IFoo:
                pass
            """,
        )
        f2 = _write(
            d / "test_IFoo.py",
            """\
            class IFoo:
                pass
            """,
        )
        violations = fca_instance._detect_semantic_duplicates([f1, f2])
        assert len(violations) == 0
