"""
Tests for SovereignLLMGateway.
"""

import time

import pytest

from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
    REASONING_PATH_TABLE,
    CircuitBreaker,
    CircuitBreakerOpenError,
    GatewayError,
    ProviderConfig,
    ProviderType,
    ReasoningPath,
    SignatureVerificationError,
    SovereignLLMGateway,
    TelemetryLedger,
    TelemetryRecord,
    create_gateway,
    create_openai_gateway,
)
from agentic_core.L2_execution.reasoning import (
    AuthorityLevel,
    AuthoritySlot,
    SlotAssemblyEngine,
)


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_initial_state_closed(self):
        """Circuit breaker starts in closed state."""
        cb = CircuitBreaker()
        assert cb._state == "closed"

    def test_opens_after_failures(self):
        """Circuit breaker opens after threshold failures."""
        cb = CircuitBreaker(failure_threshold=3)

        # Simulate failures
        for _ in range(3):
            try:
                cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
            except ValueError:
                pass

        assert cb._state == "open"

    def test_raises_when_open(self):
        """Circuit breaker raises when open."""
        cb = CircuitBreaker()
        cb._state = "open"
        cb._last_failure_time = time.time()  # Not expired - still open

        def success():
            return "ok"

        with pytest.raises(CircuitBreakerOpenError, match="Circuit breaker is open"):
            cb.call(success)


class TestTelemetryLedger:
    """Test telemetry ledger functionality."""

    def test_record_creation(self):
        """Test telemetry record creation."""
        record = TelemetryRecord.create(
            trace_id="test-123",
            provider=ProviderType.OPENAI,
            model="gpt-4",
            tokens_in=100,
            tokens_out=50,
            latency_ms=250.0,
            success=True,
        )

        assert record.trace_id == "test-123"
        assert record.provider == ProviderType.OPENAI
        assert record.success is True

    def test_ledger_record_and_stats(self):
        """Test ledger recording and statistics."""
        ledger = TelemetryLedger()

        record1 = TelemetryRecord.create(
            trace_id="test-1",
            provider=ProviderType.OPENAI,
            model="gpt-4",
            tokens_in=100,
            tokens_out=50,
            latency_ms=200.0,
            success=True,
        )

        record2 = TelemetryRecord.create(
            trace_id="test-2",
            provider=ProviderType.ANTHROPIC,
            model="claude",
            tokens_in=200,
            tokens_out=100,
            latency_ms=300.0,
            success=False,
            error_type="timeout",
        )

        ledger.record(record1)
        ledger.record(record2)

        stats = ledger.get_stats()
        assert stats["total_calls"] == 2
        assert stats["successful_calls"] == 1
        assert stats["failed_calls"] == 1
        assert stats["total_tokens_in"] == 300
        assert stats["total_tokens_out"] == 150

    def test_ledger_filter_by_trace_id(self):
        """Test filtering telemetry records by trace_id."""
        ledger = TelemetryLedger()

        record1 = TelemetryRecord.create(
            trace_id="trace-a",
            provider=ProviderType.OPENAI,
            model="gpt-4",
            tokens_in=100,
            tokens_out=50,
            latency_ms=200.0,
            success=True,
        )

        record2 = TelemetryRecord.create(
            trace_id="trace-b",
            provider=ProviderType.ANTHROPIC,
            model="claude",
            tokens_in=200,
            tokens_out=100,
            latency_ms=300.0,
            success=False,
        )

        ledger.record(record1)
        ledger.record(record2)

        # Filter by trace_id
        filtered = ledger.get_records(trace_id="trace-a")
        assert len(filtered) == 1
        assert filtered[0].trace_id == "trace-a"

    def test_ledger_filter_by_provider(self):
        """Test filtering telemetry records by provider."""
        ledger = TelemetryLedger()

        record1 = TelemetryRecord.create(
            trace_id="trace-1",
            provider=ProviderType.OPENAI,
            model="gpt-4",
            tokens_in=100,
            tokens_out=50,
            latency_ms=200.0,
            success=True,
        )

        record2 = TelemetryRecord.create(
            trace_id="trace-2",
            provider=ProviderType.ANTHROPIC,
            model="claude",
            tokens_in=200,
            tokens_out=100,
            latency_ms=300.0,
            success=True,
        )

        ledger.record(record1)
        ledger.record(record2)

        # Filter by provider
        filtered = ledger.get_records(provider=ProviderType.OPENAI)
        assert len(filtered) == 1
        assert filtered[0].provider == ProviderType.OPENAI


