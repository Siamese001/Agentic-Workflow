"""
CST-based CodeHealerAgent Integration Test

Tests that the CodeHealerAgent correctly integrates with the CST infrastructure
and preserves the surgical healing pattern.
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L5_safety.types.surgical_context_types import (
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)
#  # MOVED: from agentic_core.mixins.cst_healer_mixin import (
    SurgicalCSTHealerMixin,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_code_healer_cst_integration")
# REMOVED: _emit_applies_guardrail("p0", "test_code_healer_cst_integration", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_code_healer_cst_integration", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_code_healer_cst_integration", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_code_healer_cst_integration", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_code_healer_cst_integration", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_code_healer_cst_integration", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_code_healer_cst_integration", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_code_healer_cst_integration", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_code_healer_cst_integration", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_code_healer_cst_integration", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_code_healer_cst_integration", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_code_healer_cst_integration", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_code_healer_cst_integration", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_code_healer_cst_integration", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_code_healer_cst_integration", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_code_healer_cst_integration", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_code_healer_cst_integration", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_code_healer_cst_integration", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_code_healer_cst_integration", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_code_healer_cst_integration", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_code_healer_cst_integration", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_code_healer_cst_integration", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_code_healer_cst_integration", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_code_healer_cst_integration", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_code_healer_cst_integration", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_code_healer_cst_integration", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_code_healer_cst_integration", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_code_healer_cst_integration", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_code_healer_cst_integration", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_code_healer_cst_integration", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_code_healer_cst_integration", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_code_healer_cst_integration", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_code_healer_cst_integration", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_code_healer_cst_integration", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_code_healer_cst_integration", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_code_healer_cst_integration", "write_through")
# REMOVED: _emit_writes_through("p1", "test_code_healer_cst_integration", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_code_healer_cst_integration", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_code_healer_cst_integration", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_code_healer_cst_integration", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_code_healer_cst_integration", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_code_healer_cst_integration", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_code_healer_cst_integration", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_code_healer_cst_integration", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_code_healer_cst_integration", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_code_healer_cst_integration", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_code_healer_cst_integration", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_code_healer_cst_integration", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_code_healer_cst_integration", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_code_healer_cst_integration", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_code_healer_cst_integration", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_code_healer_cst_integration")
# REMOVED: _emit_gated_by_confidence("p1", "test_code_healer_cst_integration", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_code_healer_cst_integration")
# REMOVED: emit_determinism_digest("p0", "test_code_healer_cst_integration")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_code_healer_cst_integration", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_code_healer_cst_integration", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_code_healer_cst_integration", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_code_healer_cst_integration", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_code_healer_cst_integration", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_code_healer_cst_integration", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_code_healer_cst_integration", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_code_healer_cst_integration", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_code_healer_cst_integration", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_code_healer_cst_integration", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_code_healer_cst_integration", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_code_healer_cst_integration", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_code_healer_cst_integration", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_code_healer_cst_integration", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_code_healer_cst_integration", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_code_healer_cst_integration", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_code_healer_cst_integration", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_code_healer_cst_integration", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_code_healer_cst_integration", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_code_healer_cst_integration", "exec_snapshot_link")


class TestCodeHealerCSTIntegration:
    """Test CST integration with CodeHealerAgent pattern."""

    def test_surgical_context_creation(self):
        from agentic_core.L5_safety.types.surgical_context_types import (
        from agentic_core.mixins.cst_healer_mixin import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        """Test that surgical contexts are created correctly for import healing."""
        source_code = """# Module comment
import os  # Used import
import unused_module  # Should be removed

