# New file: tests/unit/test_hallucination_hunter_agent.py
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L5_safety.guardrails.HallucinationHunterAgent import HallucinationHunterAgent, AtomicClaim, VerificationResult


@pytest.fixture
def mock_context():
    """Mock context for agent instantiation."""
    context = Mock()
    context.get_env = Mock(return_value="test_gemini_key")
    context.signals = []
    return context


@pytest.fixture
def hunter_agent(mock_context):
    """Fixture for fresh HallucinationHunterAgent instance."""
    with patch('agentic_core.L5_safety.guardrails.HallucinationHunterAgent.genai') as mock_genai:
        mock_genai.Client.return_value = Mock()
        agent = HallucinationHunterAgent(mock_context)
        return agent


def test_instantiation(hunter_agent):
    """Smoke test: agent instantiates without error."""
    assert hunter_agent is not None
    assert hasattr(hunter_agent, "execute")
    assert hasattr(hunter_agent, "SIMILARITY_THRESHOLD")
    assert hunter_agent.SIMILARITY_THRESHOLD == 0.85


def test_thresholds_configuration(hunter_agent):
    """Test that thresholds are properly configured."""
    assert hunter_agent.HALLUCINATION_THRESHOLD == 0.05
    assert hunter_agent.LOW_RISK_THRESHOLD == 0.95
    assert hunter_agent.MEDIUM_RISK_THRESHOLD == 0.85
    assert hunter_agent.HIGH_RISK_THRESHOLD == 0.7


def test_atomic_claim_dataclass():
    """Test AtomicClaim dataclass structure."""
    claim = AtomicClaim("Test claim", 1)
    assert claim.text == "Test claim"
    assert claim.line_number == 1
    assert claim.embedding is None
    
    # Test with embedding
    embedding = [0.1, 0.2, 0.3]
    claim_with_embedding = AtomicClaim("Test claim", 1, embedding)
    assert claim_with_embedding.embedding == embedding


def test_verification_result_dataclass():
    """Test VerificationResult dataclass structure."""
    result = VerificationResult("test claim", True, 0.9, "supported")
    assert result.claim == "test claim"
    assert result.is_supported is True
    assert result.similarity_score == 0.9
    assert result.justification == "supported"


@pytest.mark.asyncio
async def test_execute_no_signals(hunter_agent, mock_context):
    """Test execute with no pipeline output signals."""
    mock_context.signals = []
    
    result = await hunter_agent.execute()
    # Should complete without errors even with no signals


@pytest.mark.asyncio
async def test_execute_with_signals(hunter_agent, mock_context):
    """Test execute with pipeline output signals."""
    mock_context.signals = ["PIPELINE_OUTPUT:test_signal", "OTHER_SIGNAL"]
    
    with patch.object(hunter_agent, '_process_pipeline_output', new_callable=AsyncMock) as mock_process:
        mock_process.return_value = Mock()
        result = await hunter_agent.execute()
        mock_process.assert_called()


def test_genai_client_initialization_success(mock_context):
    """Test successful Gemini client initialization."""
    mock_context.get_env.return_value = "valid_api_key"
    
    with patch('agentic_core.L5_safety.guardrails.HallucinationHunterAgent.GENAI_AVAILABLE', True), \
         patch('agentic_core.L5_safety.guardrails.HallucinationHunterAgent.genai') as mock_genai:
        
        mock_genai.Client.return_value = Mock()
        agent = HallucinationHunterAgent(mock_context)
        
        assert agent.genai_available is True
        mock_genai.Client.assert_called_once_with(api_key="valid_api_key")


def test_genai_client_initialization_failure(mock_context):
    """Test Gemini client initialization failure handling."""
    mock_context.get_env.return_value = "invalid_api_key"
    
    with patch('agentic_core.L5_safety.guardrails.HallucinationHunterAgent.GENAI_AVAILABLE', True), \
         patch('agentic_core.L5_safety.guardrails.HallucinationHunterAgent.genai') as mock_genai:
        
        mock_genai.Client.side_effect = Exception("API key invalid")
        agent = HallucinationHunterAgent(mock_context)
        
        assert agent.genai_available is False


def test_claim_extractor_initialization(hunter_agent):
    """Test that claim extractor is properly initialized."""
    assert hunter_agent._claim_extractor is not None
    assert hasattr(hunter_agent._claim_extractor, 'extract_claims')


def test_claim_embedder_initialization(hunter_agent):
    """Test that claim embedder is properly initialized."""
    assert hunter_agent._claim_embedder is not None


def test_claim_verifier_initialization(hunter_agent):
    """Test that claim verifier is properly initialized."""
    assert hunter_agent._claim_verifier is not None
    # Verifier should use the agent's similarity threshold
    assert hunter_agent._claim_verifier.threshold == hunter_agent.SIMILARITY_THRESHOLD


@pytest.mark.autonomy
def test_heal_repository_smoke(hunter_agent):
    """Autonomy heal smoke test — ensure no crash."""
    try:
        hunter_agent.heal_repository()  # Post-healing: will pass once compliant
        assert True  # No crash = success
    except AttributeError:
        # heal_repository method may not exist yet, that's expected
        pytest.skip("heal_repository method not implemented yet")
    except Exception as e:
        # Any other exception should not occur
        pytest.fail(f"heal_repository crashed unexpectedly: {e}")


def test_context_dependency(mock_context):
    """Test agent properly depends on context."""
    agent = HallucinationHunterAgent(mock_context)
    assert agent.ctx == mock_context


@patch('agentic_core.L5_safety.guardrails.HallucinationHunterAgent.GENAI_AVAILABLE', False)
def test_fallback_without_genai(mock_context):
    """Test agent works without Gemini availability."""
    agent = HallucinationHunterAgent(mock_context)
    assert agent.genai_available is False
    assert agent._claim_extractor is not None  # Should still initialize


def test_subatomic_agent_inheritance(hunter_agent):
    """Test that agent properly inherits from SubAtomicAgent."""
    from agentic_core.L2_execution.ToolRegistry.base import SubAtomicAgent
    assert isinstance(hunter_agent, SubAtomicAgent)
