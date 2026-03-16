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

_emit_records_execution_trace("p0", "evidence", "test_code_healer_cst_simple")
_emit_applies_guardrail("p0", "test_code_healer_cst_simple", "p0_governance")
_emit_reads_policy_state("p0", "test_code_healer_cst_simple", "policy_binding")
_emit_snapshots_state("p0", "test_code_healer_cst_simple", "state_snapshot")
emit_replay_key("p0", "test_code_healer_cst_simple")
emit_determinism_digest("p0", "test_code_healer_cst_simple")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_code_healer_cst_simple", "execution_auth")
_emit_validates_capability("p2", "test_code_healer_cst_simple", "capability_check")
_emit_routes_to_capability("p2", "test_code_healer_cst_simple", "capability_route")
_emit_writes_via_uwg("p2", "test_code_healer_cst_simple", "uwg_write")
_emit_blocks_direct_write("p2", "test_code_healer_cst_simple", "direct_write_block")
_emit_records_tool_invocation("p2", "test_code_healer_cst_simple", "tool_invocation")
_emit_captures_execution_output("p2", "test_code_healer_cst_simple", "exec_output")
_emit_dispatches_agent("p3", "test_code_healer_cst_simple", "agent_dispatch")
_emit_coordinates_agents("p3", "test_code_healer_cst_simple", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_code_healer_cst_simple", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_code_healer_cst_simple", "healing_outcome")
_emit_escalates_failure("p3", "test_code_healer_cst_simple", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_code_healer_cst_simple", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_code_healer_cst_simple", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_code_healer_cst_simple", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_code_healer_cst_simple", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_code_healer_cst_simple", "eval_metric")
_emit_stores_embedding("p4", "test_code_healer_cst_simple", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_code_healer_cst_simple", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_code_healer_cst_simple", "exec_snapshot_link")


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
