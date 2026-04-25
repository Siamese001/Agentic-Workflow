"""Tests for routing_contract.py module."""

from __future__ import annotations

import hashlib
import threading
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.enforcement.routing_contract import (
    RoutingContext,
    RoutingContract,
    RoutingProposal,
    ProposalCommitter,
    UngovernnedRouteError,
    RoutingContractError,
    RoutingOptimizationError,
    StaleRoutingContractError,
    RoutingContractValidationError,
    CONTRACT_VERSION,
    reset_contract_registry,
    create_and_commit_routing_contract,
    commit_proposal,
    execute_route,
    _get_contract_registry,
    _emit_references_policy_hash,
    emit_replay_key,
    emit_determinism_digest,
    _emit_records_execution_trace,
)


class TestErrorClasses:
    """Tests for error classes."""

    def test_ungoverned_route_error_is_runtime_error(self):
        """Test that UngovernnedRouteError is a RuntimeError."""
        assert issubclass(UngovernnedRouteError, RuntimeError)

    def test_routing_contract_error_is_runtime_error(self):
        """Test that RoutingContractError is a RuntimeError."""
        assert issubclass(RoutingContractError, RuntimeError)

    def test_routing_optimization_error_is_runtime_error(self):
        """Test that RoutingOptimizationError is a RuntimeError."""
        assert issubclass(RoutingOptimizationError, RuntimeError)

    def test_stale_routing_contract_error_is_runtime_error(self):
        """Test that StaleRoutingContractError is a RuntimeError."""
        assert issubclass(StaleRoutingContractError, RuntimeError)

    def test_routing_contract_validation_error_is_value_error(self):
        """Test that RoutingContractValidationError is a ValueError."""
        assert issubclass(RoutingContractValidationError, ValueError)


class TestRoutingContext:
    """Tests for RoutingContext dataclass."""

    def test_routing_context_creation(self):
        """Test creating RoutingContext with all fields."""
        context = RoutingContext(
            run_id="test-run",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes=["R1", "R2", "R3"],
            chosen_route="R2",
            policy_hash="policy-hash",
            policy_version="1.0",
            metadata={"key": "value"},
        )
        assert context.run_id == "test-run"
        assert context.router_id == "test-router"
        assert context.chosen_route == "R2"
        assert context.metadata == {"key": "value"}

    def test_routing_context_default_metadata(self):
        """Test RoutingContext with default metadata."""
        context = RoutingContext(
            run_id="test-run",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes=["R1", "R2"],
            chosen_route="R1",
            policy_hash="policy-hash",
            policy_version="1.0",
        )
        assert context.metadata == {}

    def test_routing_context_validate_success(self):
        """Test RoutingContext.validate with all required fields."""
        context = RoutingContext(
            run_id="test-run",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes=["R1", "R2"],
            chosen_route="R1",
            policy_hash="policy-hash",
            policy_version="1.0",
        )
        with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_snapshots_state"):
            with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_signs_execution_trace"):
                with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_verifies_policy"):
                    context.validate()  # Should not raise

    def test_routing_context_validate_missing_run_id(self):
        """Test RoutingContext.validate with missing run_id."""
        context = RoutingContext(
            run_id="",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes=["R1"],
            chosen_route="R1",
            policy_hash="policy-hash",
            policy_version="1.0",
        )
        with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_snapshots_state"):
            with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_signs_execution_trace"):
                with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_verifies_policy"):
                    with pytest.raises(RoutingContractValidationError, match="run_id"):
                        context.validate()

    def test_routing_context_validate_missing_router_id(self):
        """Test RoutingContext.validate with missing router_id."""
        context = RoutingContext(
            run_id="test-run",
            router_id="",
            request_hash="abc123",
            candidate_routes=["R1"],
            chosen_route="R1",
            policy_hash="policy-hash",
            policy_version="1.0",
        )
        with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_snapshots_state"):
            with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_signs_execution_trace"):
                with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_verifies_policy"):
                    with pytest.raises(RoutingContractValidationError, match="router_id"):
                        context.validate()

    def test_routing_context_validate_missing_candidate_routes(self):
        """Test RoutingContext.validate with missing candidate_routes."""
        context = RoutingContext(
            run_id="test-run",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes=[],
            chosen_route="R1",
            policy_hash="policy-hash",
            policy_version="1.0",
        )
        with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_snapshots_state"):
            with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_signs_execution_trace"):
                with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_verifies_policy"):
                    with pytest.raises(RoutingContractValidationError, match="candidate_routes"):
                        context.validate()


