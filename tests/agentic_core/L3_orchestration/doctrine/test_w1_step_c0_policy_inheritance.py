"""W1 c0-policy-rectification-deferred-f7b2a9 — Step-level C0 policy inheritance tests.

Test categories:
1. L3StepContract accepts c0_policy field
2. Step-level c0_policy overrides parent workflow policy
3. Inheritance when step c0_policy is None
4. resolve_step_c0_policy helper function
5. emit_step_contract propagates parent c0_policy
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval.route_contract import C0Policy
from agentic_core.L0_routing.c0_retrieval.verdicts import (
    FreshnessClass,
    SourceClass,
    SupportTarget as C0SupportTarget,
)
from agentic_core.L3_orchestration.doctrine.contracts_l3_6 import (
    ManagedWorkflowBlueprint,
    WorkflowNode,
    WorkflowNodeType,
)
from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import (
    L3ContextBus,
    L3StateLedger,
    L3StepContract,
    NodeReadinessDecision,
    NodeState,
    StepInputs,
    resolve_step_c0_policy,
)
from agentic_core.L3_orchestration.doctrine.state import (
    emit_step_contract,
)
from agentic_core.L3_orchestration.doctrine import L3DoctrineContractError


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_c0_policy_retrieve() -> C0Policy:
    """C0Policy requiring C0 retrieval."""
    return C0Policy(
        grounding_required=True,
        c0_mode="RETRIEVE_REQUIRED",
        decision_source="L1_PLAN_DERIVED",
        evidence_contract_required=True,
        support_target="SOURCE_SUMMARY",
    )


@pytest.fixture
def sample_c0_policy_bypass() -> C0Policy:
    """C0Policy bypassing C0 retrieval."""
    return C0Policy(
        grounding_required=False,
        c0_mode="BYPASS_PRELOADED_CONTEXT",
        decision_source="PRELOADED_CONTEXT",
        evidence_contract_required=False,
        bypass_reason="Preloaded context available",
        preloaded_context_ref="preload-123",
    )


@pytest.fixture
def sample_blueprint() -> ManagedWorkflowBlueprint:
    """Minimal workflow blueprint for testing."""
    return ManagedWorkflowBlueprint(
        blueprint_id="bp-001",
        workflow_name="test_workflow",
        graph_hash="hash123",
        nodes=(
            WorkflowNode(
                node_id="node-1",
                node_type=WorkflowNodeType.C0_GROUNDING_STEP,
                current_ask="Retrieve evidence",
                capability_requirement="c0_retrieval",
                sandbox_requirement="none",
                timeout_ms=5000,
                retry_policy="fail_fast",
                fallback_policy="abort",
            ),
        ),
        edges=(),
        entry_node_id="node-1",
        policy_hash="policy-hash-123",
        replay_key="replay-123",
    )


@pytest.fixture
def sample_ledger() -> L3StateLedger:
    """Minimal L3 state ledger for testing."""
    return L3StateLedger(
        workflow_id="wf-001",
        ledger_hash="ledger-hash-123",
        node_states=(("node-1", NodeState.READY),),
        attempt_counts=(),
        sealed_step_contract_refs=(),
        context_bus_hash="ctx-hash-123",
        policy_hash="policy-hash-123",
        replay_key="replay-123",
    )


@pytest.fixture
def sample_context_bus() -> L3ContextBus:
    """Minimal L3 context bus for testing."""
    return L3ContextBus(
        workflow_id="wf-001",
        bus_hash="bus-hash-123",
    )


@pytest.fixture
def sample_ready_decision() -> NodeReadinessDecision:
    """Ready node decision for testing."""
    return NodeReadinessDecision(
        decision_id="dec-001",
        node_id="node-1",
        ready=True,
        blocked_reasons=(),
        satisfied_dependencies=(),
        unsatisfied_dependencies=(),
        required_evidence_refs=(),
        required_policy_refs=(),
        required_capability_refs=(),
    )


# =============================================================================
# Test Category 1: L3StepContract accepts c0_policy field
# =============================================================================

class TestL3StepContractC0PolicyField:
    """L3StepContract dataclass properly handles c0_policy field."""

    def test_step_contract_with_c0_policy(self, sample_c0_policy_retrieve):
        """L3StepContract accepts c0_policy parameter."""
        contract = L3StepContract(
            step_contract_id="sc-001",
            workflow_id="wf-001",
            node_id="node-1",
            attempt_id="a001",
            parent_route_id="route-001",
            route_digest="digest-123",
            policy_hash="policy-hash",
            blueprint_hash="blueprint-hash",
            snapshot_id="snap-001",
            replay_key="replay-123",
            idempotency_key="idemp-123",
            node_type=WorkflowNodeType.C0_GROUNDING_STEP,
            current_work_order="Retrieve evidence",
            inputs=StepInputs(),
            expected_output_contract="FinalEvidenceContract",
            capability_token_requirement="c0_retrieval",
            sandbox_envelope_requirement="none",
            timeout_ms=5000,
            retry_policy="fail_fast",
            fallback_permission="abort",
            telemetry_keys=(),
            expected_receipts=(),
            step_contract_hash="hash-123",
            c0_policy=sample_c0_policy_retrieve,  # W1: New field
        )
        assert contract.c0_policy is sample_c0_policy_retrieve
        assert contract.c0_policy.c0_mode == "RETRIEVE_REQUIRED"

    def test_step_contract_without_c0_policy(self):
        """L3StepContract works without c0_policy (backward compatible)."""
        contract = L3StepContract(
            step_contract_id="sc-001",
            workflow_id="wf-001",
            node_id="node-1",
            attempt_id="a001",
            parent_route_id="route-001",
            route_digest="digest-123",
            policy_hash="policy-hash",
            blueprint_hash="blueprint-hash",
            snapshot_id="snap-001",
            replay_key="replay-123",
            idempotency_key="idemp-123",
            node_type=WorkflowNodeType.C0_GROUNDING_STEP,
            current_work_order="Retrieve evidence",
            inputs=StepInputs(),
            expected_output_contract="FinalEvidenceContract",
            capability_token_requirement="c0_retrieval",
            sandbox_envelope_requirement="none",
            timeout_ms=5000,
            retry_policy="fail_fast",
            fallback_permission="abort",
            telemetry_keys=(),
            expected_receipts=(),
            step_contract_hash="hash-123",
            # c0_policy defaults to None
        )
        assert contract.c0_policy is None

    def test_step_contract_invalid_c0_policy_type(self):
        """L3StepContract rejects invalid c0_policy type."""
        with pytest.raises(L3DoctrineContractError, match="c0_policy must be C0Policy"):
            L3StepContract(
                step_contract_id="sc-001",
                workflow_id="wf-001",
                node_id="node-1",
                attempt_id="a001",
                parent_route_id="route-001",
                route_digest="digest-123",
                policy_hash="policy-hash",
                blueprint_hash="blueprint-hash",
                snapshot_id="snap-001",
                replay_key="replay-123",
                idempotency_key="idemp-123",
                node_type=WorkflowNodeType.C0_GROUNDING_STEP,
                current_work_order="Retrieve evidence",
                inputs=StepInputs(),
                expected_output_contract="FinalEvidenceContract",
                capability_token_requirement="c0_retrieval",
                sandbox_envelope_requirement="none",
                timeout_ms=5000,
                retry_policy="fail_fast",
                fallback_permission="abort",
                telemetry_keys=(),
                expected_receipts=(),
                step_contract_hash="hash-123",
                c0_policy="invalid-string",  # Invalid type
            )


# =============================================================================
# Test Category 2 & 4: resolve_step_c0_policy helper
# =============================================================================

class TestResolveStepC0Policy:
    """resolve_step_c0_policy implements correct inheritance logic."""

    def test_step_override_takes_precedence(
        self, sample_c0_policy_retrieve, sample_c0_policy_bypass
    ):
        """Step-level c0_policy overrides parent policy."""
        step = L3StepContract(
            step_contract_id="sc-001",
            workflow_id="wf-001",
            node_id="node-1",
            attempt_id="a001",
            parent_route_id="route-001",
            route_digest="digest-123",
            policy_hash="policy-hash",
            blueprint_hash="blueprint-hash",
            snapshot_id="snap-001",
            replay_key="replay-123",
            idempotency_key="idemp-123",
            node_type=WorkflowNodeType.C0_GROUNDING_STEP,
            current_work_order="Retrieve evidence",
            inputs=StepInputs(),
            expected_output_contract="FinalEvidenceContract",
            capability_token_requirement="c0_retrieval",
            sandbox_envelope_requirement="none",
            timeout_ms=5000,
            retry_policy="fail_fast",
            fallback_permission="abort",
            telemetry_keys=(),
            expected_receipts=(),
            step_contract_hash="hash-123",
            c0_policy=sample_c0_policy_bypass,  # Step says bypass
        )
        parent_policy = sample_c0_policy_retrieve  # Parent says retrieve

        effective = resolve_step_c0_policy(step, parent_policy)

        # Step-level override wins
        assert effective is sample_c0_policy_bypass
        assert effective.c0_mode == "BYPASS_PRELOADED_CONTEXT"

    def test_inheritance_when_step_has_no_policy(
        self, sample_c0_policy_retrieve
    ):
        """Step inherits parent policy when step c0_policy is None."""
        step = L3StepContract(
            step_contract_id="sc-001",
            workflow_id="wf-001",
            node_id="node-1",
            attempt_id="a001",
            parent_route_id="route-001",
            route_digest="digest-123",
            policy_hash="policy-hash",
            blueprint_hash="blueprint-hash",
            snapshot_id="snap-001",
            replay_key="replay-123",
            idempotency_key="idemp-123",
            node_type=WorkflowNodeType.C0_GROUNDING_STEP,
            current_work_order="Retrieve evidence",
            inputs=StepInputs(),
            expected_output_contract="FinalEvidenceContract",
            capability_token_requirement="c0_retrieval",
            sandbox_envelope_requirement="none",
            timeout_ms=5000,
            retry_policy="fail_fast",
            fallback_permission="abort",
            telemetry_keys=(),
            expected_receipts=(),
            step_contract_hash="hash-123",
            c0_policy=None,  # No step-level policy
        )

        effective = resolve_step_c0_policy(step, sample_c0_policy_retrieve)

        # Inherits from parent
        assert effective is sample_c0_policy_retrieve

    def test_none_when_neither_has_policy(self):
        """Returns None when neither step nor parent has policy."""
        step = L3StepContract(
            step_contract_id="sc-001",
            workflow_id="wf-001",
            node_id="node-1",
            attempt_id="a001",
            parent_route_id="route-001",
            route_digest="digest-123",
            policy_hash="policy-hash",
            blueprint_hash="blueprint-hash",
            snapshot_id="snap-001",
            replay_key="replay-123",
            idempotency_key="idemp-123",
            node_type=WorkflowNodeType.C0_GROUNDING_STEP,
            current_work_order="Retrieve evidence",
            inputs=StepInputs(),
            expected_output_contract="FinalEvidenceContract",
            capability_token_requirement="c0_retrieval",
            sandbox_envelope_requirement="none",
            timeout_ms=5000,
            retry_policy="fail_fast",
            fallback_permission="abort",
            telemetry_keys=(),
            expected_receipts=(),
            step_contract_hash="hash-123",
            c0_policy=None,
        )

        effective = resolve_step_c0_policy(step, None)

        assert effective is None

    def test_resolve_requires_l3_step_contract(self):
        """resolve_step_c0_policy validates input type."""
        with pytest.raises(L3DoctrineContractError, match="expects L3StepContract"):
            resolve_step_c0_policy("not-a-step-contract", None)  # type: ignore


# =============================================================================
# Test Category 5: emit_step_contract propagates c0_policy
# =============================================================================

class TestEmitStepContractC0Policy:
    """emit_step_contract correctly handles c0_policy parameter."""

    def test_emit_step_contract_with_parent_c0_policy(
        self,
        sample_ready_decision,
        sample_ledger,
        sample_blueprint,
        sample_context_bus,
        sample_c0_policy_retrieve,
    ):
        """emit_step_contract accepts and stores parent c0_policy."""
        contract = emit_step_contract(
            decision=sample_ready_decision,
            ledger=sample_ledger,
            blueprint=sample_blueprint,
            context_bus=sample_context_bus,
            parent_route_id="route-001",
            route_digest="digest-123",
            snapshot_id="snap-001",
            c0_policy=sample_c0_policy_retrieve,
        )

        assert contract.c0_policy is sample_c0_policy_retrieve
        assert contract.c0_policy.c0_mode == "RETRIEVE_REQUIRED"

    def test_emit_step_contract_without_c0_policy(
        self,
        sample_ready_decision,
        sample_ledger,
        sample_blueprint,
        sample_context_bus,
    ):
        """emit_step_contract works without c0_policy (backward compatible)."""
        contract = emit_step_contract(
            decision=sample_ready_decision,
            ledger=sample_ledger,
            blueprint=sample_blueprint,
            context_bus=sample_context_bus,
            parent_route_id="route-001",
            route_digest="digest-123",
            snapshot_id="snap-001",
            # No c0_policy passed
        )

        assert contract.c0_policy is None


# =============================================================================
# Integration Test: Mixed Workflow
# =============================================================================

class TestMixedWorkflow:
    """Mixed workflow with some steps bypassing, some retrieving."""

    def test_mixed_workflow_c0_policies(
        self, sample_blueprint, sample_ledger, sample_context_bus
    ):
        """Workflow with mixed C0 policies per step."""
        # Step 1: C0 retrieval required
        retrieve_policy = C0Policy(
            grounding_required=True,
            c0_mode="RETRIEVE_REQUIRED",
            decision_source="L1_PLAN_DERIVED",
            evidence_contract_required=True,
            support_target="SOURCE_SUMMARY",
        )

        # Step 2: Bypass with preloaded context
        bypass_policy = C0Policy(
            grounding_required=False,
            c0_mode="BYPASS_PRELOADED_CONTEXT",
            decision_source="PRELOADED_CONTEXT",
            evidence_contract_required=False,
            bypass_reason="Context from step 1",
        )

        ready_decision_1 = NodeReadinessDecision(
            decision_id="dec-001",
            node_id="node-1",
            ready=True,
            blocked_reasons=(),
            satisfied_dependencies=(),
            unsatisfied_dependencies=(),
            required_evidence_refs=(),
            required_policy_refs=(),
            required_capability_refs=(),
        )

        # Emit step 1 with retrieval policy
        step_1 = emit_step_contract(
            decision=ready_decision_1,
            ledger=sample_ledger,
            blueprint=sample_blueprint,
            context_bus=sample_context_bus,
            parent_route_id="route-001",
            route_digest="digest-123",
            snapshot_id="snap-001",
            c0_policy=retrieve_policy,
        )

        # Step 1 should have retrieval policy
        assert step_1.c0_policy is retrieve_policy
        assert step_1.c0_policy.c0_mode == "RETRIEVE_REQUIRED"

        # Step 2 could override with bypass
        # (In real usage, this would be a different node with different policy)
        effective_policy = resolve_step_c0_policy(step_1, bypass_policy)
        # Step 1's own policy takes precedence over parent/workflow policy
        assert effective_policy is retrieve_policy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