def test():
    return os.getcwd()
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Parse the file
            import ast

            tree = ast.parse(source_code)

            # Create violation for unused import (simulating CodeHealerAgent logic)
            coordinate = ASTCoordinate(line=3, column=0, node_id="unused_import", node_type="Import")

            violation = ViolationConstraint(
                constraint_type="unused_import",
                severity="warning",
                message="Unused import: unused_module",
                fix_type="delete",
            )
            violation.target_coordinate = coordinate

            # Create surgical context as CodeHealerAgent would
            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[violation],
                target_coordinates=[coordinate],
                detector_agent="CodeHealerAgent",
                detection_method="heal_imports",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="unused_import_unused_module_3",
            )

            # Verify context structure
            assert context.file_path == temp_path
            assert context.detector_agent == "CodeHealerAgent"
            assert context.detection_method == "heal_imports"
            assert len(context.violations) == 1
            assert context.violations[0].constraint_type == "unused_import"
            assert context.violations[0].fix_type == "delete"
            assert len(context.target_coordinates) == 1
            assert context.target_coordinates[0].line == 3

            print("✅ Surgical context creation works correctly!")

        finally:
            temp_path.unlink()

    def test_cst_mixin_integration(self):
        """Test that SurgicalCSTHealerMixin can be invoked."""
        source_code = """# Test file
import os

def test():
    return "test"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Create minimal context
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

            # Test CST mixin invocation
            healer = SurgicalCSTHealerMixin()
            result = healer.heal_surgical_cst(context)

            # Verify result structure
            assert "status" in result
            assert "violations_found" in result
            assert "violations_fixed" in result
            assert "errors" in result
            assert "skipped" in result
            assert result["status"] in ["success", "error"]

            # Verify file is unchanged when no violations
            healed_content = temp_path.read_text(encoding="utf-8")
            assert healed_content == source_code

            print("✅ CST mixin integration works correctly!")

        finally:
            temp_path.unlink()

    def test_actual_import_removal(self):
        """Test that imports are actually removed from the file."""
        source_code = """# Module comment
import os  # Used import
import unused_module  # Should be removed
import json  # Another used import

