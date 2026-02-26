"""
Tests for Phase 5: Agent 2x2 Classification and Gateway Sovereignty.
"""

import ast
import os
from dataclasses import replace
from unittest.mock import patch

import pytest

from agentic_core.agents.agent_registry import AGENT_REGISTRY
from agentic_core.L2_execution.determinism import compute_p5_determinism_digest
from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
    GenerationRequest,
    SovereignLLMGateway,
    SovereigntyViolation,
)

FORBIDDEN_IMPORTS = {"openai", "anthropic", "google.generativeai", "google.genai"}
ALLOWED_IMPORT_PATHS = {
    "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
}


class ImportScanner(ast.NodeVisitor):
    def __init__(self, file_path):
        self.file_path = file_path
        self.violations = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in FORBIDDEN_IMPORTS:
                self.violations.append((alias.name, node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module in FORBIDDEN_IMPORTS:
            self.violations.append((node.module, node.lineno))
        self.generic_visit(node)


@pytest.mark.governance
def test_no_forbidden_sdk_imports():
    """Verify that no direct provider SDK imports exist outside the gateway."""
    violations = []
    for root, _, files in os.walk("agentic_core"):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file).replace("\\", "/")
                if file_path in ALLOWED_IMPORT_PATHS:
                    continue

                with open(file_path, encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=file_path)
                        scanner = ImportScanner(file_path)
                        scanner.visit(tree)
                        for name, line in scanner.violations:
                            violations.append(f"{file_path}:{line} -> Forbidden import: {name}")
                    except SyntaxError as e:
                        violations.append(f"SyntaxError in {file_path}: {e}")

    assert not violations, "\n".join(violations)


@pytest.fixture
def gateway():
    """Fixture for a fresh SovereignLLMGateway instance."""
    SovereignLLMGateway.reset_instance()
    return SovereignLLMGateway()


@pytest.mark.governance
@pytest.mark.asyncio
async def test_deterministic_agent_fails(gateway):
    """Prove that a deterministic agent calling route_generation raises SovereigntyViolation."""
    request = GenerationRequest(
        prompt="test prompt",
        agent_id="ClassificationComplianceHealer",  # A DETERMINISTIC agent
    )
    with pytest.raises(SovereigntyViolation, match="is DETERMINISTIC and cannot call the LLM gateway"):
        await gateway.route_generation(request)


@pytest.mark.governance
@pytest.mark.asyncio
async def test_llm_agent_non_allowed_model_fails(gateway):
    """Prove that an LLM agent calling a non-allowed model raises SovereigntyViolation."""
    request = GenerationRequest(
        prompt="test prompt",
        agent_id="ExecutiveStrategyAgent",  # LLM_API agent
        model="gpt-3.5-turbo",  # Not in allowed_models for this agent
    )
    with pytest.raises(SovereigntyViolation, match="is not allowed to use model"):
        await gateway.route_generation(request)


@pytest.mark.governance
@pytest.mark.asyncio
async def test_unregistered_agent_fails(gateway):
    """Prove that an unregistered agent raises SovereigntyViolation."""
    request = GenerationRequest(
        prompt="test prompt",
        agent_id="UnregisteredAgent",
    )
    with pytest.raises(SovereigntyViolation, match="not found in registry"):
        await gateway.route_generation(request)


@pytest.mark.governance
@pytest.mark.asyncio
@patch("agentic_core.L2_execution.enforcement.SovereignLLMGateway.SovereignLLMGateway._call_provider")
async def test_llm_agent_allowed_model_passes(mock_call_provider, gateway):
    """Prove that an LLM agent with an allowed model passes and calls the provider."""
    mock_call_provider.return_value = {
        "content": "mock response",
        "tokens": 10,
        "provider": "openai",
        "model": "gpt-4",
    }
    request = GenerationRequest(
        prompt="test prompt",
        agent_id="ExecutiveStrategyAgent",
        model="gpt-4",
        provider="openai",
    )
    response = await gateway.route_generation(request)
    assert response.content == "mock response"
    mock_call_provider.assert_called_once()


@pytest.mark.governance
def test_p5_determinism_digest_is_stable():
    """P5 digest must be deterministic across repeated calls."""
    digest_a = compute_p5_determinism_digest()
    digest_b = compute_p5_determinism_digest()
    assert digest_a == digest_b


@pytest.mark.governance
def test_p5_determinism_digest_is_hex():
    """P5 digest must be a lowercase 64-char hex string."""
    digest = compute_p5_determinism_digest()
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


@pytest.mark.governance
@pytest.mark.xfail(strict=True, reason="Negative control: This test should fail due to policy violation")
@pytest.mark.asyncio
async def test_negative_control_tamper_fails():
    """Negative control to ensure tampering with the registry is caught."""
    if not os.getenv("P5_NEGCTRL_TAMPER") == "1":
        pytest.skip("Skipping negative control tamper test")

    SovereignLLMGateway.reset_instance()
    gateway = SovereignLLMGateway()

    # Tamper with the registry at runtime
    original_profile = AGENT_REGISTRY["ExecutiveStrategyAgent"]
    tampered_profile = replace(original_profile, allowed_models=("gpt-3.5-turbo",))

    with patch.dict(AGENT_REGISTRY, {"ExecutiveStrategyAgent": tampered_profile}):
        request = GenerationRequest(
            prompt="test prompt",
            agent_id="ExecutiveStrategyAgent",
            model="gpt-4",  # This model is no longer allowed after tampering
            provider="openai",
        )
        # This should fail because the policy was violated at runtime
        await gateway.route_generation(request)
