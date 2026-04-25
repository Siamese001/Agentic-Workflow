"""Tests for execution_gateway.py module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.enforcement.execution_gateway import (
    ExecutionGatewayError,
    UnregisteredAgentError,
    GatewayResult,
    V15ExecutionGateway,
    MUTATION_COUNTER,
    CURRENT_PHASE,
)


class TestExecutionGatewayError:
    """Tests for ExecutionGatewayError exception."""

    def test_execution_gateway_error_message_only(self):
        """Test ExecutionGatewayError with message only."""
        error = ExecutionGatewayError("Test error")
        assert str(error) == "Test error"
        assert error.original_error is None

    def test_execution_gateway_error_with_original(self):
        """Test ExecutionGatewayError with original error."""
        original = ValueError("Original error")
        error = ExecutionGatewayError("Test error", original)
        assert str(error) == "Test error"
        assert error.original_error is original


class TestUnregisteredAgentError:
    """Tests for UnregisteredAgentError exception."""

    def test_unregistered_agent_error(self):
        """Test UnregisteredAgentError can be raised."""
        with pytest.raises(UnregisteredAgentError):
            raise UnregisteredAgentError("Agent not registered")


class TestGatewayResult:
    """Tests for GatewayResult dataclass."""

    def test_gateway_result_success(self):
        """Test GatewayResult with success=True."""
        manifest = MagicMock()
        result = GatewayResult(
            success=True,
            manifest=manifest,
            semantic_clock_tick=1,
            pre_snapshot=MagicMock(),
        )
        assert result.success is True
        assert result.manifest is manifest
        assert result.semantic_clock_tick == 1

    def test_gateway_result_failure(self):
        """Test GatewayResult with success=False."""
        result = GatewayResult(
            success=False,
            manifest=None,
            semantic_clock_tick=1,
            pre_snapshot=None,
            error="Test error",
        )
        assert result.success is False
        assert result.manifest is None
        assert result.error == "Test error"

    def test_gateway_result_default_fields(self):
        """Test GatewayResult default field values."""
        result = GatewayResult(
            success=True,
            manifest=None,
            semantic_clock_tick=1,
            pre_snapshot=None,
        )
        assert result.post_snapshot is None
        assert result.rollback_verified is False
        assert result.healing_output == {}
        assert result.error is None
        assert result.dedupe_hit is False
        assert result.registry_hash == ""


class TestV15ExecutionGateway:
    """Tests for V15ExecutionGateway class."""

    def test_gateway_init(self):
        """Test V15ExecutionGateway initialization."""
        gateway = V15ExecutionGateway()
        assert gateway.clock is not None
        assert gateway._seen_signals == set()
        assert gateway._pipe_violations == []
        assert gateway._policy_violations == []

    def test_gateway_clock_property(self):
        """Test clock property returns SemanticClock."""
        gateway = V15ExecutionGateway()
        clock = gateway.clock
        assert clock is not None

    def test_enforce_agent_registered_empty_agent_id(self):
        """Test _enforce_agent_registered raises for empty agent_id."""
        gateway = V15ExecutionGateway()
        with pytest.raises(UnregisteredAgentError, match="agent_id must be a non-empty string"):
            gateway._enforce_agent_registered("")

    def test_enforce_agent_registered_whitespace_agent_id(self):
        """Test _enforce_agent_registered raises for whitespace agent_id."""
        gateway = V15ExecutionGateway()
        with pytest.raises(UnregisteredAgentError, match="agent_id must be a non-empty string"):
            gateway._enforce_agent_registered("   ")

    def test_enforce_agent_registered_not_found(self):
        """Test _enforce_agent_registered raises for unregistered agent."""
        gateway = V15ExecutionGateway()
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.get_profile") as mock_get_profile:
            mock_get_profile.side_effect = KeyError("Not found")
            with pytest.raises(UnregisteredAgentError, match="not registered"):
                gateway._enforce_agent_registered("unknown_agent")

    def test_enforce_agent_registered_runtime_error(self):
        """Test _enforce_agent_registered raises ExecutionGatewayError on RuntimeError."""
        gateway = V15ExecutionGateway()
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.get_profile") as mock_get_profile:
            mock_get_profile.side_effect = RuntimeError("Registry error")
            with pytest.raises(ExecutionGatewayError, match="Agent registry lookup failed"):
                gateway._enforce_agent_registered("test_agent")

    def test_execute_soft_fail_abort(self):
        """Test execute returns failure result on V15SoftFailAbort."""
        gateway = V15ExecutionGateway()
        manifest = MagicMock()
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway._enforce_agent_registered"):
            with patch("agentic_core.L0_routing.enforcement.execution_gateway.V15SoftFailAbort") as mock_abort:
                mock_abort.side_effect = Exception("SOFT_FAIL")
                
                result = gateway.execute(
                    execution_input=manifest,
                    heal_fn=MagicMock(),
                    state_hash_fn=MagicMock(return_value=("fs", "git", "mem")),
                    agent_id="test_agent",
                )
                
                assert result.success is False
                assert "SOFT_FAIL" in result.error

    def test_execute_with_envelope_success(self):
        """Test _execute_with_envelope with successful execution."""
        gateway = V15ExecutionGateway()
        manifest = MagicMock()
        manifest.node_id = "node1"
        manifest.correlation_id = "corr1"
        manifest.target_layer = "L0_routing"
        manifest.policy_hash = None
        manifest.routing_hash = None
        manifest.model_hash = None
        manifest.budget_hash = None
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.validate_execution_input") as mock_validate:
            mock_validate.return_value = manifest
            with patch("agentic_core.L0_routing.enforcement.execution_gateway.validate_manifest_emission"):
                with patch("agentic_core.L0_routing.enforcement.execution_gateway.dedupe_sha256") as mock_dedupe:
                    mock_dedupe.return_value = "hash1"
                    with patch("agentic_core.L0_routing.enforcement.execution_gateway._get_manifest_hash_validator"):
                        with patch("agentic_core.L0_routing.enforcement.execution_gateway._get_guardian_decision") as mock_guardian:
                            mock_guardian.return_value = (MagicMock(), MagicMock())
                            with patch("agentic_core.L0_routing.enforcement.execution_gateway.PolicyConfigGuard"):
                                with patch("agentic_core.L0_routing.enforcement.execution_gateway.GuardrailGuard"):
                                    guardrail = MagicMock()
                                    guardrail.enforce_all.return_value = True
                                    with patch("agentic_core.L0_routing.enforcement.execution_gateway.create_boundary_snapshot") as mock_snapshot:
                                        mock_snapshot.return_value = MagicMock()
                                        with patch("agentic_core.L0_routing.enforcement.execution_gateway.TokenCapArtifact"):
                                            with patch("agentic_core.L0_routing.enforcement.execution_gateway.TokenGateResult"):
                                                with patch("agentic_core.L0_routing.enforcement.execution_gateway.get_clock") as mock_get_clock:
                                                    clk = MagicMock()
                                                    mock_get_clock.return_value = clk
                                                    with patch("agentic_core.L0_routing.enforcement.execution_gateway.get_routing_gateway"):
                                                        heal_fn = MagicMock(return_value={"errors": 0})
                                                        state_hash_fn = MagicMock(return_value=("fs", "git", "mem"))
                                                        
                                                        result = gateway._execute_with_envelope(
                                                            execution_input=manifest,
                                                            heal_fn=heal_fn,
                                                            state_hash_fn=state_hash_fn,
                                                            trace_id="trace-123",
                                                        )
                                                        
                                                        assert result.success is True

    def test_commit_mutation_success(self):
        """Test _commit_mutation with successful healing."""
        gateway = V15ExecutionGateway()
        manifest = MagicMock()
        manifest.target_layer = "L0_routing"
        manifest.correlation_id = "corr1"
        manifest.node_id = "node1"
        
        heal_fn = MagicMock(return_value={"errors": 0})
        state_hash_fn = MagicMock(return_value=("fs", "git", "mem"))
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.create_boundary_snapshot") as mock_snapshot:
            mock_snapshot.return_value = MagicMock()
            with patch("agentic_core.L0_routing.enforcement.execution_gateway.verify_rollback_integrity"):
                with patch("agentic_core.L0_routing.enforcement.execution_gateway.dedupe_sha256"):
                    with patch("agentic_core.L0_routing.enforcement.execution_gateway.validate_execution_input") as mock_validate:
                        mock_validate.return_value = manifest
                        with patch("agentic_core.L0_routing.enforcement.execution_gateway.validate_manifest_emission"):
                            with patch("agentic_core.L0_routing.enforcement.execution_gateway._get_manifest_hash_validator"):
                                with patch("agentic_core.L0_routing.enforcement.execution_gateway._get_guardian_decision") as mock_guardian:
                                    mock_guardian.return_value = (MagicMock(), MagicMock())
                                    with patch("agentic_core.L0_routing.enforcement.execution_gateway.PolicyConfigGuard"):
                                        with patch("agentic_core.L0_routing.enforcement.execution_gateway.GuardrailGuard"):
                                            guardrail = MagicMock()
                                            guardrail.enforce_all.return_value = True
                                            with patch("agentic_core.L0_routing.enforcement.execution_gateway.TokenCapArtifact"):
                                                with patch("agentic_core.L0_routing.enforcement.execution_gateway.TokenGateResult"):
                                                    with patch("agentic_core.L0_routing.enforcement.execution_gateway.get_clock") as mock_get_clock:
                                                        clk = MagicMock()
                                                        mock_get_clock.return_value = clk
                                                        with patch("agentic_core.L0_routing.enforcement.execution_gateway.get_routing_gateway"):
                                                            result = gateway._commit_mutation(
                                                                manifest=manifest,
                                                                heal_fn=heal_fn,
                                                                state_hash_fn=state_hash_fn,
                                                                trace_id="trace-123",
                                                            )
                                                            
                                                            assert result.success is True

    def test_commit_mutation_healing_error_known(self):
        """Test _commit_mutation handles known healing errors gracefully."""
        gateway = V15ExecutionGateway()
        manifest = MagicMock()
        manifest.target_layer = "L0_routing"
        manifest.correlation_id = "corr1"
        manifest.node_id = "node1"
        
        heal_fn = MagicMock(side_effect=ValueError("Healing error"))
        state_hash_fn = MagicMock(return_value=("fs", "git", "mem"))
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.create_boundary_snapshot") as mock_snapshot:
            mock_snapshot.return_value = MagicMock()
            with patch("agentic_core.L0_routing.enforcement.execution_gateway.verify_rollback_integrity"):
                with patch("agentic_core.L0_routing.enforcement.execution_gateway.dedupe_sha256"):
                    with patch("agentic_core.L0_routing.enforcement.execution_gateway.validate_execution_input") as mock_validate:
                        mock_validate.return_value = manifest
                        with patch("agentic_core.L0_routing.enforcement.execution_gateway.validate_manifest_emission"):
                            with patch("agentic_core.L0_routing.enforcement.execution_gateway._get_manifest_hash_validator"):
                                with patch("agentic_core.L0_routing.enforcement.execution_gateway._get_guardian_decision") as mock_guardian:
                                    mock_guardian.return_value = (MagicMock(), MagicMock())
                                    with patch("agentic_core.L0_routing.enforcement.execution_gateway.PolicyConfigGuard"):
                                        with patch("agentic_core.L0_routing.enforcement.execution_gateway.GuardrailGuard"):
                                            guardrail = MagicMock()
                                            guardrail.enforce_all.return_value = True
                                            with patch("agentic_core.L0_routing.enforcement.execution_gateway.TokenCapArtifact"):
                                                with patch("agentic_core.L0_routing.enforcement.execution_gateway.TokenGateResult"):
                                                    with patch("agentic_core.L0_routing.enforcement.execution_gateway.get_clock") as mock_get_clock:
                                                        clk = MagicMock()
                                                        mock_get_clock.return_value = clk
                                                        with patch("agentic_core.L0_routing.enforcement.execution_gateway.get_routing_gateway"):
                                                            result = gateway._commit_mutation(
                                                                manifest=manifest,
                                                                heal_fn=heal_fn,
                                                                state_hash_fn=state_hash_fn,
                                                                trace_id="trace-123",
                                                            )
                                                            
                                                            assert result.success is False
                                                            assert "Healing error" in result.error

    def test_commit_mutation_healing_error_critical(self):
        """Test _commit_mutation raises ExecutionGatewayError on critical errors."""
        gateway = V15ExecutionGateway()
        manifest = MagicMock()
        manifest.target_layer = "L0_routing"
        manifest.correlation_id = "corr1"
        manifest.node_id = "node1"
        
        heal_fn = MagicMock(side_effect=OSError("Critical error"))
        state_hash_fn = MagicMock(return_value=("fs", "git", "mem"))
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.create_boundary_snapshot") as mock_snapshot:
            mock_snapshot.return_value = MagicMock()
            with pytest.raises(ExecutionGatewayError, match="Critical healing operation failed"):
                gateway._commit_mutation(
                    manifest=manifest,
                    heal_fn=heal_fn,
                    state_hash_fn=state_hash_fn,
                    trace_id="trace-123",
                )

    def test_heal_and_retry_success(self):
        """Test _heal_and_retry with successful retry."""
        gateway = V15ExecutionGateway()
        manifest = MagicMock()
        manifest.correlation_id = "corr1"
        manifest.node_id = "node1"
        manifest.target_layer = "L0_routing"
        manifest.policy_hash = None
        manifest.routing_hash = None
        manifest.model_hash = None
        manifest.budget_hash = None
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.validate_execution_input") as mock_validate:
            mock_validate.return_value = manifest
            with patch("agentic_core.L0_routing.enforcement.execution_gateway.validate_manifest_emission"):
                with patch("agentic_core.L0_routing.enforcement.execution_gateway.dedupe_sha256") as mock_dedupe:
                    mock_dedupe.return_value = "hash1"
                    with patch("agentic_core.L0_routing.enforcement.execution_gateway._get_manifest_hash_validator"):
                        with patch("agentic_core.L0_routing.enforcement.execution_gateway._get_guardian_decision") as mock_guardian:
                            mock_guardian.return_value = (MagicMock(), MagicMock())
                            with patch("agentic_core.L0_routing.enforcement.execution_gateway.PolicyConfigGuard"):
                                with patch("agentic_core.L0_routing.enforcement.execution_gateway.GuardrailGuard"):
                                    guardrail = MagicMock()
                                    guardrail.enforce_all.return_value = True
                                    with patch("agentic_core.L0_routing.enforcement.execution_gateway.create_boundary_snapshot") as mock_snapshot:
                                        mock_snapshot.return_value = MagicMock()
                                        with patch("agentic_core.L0_routing.enforcement.execution_gateway.TokenCapArtifact"):
                                            with patch("agentic_core.L0_routing.enforcement.execution_gateway.TokenGateResult"):
                                                with patch("agentic_core.L0_routing.enforcement.execution_gateway.get_clock") as mock_get_clock:
                                                    clk = MagicMock()
                                                    mock_get_clock.return_value = clk
                                                    with patch("agentic_core.L0_routing.enforcement.execution_gateway.get_routing_gateway"):
                                                        heal_fn = MagicMock(return_value={"errors": 0})
                                                        state_hash_fn = MagicMock(return_value=("fs", "git", "mem"))
                                                        
                                                        result = gateway._heal_and_retry(
                                                            manifest=manifest,
                                                            heal_fn=heal_fn,
                                                            state_hash_fn=state_hash_fn,
                                                            trace_id="trace-123",
                                                        )
                                                        
                                                        assert result.success is True

    def test_heal_and_retry_known_error(self):
        """Test _heal_and_retry returns failure on known errors."""
        gateway = V15ExecutionGateway()
        manifest = MagicMock()
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway._execute_with_envelope") as mock_exec:
            mock_exec.side_effect = ValueError("Known error")
            
            result = gateway._heal_and_retry(
                manifest=manifest,
                heal_fn=MagicMock(),
                state_hash_fn=MagicMock(return_value=("fs", "git", "mem")),
                trace_id="trace-123",
            )
            
            assert result.success is False
            assert "Known error" in result.error

    def test_pipe_advance_hard_fail(self):
        """Test _pipe_advance raises V15HardFailAbort in hard fail mode."""
        gateway = V15ExecutionGateway()
        pipe = MagicMock()
        pipe.advance.side_effect = Exception("Pipe violation")
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.is_v15_hard_fail") as mock_hard_fail:
            mock_hard_fail.return_value = True
            with patch("agentic_core.L0_routing.enforcement.execution_gateway.is_v15_soft_fail") as mock_soft_fail:
                mock_soft_fail.return_value = False
                with pytest.raises(Exception):  # V15HardFailAbort
                    gateway._pipe_advance(pipe, "step1", "trace-123")

    def test_pipe_advance_soft_fail(self):
        """Test _pipe_advance raises V15SoftFailAbort in soft fail mode."""
        gateway = V15ExecutionGateway()
        pipe = MagicMock()
        pipe.advance.side_effect = Exception("Pipe violation")
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.is_v15_hard_fail") as mock_hard_fail:
            mock_hard_fail.return_value = False
            with patch("agentic_core.L0_routing.enforcement.execution_gateway.is_v15_soft_fail") as mock_soft_fail:
                mock_soft_fail.return_value = True
                with pytest.raises(Exception):  # V15SoftFailAbort
                    gateway._pipe_advance(pipe, "step1", "trace-123")

    def test_pipe_advance_log_only(self):
        """Test _pipe_advance logs violation in log-only mode."""
        gateway = V15ExecutionGateway()
        pipe = MagicMock()
        pipe.advance.side_effect = Exception("Pipe violation")
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.is_v15_hard_fail") as mock_hard_fail:
            mock_hard_fail.return_value = False
            with patch("agentic_core.L0_routing.enforcement.execution_gateway.is_v15_soft_fail") as mock_soft_fail:
                mock_soft_fail.return_value = False
                # Should not raise, just log
                gateway._pipe_advance(pipe, "step1", "trace-123")
                assert len(gateway._pipe_violations) == 1

    def test_policy_check_hard_fail(self):
        """Test _policy_check raises V15HardFailAbort in hard fail mode."""
        gateway = V15ExecutionGateway()
        guard = MagicMock()
        guard.read_config.side_effect = Exception("Policy mutation")
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.is_v15_hard_fail") as mock_hard_fail:
            mock_hard_fail.return_value = True
            with patch("agentic_core.L0_routing.enforcement.execution_gateway.is_v15_soft_fail") as mock_soft_fail:
                mock_soft_fail.return_value = False
                with pytest.raises(Exception):  # V15HardFailAbort
                    gateway._policy_check(guard, {}, "trace-123")

    def test_policy_check_soft_fail(self):
        """Test _policy_check raises V15SoftFailAbort in soft fail mode."""
        gateway = V15ExecutionGateway()
        guard = MagicMock()
        guard.read_config.side_effect = Exception("Policy mutation")
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.is_v15_hard_fail") as mock_hard_fail:
            mock_hard_fail.return_value = False
            with patch("agentic_core.L0_routing.enforcement.execution_gateway.is_v15_soft_fail") as mock_soft_fail:
                mock_soft_fail.return_value = True
                with pytest.raises(Exception):  # V15SoftFailAbort
                    gateway._policy_check(guard, {}, "trace-123")

    def test_policy_check_log_only(self):
        """Test _policy_check logs violation in log-only mode."""
        gateway = V15ExecutionGateway()
        guard = MagicMock()
        guard.read_config.side_effect = Exception("Policy mutation")
        
        with patch("agentic_core.L0_routing.enforcement.execution_gateway.is_v15_hard_fail") as mock_hard_fail:
            mock_hard_fail.return_value = False
            with patch("agentic_core.L0_routing.enforcement.execution_gateway.is_v15_soft_fail") as mock_soft_fail:
                mock_soft_fail.return_value = False
                # Should not raise, just log
                gateway._policy_check(guard, {}, "trace-123")
                assert len(gateway._policy_violations) == 1


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_mutation_counter_initial_value(self):
        """Test MUTATION_COUNTER is initialized to 0."""
        assert MUTATION_COUNTER == 0

    def test_current_phase_initial_value(self):
        """Test CURRENT_PHASE is initialized to UNKNOWN."""
        assert CURRENT_PHASE == "UNKNOWN"
