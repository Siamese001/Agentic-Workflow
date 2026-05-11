"""RB13 tests — Provider gateway.

Tests:
- test_provider_gateway_loads_provider_profile
- test_provider_gateway_blocks_missing_provider_profile
- test_provider_gateway_blocks_disallowed_provider
- test_provider_gateway_blocks_missing_credentials_for_external_provider
- test_provider_gateway_supports_stub_provider
- test_provider_gateway_emits_invocation_receipt
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from agentic_core.runtime.providers import (
    BudgetStatus,
    ProviderGateway,
    ProviderGatewayError,
    ProviderInvocationReceipt,
    ProviderKind,
    ProviderMode,
    ProviderModeBlockedError,
    ProviderNotAllowedError,
    ProviderProfile,
    ProviderProfileNotFoundError,
    ProviderRegistry,
    ProviderRequest,
    ProviderResponse,
    SafetyStatus,
    TimeoutStatus,
    TokenUsage,
    get_provider_registry,
    reset_provider_registry,
)
from agentic_core.runtime.contracts.l3_to_l2_step_contract import L3ToL2StepContract


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_registry():
    """Reset registry before each test."""
    reset_provider_registry()
    yield
    reset_provider_registry()


@pytest.fixture
def stub_provider_profile():
    """Create a stub provider profile."""
    return ProviderProfile(
        profile_id="test_stub",
        provider_kind=ProviderKind.STUB,
        model_id=None,
        capabilities=("text_generation",),
        sandbox_safe=True,
        requires_network=False,
    )


@pytest.fixture
def local_vllm_profile():
    """Create a local vLLM provider profile."""
    return ProviderProfile(
        profile_id="test_local_vllm",
        provider_kind=ProviderKind.LOCAL_VLLM,
        model_id="Qwen/Qwen2.5-32B-Instruct-AWQ",
        endpoint_url="http://localhost:8000/v1",
        capabilities=("text_generation", "structured_json_generation"),
        sandbox_safe=True,
        requires_network=True,
    )


@pytest.fixture
def external_api_profile():
    """Create an external API provider profile."""
    return ProviderProfile(
        profile_id="test_external",
        provider_kind=ProviderKind.EXTERNAL_API,
        model_id="gpt-4",
        endpoint_url="https://api.openai.com/v1",
        api_key_env_var="OPENAI_API_KEY",
        capabilities=("text_generation",),
        sandbox_safe=False,
        requires_network=True,
    )


# ── Test Cases ────────────────────────────────────────────────────────────────


class TestProviderGatewayLoadsProfile:
    """test_provider_gateway_loads_provider_profile"""
    
    def test_loads_stub_profile(self, stub_provider_profile):
        """Gateway can load and use stub provider profile."""
        gateway = ProviderGateway(provider_mode=ProviderMode.STUB_ONLY)
        
        request = ProviderRequest(
            prompt_text="Test prompt",
            provider_profile=stub_provider_profile,
            run_id="test-run-001",
            node_id="node-001",
        )
        
        response = gateway.invoke(request)
        
        assert response.success is True
        assert response.text is not None
        assert len(response.text) > 0
        assert response.receipt is not None
        assert response.receipt.provider_profile_ref == "test_stub"
        assert response.receipt.provider_kind == ProviderKind.STUB
    
    def test_loads_local_vllm_profile(self, local_vllm_profile):
        """Gateway can load local vLLM profile (stub mode may block)."""
        gateway = ProviderGateway(provider_mode=ProviderMode.LOCAL_ONLY)
        
        request = ProviderRequest(
            prompt_text="Test prompt",
            provider_profile=local_vllm_profile,
            run_id="test-run-002",
            node_id="node-002",
        )
        
        # In test mode without real vLLM, this may fail or return stub
        # depending on health probe
        response = gateway.invoke(request)
        
        # Should either succeed or fail gracefully with receipt
        assert response.receipt is not None
        assert response.receipt.provider_profile_ref == "test_local_vllm"


class TestProviderGatewayBlocksMissingProfile:
    """test_provider_gateway_blocks_missing_provider_profile"""
    
    def test_registry_raises_on_missing_profile(self):
        """Registry raises ProviderProfileNotFoundError for missing profile."""
        registry = get_provider_registry()
        
        with pytest.raises(ProviderProfileNotFoundError):
            registry.get_profile("nonexistent_profile_xyz")
    
    def test_registry_loads_from_yaml(self, tmp_path):
        """Registry loads profiles from YAML file."""
        registry = ProviderRegistry()
        
        yaml_content = {
            "provider_profile_registry_id": "test::registry",
            "profiles": {
                "test_profile": {
                    "profile_id": "pvp::test::test_profile",
                    "provider_class": "stub",
                    "capabilities": ["text_generation"],
                }
            }
        }
        
        yaml_path = tmp_path / "test_providers.yaml"
        yaml_path.write_text(yaml.safe_dump(yaml_content))
        
        count = registry.load_from_yaml(yaml_path)
        assert count == 1
        
        profile = registry.get_profile("test_profile")
        assert profile.profile_id == "pvp::test::test_profile"
        assert profile.provider_kind == ProviderKind.STUB


class TestProviderGatewayBlocksDisallowedProvider:
    """test_provider_gateway_blocks_disallowed_provider"""
    
    def test_blocks_provider_not_in_allowlist(self, stub_provider_profile):
        """Gateway blocks provider not in step contract allowlist."""
        gateway = ProviderGateway(provider_mode=ProviderMode.LIVE_ALLOWED)
        
        # Create step contract with allowlist
        step = L3ToL2StepContract(
            node_id="node-001",
            run_id="run-001",
            allowed_execution_lane="ENSEMBLE_MODEL",
            provider_allowlist=("allowed_provider_1", "allowed_provider_2"),
            provider_profile_ref="different_provider",
        )
        
        request = ProviderRequest(
            prompt_text="Test",
            provider_profile=stub_provider_profile,  # Not in allowlist
        )
        
        with pytest.raises(ProviderNotAllowedError):
            gateway.invoke(request, step_contract=step)
    
    def test_allows_provider_in_allowlist(self, stub_provider_profile):
        """Gateway allows provider in step contract allowlist."""
        gateway = ProviderGateway(provider_mode=ProviderMode.LIVE_ALLOWED)
        
        step = L3ToL2StepContract(
            node_id="node-001",
            run_id="run-001",
            allowed_execution_lane="ENSEMBLE_MODEL",
            provider_allowlist=("test_stub",),
            provider_profile_ref="test_stub",
        )
        
        request = ProviderRequest(
            prompt_text="Test",
            provider_profile=stub_provider_profile,
        )
        
        response = gateway.invoke(request, step_contract=step)
        assert response.success is True


class TestProviderGatewayBlocksMissingCredentials:
    """test_provider_gateway_blocks_missing_credentials_for_external_provider"""
    
    def test_blocks_external_without_credentials(self, external_api_profile):
        """Gateway blocks external provider when credentials missing."""
        # Ensure env var is not set
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        gateway = ProviderGateway(provider_mode=ProviderMode.LIVE_ALLOWED)
        
        request = ProviderRequest(
            prompt_text="Test",
            provider_profile=external_api_profile,
        )
        
        from agentic_core.runtime.providers.provider_types import ProviderCredentialsMissingError
        with pytest.raises(ProviderCredentialsMissingError):
            gateway.invoke(request)
    
    def test_allows_external_with_credentials(self, external_api_profile, monkeypatch):
        """Gateway allows external provider when credentials present."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123")
        
        gateway = ProviderGateway(provider_mode=ProviderMode.LIVE_ALLOWED)
        
        request = ProviderRequest(
            prompt_text="Test",
            provider_profile=external_api_profile,
        )
        
        # Should not raise credentials error (but may fail for other reasons)
        try:
            response = gateway.invoke(request)
            # RB13: External providers not fully implemented, expect error response
            assert response.success is False
            assert "not implemented" in response.error_message.lower() or "external" in response.error_message.lower()
        except Exception as exc:
            # Should not be credentials error
            assert "credentials" not in str(exc).lower()


