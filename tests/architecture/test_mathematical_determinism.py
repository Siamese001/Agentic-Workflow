"""
Test Mathematical Determinism - Zero Nondeterminism Surfaces.

Tests that identical healing inputs produce mathematically identical outputs
with 100% reproducibility across runs, environments, and time.
"""

import pytest
import hashlib
from agentic_core.L2_execution.healers.healing_tier_router import (
    compute_heal_confidence,
    route_healing_tier,
    _compute_replay_key,
    HISTORICAL_DATA_VERSION,
    HISTORICAL_DATA_HASH,
    HISTORICAL_SUCCESS_RATES,
)
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingInput,
    HealingTier,
    InvocationRecord,
)
from agentic_core.L2_execution.healers.healing_provider_adapters import (
    QwenInvokerAdapter,
    GeminiInvokerAdapter,
    LocalAgentAdapter,
    QWEN_CONFIG_HASH,
    GEMINI_CONFIG_HASH,
)


class TestMathematicalDeterminism:
    """Test suite for mathematical determinism guarantees."""

    def test_confidence_calculation_determinism(self):
        """Test that confidence calculation is mathematically deterministic."""
        # Create identical input
        healing_input = HealingInput(
            agent_id="test_agent",
            failure_type="syntax_error",
            error_signature="syntax_error:file:42",
            trace_id="trace-123",
            retry_count=0,
            blast_radius_estimate=0.3,
            required_tools=("ast_rewrite",),
            violation_metadata_refs=("file.py",),
        )

        # Calculate confidence multiple times
        results = [compute_heal_confidence(healing_input) for _ in range(10)]

        # All results must be identical
        assert all(r == results[0] for r in results), f"Confidence not deterministic: {results}"

        # Verify fixed precision (6 decimal places)
        confidence = results[0]
        assert len(str(confidence).split('.')[-1]) <= 6, f"Precision not fixed: {confidence}"

    def test_routing_determinism(self):
        """Test that routing decisions are mathematically deterministic."""
        healing_input = HealingInput(
            agent_id="DispatchOutreachToolsAgent",  # In both registry and allowlist
            failure_type="syntax_error",
            error_signature="syntax_error:file:42",
            trace_id="trace-123",
            retry_count=0,
            blast_radius_estimate=0.3,
            required_tools=("ast_rewrite",),
            violation_metadata_refs=("file.py",),
        )

        # Route multiple times
        decisions = [route_healing_tier(healing_input) for _ in range(10)]

        # All decisions must be identical
        assert all(d.tier == decisions[0].tier for d in decisions)
        assert all(d.heal_confidence == decisions[0].heal_confidence for d in decisions)
        assert all(d.reason_codes == decisions[0].reason_codes for d in decisions)

    def test_replay_key_determinism(self):
        """Test that replay keys are mathematically deterministic."""
        healing_input = HealingInput(
            agent_id="DispatchOutreachToolsAgent",  # In both registry and allowlist
            failure_type="syntax_error",
            error_signature="syntax_error:file:42",
            trace_id="trace-123",
            retry_count=0,
            blast_radius_estimate=0.3,
            required_tools=("ast_rewrite",),
            violation_metadata_refs=("file.py",),
        )

        decision = route_healing_tier(healing_input)

        # Compute replay key multiple times
        replay_keys = [_compute_replay_key(healing_input, decision) for _ in range(10)]

        # All replay keys must be identical
        assert all(k == replay_keys[0] for k in replay_keys), f"Replay keys not deterministic: {replay_keys}"

        # Verify timestamp is not included
        assert "timestamp" not in str(replay_keys[0]), "Timestamp leaked into replay key"

    def test_historical_data_versioning(self):
        """Test that historical data is properly versioned and hashed."""
        # Verify version is frozen
        assert HISTORICAL_DATA_VERSION == "v1.0.0"

        # Verify hash is computed from version
        expected_hash = hashlib.sha256(HISTORICAL_DATA_VERSION.encode()).hexdigest()[:16]
        assert HISTORICAL_DATA_HASH == expected_hash

        # Verify historical data is frozen
        assert "syntax_error" in HISTORICAL_SUCCESS_RATES
        assert HISTORICAL_SUCCESS_RATES["syntax_error"] == 0.85

    def test_provider_config_hashing(self):
        """Test that provider configurations are properly hashed."""
        # Verify config hashes are pre-computed
        assert len(QWEN_CONFIG_HASH) == 16
        assert len(GEMINI_CONFIG_HASH) == 16

        # Verify hashes are deterministic
        assert QWEN_CONFIG_HASH == hashlib.sha256(
            "frequency_penalty=0.0|max_tokens=2048|presence_penalty=0.0|temperature=0.0|top_p=1.0".encode()
        ).hexdigest()[:16]

        assert GEMINI_CONFIG_HASH == hashlib.sha256(
            "max_tokens=2048|temperature=0.1|top_k=40|top_p=1.0".encode()
        ).hexdigest()[:16]

    @pytest.mark.asyncio
    async def test_invocation_record_determinism(self):
        """Test that invocation records are replay-deterministic."""
        healing_input = HealingInput(
            agent_id="DispatchOutreachToolsAgent",  # In both registry and allowlist
            failure_type="syntax_error",
            error_signature="syntax_error:file:42",
            trace_id="trace-123",
            retry_count=0,
            blast_radius_estimate=0.3,
            required_tools=("ast_rewrite",),
            violation_metadata_refs=("file.py",),
        )

        decision = route_healing_tier(healing_input)

        # Test local adapter
        local_adapter = LocalAgentAdapter()
        record1 = await local_adapter.invoke_local(healing_input, decision)
        record2 = await local_adapter.invoke_local(healing_input, decision)

        # Records must be identical
        assert record1.replay_key == record2.replay_key
        assert record1.provider_config_hash == record2.provider_config_hash
        assert record1.historical_data_hash == record2.historical_data_hash

    def test_mathematical_properties(self):
        """Test mathematical properties of deterministic calculations."""
        # Test confidence bounds
        healing_input = HealingInput(
            agent_id="test_agent",
            failure_type="unknown",  # Lowest prior
            error_signature="unknown:file:42",
            trace_id="trace-123",
            retry_count=10,  # High retry count
            blast_radius_estimate=1.0,  # Maximum blast radius
            required_tools=(),
            violation_metadata_refs=(),
        )

        confidence = compute_heal_confidence(healing_input)

        # Confidence must be in [0.0, 1.0]
        assert 0.0 <= confidence <= 1.0

        # Test monotonicity: higher blast radius should reduce confidence
        healing_input_low_blast = HealingInput(
            agent_id="test_agent",
            failure_type="unknown",
            error_signature="unknown:file:42",
            trace_id="trace-123",
            retry_count=10,
            blast_radius_estimate=0.0,  # Minimum blast radius
            required_tools=(),
            violation_metadata_refs=(),
        )

        confidence_low_blast = compute_heal_confidence(healing_input_low_blast)
        assert confidence_low_blast > confidence, "Blast radius penalty not monotonic"

    def test_no_environment_leakage(self):
        """Test that no environment variables are accessed."""
        # This test verifies that the router doesn't access environment variables
        # by ensuring it works without any environment setup
        import os

        # Clear any relevant environment variables
        original_env = {}
        for key in list(os.environ.keys()):
            if key.startswith(("QWEN_", "GEMINI_", "LLM_")):
                original_env[key] = os.environ.pop(key)

        try:
            healing_input = HealingInput(
                agent_id="DispatchOutreachToolsAgent",  # In both registry and allowlist
                failure_type="syntax_error",
                error_signature="syntax_error:file:42",
                trace_id="trace-123",
                retry_count=0,
                blast_radius_estimate=0.3,
                required_tools=("ast_rewrite",),
                violation_metadata_refs=("file.py",),
            )

            # Should work without environment variables
            decision = route_healing_tier(healing_input)
            assert decision is not None

        finally:
            # Restore environment
            os.environ.update(original_env)

    def test_deterministic_across_failures(self):
        """Test determinism across different failure types."""
        failure_types = [
            "syntax_error",
            "import_cycle",
            "missing_import",
            "type_hint_error",
            "naming_violation",
            "location_violation",
            "structure_violation",
            "gravity_leak",
            "integrity_gate_failure",
            "test_failure",
            "runtime_error",
            "unknown",
        ]

        for failure_type in failure_types:
            healing_input = HealingInput(
                agent_id="CodeHealerAgent",  # In allowlist
                failure_type=failure_type,
                error_signature=f"{failure_type}:file:42",
                trace_id="trace-123",
                retry_count=0,
                blast_radius_estimate=0.3,
                required_tools=("ast_rewrite",),
                violation_metadata_refs=("file.py",),
            )

            # Calculate confidence multiple times
            results = [compute_heal_confidence(healing_input) for _ in range(5)]

            # Must be deterministic for each failure type
            assert all(r == results[0] for r in results), f"Non-deterministic for {failure_type}: {results}"
