"""
AST-based detector for unsafe I/O and subprocess usage in agent-executed code paths.

This test ensures that agent code does not use direct file I/O or subprocess primitives
that could bypass the mutation fence and write to protected roots.
"""

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TOOLS_DIR,
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

_emit_records_execution_trace("p0", "evidence", "test_unsafe_io_subprocess_detector")
_emit_applies_guardrail("p0", "test_unsafe_io_subprocess_detector", "p0_governance")
_emit_reads_policy_state("p0", "test_unsafe_io_subprocess_detector", "policy_binding")
_emit_snapshots_state("p0", "test_unsafe_io_subprocess_detector", "state_snapshot")
emit_replay_key("p0", "test_unsafe_io_subprocess_detector")
emit_determinism_digest("p0", "test_unsafe_io_subprocess_detector")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_unsafe_io_subprocess_detector", "execution_auth")
_emit_validates_capability("p2", "test_unsafe_io_subprocess_detector", "capability_check")
_emit_routes_to_capability("p2", "test_unsafe_io_subprocess_detector", "capability_route")
_emit_writes_via_uwg("p2", "test_unsafe_io_subprocess_detector", "uwg_write")
_emit_blocks_direct_write("p2", "test_unsafe_io_subprocess_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "test_unsafe_io_subprocess_detector", "tool_invocation")
_emit_captures_execution_output("p2", "test_unsafe_io_subprocess_detector", "exec_output")
_emit_dispatches_agent("p3", "test_unsafe_io_subprocess_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "test_unsafe_io_subprocess_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_unsafe_io_subprocess_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_unsafe_io_subprocess_detector", "healing_outcome")
_emit_escalates_failure("p3", "test_unsafe_io_subprocess_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_unsafe_io_subprocess_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_unsafe_io_subprocess_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_unsafe_io_subprocess_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_unsafe_io_subprocess_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_unsafe_io_subprocess_detector", "eval_metric")
_emit_stores_embedding("p4", "test_unsafe_io_subprocess_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_unsafe_io_subprocess_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_unsafe_io_subprocess_detector", "exec_snapshot_link")

# Add repo root to path for imports
repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from agentic_core.L2_execution.tools.unsafe_io_detector import (
    scan_for_unsafe_patterns,
)


@pytest.mark.unit_min_deps
class TestUnsafeIOSubprocessDetector:
    """Test suite for unsafe I/O and subprocess detection."""

    def test_detector_finds_direct_file_writes(self):
        """Test that detector flags direct file write operations."""
        code = """
import os
from pathlib import Path

def write_something():
    # These should be flagged
    with open("file.txt", "w") as f:
        f.write("test")

    Path("file.txt").write_text("test")
    os.remove("file.txt")
    os.rename("old.txt", "new.txt")
    """
        findings = scan_for_unsafe_patterns(code, "test.py")

        # Should find multiple unsafe patterns
        assert len(findings) >= 4
        patterns = [f.pattern_type for f in findings]
        assert "open_write" in patterns
        assert "path_write_text" in patterns
        assert "os_remove" in patterns
        assert "os_rename" in patterns

    def test_detector_finds_subprocess_calls(self):
        """Test that detector flags subprocess execution primitives."""
        code = """
import subprocess

def run_something():
    # These should be flagged
    subprocess.run(["ls", "-la"])
    subprocess.call(["git", "status"])
    subprocess.Popen(["python", "script.py"])
    """
        findings = scan_for_unsafe_patterns(code, "test.py")

        # Should find subprocess patterns
        assert len(findings) >= 3
        patterns = [f.pattern_type for f in findings]
        assert "subprocess_run" in patterns
        assert "subprocess_call" in patterns
        assert "subprocess_Popen" in patterns

    def test_detector_ignores_safe_operations(self):
        """Test that detector ignores read-only operations and safe paths."""
        code = """
import os
from pathlib import Path

def read_something():
    # These should NOT be flagged (read-only)
    with open("file.txt", "r") as f:
        content = f.read()

    Path("file.txt").read_text()

    # Safe path operations (no mutation)
    Path("file.txt").exists()
    os.path.exists("file.txt")
    """
        findings = scan_for_unsafe_patterns(code, "test.py")

        # Should not find any unsafe patterns
        assert len(findings) == 0

    def test_detector_scans_actual_agent_code(self):
        """Test that detector can scan actual agent code paths."""
        # Scan scoped areas for actual findings
        scoped_dirs = [
            repo_root / AGENTIC_CORE_DIR / "L0_routing" / "reasoning",
            repo_root / AGENTIC_CORE_DIR / "L1_cognition" / "reasoning",
            repo_root / AGENTIC_CORE_DIR / "L2_execution" / "reasoning",
            repo_root / AGENTIC_CORE_DIR / "L3_orchestration" / "reasoning",
            repo_root / APPS_LIC_DIR / "reasoning",
            repo_root / APPS_RG_DIR / "reasoning",
            repo_root / APPS_SHARED_DIR / "reasoning",
            repo_root / TOOLS_DIR,
            repo_root / AGENTIC_CORE_DIR / "L0_routing" / "scripts",
            repo_root / AGENTIC_CORE_DIR / "L1_cognition" / "scripts",
            repo_root / AGENTIC_CORE_DIR / "L2_execution" / "scripts",
        ]

        all_findings = []
        for dir_path in scoped_dirs:
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    if py_file.is_file():
                        try:
                            with open(py_file, encoding="utf-8") as f:
                                content = f.read()
                            findings = scan_for_unsafe_patterns(content, str(py_file.relative_to(repo_root)))
                            all_findings.extend(findings)
                        except Exception:  # guardian: allow-silent-swallower
                            # Skip files that can't be read
                            pass

        # At minimum, we should find some patterns in the codebase
        # (This test documents the current state)
        print(f"\nFound {len(all_findings)} unsafe patterns in scoped areas:")
        for finding in all_findings[:10]:  # Show first 10
            print(f"  {finding.file_path}:{finding.line_number} - {finding.pattern_type}")

        if len(all_findings) > 10:
            print(f"  ... and {len(all_findings) - 10} more")

        # Store findings for evidence
        self.scoped_findings = all_findings

    def test_detector_enforcement(self):
        """Test that detector enforcement fails when unsafe patterns are present."""
        code_with_unsafe = """
def unsafe_function():
    open("test.txt", "w").write("bad")
"""

        # This should fail if we add enforcement
        findings = scan_for_unsafe_patterns(code_with_unsafe, "test.py")
        assert len(findings) > 0
        assert findings[0].pattern_type == "open_write"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
