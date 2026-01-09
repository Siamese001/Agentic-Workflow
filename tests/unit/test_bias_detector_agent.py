# New file: tests/unit/test_bias_detector_agent.py
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L5_safety.guardrails.BiasDetectorAgent import BiasDetectorAgent


@pytest.fixture
def mock_context():
    """Mock context for agent instantiation."""
    context = Mock()
    return context


@pytest.fixture
def bias_detector_agent(mock_context):
    """Fixture for fresh BiasDetectorAgent instance."""
    return BiasDetectorAgent(mock_context)


def test_instantiation(bias_detector_agent):
    """Smoke test: agent instantiates without error."""
    assert bias_detector_agent is not None
    assert hasattr(bias_detector_agent, "run")
    assert hasattr(bias_detector_agent, "heal_repository")


@patch('agentic_core.L5_safety.guardrails.BiasDetectorAgent.detect_bias')
def test_run_clean_text(mock_detect_bias, bias_detector_agent):
    """Test bias detection on neutral text."""
    mock_detect_bias.return_value = {
        "bias_detected": False,
        "score": 0.1,
        "patterns": []
    }
    
    clean_text = "The software development process requires careful planning and execution."
    result = bias_detector_agent.run(clean_text, "test_workflow_123")
    
    assert isinstance(result, dict)
    assert "bias_detected" in result
    assert result["bias_detected"] is False
    mock_detect_bias.assert_called_once()


@patch('agentic_core.L5_safety.guardrails.BiasDetectorAgent.detect_bias')
def test_run_biased_text(mock_detect_bias, bias_detector_agent):
    """Test detection of potentially biased content."""
    mock_detect_bias.return_value = {
        "bias_detected": True,
        "score": 0.8,
        "patterns": ["gender_bias", "age_bias"]
    }
    
    potentially_biased_text = "Young men are naturally better at programming than others."
    result = bias_detector_agent.run(potentially_biased_text, "test_workflow_456")
    
    assert isinstance(result, dict)
    assert "bias_detected" in result
    assert result["bias_detected"] is True
    mock_detect_bias.assert_called_once()


@patch('agentic_core.L5_safety.guardrails.BiasDetectorAgent.detect_bias')
def test_run_without_workflow_id(mock_detect_bias, bias_detector_agent):
    """Test bias detection without workflow_id (no logging)."""
    mock_detect_bias.return_value = {
        "bias_detected": False,
        "score": 0.2,
        "patterns": []
    }
    
    text = "This is neutral content for testing."
    result = bias_detector_agent.run(text)
    
    assert isinstance(result, dict)
    mock_detect_bias.assert_called_once_with(bias_detector_agent.context, text, "")


@patch('agentic_core.L5_safety.guardrails.BiasDetectorAgent.detect_bias')
def test_run_with_workflow_logging(mock_detect_bias, bias_detector_agent):
    """Test bias detection with workflow feedback logging."""
    mock_detect_bias.return_value = {
        "bias_detected": True,
        "score": 0.7,
        "patterns": ["implicit_bias", "cultural_bias"]
    }
    
    with patch.object(bias_detector_agent, 'log_feedback') as mock_log:
        text = "Potentially problematic content for testing."
        result = bias_detector_agent.run(text, "workflow_with_logging")
        
        assert isinstance(result, dict)
        mock_log.assert_called_once_with(
            "workflow_with_logging",
            "bias_detection", 
            "warning",
            {"patterns_found": 2}
        )


@pytest.mark.autonomy
def test_heal_repository_smoke(bias_detector_agent):
    """Autonomy heal smoke test — ensure no crash."""
    result = bias_detector_agent.heal_repository()
    
    # BiasDetectorAgent is operational guardrail - should skip healing
    assert isinstance(result, dict)
    assert result.get("skipped") == 1


def test_heal_repository_parameters(bias_detector_agent):
    """Test heal_repository accepts expected parameters."""
    result = bias_detector_agent.heal_repository(
        dry_run=False,
        execute=True, 
        depth=1,
        max_depth=2
    )
    
    assert isinstance(result, dict)
    assert result.get("skipped") == 1


def test_timeout_decorator_applied(bias_detector_agent):
    """Test that heal_repository has timeout decorator applied."""
    # The method should have timeout applied - we verify it exists
    assert hasattr(bias_detector_agent.heal_repository, '__wrapped__')


@patch('agentic_core.L5_safety.guardrails.BiasDetectorAgent.detect_bias')
def test_run_edge_cases(mock_detect_bias, bias_detector_agent):
    """Test edge cases like empty text."""
    mock_detect_bias.return_value = {
        "bias_detected": False,
        "score": 0.0,
        "patterns": []
    }
    
    # Test empty string
    result = bias_detector_agent.run("", "empty_test")
    assert isinstance(result, dict)
    
    # Test whitespace only
    result = bias_detector_agent.run("   ", "whitespace_test")
    assert isinstance(result, dict)
    
    assert mock_detect_bias.call_count == 2
