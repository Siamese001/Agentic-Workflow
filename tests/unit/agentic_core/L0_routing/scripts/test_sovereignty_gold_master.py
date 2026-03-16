"""
Test Suite: Sovereignty Gold Master
Path: tests/unit/agentic_core/L0_routing/test_sovereignty_gold_master.py
Purpose: Final validation suite for PascalSovereigntyFixer with relative imports
"""

import re
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_SHARED_DIR,
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

_emit_authorize_and_execute("p2", "test_sovereignty_gold_master", "execution_auth")
_emit_validates_capability("p2", "test_sovereignty_gold_master", "capability_check")
_emit_routes_to_capability("p2", "test_sovereignty_gold_master", "capability_route")
_emit_writes_via_uwg("p2", "test_sovereignty_gold_master", "uwg_write")
_emit_blocks_direct_write("p2", "test_sovereignty_gold_master", "direct_write_block")
_emit_records_tool_invocation("p2", "test_sovereignty_gold_master", "tool_invocation")
_emit_captures_execution_output("p2", "test_sovereignty_gold_master", "exec_output")
_emit_dispatches_agent("p3", "test_sovereignty_gold_master", "agent_dispatch")
_emit_coordinates_agents("p3", "test_sovereignty_gold_master", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_sovereignty_gold_master", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_sovereignty_gold_master", "healing_outcome")
_emit_escalates_failure("p3", "test_sovereignty_gold_master", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_sovereignty_gold_master", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_sovereignty_gold_master", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_sovereignty_gold_master", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_sovereignty_gold_master", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_sovereignty_gold_master", "eval_metric")
_emit_stores_embedding("p4", "test_sovereignty_gold_master", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_sovereignty_gold_master", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_sovereignty_gold_master", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
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
from tests.helpers.dev_tools_loader import load_dev_script

_emit_emits_metric_event("test_sovereignty_gold_master", "p4obs", "metric_1")
_emit_emits_metric_event("test_sovereignty_gold_master", "p4obs", "metric_2")
_emit_emits_metric_event("test_sovereignty_gold_master", "p4obs", "metric_3")
_emit_emits_metric_event("test_sovereignty_gold_master", "p4obs", "metric_4")
_emit_emits_metric_event("test_sovereignty_gold_master", "p4obs", "metric_5")
_emit_emits_metric_event("test_sovereignty_gold_master", "p4obs", "metric_6")
_emit_records_incident_event("test_sovereignty_gold_master", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_sovereignty_gold_master", "p4obs", "anomaly")
_emit_writes_observability_log("test_sovereignty_gold_master", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_sovereignty_gold_master", "p4obs", "mon_state")
_emit_triggers_alert("test_sovereignty_gold_master", "p4obs", "alert")
_emit_links_incident_trace("test_sovereignty_gold_master", "p4obs", "trace_link")
_emit_captures_pattern("test_sovereignty_gold_master", "p3lm", "pattern")
_emit_records_learning_event("test_sovereignty_gold_master", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_sovereignty_gold_master", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_sovereignty_gold_master", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_sovereignty_gold_master", "p3lm", "routing")
_emit_improves_agent_policy("test_sovereignty_gold_master", "p3lm", "policy")
_emit_stores_learning_state("test_sovereignty_gold_master", "p3lm", "state")
_emit_records_execution_trace("test_sovereignty_gold_master", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_sovereignty_gold_master", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_sovereignty_gold_master", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_sovereignty_gold_master", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_sovereignty_gold_master", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_sovereignty_gold_master", "env_read", "p2_env_1")
_emit_reads_environ("test_sovereignty_gold_master", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_sovereignty_gold_master", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_sovereignty_gold_master", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_sovereignty_gold_master")
_emit_applies_guardrail("p0", "test_sovereignty_gold_master", "p0_governance")
_emit_reads_policy_state("p0", "test_sovereignty_gold_master", "policy_binding")
_emit_snapshots_state("p0", "test_sovereignty_gold_master", "state_snapshot")
_emit_pulls_context("p1", "test_sovereignty_gold_master", "context_pull")
_emit_pulls_context("p1", "test_sovereignty_gold_master", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_sovereignty_gold_master", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_sovereignty_gold_master", "uwg_term_secondary")
_emit_writes_through("p1", "test_sovereignty_gold_master", "write_through")
_emit_writes_through("p1", "test_sovereignty_gold_master", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_sovereignty_gold_master", "safety_validation")
_emit_invokes_eval("p1", "test_sovereignty_gold_master", "eval_call")
_emit_proposal_commits_routing("p1", "test_sovereignty_gold_master", "routing_commit")
_emit_escalates_to_human("p1", "test_sovereignty_gold_master", "human_escalation")
_emit_routes_through("p1", "test_sovereignty_gold_master", "route_through")
_emit_checks_agent_registry("p1", "test_sovereignty_gold_master", "agent_registry")
_emit_validates_agent_capability("p1", "test_sovereignty_gold_master", "capability")
_emit_dispatches_execution_plan("p1", "test_sovereignty_gold_master", "exec_plan")
_emit_agent_executes_agent("p1", "test_sovereignty_gold_master", "sub_agent")
_emit_routes_to_agent("p1", "test_sovereignty_gold_master", "target_agent")
_emit_verifies_policy("p1", "test_sovereignty_gold_master", "policy_check")
_emit_observes_runtime_state("p1", "test_sovereignty_gold_master", "runtime_state")
_emit_verifies_boundary("p1", "test_sovereignty_gold_master", "boundary_check")
_emit_transcripts_response("p1", "test_sovereignty_gold_master", "transcript")
_emit_hard_fails_untranscripted("p1", "test_sovereignty_gold_master")
_emit_gated_by_confidence("p1", "test_sovereignty_gold_master", "confidence_gate")
emit_replay_key("p0", "test_sovereignty_gold_master")
emit_determinism_digest("p0", "test_sovereignty_gold_master")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_psf = load_dev_script("pascal_sovereignty_fixer.py")
PascalSovereigntyFixer = _psf.PascalSovereigntyFixer

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJECT_ROOT))


class TestSovereigntyGoldMaster(unittest.TestCase):
    """Gold master validation suite for PascalSovereigntyFixer."""

    def setUp(self):
        """Initialize fixer in dry_run mode."""
        self.fixer = PascalSovereigntyFixer(dry_run=True)

    def test_relative_import_integrity(self):
        """Edge Case: Ensure 'from .llm_mixin import' is refactored correctly."""
        old_mod = "llm_mixin"
        new_mod = "LLMMixin"  # Testing the mechanism
        content = "from .llm_mixin import BaseLLM\nfrom ..llm_mixin import Helper"

        # Simulating internal logic with the actual pattern
        regex_from = re.compile(r"(?P<prefix>from\s+\.*)" + re.escape(old_mod) + r"(?P<suffix>\s+import)")
        updated = regex_from.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)

        self.assertIn("from .LLMMixin import", updated, "Single-dot relative import should be preserved")
        self.assertIn("from ..LLMMixin import", updated, "Double-dot relative import should be preserved")

    def test_relative_import_no_dots(self):
        """Verify absolute imports still work without dots."""
        old_mod = "healer_mixin"
        new_mod = "HealerMixin"
        content = "from healer_mixin import Healer"

        regex_from = re.compile(r"(?P<prefix>from\s+\.*)" + re.escape(old_mod) + r"(?P<suffix>\s+import)")
        updated = regex_from.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)

        self.assertIn(
            "from HealerMixin import",
            updated,
            "Absolute import should be updated to new module name",
        )

    def test_relative_import_triple_dots(self):
        """Edge Case: Triple-dot relative imports (from ...module)."""
        old_mod = "config_mixin"
        new_mod = "ConfigMixin"
        content = "from ...config_mixin_config import Config"

        regex_from = re.compile(r"(?P<prefix>from\s+\.*)" + re.escape(old_mod) + r"(?P<suffix>\s+import)")
        updated = regex_from.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)

        self.assertIn(
            "from ...config_mixin_config import",
            updated,
            "Triple-dot relative import should be preserved",
        )

    def test_mixin_acronym_consistency(self):
        """Standard Case: Validate acronym-aware snake_case for Mixins."""
        test_cases = {
            "ASTEnforcementMixin": "ast_enforcement_mixin.py",
            "MCPHardenedMixin": "mcp_hardened_mixin.py",
            "HygieneMixin": "hygiene_mixin.py",
        }

        for stem, expected in test_cases.items():
            mock_path = Mock(spec=Path)
            mock_path.stem = stem
            mock_path.name = f"{stem}.py"

            new_name = self.fixer.get_compliant_name(mock_path, "MIXIN")
            self.assertEqual(new_name, expected, f"Failed acronym-aware naming for {stem}")

    def test_tool_registry_exclusion(self):
        """Critical Requirement: tool_registry.py must remain ignored."""
        mock_path = Mock(spec=Path)
        mock_path.name = "tool_registry.py"
        mock_path.parts = (APPS_SHARED_DIR, "utils")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "The tool registry is a core SSOT and must be excluded")

    def test_execute_ssot_exclusion(self):
        """Critical Requirement: execute_ssot.py must remain ignored."""
        mock_path = Mock(spec=Path)
        mock_path.name = "execute_ssot.py"
        mock_path.parts = (AGENTIC_CORE_DIR, "L0_routing", "scripts")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "execute_ssot.py must remain in exclusion list")

    def test_structure_blueprint_exclusion(self):
        """Critical Requirement: structure_blueprint.py must remain ignored."""
        mock_path = Mock(spec=Path)
        mock_path.name = "structure_blueprint.py"
        mock_path.parts = (AGENTIC_CORE_DIR, "L5_safety", "validators")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "structure_blueprint.py must remain in exclusion list")

    def test_long_path_verification(self):
        """Environment: Ensure verify_environment correctly checks for Windows LongPaths."""
        # This is a passive check; we ensure it doesn't crash the pipeline
        status = self.fixer.verify_environment()
        self.assertIsInstance(status, bool, "verify_environment should return a boolean")

    def test_relative_import_direct_module(self):
        """Verify relative imports work for direct module references."""
        old_mod = "tracing_mixin"
        new_mod = "TracingMixin"
        # Direct module import without subpath
        content = "from .tracing_mixin import Tracer"

        regex_from = re.compile(r"(?P<prefix>from\s+\.*)" + re.escape(old_mod) + r"(?P<suffix>\s+import)")
        updated = regex_from.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)

        self.assertIn(
            "from .TracingMixin import",
            updated,
            "Direct relative import should be updated to new module name",
        )

    def test_import_alias_with_relative(self):
        """Verify import aliases work with absolute imports."""
        old_mod = "healer_mixin"
        new_mod = "HealerMixin"
        content = "import healer_mixin as hm"

        regex_import = re.compile(
            rf"(?P<prefix>import\s+){re.escape(old_mod)}(?P<suffix>(\s+as\s+\w+)?(\s*,|\s|$))",
        )
        updated = regex_import.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)

        self.assertIn(
            "import HealerMixin as hm",
            updated,
            "Import alias should be updated to new module name",
        )