class TestProviderGatewaySupportsStub:
    """test_provider_gateway_supports_stub_provider"""
    
    def test_stub_provider_always_works(self, stub_provider_profile):
        """Stub provider works in all modes."""
        for mode in [ProviderMode.STUB_ONLY, ProviderMode.LOCAL_ONLY, ProviderMode.LIVE_ALLOWED]:
            gateway = ProviderGateway(provider_mode=mode)
            
            request = ProviderRequest(
                prompt_text=f"Test in {mode.value}",
                provider_profile=stub_provider_profile,
            )
            
            response = gateway.invoke(request)
            assert response.success is True, f"Failed in mode {mode.value}"
            assert "stub_response" in response.text or "stub" in response.text.lower()
    
    def test_stub_response_is_deterministic(self, stub_provider_profile):
        """Stub provider returns deterministic responses."""
        gateway = ProviderGateway(provider_mode=ProviderMode.STUB_ONLY)
        
        request = ProviderRequest(
            prompt_text="Deterministic test prompt",
            provider_profile=stub_provider_profile,
        )
        
        response1 = gateway.invoke(request)
        response2 = gateway.invoke(request)
        
        # Same prompt should yield same response
        assert response1.text == response2.text


class TestProviderGatewayEmitsReceipt:
    """test_provider_gateway_emits_invocation_receipt"""
    
    def test_receipt_has_required_fields(self, stub_provider_profile):
        """Receipt contains all RB13 required fields."""
        gateway = ProviderGateway(provider_mode=ProviderMode.STUB_ONLY)
        
        request = ProviderRequest(
            prompt_text="Test for receipt",
            provider_profile=stub_provider_profile,
            run_id="run-123",
            node_id="node-456",
            trace_root="trace-789",
            prompt_artifact_ref="prompt-artifact-001",
        )
        
        response = gateway.invoke(request)
        receipt = response.receipt
        
        # All required fields per RB13 spec
        assert receipt.invocation_id is not None and len(receipt.invocation_id) > 0
        assert receipt.provider_profile_ref == "test_stub"
        assert receipt.provider_kind == ProviderKind.STUB
        assert receipt.run_id == "run-123"
        assert receipt.node_id == "node-456"
        assert receipt.trace_root == "trace-789"
        assert receipt.prompt_artifact_ref == "prompt-artifact-001"
        assert receipt.input_digest is not None and len(receipt.input_digest) == 32
        assert receipt.output_digest is not None and len(receipt.output_digest) == 32
        assert receipt.latency_ms >= 0
        assert receipt.token_usage is not None
        assert receipt.budget_status in BudgetStatus
        assert receipt.timeout_status in TimeoutStatus
        assert receipt.safety_status in SafetyStatus
        assert receipt.deterministic_digest is not None and len(receipt.deterministic_digest) == 32
    
    def test_receipt_as_dict(self, stub_provider_profile):
        """Receipt can be serialized to dict."""
        gateway = ProviderGateway(provider_mode=ProviderMode.STUB_ONLY)
        
        request = ProviderRequest(
            prompt_text="Test dict serialization",
            provider_profile=stub_provider_profile,
        )
        
        response = gateway.invoke(request)
        receipt_dict = response.receipt.as_dict()
        
        assert receipt_dict["schema_version"] == "rb13.1"
        assert "invocation_id" in receipt_dict
        assert "token_usage" in receipt_dict
        assert "latency_ms" in receipt_dict