class TestRoutingContract:
    """Tests for RoutingContract dataclass."""

    def test_routing_contract_creation(self):
        """Test creating RoutingContract with all fields."""
        contract = RoutingContract(
            routing_contract_id="rc-123",
            run_id="test-run",
            trace_id="trace-123",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes_hash="hash1",
            chosen_route_hash="hash2",
            policy_hash="policy-hash",
            policy_version="1.0",
            replay_key="rk-123",
            determinism_digest="dd-123",
            contract_version="1.0.0",
            created_at_tick=1000.0,
            expiry_tick=4600.0,
        )
        assert contract.routing_contract_id == "rc-123"
        assert contract.is_policy_current("policy-hash")

    def test_routing_contract_is_frozen(self):
        """Test that RoutingContract is frozen (immutable)."""
        contract = RoutingContract(
            routing_contract_id="rc-123",
            run_id="test-run",
            trace_id="trace-123",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes_hash="hash1",
            chosen_route_hash="hash2",
            policy_hash="policy-hash",
            policy_version="1.0",
            replay_key="rk-123",
            determinism_digest="dd-123",
            contract_version="1.0.0",
            created_at_tick=1000.0,
            expiry_tick=4600.0,
        )
        with pytest.raises(FrozenInstanceError):
            contract.chosen_route = "R2"

    def test_routing_contract_is_policy_current(self):
        """Test is_policy_current method."""
        contract = RoutingContract(
            routing_contract_id="rc-123",
            run_id="test-run",
            trace_id="trace-123",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes_hash="hash1",
            chosen_route_hash="hash2",
            policy_hash="policy-hash",
            policy_version="1.0",
            replay_key="rk-123",
            determinism_digest="dd-123",
            contract_version="1.0.0",
            created_at_tick=1000.0,
            expiry_tick=4600.0,
        )
        assert contract.is_policy_current("policy-hash")
        assert not contract.is_policy_current("different-policy")

    def test_routing_contract_is_expired(self):
        """Test is_expired method."""
        contract = RoutingContract(
            routing_contract_id="rc-123",
            run_id="test-run",
            trace_id="trace-123",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes_hash="hash1",
            chosen_route_hash="hash2",
            policy_hash="policy-hash",
            policy_version="1.0",
            replay_key="rk-123",
            determinism_digest="dd-123",
            contract_version="1.0.0",
            created_at_tick=1000.0,
            expiry_tick=4600.0,
        )
        assert not contract.is_expired(2000.0)
        assert contract.is_expired(5000.0)

    def test_routing_contract_require_valid_success(self):
        """Test require_valid with valid contract."""
        contract = RoutingContract(
            routing_contract_id="rc-123",
            run_id="test-run",
            trace_id="trace-123",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes_hash="hash1",
            chosen_route_hash="hash2",
            policy_hash="policy-hash",
            policy_version="1.0",
            replay_key="rk-123",
            determinism_digest="dd-123",
            contract_version="1.0.0",
            created_at_tick=1000.0,
            expiry_tick=4600.0,
        )
        contract.require_valid("policy-hash", 2000.0)  # Should not raise

    def test_routing_contract_require_valid_policy_mismatch(self):
        """Test require_valid with policy mismatch."""
        contract = RoutingContract(
            routing_contract_id="rc-123",
            run_id="test-run",
            trace_id="trace-123",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes_hash="hash1",
            chosen_route_hash="hash2",
            policy_hash="policy-hash",
            policy_version="1.0",
            replay_key="rk-123",
            determinism_digest="dd-123",
            contract_version="1.0.0",
            created_at_tick=1000.0,
            expiry_tick=4600.0,
        )
        with pytest.raises(StaleRoutingContractError, match="policy mismatch"):
            contract.require_valid("different-policy", 2000.0)

    def test_routing_contract_require_valid_expired(self):
        """Test require_valid with expired contract."""
        contract = RoutingContract(
            routing_contract_id="rc-123",
            run_id="test-run",
            trace_id="trace-123",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes_hash="hash1",
            chosen_route_hash="hash2",
            policy_hash="policy-hash",
            policy_version="1.0",
            replay_key="rk-123",
            determinism_digest="dd-123",
            contract_version="1.0.0",
            created_at_tick=1000.0,
            expiry_tick=4600.0,
        )
        with pytest.raises(StaleRoutingContractError, match="expired"):
            contract.require_valid("policy-hash", 5000.0)


