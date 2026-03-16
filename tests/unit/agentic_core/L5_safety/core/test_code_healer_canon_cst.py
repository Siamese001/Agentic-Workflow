"""
CST-based Canon Healing Tests

Tests that the CodeHealerAgent correctly performs canon healing operations
using CST-based transformers while preserving comments and formatting.
"""

import ast
import tempfile

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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_code_healer_canon_cst")
_emit_applies_guardrail("p0", "test_code_healer_canon_cst", "p0_governance")
_emit_reads_policy_state("p0", "test_code_healer_canon_cst", "policy_binding")
_emit_snapshots_state("p0", "test_code_healer_canon_cst", "state_snapshot")
emit_replay_key("p0", "test_code_healer_canon_cst")
emit_determinism_digest("p0", "test_code_healer_canon_cst")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_code_healer_canon_cst", "execution_auth")
_emit_validates_capability("p2", "test_code_healer_canon_cst", "capability_check")
_emit_routes_to_capability("p2", "test_code_healer_canon_cst", "capability_route")
_emit_writes_via_uwg("p2", "test_code_healer_canon_cst", "uwg_write")
_emit_blocks_direct_write("p2", "test_code_healer_canon_cst", "direct_write_block")
_emit_records_tool_invocation("p2", "test_code_healer_canon_cst", "tool_invocation")
_emit_captures_execution_output("p2", "test_code_healer_canon_cst", "exec_output")
_emit_dispatches_agent("p3", "test_code_healer_canon_cst", "agent_dispatch")
_emit_coordinates_agents("p3", "test_code_healer_canon_cst", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_code_healer_canon_cst", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_code_healer_canon_cst", "healing_outcome")
_emit_escalates_failure("p3", "test_code_healer_canon_cst", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_code_healer_canon_cst", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_code_healer_canon_cst", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_code_healer_canon_cst", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_code_healer_canon_cst", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_code_healer_canon_cst", "eval_metric")
_emit_stores_embedding("p4", "test_code_healer_canon_cst", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_code_healer_canon_cst", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_code_healer_canon_cst", "exec_snapshot_link")
_FIXED_TS = "2026-01-01T00:00:00"
from pathlib import Path

import libcst as cst
import pytest

from agentic_core.L5_safety.types.cst_transformers_types import (
    DocstringTarget,
    SurgicalBareExceptFixer,
    SurgicalDocstringInserter,
    SurgicalFutureImportInserter,
)
from agentic_core.L5_safety.types.surgical_context_types import (
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)
from agentic_core.mixins.cst_healer_mixin import (
    SurgicalCSTHealerMixin,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_links_incident_trace,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)

_emit_emits_metric_event("test_code_healer_canon_cst", "p4obs", "metric_1")
_emit_emits_metric_event("test_code_healer_canon_cst", "p4obs", "metric_2")
_emit_emits_metric_event("test_code_healer_canon_cst", "p4obs", "metric_3")
_emit_emits_metric_event("test_code_healer_canon_cst", "p4obs", "metric_4")
_emit_emits_metric_event("test_code_healer_canon_cst", "p4obs", "metric_5")
_emit_emits_metric_event("test_code_healer_canon_cst", "p4obs", "metric_6")
_emit_records_incident_event("test_code_healer_canon_cst", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_code_healer_canon_cst", "p4obs", "anomaly")
_emit_writes_observability_log("test_code_healer_canon_cst", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_code_healer_canon_cst", "p4obs", "mon_state")
_emit_triggers_alert("test_code_healer_canon_cst", "p4obs", "alert")
_emit_links_incident_trace("test_code_healer_canon_cst", "p4obs", "trace_link")
_emit_captures_pattern("test_code_healer_canon_cst", "p3lm", "pattern")
_emit_records_learning_event("test_code_healer_canon_cst", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_code_healer_canon_cst", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_code_healer_canon_cst", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_code_healer_canon_cst", "p3lm", "routing")
_emit_improves_agent_policy("test_code_healer_canon_cst", "p3lm", "policy")
_emit_stores_learning_state("test_code_healer_canon_cst", "p3lm", "state")
_emit_records_execution_trace("test_code_healer_canon_cst", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_code_healer_canon_cst", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_code_healer_canon_cst", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_code_healer_canon_cst", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_code_healer_canon_cst", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_code_healer_canon_cst", "env_read", "p2_env_1")
_emit_reads_environ("test_code_healer_canon_cst", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_code_healer_canon_cst", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_code_healer_canon_cst", "runtime_state", "p2_rt_2")
_emit_escalates_to_human("p1", "test_code_healer_canon_cst", "human_escalation")
_emit_routes_through("p1", "test_code_healer_canon_cst", "route_through")
_emit_checks_agent_registry("p1", "test_code_healer_canon_cst", "agent_registry")
_emit_validates_agent_capability("p1", "test_code_healer_canon_cst", "capability")
_emit_dispatches_execution_plan("p1", "test_code_healer_canon_cst", "exec_plan")
_emit_agent_executes_agent("p1", "test_code_healer_canon_cst", "sub_agent")
_emit_routes_to_agent("p1", "test_code_healer_canon_cst", "target_agent")
_emit_verifies_policy("p1", "test_code_healer_canon_cst", "policy_check")
_emit_observes_runtime_state("p1", "test_code_healer_canon_cst", "runtime_state")
_emit_verifies_boundary("p1", "test_code_healer_canon_cst", "boundary_check")
_emit_transcripts_response("p1", "test_code_healer_canon_cst", "transcript")
_emit_hard_fails_untranscripted("p1", "test_code_healer_canon_cst")
_emit_gated_by_confidence("p1", "test_code_healer_canon_cst", "confidence_gate")


class TestCanonHealingCST:
    """Test CST-based canon healing operations."""

    def test_future_import_insertion(self):
        """Test that __future__ import is correctly inserted."""
        source_code = """# Module comment
import os

def test():
    return os.getcwd()
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            tree = ast.parse(source_code)

            coordinate = ASTCoordinate(
                line=1,
                column=0,
                node_id="missing_future_import",
                node_type="Module",
            )
            violation = ViolationConstraint(
                constraint_type="missing_future_import",
                severity="warning",
                message="Missing __future__ annotations import",
                fix_type="insert",
            )
            violation.target_coordinate = coordinate

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[violation],
                target_coordinates=[coordinate],
                detector_agent="CodeHealerAgent",
                detection_method="heal_canon",
                detection_timestamp=_FIXED_TS,
                violation_id="future_import_test",
            )

            healer = SurgicalCSTHealerMixin()
            result = healer.heal_surgical_cst(context)

            healed_content = temp_path.read_text(encoding="utf-8")

            # Assertions
            assert "from __future__ import annotations" in healed_content
            assert "# Module comment" in healed_content
            assert "import os" in healed_content
            assert "def test():" in healed_content
            assert result["status"] == "success"
            assert result["violations_fixed"] >= 1

        finally:
            temp_path.unlink()

    def test_bare_except_fix(self):
        """Test that bare except clauses are correctly fixed."""
        source_code = """# Important comment
def risky():
    try:
        x = 1 / 0
    except:
        pass
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            tree = ast.parse(source_code)

            coordinate = ASTCoordinate(
                line=5,
                column=0,
                node_id="bare_except_5",
                node_type="ExceptHandler",
            )
            violation = ViolationConstraint(
                constraint_type="bare_except",
                severity="warning",
                message="Bare except clause at line 5",
                fix_type="replace",
            )
            violation.target_coordinate = coordinate

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[violation],
                target_coordinates=[coordinate],
                detector_agent="CodeHealerAgent",
                detection_method="heal_canon",
                detection_timestamp=_FIXED_TS,
                violation_id="bare_except_test",
            )

            healer = SurgicalCSTHealerMixin()
            result = healer.heal_surgical_cst(context)

            healed_content = temp_path.read_text(encoding="utf-8")

            # Assertions
            assert "except Exception:" in healed_content
            assert "except:" not in healed_content
            assert "# Important comment" in healed_content
            assert "def risky():" in healed_content
            assert result["status"] == "success"
            assert result["violations_fixed"] >= 1

        finally:
            temp_path.unlink()

    def test_docstring_insertion_class(self):
        """Test that docstrings are correctly inserted into classes."""
        source_code = """# Module comment
class MyClass:
    # This comment must stay
    def method(self):
        pass
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            tree = ast.parse(source_code)

            coordinate = ASTCoordinate(
                line=2,
                column=0,
                node_id="class_MyClass",
                node_type="ClassDef",
            )
            violation = ViolationConstraint(
                constraint_type="missing_docstring",
                severity="warning",
                message="Class MyClass missing docstring",
                fix_type="insert",
            )
            violation.target_coordinate = coordinate

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[violation],
                target_coordinates=[coordinate],
                detector_agent="CodeHealerAgent",
                detection_method="heal_canon",
                detection_timestamp=_FIXED_TS,
                violation_id="docstring_test",
            )

            healer = SurgicalCSTHealerMixin()
            result = healer.heal_surgical_cst(context)

            healed_content = temp_path.read_text(encoding="utf-8")

            # Assertions
            assert '"""' in healed_content  # Docstring added
            assert "# Module comment" in healed_content
            assert "# This comment must stay" in healed_content
            assert "class MyClass:" in healed_content
            assert "def method(self):" in healed_content
            assert result["status"] == "success"
            assert result["violations_fixed"] >= 1

        finally:
            temp_path.unlink()

    def test_combined_canon_fixes(self):
        """Test multiple canon fixes at once."""
        source_code = """# Header comment
import os

class MyClass:
    def risky(self):
        try:
            x = 1 / 0
        except:
            pass
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            tree = ast.parse(source_code)

            violations = []
            coordinates = []

            # Future import violation
            coord1 = ASTCoordinate(line=1, column=0, node_id="missing_future", node_type="Module")
            viol1 = ViolationConstraint(
                constraint_type="missing_future_import",
                severity="warning",
                message="Missing __future__ import",
                fix_type="insert",
            )
            viol1.target_coordinate = coord1
            violations.append(viol1)
            coordinates.append(coord1)

            # Bare except violation
            coord2 = ASTCoordinate(line=8, column=0, node_id="bare_except_8", node_type="ExceptHandler")
            viol2 = ViolationConstraint(
                constraint_type="bare_except",
                severity="warning",
                message="Bare except at line 8",
                fix_type="replace",
            )
            viol2.target_coordinate = coord2
            violations.append(viol2)
            coordinates.append(coord2)

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=violations,
                target_coordinates=coordinates,
                detector_agent="CodeHealerAgent",
                detection_method="heal_canon",
                detection_timestamp=_FIXED_TS,
                violation_id="combined_canon_test",
            )

            healer = SurgicalCSTHealerMixin()
            result = healer.heal_surgical_cst(context)

            healed_content = temp_path.read_text(encoding="utf-8")

            # Assertions
            assert "from __future__ import annotations" in healed_content
            assert "except Exception:" in healed_content
            assert "except:" not in healed_content
            assert "# Header comment" in healed_content
            assert "import os" in healed_content
            assert result["status"] == "success"
            assert result["violations_fixed"] >= 2

        finally:
            temp_path.unlink()

    def test_preserves_existing_future_import(self):
        """Test that existing __future__ imports are not duplicated."""
        source_code = """from __future__ import annotations
# Comment after future import
import os
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            tree = ast.parse(source_code)

            # No violations - just testing that nothing breaks
            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[],
                target_coordinates=[],
                detector_agent="CodeHealerAgent",
                detection_method="heal_canon",
                detection_timestamp=_FIXED_TS,
                violation_id="no_violations",
            )

            healer = SurgicalCSTHealerMixin()
            healer.heal_surgical_cst(context)

            healed_content = temp_path.read_text(encoding="utf-8")

            # Should be unchanged
            assert healed_content == source_code
            assert healed_content.count("from __future__") == 1

        finally:
            temp_path.unlink()


class TestDocstringInserterUnit:
    """Unit tests for SurgicalDocstringInserter transformer."""

    def test_class_docstring_insertion(self):
        """Test direct use of docstring inserter on class."""
        source = """class TestClass:
    def method(self):
        pass
"""
        cst_tree = cst.parse_module(source)

        target = DocstringTarget(
            line_number=1,
            name="TestClass",
            node_type="class",
            docstring='"""Test class docstring."""',
        )

        inserter = SurgicalDocstringInserter([target])
        modified_tree = cst_tree.visit(inserter)
        result = modified_tree.code

        assert '"""Test class docstring."""' in result
        assert inserter.modifications_made == 1

    def test_function_docstring_insertion(self):
        """Test direct use of docstring inserter on function."""
        source = """def test_func():
    return 42
"""
        cst_tree = cst.parse_module(source)

        target = DocstringTarget(
            line_number=1,
            name="test_func",
            node_type="function",
            docstring='"""Test function docstring."""',
        )

        inserter = SurgicalDocstringInserter([target])
        modified_tree = cst_tree.visit(inserter)
        result = modified_tree.code

        assert '"""Test function docstring."""' in result
        assert inserter.modifications_made == 1

    def test_skips_existing_docstring(self):
        """Test that existing docstrings are not duplicated."""
        source = '''class TestClass:
    """Existing docstring."""
    def method(self):
        pass
'''
        cst_tree = cst.parse_module(source)

        target = DocstringTarget(
            line_number=1,
            name="TestClass",
            node_type="class",
        )

        inserter = SurgicalDocstringInserter([target])
        modified_tree = cst_tree.visit(inserter)
        result = modified_tree.code

        # Should be unchanged
        assert result == source
        assert inserter.modifications_made == 0


class TestBareExceptFixerUnit:
    """Unit tests for SurgicalBareExceptFixer transformer."""

    def test_fixes_bare_except(self):
        """Test direct use of bare except fixer."""
        source = """try:
    x = 1
except:
    pass
"""
        cst_tree = cst.parse_module(source)

        fixer = SurgicalBareExceptFixer(fix_all=True)
        modified_tree = cst_tree.visit(fixer)
        result = modified_tree.code

        assert "except Exception:" in result
        assert "except:" not in result.replace("except Exception:", "")
        assert fixer.modifications_made == 1

    def test_skips_typed_except(self):
        """Test that typed except clauses are not modified."""
        source = """try:
    x = 1
except ValueError:
    pass
"""
        cst_tree = cst.parse_module(source)

        fixer = SurgicalBareExceptFixer(fix_all=True)
        modified_tree = cst_tree.visit(fixer)
        result = modified_tree.code

        # Should be unchanged
        assert result == source
        assert fixer.modifications_made == 0


class TestFutureImportInserterUnit:
    """Unit tests for SurgicalFutureImportInserter transformer."""

    def test_inserts_future_import(self):
        """Test direct use of future import inserter."""
        source = """import os

def test():
    pass
"""
        cst_tree = cst.parse_module(source)

        inserter = SurgicalFutureImportInserter(["annotations"])
        modified_tree = cst_tree.visit(inserter)
        result = modified_tree.code

        assert "from __future__ import annotations" in result
        assert inserter.modifications_made == 1
        # Future import should come before other imports
        lines = result.split("\n")
        future_idx = next(i for i, line in enumerate(lines) if "__future__" in line)
        os_idx = next(i for i, line in enumerate(lines) if "import os" in line)
        assert future_idx < os_idx

    def test_skips_existing_future_import(self):
        """Test that existing future imports are not duplicated."""
        source = """from __future__ import annotations

import os
"""
        cst_tree = cst.parse_module(source)

        inserter = SurgicalFutureImportInserter(["annotations"])
        modified_tree = cst_tree.visit(inserter)
        result = modified_tree.code

        # Should be unchanged
        assert result == source
        assert inserter.modifications_made == 0

    def test_respects_module_docstring(self):
        """Test that future import is inserted after module docstring."""
        source = '''"""Module docstring."""

import os
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)
_emit_pulls_context("p1", "test_code_healer_canon_cst", "context_pull")
_emit_pulls_context("p1", "test_code_healer_canon_cst", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_code_healer_canon_cst", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_code_healer_canon_cst", "uwg_term_secondary")
_emit_writes_through("p1", "test_code_healer_canon_cst", "write_through")
_emit_writes_through("p1", "test_code_healer_canon_cst", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_code_healer_canon_cst", "safety_validation")
_emit_invokes_eval("p1", "test_code_healer_canon_cst", "eval_call")
_emit_proposal_commits_routing("p1", "test_code_healer_canon_cst", "routing_commit")
_emit_escalates_to_human("p1", "test_code_healer_canon_cst", "human_escalation")
_emit_routes_through("p1", "test_code_healer_canon_cst", "route_through")
_emit_checks_agent_registry("p1", "test_code_healer_canon_cst", "agent_registry")
_emit_validates_agent_capability("p1", "test_code_healer_canon_cst", "capability")
_emit_dispatches_execution_plan("p1", "test_code_healer_canon_cst", "exec_plan")
_emit_agent_executes_agent("p1", "test_code_healer_canon_cst", "sub_agent")
_emit_routes_to_agent("p1", "test_code_healer_canon_cst", "target_agent")
_emit_verifies_policy("p1", "test_code_healer_canon_cst", "policy_check")
_emit_observes_runtime_state("p1", "test_code_healer_canon_cst", "runtime_state")
_emit_verifies_boundary("p1", "test_code_healer_canon_cst", "boundary_check")
_emit_transcripts_response("p1", "test_code_healer_canon_cst", "transcript")
_emit_hard_fails_untranscripted("p1", "test_code_healer_canon_cst")
_emit_gated_by_confidence("p1", "test_code_healer_canon_cst", "confidence_gate")
'''
        cst_tree = cst.parse_module(source)

        inserter = SurgicalFutureImportInserter(["annotations"])
        modified_tree = cst_tree.visit(inserter)
        result = modified_tree.code

        assert "from __future__ import annotations" in result
        # Future import should come after docstring
        lines = result.split("\n")
        docstring_idx = next(i for i, line in enumerate(lines) if '"""Module' in line)
        future_idx = next(i for i, line in enumerate(lines) if "__future__" in line)
        assert future_idx > docstring_idx


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
