"""
Simple CST-based CodeHealerAgent Test - Zero-Loss Healing Verification

Minimal test to verify CST integration without complex imports.
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from agentic_core.L5_safety.types.surgical_context_types import (
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)

# Test the CST healing directly without full agent import
from agentic_core.mixins.cst_healer_mixin import (
    SurgicalCSTHealerMixin,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_code_healer_cst_simple")
# REMOVED: _emit_applies_guardrail("p0", "test_code_healer_cst_simple", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_code_healer_cst_simple", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_code_healer_cst_simple", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_code_healer_cst_simple", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_code_healer_cst_simple", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_code_healer_cst_simple", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_code_healer_cst_simple", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_code_healer_cst_simple", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_code_healer_cst_simple", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_code_healer_cst_simple", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_code_healer_cst_simple", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_code_healer_cst_simple", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_code_healer_cst_simple", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_code_healer_cst_simple", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_code_healer_cst_simple", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_code_healer_cst_simple", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_code_healer_cst_simple", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_code_healer_cst_simple", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_code_healer_cst_simple", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_code_healer_cst_simple", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_code_healer_cst_simple", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_code_healer_cst_simple", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_code_healer_cst_simple", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_code_healer_cst_simple", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_code_healer_cst_simple", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_code_healer_cst_simple", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_code_healer_cst_simple", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_code_healer_cst_simple", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_code_healer_cst_simple", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_code_healer_cst_simple", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_code_healer_cst_simple", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_code_healer_cst_simple", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_code_healer_cst_simple", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_code_healer_cst_simple", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_code_healer_cst_simple", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_code_healer_cst_simple", "write_through")
# REMOVED: _emit_writes_through("p1", "test_code_healer_cst_simple", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_code_healer_cst_simple", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_code_healer_cst_simple", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_code_healer_cst_simple", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_code_healer_cst_simple", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_code_healer_cst_simple", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_code_healer_cst_simple", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_code_healer_cst_simple", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_code_healer_cst_simple", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_code_healer_cst_simple", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_code_healer_cst_simple", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_code_healer_cst_simple", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_code_healer_cst_simple", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_code_healer_cst_simple", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_code_healer_cst_simple", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_code_healer_cst_simple")
# REMOVED: _emit_gated_by_confidence("p1", "test_code_healer_cst_simple", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_code_healer_cst_simple")
# REMOVED: emit_determinism_digest("p0", "test_code_healer_cst_simple")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_code_healer_cst_simple", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_code_healer_cst_simple", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_code_healer_cst_simple", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_code_healer_cst_simple", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_code_healer_cst_simple", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_code_healer_cst_simple", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_code_healer_cst_simple", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_code_healer_cst_simple", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_code_healer_cst_simple", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_code_healer_cst_simple", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_code_healer_cst_simple", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_code_healer_cst_simple", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_code_healer_cst_simple", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_code_healer_cst_simple", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_code_healer_cst_simple", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_code_healer_cst_simple", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_code_healer_cst_simple", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_code_healer_cst_simple", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_code_healer_cst_simple", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_code_healer_cst_simple", "exec_snapshot_link")


class TestCodeHealerCSTSimple:
    """Simple test for CST-based healing functionality."""

    def test_cst_import_removal_preserves_comments(self):
        """
        Test that CST-based import removal preserves comments and formatting.

        This simulates what the CodeHealerAgent would do when removing unused imports.
        """
        # Create test file with unused import and important comments
        source_code = '''#!/usr/bin/env python3
"""
Module docstring with important information.
"""

# Standard library imports
import os  # OS operations
import sys  # System-specific parameters
import unused_module  # This should be removed
import json  # JSON operations

class TestClass:
    """Class docstring."""

    def method(self):
        # Important comment inside method
        return os.getcwd()

# End of file comment
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Read and parse the file
            content = temp_path.read_text(encoding="utf-8")

            # Create surgical context for removing unused import
            import ast

            tree = ast.parse(content)

            # Find the unused import node
            unused_import_line = 8  # Line with "import unused_module"

            # Create violation and coordinate separately
            coordinate = ASTCoordinate(
                line=unused_import_line,
                column=0,
                node_id="unused_import",
                node_type="Import",
            )

            violation = ViolationConstraint(
                constraint_type="unused_import",
                severity="warning",
                message="Unused import: unused_module",
                fix_type="delete",
            )

            # Add target_coordinate to violation
            violation.target_coordinate = coordinate

            context = SurgicalContext(
                file_path=temp_path,
                file_content=content,
                ast_tree=tree,
                violations=[violation],
                target_coordinates=[violation.target_coordinate],
                detector_agent="CodeHealerAgent",
                detection_method="heal_imports",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="unused_import_unused_module_8",
            )

            # Apply CST-based healing
            healer = SurgicalCSTHealerMixin()
            healer.heal_surgical_cst(context)

            # Read the healed file
            healed_content = temp_path.read_text(encoding="utf-8")

            # CRITICAL: Verify all comments are preserved
            assert "#!/usr/bin/env python3" in healed_content
            assert '"""' in healed_content  # Module docstring
            assert "Module docstring with important information." in healed_content
            assert "# Standard library imports" in healed_content
            assert "# OS operations" in healed_content
            assert "# System-specific parameters" in healed_content
            assert "# JSON operations" in healed_content
            assert "# Important comment inside method" in healed_content
            assert "# End of file comment" in healed_content

            # Verify class docstring is preserved
            assert '"""Class docstring."""' in healed_content

            # Verify unused import was removed
            assert "import unused_module" not in healed_content

            # Verify other imports are preserved
            assert "import os" in healed_content
            assert "import sys" in healed_content
            assert "import json" in healed_content

            # Verify method and comment are preserved
            assert "def method(self):" in healed_content
            assert "# Important comment inside method" in healed_content
            assert "return os.getcwd()" in healed_content

            print("✅ CST-based import removal preserves all metadata!")

        finally:
            temp_path.unlink()

    def test_cst_zero_loss_no_violations(self):
        """Test that CST healing doesn't modify files when no violations exist."""
        source_code = """# Important header
import os

def test():
    # Important comment
    return "test"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Create context with no violations
            import ast

            tree = ast.parse(source_code)

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[],  # No violations
                target_coordinates=[],
                detector_agent="CodeHealerAgent",
                detection_method="heal_imports",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="no_violations",
            )

            # Apply CST-based healing
            healer = SurgicalCSTHealerMixin()
            healer.heal_surgical_cst(context)

            # File should be unchanged
            healed_content = temp_path.read_text(encoding="utf-8")
            assert healed_content == source_code

            print("✅ Zero-loss verification passed!")

        finally:
            temp_path.unlink()

    def test_cst_preserves_weird_formatting(self):
        """Test that CST preserves weird spacing and formatting."""
        source_code = '''# Header comment
import      os     # Weird spacing
import sys

class      TestClass:  # More weird spacing
    """  # Docstring with weird spacing
    This has weird formatting.
    """

    def method(self):
        # Comment with    extra spaces
        pass
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Create context to remove sys import
            import ast

            tree = ast.parse(source_code)

            # Create violation and coordinate separately
            coordinate = ASTCoordinate(line=3, column=0, node_id="sys_import", node_type="Import")

            violation = ViolationConstraint(
                constraint_type="unused_import",
                severity="warning",
                message="Unused import: sys",
                fix_type="delete",
            )

            # Add target_coordinate to violation
            violation.target_coordinate = coordinate

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[violation],
                target_coordinates=[violation.target_coordinate],
                detector_agent="CodeHealerAgent",
                detection_method="heal_imports",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="unused_import_sys_3",
            )

            # Apply CST-based healing
            healer = SurgicalCSTHealerMixin()
            healer.heal_surgical_cst(context)

            # Read healed content
            healed_content = temp_path.read_text(encoding="utf-8")

            # Verify weird formatting is preserved
            assert "import      os     # Weird spacing" in healed_content
            assert "class      TestClass:  # More weird spacing" in healed_content
            assert '"""  # Docstring with weird spacing' in healed_content
            assert "# Comment with    extra spaces" in healed_content

            # Verify sys import was removed
            assert "import sys" not in healed_content

            print("✅ CST preserves weird formatting!")

        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
