"""
Performance Tests for Zero-Loss Agent Consolidation - Phase 6

Comprehensive performance testing including:
- Strategy execution benchmarks
- Memory usage validation
- Concurrent execution tests
- Facade overhead measurement
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import Mock, patch

import pytest

from agentic_core.L3_orchestration.reasoning.UnifiedAgent import (
    STRATEGY_MAP,
    AgentCategory,
    GenericStrategy,
    HealingResult,
    HealingStrategy,
    OrchestrationResult,
    OrchestrationStrategy,
    UnifiedAgent,
    ValidationResult,
    ValidatorStrategy,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_unified_agent_performance", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_unified_agent_performance", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_unified_agent_performance", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_unified_agent_performance", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_unified_agent_performance", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_unified_agent_performance", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_unified_agent_performance", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_unified_agent_performance", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_unified_agent_performance", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_unified_agent_performance", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_unified_agent_performance", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_unified_agent_performance", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_unified_agent_performance", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_unified_agent_performance", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_unified_agent_performance", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_unified_agent_performance", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_unified_agent_performance", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_unified_agent_performance", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_unified_agent_performance", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_unified_agent_performance", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_unified_agent_performance", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_unified_agent_performance", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_unified_agent_performance", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_unified_agent_performance", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_unified_agent_performance", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_unified_agent_performance", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_unified_agent_performance", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_unified_agent_performance", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_unified_agent_performance")
# REMOVED: _emit_applies_guardrail("p0", "test_unified_agent_performance", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_unified_agent_performance", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_unified_agent_performance", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_unified_agent_performance", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_unified_agent_performance", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_unified_agent_performance", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_unified_agent_performance", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_unified_agent_performance", "write_through")
# REMOVED: _emit_writes_through("p1", "test_unified_agent_performance", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_unified_agent_performance", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_unified_agent_performance", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_unified_agent_performance", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_unified_agent_performance", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_unified_agent_performance", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_unified_agent_performance", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_unified_agent_performance", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_unified_agent_performance", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_unified_agent_performance", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_unified_agent_performance", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_unified_agent_performance", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_unified_agent_performance", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_unified_agent_performance", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_unified_agent_performance", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_unified_agent_performance")
# REMOVED: _emit_gated_by_confidence("p1", "test_unified_agent_performance", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_unified_agent_performance")
# REMOVED: emit_determinism_digest("p0", "test_unified_agent_performance")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_unified_agent_performance", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_unified_agent_performance", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_unified_agent_performance", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_unified_agent_performance", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_unified_agent_performance", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_unified_agent_performance", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_unified_agent_performance", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_unified_agent_performance", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_unified_agent_performance", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_unified_agent_performance", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_unified_agent_performance", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_unified_agent_performance", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_unified_agent_performance", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_unified_agent_performance", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_unified_agent_performance", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_unified_agent_performance", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_unified_agent_performance", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_unified_agent_performance", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_unified_agent_performance", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_unified_agent_performance", "exec_snapshot_link")


class TestStrategyPerformance:
    """Performance tests for strategy execution."""

    @pytest.fixture
    def validator_config(self):
        """Validator configuration."""
        return {
            "validation_rules": {"test": {}},
            "forbidden_content": ["bad"],
            "required_content": [],
            "thresholds": {"min_score": 0.3},
        }

    @pytest.fixture
    def orchestrator_config(self):
        """Orchestrator configuration."""
        return {
            "workflow_steps": [
                {"name": "step1", "type": "validation"},
                {"name": "step2", "type": "agent_call"},
            ],
            "signal_handlers": {},
        }

    @pytest.fixture
    def healer_config(self):
        """Healer configuration."""
        return {
            "healing_rules": {},
            "auto_fix": False,
            "dry_run_default": True,
        }

    @pytest.mark.asyncio
    async def test_validator_strategy_performance(self, validator_config):
        """Test validator strategy executes within acceptable time."""
        strategy = ValidatorStrategy(validator_config)

        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            agent._unified_config = validator_config
            agent.log_info = Mock()

            start = time.perf_counter()
            for _ in range(100):
                await strategy.execute(agent, data={"content": "test content"})
            elapsed = time.perf_counter() - start

            # Should complete 100 executions in under 1 second
            assert elapsed < 1.0, f"Validator too slow: {elapsed:.3f}s for 100 executions"

    @pytest.mark.asyncio
    async def test_orchestrator_strategy_performance(self, orchestrator_config):
        """Test orchestrator strategy executes within acceptable time."""
        strategy = OrchestrationStrategy(orchestrator_config)

        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.ORCHESTRATOR
            agent._unified_config = orchestrator_config
            agent.log_info = Mock()
            agent.log_error = Mock()

            start = time.perf_counter()
            for _ in range(100):
                await strategy.execute(agent)
            elapsed = time.perf_counter() - start

            # Should complete 100 executions in under 1 second
            assert elapsed < 1.0, f"Orchestrator too slow: {elapsed:.3f}s for 100 executions"

    @pytest.mark.asyncio
    async def test_healer_strategy_performance(self, healer_config):
        """Test healer strategy executes within acceptable time."""
        strategy = HealingStrategy(healer_config)

        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.HEALER
            agent._unified_config = healer_config
            agent.log_info = Mock()

            start = time.perf_counter()
            for _ in range(100):
                await strategy.execute(agent, dry_run=True)
            elapsed = time.perf_counter() - start

            # Should complete 100 executions in under 1 second
            assert elapsed < 1.0, f"Healer too slow: {elapsed:.3f}s for 100 executions"


class TestConcurrentExecution:
    """Tests for concurrent strategy execution."""

    @pytest.mark.asyncio
    async def test_concurrent_validator_execution(self):
        """Test multiple validators can run concurrently."""
        config = {
            "validation_rules": {},
            "forbidden_content": [],
            "required_content": [],
            "thresholds": {"min_score": 0.3},
        }

        async def run_validator():
            strategy = ValidatorStrategy(config)
            with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
                agent = UnifiedAgent()
                agent._category = AgentCategory.VALIDATOR
                agent._unified_config = config
                agent.log_info = Mock()
                return await strategy.execute(agent, data={"content": "test"})

        # Run 10 validators concurrently
        tasks = [run_validator() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert all(isinstance(r, ValidationResult) for r in results)

    @pytest.mark.asyncio
    async def test_mixed_strategy_concurrent_execution(self):
        """Test different strategies can run concurrently."""
        validator_config = {"validation_rules": {}, "forbidden_content": [], "thresholds": {}}
        orchestrator_config = {"workflow_steps": [], "signal_handlers": {}}
        healer_config = {"healing_rules": {}, "auto_fix": False}

        async def run_validator():
            strategy = ValidatorStrategy(validator_config)
            with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
                agent = UnifiedAgent()
                agent._category = AgentCategory.VALIDATOR
                agent._unified_config = validator_config
                agent.log_info = Mock()
                return await strategy.execute(agent, data={"content": "test"})

        async def run_orchestrator():
            strategy = OrchestrationStrategy(orchestrator_config)
            with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
                agent = UnifiedAgent()
                agent._category = AgentCategory.ORCHESTRATOR
                agent._unified_config = orchestrator_config
                agent.log_info = Mock()
                agent.log_error = Mock()
                return await strategy.execute(agent)

        async def run_healer():
            strategy = HealingStrategy(healer_config)
            with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
                agent = UnifiedAgent()
                agent._category = AgentCategory.HEALER
                agent._unified_config = healer_config
                agent.log_info = Mock()
                return await strategy.execute(agent, dry_run=True)

        # Run mixed strategies concurrently
        tasks = [run_validator(), run_orchestrator(), run_healer()]
        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert isinstance(results[0], ValidationResult)
        assert isinstance(results[1], OrchestrationResult)
        assert isinstance(results[2], HealingResult)


class TestStrategyMapIntegrity:
    """Tests for strategy map integrity."""

    def test_all_categories_mapped(self):
        """Test all agent categories have strategy mappings."""
        for category in AgentCategory:
            assert category in STRATEGY_MAP, f"Missing strategy for {category}"

    def test_strategy_types_correct(self):
        """Test strategy types are correct for categories."""
        assert STRATEGY_MAP[AgentCategory.VALIDATOR] == ValidatorStrategy
        assert STRATEGY_MAP[AgentCategory.ORCHESTRATOR] == OrchestrationStrategy
        assert STRATEGY_MAP[AgentCategory.HEALER] == HealingStrategy
        assert STRATEGY_MAP[AgentCategory.GENERIC] == GenericStrategy

    def test_analyzer_uses_validator_strategy(self):
        """Test analyzer category uses validator strategy."""
        assert STRATEGY_MAP[AgentCategory.ANALYZER] == ValidatorStrategy

    def test_governor_uses_validator_strategy(self):
        """Test governor category uses validator strategy."""
        assert STRATEGY_MAP[AgentCategory.GOVERNOR] == ValidatorStrategy


class TestResultTypeConsistency:
    """Tests for result type consistency."""

    def test_validation_result_to_dict(self):
        """Test ValidationResult serializes correctly."""
        result = ValidationResult(
            passed=True,
            issues=["issue1"],
            suggestions=["suggestion1"],
            score=0.85,
            metadata={"key": "value"},
        )

        d = result.to_dict()

        assert d["passed"] is True
        assert d["issues"] == ["issue1"]
        assert d["suggestions"] == ["suggestion1"]
        assert d["score"] == 0.85
        assert d["metadata"] == {"key": "value"}

    def test_orchestration_result_to_dict(self):
        """Test OrchestrationResult serializes correctly."""
        result = OrchestrationResult(
            completed=True,
            stage="final",
            signals=["signal1"],
            metadata={"key": "value"},
        )

        d = result.to_dict()

        assert d["completed"] is True
        assert d["stage"] == "final"
        assert d["signals"] == ["signal1"]
        assert d["metadata"] == {"key": "value"}

    def test_healing_result_to_dict(self):
        """Test HealingResult serializes correctly."""
        result = HealingResult(
            violations_found=5,
            violations_fixed=3,
            errors=["error1"],
            skipped=["skipped1"],
        )

        d = result.to_dict()

        assert d["violations_found"] == 5
        assert d["violations_fixed"] == 3
        assert d["errors"] == ["error1"]
        assert d["skipped"] == ["skipped1"]


class TestFacadeOverhead:
    """Tests measuring facade pattern overhead."""

    @pytest.mark.asyncio
    async def test_facade_overhead_acceptable(self):
        """Test facade pattern adds minimal overhead."""
        config = {"validation_rules": {}, "forbidden_content": [], "thresholds": {}}

        # Direct strategy execution
        strategy = ValidatorStrategy(config)
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            agent._unified_config = config
            agent.log_info = Mock()

            start = time.perf_counter()
            for _ in range(50):
                await strategy.execute(agent, data={"content": "test"})
            direct_time = time.perf_counter() - start

        # Facade execution (through UnifiedAgent.execute)
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            agent._unified_config = config
            agent._strategy = ValidatorStrategy(config)
            agent.log_info = Mock()

            start = time.perf_counter()
            for _ in range(50):
                await agent.execute(data={"content": "test"})
            facade_time = time.perf_counter() - start

        # Facade overhead should be less than 50%
        overhead = (facade_time - direct_time) / direct_time if direct_time > 0 else 0
        assert overhead < 0.5, f"Facade overhead too high: {overhead:.1%}"


class TestComprehensiveIntegration:
    """Comprehensive integration tests."""

    @pytest.mark.asyncio
    async def test_full_workflow_integration(self):
        """Test complete workflow through unified agent."""
        # Validator
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            validator = UnifiedAgent()
            validator._category = AgentCategory.VALIDATOR
            validator._unified_config = {"validation_rules": {}, "forbidden_content": []}
            validator._strategy = ValidatorStrategy(validator._unified_config)
            validator.log_info = Mock()

            v_result = await validator.execute(data={"content": "test"})
            assert isinstance(v_result, ValidationResult)

        # Orchestrator
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            orchestrator = UnifiedAgent()
            orchestrator._category = AgentCategory.ORCHESTRATOR
            orchestrator._unified_config = {"workflow_steps": [], "signal_handlers": {}}
            orchestrator._strategy = OrchestrationStrategy(orchestrator._unified_config)
            orchestrator.log_info = Mock()
            orchestrator.log_error = Mock()

            o_result = await orchestrator.execute()
            assert isinstance(o_result, OrchestrationResult)

        # Healer
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            healer = UnifiedAgent()
            healer._category = AgentCategory.HEALER
            healer._unified_config = {"healing_rules": {}, "auto_fix": False}
            healer._strategy = HealingStrategy(healer._unified_config)
            healer.log_info = Mock()

            h_result = await healer.execute(dry_run=True)
            assert isinstance(h_result, HealingResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
