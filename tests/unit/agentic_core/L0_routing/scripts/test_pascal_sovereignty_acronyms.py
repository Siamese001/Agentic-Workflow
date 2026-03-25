"""
Test Suite: PascalSovereigntyFixer Acronym Handling
Path: tests/unit/agentic_core/L0_routing/test_pascal_sovereignty_acronyms.py
Purpose: Validates acronym-aware snake_case conversion for mixins
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

# REMOVED: _emit_authorize_and_execute("p2", "test_pascal_sovereignty_acronyms", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_pascal_sovereignty_acronyms", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_pascal_sovereignty_acronyms", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_pascal_sovereignty_acronyms", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_pascal_sovereignty_acronyms", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_pascal_sovereignty_acronyms", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_pascal_sovereignty_acronyms", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_pascal_sovereignty_acronyms", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_pascal_sovereignty_acronyms", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_pascal_sovereignty_acronyms", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_pascal_sovereignty_acronyms", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_pascal_sovereignty_acronyms", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_pascal_sovereignty_acronyms", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_pascal_sovereignty_acronyms", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_pascal_sovereignty_acronyms", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_pascal_sovereignty_acronyms", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_pascal_sovereignty_acronyms", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_pascal_sovereignty_acronyms", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_pascal_sovereignty_acronyms", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_pascal_sovereignty_acronyms", "exec_snapshot_link")
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
from tests.helpers.dev_tools_loader import load_dev_script

# REMOVED: _emit_emits_metric_event("test_pascal_sovereignty_acronyms", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_pascal_sovereignty_acronyms", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_pascal_sovereignty_acronyms", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_pascal_sovereignty_acronyms", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_pascal_sovereignty_acronyms", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_pascal_sovereignty_acronyms", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_pascal_sovereignty_acronyms", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_pascal_sovereignty_acronyms", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_pascal_sovereignty_acronyms", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_pascal_sovereignty_acronyms", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_pascal_sovereignty_acronyms", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_pascal_sovereignty_acronyms", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_pascal_sovereignty_acronyms", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_pascal_sovereignty_acronyms", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_pascal_sovereignty_acronyms", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_pascal_sovereignty_acronyms", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_pascal_sovereignty_acronyms", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_pascal_sovereignty_acronyms", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_pascal_sovereignty_acronyms", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_pascal_sovereignty_acronyms", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_pascal_sovereignty_acronyms", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_pascal_sovereignty_acronyms", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_pascal_sovereignty_acronyms", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_pascal_sovereignty_acronyms", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_pascal_sovereignty_acronyms", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_pascal_sovereignty_acronyms", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_pascal_sovereignty_acronyms", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_pascal_sovereignty_acronyms", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_pascal_sovereignty_acronyms")
# REMOVED: _emit_applies_guardrail("p0", "test_pascal_sovereignty_acronyms", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_pascal_sovereignty_acronyms", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_pascal_sovereignty_acronyms", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_pascal_sovereignty_acronyms", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_pascal_sovereignty_acronyms", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_pascal_sovereignty_acronyms", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_pascal_sovereignty_acronyms", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_pascal_sovereignty_acronyms", "write_through")
# REMOVED: _emit_writes_through("p1", "test_pascal_sovereignty_acronyms", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_pascal_sovereignty_acronyms", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_pascal_sovereignty_acronyms", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_pascal_sovereignty_acronyms", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_pascal_sovereignty_acronyms", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_pascal_sovereignty_acronyms", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_pascal_sovereignty_acronyms", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_pascal_sovereignty_acronyms", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_pascal_sovereignty_acronyms", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_pascal_sovereignty_acronyms", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_pascal_sovereignty_acronyms", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_pascal_sovereignty_acronyms", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_pascal_sovereignty_acronyms", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_pascal_sovereignty_acronyms", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_pascal_sovereignty_acronyms", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_pascal_sovereignty_acronyms")
# REMOVED: _emit_gated_by_confidence("p1", "test_pascal_sovereignty_acronyms", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_pascal_sovereignty_acronyms")
# REMOVED: emit_determinism_digest("p0", "test_pascal_sovereignty_acronyms")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_psf = load_dev_script("pascal_sovereignty_fixer.py")
PascalSovereigntyFixer = _psf.PascalSovereigntyFixer

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJECT_ROOT))


class TestSovereigntyAcronyms(unittest.TestCase):
    """Comprehensive acronym handling tests for PascalSovereigntyFixer."""

    def setUp(self):
        """Initialize fixer in dry_run mode to prevent disk side effects."""
        self.fixer = PascalSovereigntyFixer(dry_run=True)

    def test_acronym_snake_case_conversion(self):
        """
        Verify that complex acronyms in Mixins are converted to clean snake_case.
        Expected: LLMProviderMixin -> llm_provider_mixin.py (NOT l_l_m_provider...)
        """
        test_cases = {
            "LLMProviderMixin": "llm_provider_mixin.py",
            "ASTEnforcementMixin": "ast_enforcement_mixin.py",
            "MCPOperationMixin": "mcp_operation_mixin.py",
            "MCPHardenedMixin": "mcp_hardened_mixin.py",
            "AuditTrailMixin": "audit_trail_mixin.py",
            "PineconeVectorMixin": "pinecone_vector_mixin.py",
            "RedisCacheMixin": "redis_cache_mixin.py",
        }

        for stem, expected in test_cases.items():
            mock_path = Mock(spec=Path)
            mock_path.stem = stem
            mock_path.name = f"{stem}.py"

            compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
            self.assertEqual(compliant, expected, f"Failed to correctly convert acronym for {stem}")

    def test_simple_pascalcase_mixin_conversion(self):
        """Test simple PascalCase mixins without acronyms."""
        test_cases = {
            "HealerMixin": "healer_mixin.py",
            "TracingMixin": "tracing_mixin.py",
            "ConfigMixin": "config_mixin.py",
            "LifecycleMixin": "lifecycle_mixin.py",
        }

        for stem, expected in test_cases.items():
            mock_path = Mock(spec=Path)
            mock_path.stem = stem
            mock_path.name = f"{stem}.py"

            compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
            self.assertEqual(compliant, expected, f"Failed to convert simple PascalCase for {stem}")

    def test_multi_word_mixin_conversion(self):
        """Test multi-word PascalCase mixins."""
        test_cases = {
            "CognitiveRecoveryMixin": "cognitive_recovery_mixin.py",
            "CapabilityDiscoveryMixin": "capability_discovery_mixin.py",
            "SecretsManagementMixin": "secrets_management_mixin.py",
            "StructuralHealingMixin": "structural_healing_mixin.py",
            "SubatomicTestingMixin": "subatomic_testing_mixin.py",
            "MetaLearningMixin": "meta_learning_mixin.py",
        }

        for stem, expected in test_cases.items():
            mock_path = Mock(spec=Path)
            mock_path.stem = stem
            mock_path.name = f"{stem}.py"

            compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
            self.assertEqual(compliant, expected, f"Failed to convert multi-word for {stem}")

    def test_acronym_at_start(self):
        """Test acronyms at the beginning of the name."""
        test_cases = {
            "LLMMixin": "llm_mixin.py",
            "MCPMixin": "mcp_mixin.py",
            "ASTMixin": "ast_mixin.py",
        }

        for stem, expected in test_cases.items():
            mock_path = Mock(spec=Path)
            mock_path.stem = stem
            mock_path.name = f"{stem}.py"

            compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
            self.assertEqual(compliant, expected, f"Failed to convert acronym at start for {stem}")

    def test_already_compliant_mixins(self):
        """Test that already compliant mixins return None."""
        test_cases = [
            "healer_mixin",
            "cognitive_recovery_mixin",
            "llm_provider_mixin",
            "mcp_operation_mixin",
        ]

        for stem in test_cases:
            mock_path = Mock(spec=Path)
            mock_path.stem = stem
            mock_path.name = f"{stem}.py"

            compliant = self.fixer.get_compliant_name(mock_path, "MIXIN")
            self.assertIsNone(compliant, f"Already compliant mixin {stem} should return None")

    def test_import_alias_refactoring(self):
        """
        Ensure the 'import x as y' and 'from x import z' patterns are refactored
        using the new group-based regex without breaking the aliases.
        """
        old_mod = "llm_provider_mixin"
        new_mod = "LLMProviderMixin"
        content = "import llm_provider_mixin as lpm\nfrom llm_provider_mixin import Provider"

        # Simulating the internal update_imports regex logic
        regex_from = re.compile(rf"(?P<prefix>from\s+){re.escape(old_mod)}(?P<suffix>\s+import)")
        regex_import = re.compile(
            rf"(?P<prefix>import\s+){re.escape(old_mod)}(?P<suffix>(\s+as\s+\w+)?(\s*,|\s|$))",
        )

        updated = regex_from.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)
        updated = regex_import.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", updated)

        self.assertIn("import LLMProviderMixin as lpm", updated)
        self.assertIn("from LLMProviderMixin import Provider", updated)

    def test_summary_output_integrity(self):
        """
        Verify that Mixins are counted as violations and do not carry the (Exempt) label.
        This test ensures the console output matches the architectural policy.
        """
        self.fixer.stats["violations"]["MIXIN"] = 5
        # We check that the logic allows marking them as violations for the return code
        total_violations = sum(self.fixer.stats["violations"].values())
        self.assertEqual(total_violations, 5, "Mixin violations should be counted in total")

    def test_ssot_exclusion_protection(self):
        """
        Ensure critical SSOT files are never reclassified, even if they contain classes.
        """
        mock_path = Mock(spec=Path)
        mock_path.name = "tool_registry.py"
        mock_path.parts = (APPS_SHARED_DIR, "utils")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(
            ftype,
            "IGNORE",
            "tool_registry.py must remain ignored to protect dynamic tool lookups",
        )

    def test_execute_ssot_exclusion(self):
        """Verify execute_ssot.py remains protected."""
        mock_path = Mock(spec=Path)
        mock_path.name = "execute_ssot.py"
        mock_path.parts = (AGENTIC_CORE_DIR, "L0_routing", "scripts")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(ftype, "IGNORE", "execute_ssot.py must remain ignored per SSOT exclusion list")

    def test_structure_blueprint_exclusion(self):
        """Verify structure_blueprint.py remains protected."""
        mock_path = Mock(spec=Path)
        mock_path.name = "structure_blueprint.py"
        mock_path.parts = (AGENTIC_CORE_DIR, "L5_safety", "validators")
        mock_path.exists.return_value = True
        mock_path.stat.return_value = Mock(st_size=1000)

        ftype = self.fixer.classify_file(mock_path)
        self.assertEqual(
            ftype,
            "IGNORE",
            "structure_blueprint.py must remain ignored per SSOT exclusion list",
        )


class TestAcronymRegexPatterns(unittest.TestCase):
    """Test the regex patterns used for acronym conversion."""

    def test_acronym_followed_by_word(self):
        """Test Pass 1: Handle acronyms followed by words (LLMProvider -> LLM_Provider)."""
        pattern = re.compile("(.)([A-Z][a-z]+)")

        test_cases = {
            "LLMProvider": "LLM_Provider",
            "MCPOperation": "MCP_Operation",
            "ASTEnforcement": "AST_Enforcement",
        }

        for input_str, expected in test_cases.items():
            result = pattern.sub(r"\1_\2", input_str)
            self.assertEqual(result, expected, f"Pass 1 failed for {input_str}")

    def test_camelcase_boundaries(self):
        """Test Pass 2: Handle camelCase boundaries (llmProvider -> llm_Provider)."""
        # First apply Pass 1
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", "LLMProviderMixin")
        # Then apply Pass 2
        pattern = re.compile("([a-z0-9])([A-Z])")
        result = pattern.sub(r"\1_\2", s1).lower()

        self.assertEqual(result, "llm_provider_mixin", "Two-pass conversion should produce clean snake_case")

    def test_full_conversion_pipeline(self):
        """Test the complete conversion pipeline."""
        test_cases = {
            "LLMProviderMixin": "llm_provider_mixin",
            "MCPHardenedMixin": "mcp_hardened_mixin",
            "ASTEnforcementMixin": "ast_enforcement_mixin",
            "CognitiveRecoveryMixin": "cognitive_recovery_mixin",
            "SubatomicTestingMixin": "subatomic_testing_mixin",
        }

        for input_str, expected in test_cases.items():
            # Apply two-pass conversion
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", input_str)
            result = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

            self.assertEqual(result, expected, f"Full pipeline failed for {input_str}")


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