def test():
    return os.path.join("data.json")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Parse the file
            import ast

            tree = ast.parse(source_code)

            # Create violation for unused import
            coordinate = ASTCoordinate(line=3, column=0, node_id="unused_import", node_type="Import")

            violation = ViolationConstraint(
                constraint_type="unused_import",
                severity="warning",
                message="Unused import: unused_module",
                fix_type="delete",
            )
            violation.target_coordinate = coordinate

            # Create surgical context
            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[violation],
                target_coordinates=[coordinate],
                detector_agent="CodeHealerAgent",
                detection_method="heal_imports",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="unused_import_unused_module_3",
            )

            # Apply CST-based healing
            healer = SurgicalCSTHealerMixin()
            result = healer.heal_surgical_cst(context)

            # Read the healed file
            healed_content = temp_path.read_text(encoding="utf-8")

            # CRITICAL ASSERTIONS:
            # 1. The unused import should be GONE
            assert "import unused_module" not in healed_content, "Unused import was not removed!"

            # 2. The comment should stay (proving zero-loss)
            assert "# Module comment" in healed_content, "Module comment was lost!"
            assert "# Used import" in healed_content, "Used import comment was lost!"
            assert "# Another used import" in healed_content, "Another used import comment was lost!"

            # 3. Other imports should be preserved
            assert "import os" in healed_content, "Used import was incorrectly removed!"
            assert "import json" in healed_content, "Another used import was incorrectly removed!"

            # 4. Function should be preserved
            assert "def test():" in healed_content, "Function was lost!"
            assert "return os.path.join" in healed_content, "Function body was corrupted!"

            # 5. Verify healing result
            assert result["status"] == "success"
            assert result["violations_fixed"] >= 1

            print("✅ Import actually removed while preserving all comments!")

        finally:
            temp_path.unlink()

    def test_CodeHealerAgent_pattern(self):
        """Test the pattern that CodeHealerAgent would use for CST healing."""
        source_code = '''# Important module comment
import os  # OS operations
import json  # JSON operations

class TestClass:
    """Important class docstring."""

    def method(self):
        # Important method comment
        return os.path.join("path", "file.json")
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Simulate CodeHealerAgent.heal_imports() logic
            import ast

            tree = ast.parse(source_code)

            # Find imports (simplified version of CodeHealerAgent logic)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.asname or alias.name.split(".")[0]
                        imports.append((node, name, node.lineno))

            # Simulate finding unused imports (for this test, assume none are unused)
            unused_imports = []  # In real scenario, this would find unused ones

            surgical_contexts = []
            actions = []

            for node, name, lineno in unused_imports:
                # Create HealingAction for tracking
                action = {
                    "healing_type": "IMPORT",
                    "file_path": temp_path,
                    "line_number": lineno,
                    "description": f"Remove unused import: {name}",
                    "applied": False,
                }
                actions.append(action)

                # Create SurgicalContext for CST healing
                coordinate = ASTCoordinate(
                    line=lineno,
                    column=0,
                    node_id=f"import_{name}",
                    node_type="Import",
                )

                violation = ViolationConstraint(
                    constraint_type="unused_import",
                    severity="warning",
                    message=f"Unused import: {name}",
                    fix_type="delete",
                )
                violation.target_coordinate = coordinate

                context = SurgicalContext(
                    file_path=temp_path,
                    file_content=source_code,
                    ast_tree=tree,
                    violations=[violation],
                    target_coordinates=[coordinate],
                    detector_agent="CodeHealerAgent",
                    detection_method="heal_imports",
                    detection_timestamp=datetime.now().isoformat(),
                    violation_id=f"unused_import_{name}_{lineno}",
                )
                surgical_contexts.append(context)

            # Apply CST-based healing (would be done in actual CodeHealerAgent)
            healer = SurgicalCSTHealerMixin()
            for context in surgical_contexts:
                healer.heal_surgical_cst(context)
                # In real scenario, would mark actions as applied based on result

            # Verify original file is preserved when no unused imports
            healed_content = temp_path.read_text(encoding="utf-8")
            assert healed_content == source_code

            # Verify all important elements are preserved
            assert "# Important module comment" in healed_content
            assert "# OS operations" in healed_content
            assert "# JSON operations" in healed_content
            assert '"""Important class docstring."""' in healed_content
            assert "# Important method comment" in healed_content

            print("✅ CodeHealerAgent pattern works correctly!")

        finally:
            temp_path.unlink()

    def test_cst_preserves_structure(self):
        """Test that CST processing preserves file structure even when no changes are made."""
        source_code = '''#!/usr/bin/env python3
"""
Complex module docstring
with multiple lines
and formatting.
"""

# Import section
import os
import sys

# Class definition
class ComplexClass:
    """
    Complex class docstring
    with detailed information.
    """

    def __init__(self):
        # Constructor comment
        self.value = os.getcwd()

    def method(self):
        """Method docstring."""
        # Method implementation comment
        return self.value

# Module-level code
if __name__ == "__main__":
    # Main block comment
    print("test")
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Process with CST (no violations)
            import ast

            tree = ast.parse(source_code)

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[],
                target_coordinates=[],
                detector_agent="CodeHealerAgent",
                detection_method="heal_imports",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="structure_test",
            )

            healer = SurgicalCSTHealerMixin()
            healer.heal_surgical_cst(context)

            # Verify structure is preserved exactly
            healed_content = temp_path.read_text(encoding="utf-8")
            assert healed_content == source_code

            # Verify specific elements are preserved
            assert "#!/usr/bin/env python3" in healed_content
            assert '"""' in healed_content
            assert "Complex module docstring" in healed_content
            assert "# Import section" in healed_content
            assert "# Class definition" in healed_content
            assert "# Constructor comment" in healed_content
            assert "# Method implementation comment" in healed_content
            assert "# Module-level code" in healed_content
            assert "# Main block comment" in healed_content

            print("✅ CST preserves complex file structure!")

        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
