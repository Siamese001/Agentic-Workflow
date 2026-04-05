import pytest

# Check if hollow_file_detector is available
try:
    from agentic_core.L5_safety.validators.base_detector_validator import (
        AntiPatternCategory,
        EnforcementLevel,
    )
    from agentic_core.L5_safety.validators.hollow_file_detector_validator import (
        HollowFileClassification,
        HollowFileDetector,
    )
    HOLLOW_FILE_AVAILABLE = True
except ImportError:
    HOLLOW_FILE_AVAILABLE = False


"""
Test suite for HollowFileDetector

Verifies that hollow files are properly detected and classified.
"""

import ast
import tempfile
from pathlib import Path


@pytest.mark.skipif(not HOLLOW_FILE_AVAILABLE, reason="hollow_file_detector not available")
def test_hollow_file_detector_empty():
    """Test detection of completely empty files."""
    detector = HollowFileDetector()

    # Create empty file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("")
        temp_path = Path(f.name)

    try:
        tree = ast.parse(temp_path.read_text())
        violations = detector.detect(temp_path, tree)

        assert len(violations) == 1
        assert violations[0].category == AntiPatternCategory.HOLLOW_FILE
        assert violations[0].severity == "error"
        assert violations[0].metadata["classification"] == "hollow"
    finally:
        temp_path.unlink()


@pytest.mark.skipif(not HOLLOW_FILE_AVAILABLE, reason="hollow_file_detector not available")
def test_hollow_file_detector_imports_only():
    """Test detection of files with only imports."""
    detector = HollowFileDetector()

    code = """
import os
import sys
from typing import Any
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = Path(f.name)

    try:
        tree = ast.parse(temp_path.read_text())
        violations = detector.detect(temp_path, tree)

        assert len(violations) == 1
        assert violations[0].category == AntiPatternCategory.HOLLOW_FILE
        assert violations[0].metadata["classification"] == "hollow"
    finally:
        temp_path.unlink()


@pytest.mark.skipif(not HOLLOW_FILE_AVAILABLE, reason="hollow_file_detector not available")
def test_hollow_file_detector_boilerplate_heavy():
    """Test detection of boilerplate-heavy files."""
    detector = HollowFileDetector()

    code = """
import os
import sys

_emit_records_execution_trace("p0", "test", "test")
_emit_applies_guardrail("p0", "test", "test")
_emit_reads_policy_state("p0", "test", "test")
_emit_snapshots_state("p0", "test", "test")
emit_replay_key("p0", "test")
emit_determinism_digest("p0", "test")
_emit_signs_execution_trace("p0", "hash", "trace", 0)
_emit_authorize_and_execute("p2", "test", "auth")
_emit_validates_capability("p2", "test", "cap")
_emit_routes_to_capability("p2", "test", "route")
_emit_writes_via_uwg("p2", "test", "uwg")
_emit_blocks_direct_write("p2", "test", "block")
_emit_records_tool_invocation("p2", "test", "tool")
_emit_captures_execution_output("p2", "test", "output")
_emit_dispatches_agent("p3", "test", "agent")
_emit_coordinates_agents("p3", "test", "coord")
_emit_records_workflow_lineage("p3", "test", "lineage")
_emit_records_healing_outcome("p3", "test", "healing")
_emit_escalates_failure("p3", "test", "escalate")
_emit_orchestrates_workflow("p3", "test", "orchestrate")
_emit_observes_runtime_state("p3", "test", "runtime")
_emit_verifies_boundary("p3", "test", "boundary")
_emit_transcripts_response("p3", "test", "transcript")
_emit_hard_fails_untranscripted("p3", "test")
_emit_gated_by_confidence("p3", "test", "confidence")
_emit_escalates_to_human("p3", "test")
_emit_reads_policy_state("p3", "test", "policy")
_emit_records_execution_trace("p3", "test", "trace")
_emit_snapshots_state("p3", "test", "state")
_emit_stores_embedding("p4", "test", "embed")
_emit_updates_meta_learning_state("p4", "test", "meta")
_emit_links_execution_to_snapshot("p4", "test", "link")
_emit_captures_evaluation_metric("p4", "test", "metric")
_emit_records_telemetry_event("p4", "test", "telemetry")
_emit_emits_metric_event("test", "p4obs", "metric")
_emit_records_incident_event("test", "p4obs", "incident")
_emit_captures_runtime_anomaly("test", "p4obs", "anomaly")
_emit_writes_observability_log("test", "p4obs", "log")
_emit_updates_monitoring_state("test", "p4obs", "state")
_emit_triggers_alert("test", "p4obs", "alert")
_emit_links_incident_trace("test", "p4obs", "trace")
_emit_captures_pattern("test", "p3lm", "pattern")
_emit_records_learning_event("test", "p3lm", "learning")
_emit_writes_learning_snapshot("test", "p3lm", "snapshot")
_emit_feeds_meta_learning("test", "p3lm", "meta")
_emit_updates_routing_strategy("test", "p3lm", "routing")
_emit_improves_agent_policy("test", "p3lm", "policy")
_emit_stores_learning_state("test", "p3lm", "state")
_emit_records_execution_trace("test", "L0_ROUTING", "trace")
_emit_records_execution_trace("test", "L1_REASONING", "trace")
_emit_records_execution_trace("test", "L2_EXECUTION", "trace")
_emit_records_execution_trace("test", "L3_ORCHESTRATION", "trace")
_emit_records_execution_trace("test", "L4_STATE", "trace")
_emit_reads_environ("test", "env_read", "env")
_emit_reads_environ("test", "env_read", "env")
_emit_reads_runtime_state("test", "runtime_state", "rt")
_emit_reads_runtime_state("test", "runtime_state", "rt")
_emit_pulls_context("p1", "test", "context")
_emit_pulls_context("p1", "test", "context")
_emit_execution_terminates_at_uwg("p1", "test", "uwg")
_emit_execution_terminates_at_uwg("p1", "test", "uwg")
_emit_writes_through("p1", "test", "write")
_emit_writes_through("p1", "test", "write")
_emit_validated_by_safety_plane("p1", "test", "safety")
_emit_invokes_eval("p1", "test", "eval")
_emit_proposal_commits_routing("p1", "test", "routing")
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = Path(f.name)

    try:
        tree = ast.parse(temp_path.read_text())
        violations = detector.detect(temp_path, tree)

        assert len(violations) == 1
        assert violations[0].category == AntiPatternCategory.HOLLOW_FILE
        assert violations[0].metadata["classification"] == "boilerplate_heavy"
        assert violations[0].severity == "warning"
        assert violations[0].metadata["boilerplate_ratio"] > 0.7
    finally:
        temp_path.unlink()