class TestRoutingProposal:
    """Tests for RoutingProposal dataclass."""

    def test_routing_proposal_creation(self):
        """Test creating RoutingProposal."""
        proposal = RoutingProposal(
            routing_contract_id="rc-123",
            run_id="test-run",
            router_id="test-router",
            chosen_route="R2",
            policy_hash="policy-hash",
            proposal_hash="proposal-hash",
        )
        assert proposal.routing_contract_id == "rc-123"
        assert proposal.chosen_route == "R2"

    def test_routing_proposal_is_frozen(self):
        """Test that RoutingProposal is frozen."""
        proposal = RoutingProposal(
            routing_contract_id="rc-123",
            run_id="test-run",
            router_id="test-router",
            chosen_route="R2",
            policy_hash="policy-hash",
            proposal_hash="proposal-hash",
        )
        with pytest.raises(FrozenInstanceError):
            proposal.chosen_route = "R3"


class TestProposalCommitter:
    """Tests for ProposalCommitter class."""

    def test_proposal_committer_exists(self):
        """Test that ProposalCommitter class exists."""
        assert ProposalCommitter is not None

    def test_proposal_committer_is_class(self):
        """Test that ProposalCommitter is a class."""
        assert isinstance(ProposalCommitter, type)


class TestContractRegistry:
    """Tests for _ContractRegistry."""

    def test_get_contract_registry_returns_singleton(self):
        """Test that _get_contract_registry returns singleton."""
        reset_contract_registry()
        registry1 = _get_contract_registry()
        registry2 = _get_contract_registry()
        assert registry1 is registry2

    def test_reset_contract_registry(self):
        """Test that reset_contract_registry clears registry."""
        reset_contract_registry()
        registry1 = _get_contract_registry()
        reset_contract_registry()
        registry2 = _get_contract_registry()
        assert registry1 is not registry2

    def test_registry_store_and_get(self):
        """Test storing and retrieving contracts."""
        reset_contract_registry()
        registry = _get_contract_registry()
        contract = RoutingContract(
            routing_contract_id="rc-123",
            run_id="test-run",
            trace_id="trace-123",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes_hash="hash1",
            chosen_route_hash="hash2",
            policy_hash="policy-hash",
            policy_version="1.0",
            replay_key="rk-123",
            determinism_digest="dd-123",
            contract_version="1.0.0",
            created_at_tick=1000.0,
            expiry_tick=4600.0,
        )
        registry.store(contract)
        retrieved = registry.get("rc-123")
        assert retrieved is contract

    def test_registry_get_nonexistent(self):
        """Test getting non-existent contract returns None."""
        reset_contract_registry()
        registry = _get_contract_registry()
        assert registry.get("nonexistent") is None

    def test_registry_record_proposal(self):
        """Test recording proposals."""
        reset_contract_registry()
        registry = _get_contract_registry()
        proposal = RoutingProposal(
            routing_contract_id="rc-123",
            run_id="test-run",
            router_id="test-router",
            chosen_route="R2",
            policy_hash="policy-hash",
            proposal_hash="proposal-hash",
        )
        registry.record(proposal)
        proposals = registry.all_proposals()
        assert len(proposals) == 1
        assert proposals[0] is proposal

    def test_registry_thread_safety(self):
        """Test that registry is thread-safe."""
        reset_contract_registry()
        registry = _get_contract_registry()
        
        def store_contract():
            contract = RoutingContract(
                routing_contract_id=f"rc-{threading.get_ident()}",
                run_id="test-run",
                trace_id="trace-123",
                router_id="test-router",
                request_hash="abc123",
                candidate_routes_hash="hash1",
                chosen_route_hash="hash2",
                policy_hash="policy-hash",
                policy_version="1.0",
                replay_key="rk-123",
                determinism_digest="dd-123",
                contract_version="1.0.0",
                created_at_tick=1000.0,
                expiry_tick=4600.0,
            )
            registry.store(contract)

        threads = [threading.Thread(target=store_contract) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(registry.all_contracts()) == 10


class TestEmitterFunctions:
    """Tests for emitter functions."""

    def test_emit_references_policy_hash(self):
        """Test _emit_references_policy_hash function."""
        # Should not raise
        _emit_references_policy_hash("rc-123", "policy-hash", "1.0")

    def test_emit_replay_key(self):
        """Test emit_replay_key function."""
        # Should not raise
        emit_replay_key("rc-123", "rk-123")

    def test_emit_determinism_digest(self):
        """Test emit_determinism_digest function."""
        # Should not raise
        emit_determinism_digest("rc-123", "dd-123")

    def test_emit_records_execution_trace(self):
        """Test _emit_records_execution_trace function."""
        # Should not raise
        _emit_records_execution_trace("rc-123", "test-router", "R2")


class TestCommitProposal:
    """Tests for commit_proposal function."""

    def test_commit_proposal(self):
        """Test commit_proposal function."""
        reset_contract_registry()
        proposal = RoutingProposal(
            routing_contract_id="rc-123",
            run_id="test-run",
            router_id="test-router",
            chosen_route="R2",
            policy_hash="policy-hash",
            proposal_hash="proposal-hash",
        )
        commit_proposal(proposal)
        registry = _get_contract_registry()
        proposals = registry.all_proposals()
        assert len(proposals) == 1
        assert proposals[0].routing_contract_id == "rc-123"


class TestExecuteRoute:
    """Tests for execute_route function."""

    def test_execute_route_with_valid_contract(self):
        """Test execute_route with valid RoutingContract."""
        contract = RoutingContract(
            routing_contract_id="rc-123",
            run_id="test-run",
            trace_id="trace-123",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes_hash="hash1",
            chosen_route_hash="hash2",
            policy_hash="policy-hash",
            policy_version="1.0",
            replay_key="rk-123",
            determinism_digest="dd-123",
            contract_version="1.0.0",
            created_at_tick=1000.0,
            expiry_tick=4600.0,
        )
        mock_fn = MagicMock(return_value="result")
        result = execute_route(contract, mock_fn, "arg1", "arg2")
        assert result == "result"
        mock_fn.assert_called_once_with("arg1", "arg2")

    def test_execute_route_without_contract(self):
        """Test execute_route without RoutingContract raises error."""
        mock_fn = MagicMock(return_value="result")
        with pytest.raises(UngovernnedRouteError, match="requires a RoutingContract"):
            execute_route("not-a-contract", mock_fn)


class TestCreateAndCommitRoutingContract:
    """Tests for create_and_commit_routing_contract function."""

    def test_create_contract_with_valid_context(self):
        """Test creating contract with valid RoutingContext."""
        reset_contract_registry()
        context = RoutingContext(
            run_id="test-run",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes=["R1", "R2", "R3"],
            chosen_route="R2",
            policy_hash="policy-hash",
            policy_version="1.0",
        )

        mock_clock = MagicMock()
        mock_clock.now_epoch.return_value = 1000.0
        mock_clock.emit_replay_key = MagicMock()
        mock_clock.emit_determinism_digest = MagicMock()

        mock_trace = MagicMock()
        mock_trace.trace_id = "trace-123"

        with patch("agentic_core.L0_routing.enforcement.routing_contract.get_clock", return_value=mock_clock):
            with patch("agentic_core.L0_routing.enforcement.routing_contract.get_active_execution_trace", return_value=mock_trace):
                with patch("agentic_core.L0_routing.enforcement.routing_contract.optimize_simple_routing"):
                    contract = create_and_commit_routing_contract(context)

        assert contract.routing_contract_id.startswith("rc-")
        assert contract.run_id == "test-run"
        assert contract.chosen_route_hash == hashlib.sha256("R2".encode()).hexdigest()[:32]
        assert contract.contract_version == CONTRACT_VERSION
        assert contract.created_at_tick == 1000.0
        assert contract.expiry_tick == 4600.0

    def test_create_contract_with_invalid_context(self):
        """Test creating contract with invalid RoutingContext raises error."""
        reset_contract_registry()
        context = RoutingContext(
            run_id="",  # Invalid
            router_id="test-router",
            request_hash="abc123",
            candidate_routes=["R1"],
            chosen_route="R1",
            policy_hash="policy-hash",
            policy_version="1.0",
        )
        with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_snapshots_state"):
            with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_signs_execution_trace"):
                with patch("agentic_core.L0_routing.enforcement.routing_contract._emit_verifies_policy"):
                    with pytest.raises(RoutingContractValidationError):
                        create_and_commit_routing_contract(context)

    def test_create_contract_custom_expiry(self):
        """Test creating contract with custom expiry_ticks."""
        reset_contract_registry()
        context = RoutingContext(
            run_id="test-run",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes=["R1"],
            chosen_route="R1",
            policy_hash="policy-hash",
            policy_version="1.0",
        )

        mock_clock = MagicMock()
        mock_clock.now_epoch.return_value = 1000.0
        mock_clock.emit_replay_key = MagicMock()
        mock_clock.emit_determinism_digest = MagicMock()

        mock_trace = MagicMock()
        mock_trace.trace_id = "trace-123"

        with patch("agentic_core.L0_routing.enforcement.routing_contract.get_clock", return_value=mock_clock):
            with patch("agentic_core.L0_routing.enforcement.routing_contract.get_active_execution_trace", return_value=mock_trace):
                with patch("agentic_core.L0_routing.enforcement.routing_contract.optimize_simple_routing"):
                    contract = create_and_commit_routing_contract(context, expiry_ticks=7200.0)

        assert contract.expiry_tick == 8200.0  # 1000 + 7200

    def test_create_contract_persists_to_registry(self):
        """Test that created contract is persisted to registry."""
        reset_contract_registry()
        context = RoutingContext(
            run_id="test-run",
            router_id="test-router",
            request_hash="abc123",
            candidate_routes=["R1"],
            chosen_route="R1",
            policy_hash="policy-hash",
            policy_version="1.0",
        )

        mock_clock = MagicMock()
        mock_clock.now_epoch.return_value = 1000.0
        mock_clock.emit_replay_key = MagicMock()
        mock_clock.emit_determinism_digest = MagicMock()

        mock_trace = MagicMock()
        mock_trace.trace_id = "trace-123"

        with patch("agentic_core.L0_routing.enforcement.routing_contract.get_clock", return_value=mock_clock):
            with patch("agentic_core.L0_routing.enforcement.routing_contract.get_active_execution_trace", return_value=mock_trace):
                with patch("agentic_core.L0_routing.enforcement.routing_contract.optimize_simple_routing"):
                    contract = create_and_commit_routing_contract(context)

        registry = _get_contract_registry()
        retrieved = registry.get(contract.routing_contract_id)
        assert retrieved is contract


class TestContractVersion:
    """Tests for contract version constant."""

    def test_contract_version_exists(self):
        """Test that CONTRACT_VERSION constant exists."""
        assert CONTRACT_VERSION is not None

    def test_contract_version_is_string(self):
        """Test that CONTRACT_VERSION is a string."""
        assert isinstance(CONTRACT_VERSION, str)