class TestProviderModeRestrictions:
    """Provider mode restrictions per RB13."""
    
    def test_stub_only_blocks_live(self, local_vllm_profile):
        """STUB_ONLY mode blocks local_vllm providers."""
        gateway = ProviderGateway(provider_mode=ProviderMode.STUB_ONLY)
        
        request = ProviderRequest(
            prompt_text="Test",
            provider_profile=local_vllm_profile,
        )
        
        with pytest.raises(ProviderModeBlockedError):
            gateway.invoke(request)
    
    def test_stub_only_allows_deterministic(self):
        """STUB_ONLY mode allows deterministic providers."""
        profile = ProviderProfile(
            profile_id="deterministic_test",
            provider_kind=ProviderKind.DETERMINISTIC,
        )
        
        gateway = ProviderGateway(provider_mode=ProviderMode.STUB_ONLY)
        
        request = ProviderRequest(
            prompt_text="Test",
            provider_profile=profile,
        )
        
        # Deterministic providers allowed even in stub-only mode
        response = gateway.invoke(request)
        assert response.success is True
    
    def test_local_only_blocks_external(self, external_api_profile):
        """LOCAL_ONLY mode blocks external API providers."""
        gateway = ProviderGateway(provider_mode=ProviderMode.LOCAL_ONLY)
        
        request = ProviderRequest(
            prompt_text="Test",
            provider_profile=external_api_profile,
        )
        
        with pytest.raises(ProviderModeBlockedError):
            gateway.invoke(request)


class TestNoProviderHardcoding:
    """test_no_provider_hardcoding_in_core"""
    
    def test_no_hardcoded_provider_names_in_gateway(self):
        """Provider gateway has no hardcoded provider names."""
        import inspect
        from agentic_core.runtime.providers import provider_gateway
        
        source = inspect.getsource(provider_gateway)
        
        # Should not have hardcoded provider API calls or endpoints
        # Provider kinds are ok (stub, local_vllm, external_api are generic)
        hardcoded_api_calls = [
            "api.openai.com",
            "api.anthropic.com", 
            "generativelanguage.googleapis.com",
        ]
        for name in hardcoded_api_calls:
            assert name.lower() not in source.lower(), f"Hardcoded API endpoint found: {name}"


# ── Token Usage ───────────────────────────────────────────────────────────────


class TestTokenUsage:
    """Token usage tracking."""
    
    def test_token_usage_fields(self):
        """TokenUsage has required fields."""
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        )
        
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150
        
        d = usage.as_dict()
        assert d["prompt_tokens"] == 100
        assert d["completion_tokens"] == 50
        assert d["total_tokens"] == 150


# ── All Required Tests Summary ────────────────────────────────────────────────


REQUIRED_TESTS = [
    "test_provider_gateway_loads_provider_profile",
    "test_provider_gateway_blocks_missing_provider_profile",
    "test_provider_gateway_blocks_disallowed_provider",
    "test_provider_gateway_blocks_missing_credentials_for_external_provider",
    "test_provider_gateway_supports_stub_provider",
    "test_provider_gateway_emits_invocation_receipt",
    "test_no_provider_hardcoding_in_core",
]
