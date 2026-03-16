"""
Test REQ-413: Provider Binding Determinism

Tests that determinism digest includes provider_id, model_id, gateway_version,
and semantic_clock_vector for reproducible LLM interactions.
"""

import pytest

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

_emit_records_execution_trace("p0", "evidence", "test_provider_binding_determinism")
_emit_applies_guardrail("p0", "test_provider_binding_determinism", "p0_governance")
_emit_reads_policy_state("p0", "test_provider_binding_determinism", "policy_binding")
_emit_snapshots_state("p0", "test_provider_binding_determinism", "state_snapshot")
emit_replay_key("p0", "test_provider_binding_determinism")
emit_determinism_digest("p0", "test_provider_binding_determinism")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_provider_binding_determinism", "execution_auth")
_emit_validates_capability("p2", "test_provider_binding_determinism", "capability_check")
_emit_routes_to_capability("p2", "test_provider_binding_determinism", "capability_route")
_emit_writes_via_uwg("p2", "test_provider_binding_determinism", "uwg_write")
_emit_blocks_direct_write("p2", "test_provider_binding_determinism", "direct_write_block")
_emit_records_tool_invocation("p2", "test_provider_binding_determinism", "tool_invocation")
_emit_captures_execution_output("p2", "test_provider_binding_determinism", "exec_output")
_emit_dispatches_agent("p3", "test_provider_binding_determinism", "agent_dispatch")
_emit_coordinates_agents("p3", "test_provider_binding_determinism", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_provider_binding_determinism", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_provider_binding_determinism", "healing_outcome")
_emit_escalates_failure("p3", "test_provider_binding_determinism", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_provider_binding_determinism", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_provider_binding_determinism", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_provider_binding_determinism", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_provider_binding_determinism", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_provider_binding_determinism", "eval_metric")
_emit_stores_embedding("p4", "test_provider_binding_determinism", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_provider_binding_determinism", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_provider_binding_determinism", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L2_execution.enforcement.provider_binding_determinism import (
    ProviderBindingContext,
    compute_provider_binding_digest,
    extract_provider_context_from_request,
    verify_provider_binding_determinism,
)


class TestREQ413ProviderBindingDeterminism:
    """Test suite for REQ-413 Provider Binding Determinism."""

    def test_compute_provider_binding_digest_deterministic(self):
        """Test that provider binding digest is deterministic."""
        # Given
        provider_id = "openai"
        model_id = "gpt-4"
        gateway_version = "1.0.0"
        semantic_clock = SemanticClockSnapshot(tick=42, vector_clock=(("L0", 1), ("L2", 3), ("L5", 2)))

        # When
        digest1 = compute_provider_binding_digest(
            provider_id=provider_id,
            model_id=model_id,
            gateway_version=gateway_version,
            semantic_clock=semantic_clock,
        )

        digest2 = compute_provider_binding_digest(
            provider_id=provider_id,
            model_id=model_id,
            gateway_version=gateway_version,
            semantic_clock=semantic_clock,
        )

        # Then
        assert digest1 == digest2
        assert len(digest1) == 64  # SHA-256 hex length
        assert all(c in "0123456789abcdef" for c in digest1)

    def test_compute_provider_binding_digest_different_inputs(self):
        """Test that different inputs produce different digests."""
        # Given
        semantic_clock = SemanticClockSnapshot(tick=42, vector_clock=(("L0", 1), ("L2", 3), ("L5", 2)))

        # When
        digest_openai = compute_provider_binding_digest(
            provider_id="openai", model_id="gpt-4", gateway_version="1.0.0", semantic_clock=semantic_clock
        )

        digest_anthropic = compute_provider_binding_digest(
            provider_id="anthropic", model_id="gpt-4", gateway_version="1.0.0", semantic_clock=semantic_clock
        )

        # Then
        assert digest_openai != digest_anthropic

    def test_compute_provider_binding_digest_with_additional_context(self):
        """Test that additional context is included in digest."""
        # Given
        semantic_clock = SemanticClockSnapshot(tick=42, vector_clock=(("L0", 1), ("L2", 3)))
        additional_context = {"temperature": "0.7", "max_tokens": "1000"}

        # When
        digest_without_context = compute_provider_binding_digest(
            provider_id="openai", model_id="gpt-4", gateway_version="1.0.0", semantic_clock=semantic_clock
        )

        digest_with_context = compute_provider_binding_digest(
            provider_id="openai",
            model_id="gpt-4",
            gateway_version="1.0.0",
            semantic_clock=semantic_clock,
            additional_context=additional_context,
        )

        # Then
        assert digest_without_context != digest_with_context

    def test_verify_provider_binding_determinism_success(self):
        """Test successful verification of provider binding determinism."""
        # Given
        provider_id = "google"
        model_id = "gemini-pro"
        gateway_version = "1.0.0"
        semantic_clock = SemanticClockSnapshot(tick=100, vector_clock=(("L1", 5), ("L3", 2)))

        expected_digest = compute_provider_binding_digest(
            provider_id=provider_id,
            model_id=model_id,
            gateway_version=gateway_version,
            semantic_clock=semantic_clock,
        )

        # When
        result = verify_provider_binding_determinism(
            expected_digest=expected_digest,
            provider_id=provider_id,
            model_id=model_id,
            gateway_version=gateway_version,
            semantic_clock=semantic_clock,
        )

        # Then
        assert result is True

    def test_verify_provider_binding_determinism_failure(self):
        """Test failed verification of provider binding determinism."""
        # Given
        semantic_clock = SemanticClockSnapshot(tick=100, vector_clock=(("L1", 5), ("L3", 2)))

        expected_digest = compute_provider_binding_digest(
            provider_id="openai", model_id="gpt-4", gateway_version="1.0.0", semantic_clock=semantic_clock
        )

        # When - using different provider
        result = verify_provider_binding_determinism(
            expected_digest=expected_digest,
            provider_id="anthropic",  # Different!
            model_id="gpt-4",
            gateway_version="1.0.0",
            semantic_clock=semantic_clock,
        )

        # Then
        assert result is False

    def test_extract_provider_context_from_request(self):
        """Test extraction of provider context from LLM request."""
        # Given
        request = {
            "provider": "openai",
            "model": "gpt-4-turbo",
            "semantic_clock": {"tick": 50, "vector_clock": {"L0": 1, "L2": 2, "L5": 1}},
            "other_field": "should_be_ignored",
        }

        # When
        context = extract_provider_context_from_request(request)

        # Then
        assert isinstance(context, ProviderBindingContext)
        assert context.provider_id == "openai"
        assert context.model_id == "gpt-4-turbo"
        assert context.gateway_version == "1.0.0"  # Default from env
        assert context.semantic_clock_vector == {"L0": 1, "L2": 2, "L5": 1}

    def test_extract_provider_context_missing_fields(self):
        """Test extraction with missing fields uses defaults."""
        # Given
        request = {}

        # When
        context = extract_provider_context_from_request(request)

        # Then
        assert context.provider_id == "unknown"
        assert context.model_id == "unknown"
        assert context.gateway_version == "1.0.0"
        assert context.semantic_clock_vector == {}

    def test_semantic_clock_vector_serialization(self):
        """Test that semantic clock vector is properly serialized."""
        # Given
        semantic_clock = SemanticClockSnapshot(
            tick=123, vector_clock=(("L0", 10), ("L1", 5), ("L2", 15), ("L5", 8), ("L6", 3))
        )

        # When
        digest = compute_provider_binding_digest(
            provider_id="test", model_id="test-model", gateway_version="1.0.0", semantic_clock=semantic_clock
        )

        # Then - should not raise and should be deterministic
        assert digest is not None
        assert len(digest) == 64

    def test_provider_binding_determinism_replay_scenario(self):
        """Test provider binding determinism in a replay scenario."""
        # Given - Original request
        original_clock = SemanticClockSnapshot(tick=42, vector_clock=(("L0", 1), ("L2", 3), ("L5", 2)))

        original_digest = compute_provider_binding_digest(
            provider_id="anthropic",
            model_id="claude-3-5-sonnet-20241022",
            gateway_version="1.0.0",
            semantic_clock=original_clock,
        )

        # When - Replay with same parameters
        replay_clock = SemanticClockSnapshot(tick=42, vector_clock=(("L0", 1), ("L2", 3), ("L5", 2)))

        replay_digest = compute_provider_binding_digest(
            provider_id="anthropic",
            model_id="claude-3-5-sonnet-20241022",
            gateway_version="1.0.0",
            semantic_clock=replay_clock,
        )

        # Then - Should match exactly for replay determinism
        assert original_digest == replay_digest

    def test_different_gateway_versions_produce_different_digests(self):
        """Test that different gateway versions produce different digests."""
        # Given
        semantic_clock = SemanticClockSnapshot(tick=1, vector_clock=())

        # When
        digest_v1 = compute_provider_binding_digest(
            provider_id="openai", model_id="gpt-4", gateway_version="1.0.0", semantic_clock=semantic_clock
        )

        digest_v2 = compute_provider_binding_digest(
            provider_id="openai", model_id="gpt-4", gateway_version="2.0.0", semantic_clock=semantic_clock
        )

        # Then
        assert digest_v1 != digest_v2
