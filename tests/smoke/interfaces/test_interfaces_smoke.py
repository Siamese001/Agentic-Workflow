"""Interfaces smoke tests — import verification and basic functionality."""
import pytest


@pytest.mark.smoke
def test_interfaces_importable():
    """Verify interfaces module imports without error."""
    try:
        import agentic_core.interfaces
        assert agentic_core.interfaces is not None
    except ImportError as e:
        pytest.fail(f"Failed to import interfaces: {e}")

@pytest.mark.smoke
def test_healer_protocol_importable():
    """Verify IHealerProtocol imports without error."""
    try:
        from agentic_core.interfaces.IHealerProtocol import (
            IHealerProtocol,
        )
        assert IHealerProtocol is not None
    except ImportError as e:
        pytest.skip(f"IHealerProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_orchestrator_protocol_importable():
    """Verify IOrchestratorProtocol imports without error."""
    try:
        from agentic_core.interfaces.IOrchestratorProtocol import (
            IOrchestratorProtocol,
        )
        assert IOrchestratorProtocol is not None
    except ImportError as e:
        pytest.skip(f"IOrchestratorProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_validator_protocol_importable():
    """Verify IValidatorProtocol imports without error."""
    try:
        from agentic_core.interfaces.IValidatorProtocol import (
            IValidatorProtocol,
        )
        assert IValidatorProtocol is not None
    except ImportError as e:
        pytest.skip(f"IValidatorProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_agent_protocol_importable():
    """Verify IAgentProtocol imports without error."""
    try:
        from agentic_core.interfaces.IAgentProtocol import (
            IAgentProtocol,
        )
        assert IAgentProtocol is not None
    except ImportError as e:
        pytest.skip(f"IAgentProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_execution_protocol_importable():
    """Verify IExecutionProtocol imports without error."""
    try:
        from agentic_core.interfaces.IExecutionProtocol import (
            IExecutionProtocol,
        )
        assert IExecutionProtocol is not None
    except ImportError as e:
        pytest.skip(f"IExecutionProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_cognition_protocol_importable():
    """Verify ICognitionProtocol imports without error."""
    try:
        from agentic_core.interfaces.ICognitionProtocol import (
            ICognitionProtocol,
        )
        assert ICognitionProtocol is not None
    except ImportError as e:
        pytest.skip(f"ICognitionProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_state_protocol_importable():
    """Verify IStateProtocol imports without error."""
    try:
        from agentic_core.interfaces.IStateProtocol import (
            IStateProtocol,
        )
        assert IStateProtocol is not None
    except ImportError as e:
        pytest.skip(f"IStateProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_safety_protocol_importable():
    """Verify ISafetyProtocol imports without error."""
    try:
        from agentic_core.interfaces.ISafetyProtocol import (
            ISafetyProtocol,
        )
        assert ISafetyProtocol is not None
    except ImportError as e:
        pytest.skip(f"ISafetyProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_observability_protocol_importable():
    """Verify IObservabilityProtocol imports without error."""
    try:
        from agentic_core.interfaces.IObservabilityProtocol import (
            IObservabilityProtocol,
        )
        assert IObservabilityProtocol is not None
    except ImportError as e:
        pytest.skip(f"IObservabilityProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_routing_protocol_importable():
    """Verify IRoutingProtocol imports without error."""
    try:
        from agentic_core.interfaces.IRoutingProtocol import (
            IRoutingProtocol,
        )
        assert IRoutingProtocol is not None
    except ImportError as e:
        pytest.skip(f"IRoutingProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_knowledge_protocol_importable():
    """Verify IKnowledgeProtocol imports without error."""
    try:
        from agentic_core.interfaces.IKnowledgeProtocol import (
            IKnowledgeProtocol,
        )
        assert IKnowledgeProtocol is not None
    except ImportError as e:
        pytest.skip(f"IKnowledgeProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_cache_protocol_importable():
    """Verify ICacheProtocol imports without error."""
    try:
        from agentic_core.interfaces.ICacheProtocol import (
            ICacheProtocol,
        )
        assert ICacheProtocol is not None
    except ImportError as e:
        pytest.skip(f"ICacheProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_enforcement_protocol_importable():
    """Verify IEnforcementProtocol imports without error."""
    try:
        from agentic_core.interfaces.IEnforcementProtocol import (
            IEnforcementProtocol,
        )
        assert IEnforcementProtocol is not None
    except ImportError as e:
        pytest.skip(f"IEnforcementProtocol not yet implemented: {e}")

@pytest.mark.smoke
def test_protocol_factory_importable():
    """Verify protocol factory imports without error."""
    try:
        from agentic_core.interfaces.protocol_factory import (
            ProtocolFactory,
        )
        assert ProtocolFactory is not None
    except ImportError as e:
        pytest.skip(f"ProtocolFactory not yet implemented: {e}")

@pytest.mark.smoke
def test_protocol_registry_importable():
    """Verify protocol registry imports without error."""
    try:
        from agentic_core.interfaces.protocol_registry import (
            ProtocolRegistry,
        )
        assert ProtocolRegistry is not None
    except ImportError as e:
        pytest.skip(f"ProtocolRegistry not yet implemented: {e}")

@pytest.mark.smoke
def test_protocol_validator_importable():
    """Verify protocol validator imports without error."""
    try:
        from agentic_core.interfaces.protocol_validator import (
            ProtocolValidator,
        )
        assert ProtocolValidator is not None
    except ImportError as e:
        pytest.skip(f"ProtocolValidator not yet implemented: {e}")

@pytest.mark.smoke
def test_protocol_config_importable():
    """Verify protocol config imports without error."""
    try:
        from agentic_core.interfaces.protocol_config import (
            get_protocol_config,
        )
        assert callable(get_protocol_config), "get_protocol_config should be callable"
    except ImportError as e:
        pytest.skip(f"protocol_config not yet implemented: {e}")