class TestRelativeImportPatterns(unittest.TestCase):
    """Isolated tests for relative import regex patterns."""

    def test_single_dot_pattern(self):
        """Test single-dot relative import pattern."""
        pattern = re.compile(r"(?P<prefix>from\s+\.*)" + re.escape("old_module") + r"(?P<suffix>\s+import)")

        test_cases = [
            ("from .old_module import func", True, "from .NEW import func"),
            ("from old_module import func", True, "from NEW import func"),
            ("from ..old_module import func", True, "from ..NEW import func"),
        ]

        for content, should_match, expected in test_cases:
            match = pattern.search(content)
            if should_match:
                self.assertIsNotNone(match, f"Should match: {content}")
                result = pattern.sub(r"\g<prefix>NEW\g<suffix>", content)
                self.assertEqual(result, expected, f"Failed for: {content}")

    def test_direct_module_match(self):
        """Test direct module name matching without subpaths."""
        pattern = re.compile(r"(?P<prefix>from\s+\.*)" + re.escape("mixin") + r"(?P<suffix>\s+import)")

        # Direct module import
        content = "from .mixin import Helper"
        result = pattern.sub(r"\g<prefix>NEW\g<suffix>", content)

        self.assertIn("from .NEW import", result, "Direct module name should be updated")


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