class TestSovereignLLMGateway:
    """Test SovereignLLMGateway functionality."""

    def test_gateway_creation(self):
        """Test gateway creation."""
        gateway = SovereignLLMGateway(secret_key=b"test-secret")
        assert gateway._secret_key == b"test-secret"
        assert gateway._verify_signatures is True

    def test_register_provider(self):
        """Test provider registration."""
        gateway = SovereignLLMGateway(secret_key=b"test-secret")
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test-key",
            model="gpt-4",
        )

        gateway.register_provider(ProviderType.OPENAI, config)
        assert ProviderType.OPENAI in gateway._providers

    def test_generate_without_provider_raises(self):
        """Test that generate raises without registered provider."""
        gateway = SovereignLLMGateway(secret_key=b"test-secret")

        # Build a valid artifact
        engine = SlotAssemblyEngine(secret_key=b"test-secret")
        engine.add_slot(AuthoritySlot("S0", "System rules", AuthorityLevel.ABSOLUTE, "L4"))
        engine.add_slot(AuthoritySlot("U0", "User request", AuthorityLevel.ZERO, "L4"))
        artifact = engine.assemble()

        with pytest.raises(GatewayError, match="Provider not registered"):
            gateway.generate(artifact, provider=ProviderType.OPENAI)

    def test_signature_verification_failure(self):
        """Test that invalid signature raises error."""
        gateway = SovereignLLMGateway(secret_key=b"test-secret")

        # Build artifact with wrong key
        engine = SlotAssemblyEngine(secret_key=b"wrong-secret")
        engine.add_slot(AuthoritySlot("S0", "System rules", AuthorityLevel.ABSOLUTE, "L4"))
        engine.add_slot(AuthoritySlot("U0", "User request", AuthorityLevel.ZERO, "L4"))
        artifact = engine.assemble()

        with pytest.raises(SignatureVerificationError):
            gateway.generate(artifact)

    def test_signature_verification_disabled(self):
        """Test that verification can be disabled."""
        gateway = SovereignLLMGateway(secret_key=b"test-secret", verify_signatures=False)
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
        )
        gateway.register_provider(ProviderType.OPENAI, config)
        gateway._default_provider = ProviderType.OPENAI

        # Build artifact with wrong key - should still work
        engine = SlotAssemblyEngine(secret_key=b"wrong-secret")
        engine.add_slot(AuthoritySlot("S0", "System rules", AuthorityLevel.ABSOLUTE, "L4"))
        engine.add_slot(AuthoritySlot("U0", "User request", AuthorityLevel.ZERO, "L4"))
        artifact = engine.assemble()

        # Should not raise
        response = gateway.generate(artifact)
        assert "content" in response

    def test_telemetry_recorded(self):
        """Test that telemetry is recorded after generate."""
        gateway = SovereignLLMGateway(secret_key=b"test-secret")
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
        )
        gateway.register_provider(ProviderType.OPENAI, config)
        gateway._default_provider = ProviderType.OPENAI

        # Build valid artifact
        engine = SlotAssemblyEngine(secret_key=b"test-secret")
        engine.add_slot(AuthoritySlot("S0", "System rules", AuthorityLevel.ABSOLUTE, "L4"))
        engine.add_slot(AuthoritySlot("U0", "User request", AuthorityLevel.ZERO, "L4"))
        artifact = engine.assemble()

        # Generate
        gateway.generate(artifact)

        # Check telemetry
        stats = gateway.get_telemetry_stats()
        assert stats["total_calls"] == 1
        assert stats["successful_calls"] == 1

    def test_verify_artifact(self):
        """Test standalone signature verification."""
        gateway = SovereignLLMGateway(secret_key=b"test-secret")

        # Valid artifact
        engine = SlotAssemblyEngine(secret_key=b"test-secret")
        engine.add_slot(AuthoritySlot("S0", "System rules", AuthorityLevel.ABSOLUTE, "L4"))
        valid = engine.assemble()

        assert gateway.verify_artifact(valid) is True


class TestGatewayFactory:
    """Test gateway factory functions."""

    def test_create_gateway(self):
        """Test create_gateway factory."""
        gateway = create_gateway(secret_key=b"test")
        assert isinstance(gateway, SovereignLLMGateway)

    def test_create_openai_gateway(self):
        """Test create_openai_gateway factory creates gateway with OpenAI provider."""
        gateway = create_openai_gateway(api_key="test-key", model="gpt-4", secret_key=b"test")
        assert isinstance(gateway, SovereignLLMGateway)
        # Should have OpenAI provider registered and set as default
        assert ProviderType.OPENAI in gateway._providers
        provider_config = gateway._providers[ProviderType.OPENAI][1]
        assert provider_config.model == "gpt-4"
        assert provider_config.api_key == "test-key"

    def test_set_default_provider(self):
        """Test set_default_provider validates provider is registered."""
        gateway = create_gateway(secret_key=b"test")

        # Should raise if provider not registered
        with pytest.raises(GatewayError, match="not registered"):
            gateway.set_default_provider(ProviderType.OPENAI)

        # Register and then set
        config = ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            api_key="key",
            model="claude-3",
        )
        gateway.register_provider(ProviderType.ANTHROPIC, config)
        gateway.set_default_provider(ProviderType.ANTHROPIC)

        # Should be set as default
        assert gateway._default_provider == ProviderType.ANTHROPIC