@pytest.mark.skipif(not HOLLOW_FILE_AVAILABLE, reason="hollow_file_detector not available")
def test_hollow_file_detector_scaffolding():
    """Test detection of scaffolding files."""
    detector = HollowFileDetector()

    code = """
class MyScaffold:
    pass

class AnotherScaffold:
    def method(self):
        pass

class StubImplementation:
    def method(self):
        ...

class NotImplementedClass:
    def method(self):
        raise NotImplementedError("Not implemented")
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = Path(f.name)

    try:
        tree = ast.parse(temp_path.read_text())
        violations = detector.detect(temp_path, tree)

        assert len(violations) == 1
        assert violations[0].category == AntiPatternCategory.HOLLOW_FILE
        assert violations[0].severity == "warning"
        # Should be classified as scaffolding due to classes with no behavioral methods
    finally:
        temp_path.unlink()


@pytest.mark.skipif(not HOLLOW_FILE_AVAILABLE, reason="hollow_file_detector not available")
def test_hollow_file_detector_healthy():
    """Test that healthy files are not flagged."""
    detector = HollowFileDetector()

    code = """
import os

def calculate_sum(a, b):
    return a + b

class Calculator:
    def __init__(self):
        self.value = 0

    def add(self, x):
        self.value += x
        return self.value

    def clear(self):
        self.value = 0

def main():
    calc = Calculator()
    result = calc.add(10)
    print(f"Result: {result}")
    return result
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = Path(f.name)

    try:
        tree = ast.parse(temp_path.read_text())
        violations = detector.detect(temp_path, tree)

        # Should have no violations for healthy file
        assert len(violations) == 0
    finally:
        temp_path.unlink()


@pytest.mark.skipif(not HOLLOW_FILE_AVAILABLE, reason="hollow_file_detector not available")
def test_hollow_file_detector_emit_functions():
    """Test that _emit_* functions are counted as boilerplate."""
    detector = HollowFileDetector()

    code = """
def _emit_test():
    pass

def behavioral_function():
    x = 1 + 1
    return x

class TestClass:
    def _emit_method(self):
        pass

    def behavioral_method(self):
        self.value = 42
        return self.value
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = Path(f.name)

    try:
        tree = ast.parse(temp_path.read_text())
        violations = detector.detect(temp_path, tree)

        # Should have no violations - has behavioral content
        assert len(violations) == 0
    finally:
        temp_path.unlink()


if __name__ == "__main__":
    test_hollow_file_detector_empty()
    test_hollow_file_detector_imports_only()
    test_hollow_file_detector_boilerplate_heavy()
    test_hollow_file_detector_scaffolding()
    test_hollow_file_detector_healthy()
    test_hollow_file_detector_emit_functions()
    print("✅ All hollow file detector tests passed")
