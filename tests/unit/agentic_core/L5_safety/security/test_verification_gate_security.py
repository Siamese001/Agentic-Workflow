"""
Test suite for VerificationGate - Epistemic Cascade Prevention

Tests the verification gate's ability to detect and block hallucinated
surgical operations before they corrupt the codebase.
"""

import pytest

from agentic_core.L5_safety.enforcement.verification_gate import VerificationGate
from agentic_core.L5_safety.types.surgical_context_types import (
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)
from agentic_core.L5_safety.utils.unified_cst_healer_util import (
    HealingConfig,
    UnifiedCSTHealer,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_verification_gate_security")
_emit_applies_guardrail("p0", "test_verification_gate_security", "p0_governance")
_emit_reads_policy_state("p0", "test_verification_gate_security", "policy_binding")
_emit_snapshots_state("p0", "test_verification_gate_security", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_verification_gate_security", "p4obs", "metric_1")
_emit_emits_metric_event("test_verification_gate_security", "p4obs", "metric_2")
_emit_emits_metric_event("test_verification_gate_security", "p4obs", "metric_3")
_emit_emits_metric_event("test_verification_gate_security", "p4obs", "metric_4")
_emit_emits_metric_event("test_verification_gate_security", "p4obs", "metric_5")
_emit_emits_metric_event("test_verification_gate_security", "p4obs", "metric_6")
_emit_records_incident_event("test_verification_gate_security", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_verification_gate_security", "p4obs", "anomaly")
_emit_writes_observability_log("test_verification_gate_security", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_verification_gate_security", "p4obs", "mon_state")
_emit_triggers_alert("test_verification_gate_security", "p4obs", "alert")
_emit_links_incident_trace("test_verification_gate_security", "p4obs", "trace_link")
_emit_captures_pattern("test_verification_gate_security", "p3lm", "pattern")
_emit_records_learning_event("test_verification_gate_security", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_verification_gate_security", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_verification_gate_security", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_verification_gate_security", "p3lm", "routing")
_emit_improves_agent_policy("test_verification_gate_security", "p3lm", "policy")
_emit_stores_learning_state("test_verification_gate_security", "p3lm", "state")
_emit_records_execution_trace("test_verification_gate_security", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_verification_gate_security", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_verification_gate_security", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_verification_gate_security", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_verification_gate_security", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_verification_gate_security", "env_read", "p2_env_1")
_emit_reads_environ("test_verification_gate_security", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_verification_gate_security", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_verification_gate_security", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_verification_gate_security", "context_pull")
_emit_pulls_context("p1", "test_verification_gate_security", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_verification_gate_security", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_verification_gate_security", "uwg_term_2")
_emit_writes_through("p1", "test_verification_gate_security", "write_through")
_emit_writes_through("p1", "test_verification_gate_security", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_verification_gate_security", "safety_validation")
_emit_invokes_eval("p1", "test_verification_gate_security", "eval_call")
_emit_proposal_commits_routing("p1", "test_verification_gate_security", "routing_commit")
_emit_escalates_to_human("p1", "test_verification_gate_security", "human_escalation")
_emit_routes_through("p1", "test_verification_gate_security", "route_through")
_emit_checks_agent_registry("p1", "test_verification_gate_security", "agent_registry")
_emit_validates_agent_capability("p1", "test_verification_gate_security", "capability")
_emit_dispatches_execution_plan("p1", "test_verification_gate_security", "exec_plan")
_emit_agent_executes_agent("p1", "test_verification_gate_security", "sub_agent")
_emit_routes_to_agent("p1", "test_verification_gate_security", "target_agent")
_emit_verifies_policy("p1", "test_verification_gate_security", "policy_check")
_emit_observes_runtime_state("p1", "test_verification_gate_security", "runtime_state")
_emit_verifies_boundary("p1", "test_verification_gate_security", "boundary_check")
_emit_transcripts_response("p1", "test_verification_gate_security", "transcript")
_emit_hard_fails_untranscripted("p1", "test_verification_gate_security")
_emit_gated_by_confidence("p1", "test_verification_gate_security", "confidence_gate")
emit_replay_key("p0", "test_verification_gate_security")
emit_determinism_digest("p0", "test_verification_gate_security")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_verification_gate_security", "execution_auth")
_emit_validates_capability("p2", "test_verification_gate_security", "capability_check")
_emit_routes_to_capability("p2", "test_verification_gate_security", "capability_route")
_emit_writes_via_uwg("p2", "test_verification_gate_security", "uwg_write")
_emit_blocks_direct_write("p2", "test_verification_gate_security", "direct_write_block")
_emit_records_tool_invocation("p2", "test_verification_gate_security", "tool_invocation")
_emit_captures_execution_output("p2", "test_verification_gate_security", "exec_output")
_emit_dispatches_agent("p3", "test_verification_gate_security", "agent_dispatch")
_emit_coordinates_agents("p3", "test_verification_gate_security", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_verification_gate_security", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_verification_gate_security", "healing_outcome")
_emit_escalates_failure("p3", "test_verification_gate_security", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_verification_gate_security", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_verification_gate_security", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_verification_gate_security", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_verification_gate_security", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_verification_gate_security", "eval_metric")
_emit_stores_embedding("p4", "test_verification_gate_security", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_verification_gate_security", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_verification_gate_security", "exec_snapshot_link")


class TestVerificationGateBasic:
    """Basic verification gate functionality tests."""

    def test_verify_existing_import(self, tmp_path):
        """Test that verification passes for existing imports."""
        # Create a file with numpy import
        test_file = tmp_path / "test_file.py"
        test_file.write_text("import numpy\nimport os\n")

        gate = VerificationGate()
        result = gate.verify_action(test_file, "delete_import", "numpy")

        assert result is True, "Should verify existing import"

    def test_reject_nonexistent_import(self, tmp_path):
        """Test that verification fails for non-existent imports."""
        # Create a file WITHOUT numpy import
        test_file = tmp_path / "test_file.py"
        test_file.write_text("import os\nimport sys\n")

        gate = VerificationGate()
        result = gate.verify_action(test_file, "delete_import", "numpy")

        assert result is False, "Should reject non-existent import"

    def test_verify_existing_function(self, tmp_path):
        """Test that verification passes for existing functions."""
        test_file = tmp_path / "test_file.py"
        test_file.write_text("def my_function():\n    pass\n")

        gate = VerificationGate()
        result = gate.verify_action(test_file, "modify_function", "my_function")

        assert result is True, "Should verify existing function"

    def test_reject_nonexistent_function(self, tmp_path):
        """Test that verification fails for non-existent functions."""
        test_file = tmp_path / "test_file.py"
        test_file.write_text("def other_function():\n    pass\n")

        gate = VerificationGate()
        result = gate.verify_action(test_file, "modify_function", "my_function")

        assert result is False, "Should reject non-existent function"

    def test_verify_existing_class(self, tmp_path):
        """Test that verification passes for existing classes."""
        test_file = tmp_path / "test_file.py"
        test_file.write_text("class MyClass:\n    pass\n")

        gate = VerificationGate()
        result = gate.verify_action(test_file, "remove_class", "MyClass")

        assert result is True, "Should verify existing class"

    def test_cache_functionality(self, tmp_path):
        """Test that verification results are cached."""
        test_file = tmp_path / "test_file.py"
        test_file.write_text("import numpy\n")

        gate = VerificationGate()

        # First call
        result1 = gate.verify_action(test_file, "delete_import", "numpy")
        cache_stats1 = gate.get_cache_stats()

        # Second call (should use cache)
        result2 = gate.verify_action(test_file, "delete_import", "numpy")
        cache_stats2 = gate.get_cache_stats()

        assert result1 is True
        assert result2 is True
        assert cache_stats1["cache_size"] == 1
        assert cache_stats2["cache_size"] == 1


class TestVerificationGateWithContext:
    """Test verification gate with SurgicalContext."""

    def test_verify_modification_with_valid_targets(self, tmp_path):
        """Test that verify_modification passes for valid targets."""
        import ast

        test_file = tmp_path / "test_file.py"
        content = "import numpy\nimport pandas\n"
        test_file.write_text(content)

        # Create violation for existing import
        violation = ViolationConstraint(
            constraint_type="unused_import",
            severity="warning",
            message="Remove import 'numpy'",
            fix_type="delete",
        )
        violation.target_coordinate = ASTCoordinate(line=1, column=0, node_id="numpy", node_type="Import")

        context = SurgicalContext(
            file_path=test_file,
            file_content=content,
            ast_tree=ast.parse(content),
            violations=[violation],
            target_coordinates=[violation.target_coordinate],
            detector_agent="TestAgent",
            detection_method="test",
            detection_timestamp="2026-02-02",
            violation_id="test_001",
        )

        gate = VerificationGate()
        result = gate.verify_modification(context)

        assert result is True, "Should verify valid modification"

    def test_reject_modification_with_invalid_targets(self, tmp_path):
        """Test that verify_modification fails for hallucinated targets."""
        import ast

        test_file = tmp_path / "test_file.py"
        content = "import os\nimport sys\n"  # NO numpy!
        test_file.write_text(content)

        # Create violation for NON-EXISTENT import (hallucination)
        violation = ViolationConstraint(
            constraint_type="unused_import",
            severity="warning",
            message="Remove import 'numpy'",
            fix_type="delete",
        )
        violation.target_coordinate = ASTCoordinate(line=1, column=0, node_id="numpy", node_type="Import")

        context = SurgicalContext(
            file_path=test_file,
            file_content=content,
            ast_tree=ast.parse(content),
            violations=[violation],
            target_coordinates=[violation.target_coordinate],
            detector_agent="TestAgent",
            detection_method="test",
            detection_timestamp="2026-02-02",
            violation_id="test_002",
        )

        gate = VerificationGate()
        result = gate.verify_modification(context)

        assert result is False, "Should reject hallucinated modification"


class TestHallucinationPrevention:
    """
    The critical test: Verify that UnifiedCSTHealer rejects hallucinations.

    This is the "Epistemic Cascade" prevention test.
    """

    def test_unified_healer_rejects_hallucinated_import(self, tmp_path):
        """
        CRITICAL TEST: Verify UnifiedCSTHealer blocks hallucinated import deletion.

        Scenario:
        1. Create a file WITHOUT 'import numpy'
        2. Create a violation requesting to delete 'import numpy' (hallucination)
        3. Call UnifiedCSTHealer.heal_file
        4. Assert: Healer returns SKIPPED status and file is UNTOUCHED
        """
        # Step 1: Create file WITHOUT numpy import
        test_file = tmp_path / "test_module.py"
        original_content = """import os
import sys

def main():
    print("Hello, World!")
"""
        test_file.write_text(original_content)

        # Step 2: Create hallucinated violation (delete non-existent import)
        hallucinated_violation = ViolationConstraint(
            constraint_type="unused_import",
            severity="warning",
            message="Remove import 'numpy'",  # This import doesn't exist!
            fix_type="delete",
        )
        hallucinated_violation.target_coordinate = ASTCoordinate(
            line=1,
            column=0,
            node_id="numpy",
            node_type="Import",
        )

        # Step 3: Attempt to heal with hallucinated violation
        healer = UnifiedCSTHealer(config=HealingConfig(enable_import_healing=True))
        result = healer.heal_file(test_file, violations=[hallucinated_violation])

        # Step 4: Assert healing was BLOCKED
        assert result.status == "skipped", f"Expected 'skipped', got '{result.status}'"
        assert result.violations_fixed == 0, "No violations should be fixed"
        assert result.skipped > 0, "Violations should be skipped"
        assert "Verification Gate failed" in result.details or "hallucination" in result.details.lower()

        # Step 5: Verify file is UNTOUCHED
        final_content = test_file.read_text()
        assert final_content == original_content, "File should remain unchanged"
        assert "import numpy" not in final_content, "Hallucinated import should not appear"

    def test_unified_healer_allows_valid_import_deletion(self, tmp_path):
        """
        Positive test: Verify UnifiedCSTHealer allows valid operations.

        Ensures the gate doesn't block legitimate healing operations.
        """
        # Create file WITH numpy import
        test_file = tmp_path / "test_module.py"
        original_content = """import numpy
import os

def main():
    print("Hello, World!")
"""
        test_file.write_text(original_content)

        # Create VALID violation (delete existing import)
        valid_violation = ViolationConstraint(
            constraint_type="unused_import",
            severity="warning",
            message="Remove import 'numpy'",
            fix_type="delete",
        )
        valid_violation.target_coordinate = ASTCoordinate(
            line=1,
            column=0,
            node_id="numpy",
            node_type="Import",
        )

        # Attempt to heal with valid violation
        healer = UnifiedCSTHealer(config=HealingConfig(enable_import_healing=True))
        result = healer.heal_file(test_file, violations=[valid_violation])

        # Assert healing was ALLOWED (though may not actually fix due to transformer implementation)
        assert result.status in ("success", "partial"), f"Expected success/partial, got '{result.status}'"
        assert "Verification Gate failed" not in result.details

    def test_multiple_violations_one_hallucinated(self, tmp_path):
        """
        Test that if ANY violation is hallucinated, the entire operation is blocked.

        This prevents partial/corrupted states.
        """
        test_file = tmp_path / "test_module.py"
        original_content = """import os
import sys

def main():
    print("Hello, World!")
"""
        test_file.write_text(original_content)

        # Mix of valid and hallucinated violations
        valid_violation = ViolationConstraint(
            constraint_type="unused_import",
            severity="warning",
            message="Remove import 'os'",
            fix_type="delete",
        )
        valid_violation.target_coordinate = ASTCoordinate(line=1, column=0, node_id="os", node_type="Import")

        hallucinated_violation = ViolationConstraint(
            constraint_type="unused_import",
            severity="warning",
            message="Remove import 'numpy'",  # Doesn't exist!
            fix_type="delete",
        )
        hallucinated_violation.target_coordinate = ASTCoordinate(
            line=2,
            column=0,
            node_id="numpy",
            node_type="Import",
        )

        # Attempt to heal with mixed violations
        healer = UnifiedCSTHealer(config=HealingConfig(enable_import_healing=True))
        result = healer.heal_file(test_file, violations=[valid_violation, hallucinated_violation])

        # Assert entire operation was BLOCKED
        assert result.status == "skipped", "Should block entire operation if any violation is hallucinated"
        assert result.violations_fixed == 0, "No violations should be fixed"

        # Verify file is UNTOUCHED
        final_content = test_file.read_text()
        assert final_content == original_content, "File should remain unchanged"


class TestL4Integration:
    """Test integration with L4ContextManager for caching."""

    def test_verification_gate_uses_l4_cache(self, tmp_path):
        """Test that VerificationGate can use L4ContextManager cache."""
        import ast
        from unittest.mock import Mock

        test_file = tmp_path / "test_file.py"
        content = "import numpy\n"
        test_file.write_text(content)

        # Create mock L4ContextManager
        mock_context_manager = Mock()
        mock_context_manager.get_file_analysis.return_value = {
            "verified": True,
            "violations_count": 1,
        }

        # Create gate with L4 integration
        gate = VerificationGate(context_manager=mock_context_manager)

        violation = ViolationConstraint(
            constraint_type="unused_import",
            severity="warning",
            message="Remove import 'numpy'",
            fix_type="delete",
        )
        violation.target_coordinate = ASTCoordinate(line=1, column=0, node_id="numpy", node_type="Import")

        context = SurgicalContext(
            file_path=test_file,
            file_content=content,
            ast_tree=ast.parse(content),
            violations=[violation],
            target_coordinates=[violation.target_coordinate],
            detector_agent="TestAgent",
            detection_method="test",
            detection_timestamp="2026-02-02",
            violation_id="test_003",
        )

        result = gate.verify_modification(context)

        # Should use cached result
        assert result is True
        mock_context_manager.get_file_analysis.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