# G4 Fix: Path selection tests
class TestSelectReasoningPath:
    """Test SovereignLLMGateway.select_reasoning_path method — G4."""

    @pytest.fixture
    def gateway(self):
        """Create a gateway instance for testing."""
        return SovereignLLMGateway(secret_key=b"test-secret", verify_signatures=False)

    def test_simple_tier_selects_cot(self, gateway):
        """Happy path: simple tier selects COT only."""
        result = gateway.select_reasoning_path(complexity_tier="simple")
        assert result.path.path_id == "simple_cot"
        assert result.path.use_cot is True
        assert result.path.use_tot is False

    def test_moderate_tier_selects_hybrid(self, gateway):
        """Happy path: moderate tier selects hybrid."""
        result = gateway.select_reasoning_path(complexity_tier="moderate")
        assert result.path.path_id == "moderate_cot_hybrid"
        assert result.path.use_cot is True
        assert result.path.use_tot is True

    def test_complex_tier_selects_tot(self, gateway):
        """Happy path: complex tier selects TOT."""
        result = gateway.select_reasoning_path(complexity_tier="complex")
        assert result.path.path_id == "complex_tot_reflexion"
        assert result.path.use_tot is True

    def test_deep_tier_selects_full_reasoning(self, gateway):
        """Happy path: deep tier selects full reasoning."""
        result = gateway.select_reasoning_path(complexity_tier="deep")
        assert result.path.path_id == "deep_full_reasoning"
        assert result.path.use_tot is True
        assert result.path.use_reflexion is True

    def test_unknown_tier_defaults_moderate(self, gateway):
        """Edge case: unknown tier defaults to moderate."""
        result = gateway.select_reasoning_path(complexity_tier="unknown")
        assert result.path.path_id == "moderate_cot_hybrid"

    def test_result_contains_selection_reason(self, gateway):
        """Validation: result contains selection metadata."""
        result = gateway.select_reasoning_path(complexity_tier="simple")
        assert "simple" in result.selection_reason
        assert result.complexity_tier == "simple"


class TestReasoningPathStructure:
    """Test ReasoningPath dataclass structure — G4."""

    def test_path_has_required_fields(self):
        """Validation: all paths have required fields."""
        for tier, path in REASONING_PATH_TABLE.items():
            assert isinstance(path, ReasoningPath)
            assert path.path_id is not None
            assert path.use_cot in (True, False)
            assert path.use_tot in (True, False)
            assert path.use_reflexion in (True, False)
            assert 0.0 <= path.temperature <= 1.0
            assert path.adg_complexity_tier == tier

    def test_path_estimated_latency_positive(self):
        """Validation: all paths have positive latency estimates."""
        for _tier, path in REASONING_PATH_TABLE.items():
            assert path.estimated_latency_ms > 0

    def test_simple_paths_no_tot(self):
        """Validation: simple tier doesn't use TOT."""
        simple_path = REASONING_PATH_TABLE["simple"]
        assert simple_path.use_tot is False
        assert simple_path.tot_branches == 0


class TestGatewayPathSelectionIntegration:
    """Test SovereignLLMGateway path selection integration — G4."""

    @pytest.fixture
    def gateway(self):
        """Create a gateway instance for testing."""
        return SovereignLLMGateway(secret_key=b"test-secret", verify_signatures=False)

    def test_gateway_selects_path(self, gateway):
        """Happy path: gateway selects path for tier."""
        result = gateway.select_reasoning_path(complexity_tier="complex")
        assert result.path.use_tot is True
        assert result.complexity_tier == "complex"

    def test_latency_budget_fallback(self, gateway):
        """Happy path: latency budget triggers fallback to simpler path."""
        # Request deep path but with 1000ms budget (deep is 6000ms)
        result = gateway.select_reasoning_path(
            complexity_tier="deep",
            latency_budget_ms=1000,
        )
        # Should fall back to a path within budget
        assert result.path.estimated_latency_ms <= 1000
        assert result.path.path_id in ["simple_cot", "moderate_cot_hybrid"]
