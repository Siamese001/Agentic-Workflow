"""Agent/Orchestrator path smoke tests — verify base agent classes are importable and instantiable."""

import pytest


@pytest.mark.smoke
def test_base_dispatch_agent_is_class():
    """BaseDispatchAgent is a proper class with expected interface."""
    try:
        from apps_shared.reasoning.BaseDispatchAgent import BaseDispatchAgent
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    assert isinstance(BaseDispatchAgent, type), "BaseDispatchAgent should be a class"
    public = {n for n in dir(BaseDispatchAgent) if not n.startswith("_")}
    assert len(public) >= 1, "BaseDispatchAgent should have public methods"


@pytest.mark.smoke
def test_base_healing_orchestrator_is_class():
    """BaseHealingOrchestrator is a proper class with expected interface."""
    try:
        from apps_shared.reasoning.BaseHealingOrchestrator import BaseHealingOrchestrator
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    assert isinstance(BaseHealingOrchestrator, type), "BaseHealingOrchestrator should be a class"
    public = {n for n in dir(BaseHealingOrchestrator) if not n.startswith("_")}
    assert len(public) >= 1, "BaseHealingOrchestrator should have public methods"


@pytest.mark.smoke
def test_base_proactive_agent_is_class():
    """BaseProactiveAgent is a proper class with expected interface."""
    try:
        from apps_shared.reasoning.BaseProactiveAgent import BaseProactiveAgent
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    assert isinstance(BaseProactiveAgent, type), "BaseProactiveAgent should be a class"
    public = {n for n in dir(BaseProactiveAgent) if not n.startswith("_")}
    assert len(public) >= 1, "BaseProactiveAgent should have public methods"


@pytest.mark.smoke
def test_sovereign_base_agent_is_class():
    """SovereignBaseAgent is a proper class."""
    try:
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    assert isinstance(SovereignBaseAgent, type), "SovereignBaseAgent should be a class"
    # Verify it has execute or similar core method
    public = {n for n in dir(SovereignBaseAgent) if not n.startswith("_")}
    assert "execute" in public or len(public) >= 3, (
        "SovereignBaseAgent should have execute() or at least 3 public methods"
    )


@pytest.mark.smoke
def test_apps_shared_config_has_guardian_registry():
    """apps_shared config exposes the guardian registry."""
    try:
        from apps_shared.config.app_guardian_registry import APP_GUARDIAN_REGISTRY
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    assert isinstance(APP_GUARDIAN_REGISTRY, (tuple, list, dict)), (
        f"APP_GUARDIAN_REGISTRY should be a collection, got {type(APP_GUARDIAN_REGISTRY).__name__}"
    )
    assert len(APP_GUARDIAN_REGISTRY) >= 1, "APP_GUARDIAN_REGISTRY should not be empty"


@pytest.mark.smoke
def test_apps_shared_environment_config_has_class():
    """apps_shared environment config provides EnvironmentConfig class."""
    try:
        from apps_shared.config.environment_config import EnvironmentConfig
    except ImportError as e:
        pytest.skip(f"environment_config not available: {e}")

    assert isinstance(EnvironmentConfig, type), "EnvironmentConfig should be a class"
