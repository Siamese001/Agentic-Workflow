"""
Unit Tests for CodeValidatorAgent Facade - Phase 2

Tests the facade conversion of CodeValidatorAgent including:
- Legacy signature compatibility
- CodeValidatorStrategy functionality
- Validation preservation
- Return type consistency
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from agentic_core.L3_orchestration.reasoning.UnifiedAgent import (
    CodeValidatorStrategy,
    ValidationResult,
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_code_validator_facade")
# REMOVED: _emit_applies_guardrail("p0", "test_code_validator_facade", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_code_validator_facade", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_code_validator_facade", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_code_validator_facade", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_code_validator_facade", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_code_validator_facade", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_code_validator_facade", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_code_validator_facade", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_code_validator_facade", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_code_validator_facade", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_code_validator_facade", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_code_validator_facade", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_code_validator_facade", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_code_validator_facade", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_code_validator_facade", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_code_validator_facade", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_code_validator_facade", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_code_validator_facade", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_code_validator_facade", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_code_validator_facade", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_code_validator_facade", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_code_validator_facade", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_code_validator_facade", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_code_validator_facade", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_code_validator_facade", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_code_validator_facade", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_code_validator_facade", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_code_validator_facade", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_code_validator_facade", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_code_validator_facade", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_code_validator_facade", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_code_validator_facade", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_code_validator_facade", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_code_validator_facade", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_code_validator_facade", "write_through")
# REMOVED: _emit_writes_through("p1", "test_code_validator_facade", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_code_validator_facade", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_code_validator_facade", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_code_validator_facade", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_code_validator_facade", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_code_validator_facade", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_code_validator_facade", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_code_validator_facade", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_code_validator_facade", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_code_validator_facade", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_code_validator_facade", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_code_validator_facade", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_code_validator_facade", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_code_validator_facade", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_code_validator_facade", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_code_validator_facade")
# REMOVED: _emit_gated_by_confidence("p1", "test_code_validator_facade", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_code_validator_facade")
# REMOVED: emit_determinism_digest("p0", "test_code_validator_facade")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_code_validator_facade", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_code_validator_facade", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_code_validator_facade", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_code_validator_facade", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_code_validator_facade", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_code_validator_facade", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_code_validator_facade", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_code_validator_facade", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_code_validator_facade", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_code_validator_facade", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_code_validator_facade", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_code_validator_facade", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_code_validator_facade", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_code_validator_facade", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_code_validator_facade", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_code_validator_facade", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_code_validator_facade", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_code_validator_facade", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_code_validator_facade", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_code_validator_facade", "exec_snapshot_link")


class TestCodeValidatorStrategy:
    """Tests for CodeValidatorStrategy."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "check_syntax": True,
            "check_canon": True,
            "check_async": True,
            "check_prints": True,
            "print_policy": "warn",
        }

    @pytest.fixture
    def strategy(self, config):
        """Create CodeValidatorStrategy instance."""
        return CodeValidatorStrategy(config)

    def test_initialization(self, strategy, config):
        """Test strategy initialization."""
        assert strategy.check_syntax is True
        assert strategy.check_canon is True
        assert strategy.check_async is True
        assert strategy.check_prints is True
        assert strategy.print_policy == "warn"

    def test_initialization_with_disabled_features(self):
        """Test strategy initialization with disabled features."""
        config = {
            "check_syntax": False,
            "check_canon": True,
            "check_async": False,
            "check_prints": True,
            "print_policy": "error",
        }
        strategy = CodeValidatorStrategy(config)

        assert strategy.check_syntax is False
        assert strategy.check_canon is True
        assert strategy.check_async is False
        assert strategy.check_prints is True
        assert strategy.print_policy == "error"

    @pytest.mark.asyncio
    async def test_execute_returns_validation_result(self, strategy):
        """Test execute returns ValidationResult."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()

        result = await strategy.execute(mock_agent)

        assert isinstance(result, ValidationResult)
        assert result.passed is True  # No file_path provided, no violations

    @pytest.mark.asyncio
    async def test_execute_with_file_path(self, strategy):
        """Test execute with file_path parameter."""
        mock_agent = Mock()
        mock_agent.log_info = Mock()
        mock_agent.validate_file = Mock(return_value=[])

        result = await strategy.execute(mock_agent, file_path="/test/file.py")

        assert isinstance(result, ValidationResult)
        assert result.passed is True


class TestCodeValidatorAgentFacade:
    """Tests for CodeValidatorAgent facade."""

    @pytest.fixture
    def agent(self):
        """Create CodeValidatorAgent instance."""
        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (
                CodeValidatorAgent,
            )

            return CodeValidatorAgent()

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.ruleset is not None
        assert agent._validation_results == []

    def test_unified_strategy_initialized(self, agent):
        """Test unified strategy is initialized."""
        assert agent._unified_strategy is not None
        assert isinstance(agent._unified_strategy, CodeValidatorStrategy)

    def test_validate_syntax_method_exists(self, agent):
        """Test validate_syntax method exists."""
        assert hasattr(agent, "validate_syntax")
        assert callable(agent.validate_syntax)

    def test_validate_canon_method_exists(self, agent):
        """Test validate_canon method exists."""
        assert hasattr(agent, "validate_canon")
        assert callable(agent.validate_canon)

    def test_validate_async_method_exists(self, agent):
        """Test validate_async method exists."""
        assert hasattr(agent, "validate_async")
        assert callable(agent.validate_async)

    def test_validate_prints_method_exists(self, agent):
        """Test validate_prints method exists."""
        assert hasattr(agent, "validate_prints")
        assert callable(agent.validate_prints)

    def test_validate_file_method_exists(self, agent):
        """Test validate_file method exists."""
        assert hasattr(agent, "validate_file")
        assert callable(agent.validate_file)

    def test_validate_directory_method_exists(self, agent):
        """Test validate_directory method exists."""
        assert hasattr(agent, "validate_directory")
        assert callable(agent.validate_directory)

    def test_validate_project_method_exists(self, agent):
        """Test validate_project method exists."""
        assert hasattr(agent, "validate_project")
        assert callable(agent.validate_project)

    def test_heal_repository_method_exists(self, agent):
        """Test heal_repository method exists."""
        assert hasattr(agent, "heal_repository")
        assert callable(agent.heal_repository)

    def test_heal_method_exists(self, agent):
        """Test heal method exists."""
        assert hasattr(agent, "heal")
        assert callable(agent.heal)


class TestValidationTypes:
    """Tests for validation type enums and dataclasses."""

    def test_violation_type_enum(self):
        """Test ViolationType enum exists."""
        from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (
            ViolationType,
        )

        assert hasattr(ViolationType, "SYNTAX")
        assert hasattr(ViolationType, "CANON")
        assert hasattr(ViolationType, "ASYNC")
        assert hasattr(ViolationType, "PRINT")

    def test_violation_dataclass(self):
        """Test Violation dataclass exists."""
        from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (
            Violation,
            ViolationType,
        )

        violation = Violation(
            violation_type=ViolationType.SYNTAX,
            file_path="/test/file.py",
            line_number=10,
            issue="Test issue",
        )

        assert violation.violation_type == ViolationType.SYNTAX
        assert violation.severity == "MEDIUM"
        assert violation.auto_fixable is False

    def test_ruleset_dataclass(self):
        """Test RuleSet dataclass exists."""
        from agentic_core.L5_safety.reasoning.CodeValidatorAgent import RuleSet

        ruleset = RuleSet()

        assert ruleset.check_syntax is True
        assert ruleset.check_canon is True
        assert ruleset.check_async is True
        assert ruleset.check_prints is True
        assert ruleset.print_policy == "warn"

    def test_validation_report_dataclass(self):
        """Test ValidationReport dataclass exists."""
        from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (
            ValidationReport,
        )

        report = ValidationReport(
            validation_summary={"total": 0},
            violations=[],
            total_violations=0,
            auto_fixable_count=0,
            high_severity_count=0,
        )

        assert report.total_violations == 0
        assert isinstance(report.to_dict(), dict)


class TestLegacyCompatibility:
    """Tests ensuring 100% legacy compatibility."""

    def test_import_compatibility(self):
        """Test original import still works."""
        from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (
            CodeValidatorAgent,
        )

        assert CodeValidatorAgent is not None

    def test_inherits_from_sovereign_base(self):
        """Test class still inherits from SovereignBaseAgent."""
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (
            CodeValidatorAgent,
        )

        assert issubclass(CodeValidatorAgent, SovereignBaseAgent)

    def test_factory_functions_exist(self):
        """Test factory functions exist."""
        from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (
            create_legacy_async_validator,
            create_legacy_canon_validator,
            create_legacy_print_validator,
            create_legacy_syntax_validator,
        )

        assert callable(create_legacy_syntax_validator)
        assert callable(create_legacy_canon_validator)
        assert callable(create_legacy_async_validator)
        assert callable(create_legacy_print_validator)

    def test_factory_syntax_validator(self):
        """Test create_legacy_syntax_validator creates correct config."""
        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (
                create_legacy_syntax_validator,
            )

            validator = create_legacy_syntax_validator()
            assert validator.ruleset.check_syntax is True
            assert validator.ruleset.check_canon is False

    def test_factory_canon_validator(self):
        """Test create_legacy_canon_validator creates correct config."""
        with patch("agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__init__"):
            from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (
                create_legacy_canon_validator,
            )

            validator = create_legacy_canon_validator()
            assert validator.ruleset.check_canon is True
            assert validator.ruleset.check_syntax is False

    def test_all_exports(self):
        """Test __all__ exports are correct."""
        from agentic_core.L5_safety.reasoning.CodeValidatorAgent import __all__

        expected = [
            "CodeValidatorAgent",
            "ViolationType",
            "Violation",
            "RuleSet",
            "ValidationReport",
            "create_legacy_syntax_validator",
            "create_legacy_canon_validator",
            "create_legacy_async_validator",
            "create_legacy_print_validator",
        ]
        for item in expected:
            assert item in __all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
