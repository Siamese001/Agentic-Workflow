# /tests/unit/test_phase1_foundations.py
# Scope: Rigorous testing of Config, Domain entities, and Exception handling.
# Mandatory: 100% Pass Rate required.

import pytest
import os
from pydantic import ValidationError as PydanticValidationError
from agentic_core.config.settings import Settings, get_settings
from agentic_core.domain.entities import AgentConfig
from agentic_core.domain.exceptions import AgenticCoreError, ConfigurationError
from agentic_core.utils.logging import setup_logging

# --- TestCase 1: Configuration Loading & Defaults ---
def test_settings_defaults_and_env_override(monkeypatch):
    """
    Verify defaults are set correctly and ENV vars override them.
    Edge Case: Empty strings or invalid types in ENV.
    """
    # 1. Test Defaults
    monkeypatch.delenv("APP_NAME", raising=False)
    default_settings = Settings()
    assert default_settings.ENVIRONMENT == "dev"
    assert default_settings.LOG_LEVEL == "INFO"

    # 2. Test Override
    monkeypatch.setenv("APP_NAME", "TestAgent")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("ENVIRONMENT", "prod")
    
    # Force clear cache to reload
    get_settings.cache_clear()
    new_settings = get_settings()
    
    assert new_settings.APP_NAME == "TestAgent"
    assert new_settings.LOG_LEVEL == "DEBUG"
    assert new_settings.ENVIRONMENT == "prod"

# --- TestCase 2: Entity Constraints & Validation ---
def test_agent_config_validation():
    """
    Verify Pydantic constraints on Domain Entities.
    Edge Cases: Temperature out of bounds, Empty strings.
    """
    # 1. Valid Creation
    valid_conf = AgentConfig(name="Agent007", role="Spy")
    assert valid_conf.id is not None
    assert valid_conf.temperature == 0.0  # Default check

    # 2. Invalid Temperature (Edge Case: > 2.0)
    with pytest.raises(PydanticValidationError) as excinfo:
        AgentConfig(name="HotAgent", role="Tester", temperature=2.1)
    assert "less than or equal to 2" in str(excinfo.value)

    # 3. Invalid Temperature (Edge Case: < 0.0)
    with pytest.raises(PydanticValidationError) as excinfo:
        AgentConfig(name="ColdAgent", role="Tester", temperature=-0.1)
    assert "greater than or equal to 0" in str(excinfo.value)

    # 4. Missing Required Field
    with pytest.raises(PydanticValidationError):
        AgentConfig(name="NoRoleAgent") # Missing role

# --- TestCase 3: Custom Exception Hierarchy ---
def test_custom_exception_propagation():
    """
    Verify strict inheritance and code attributes of custom exceptions.
    """
    try:
        raise ConfigurationError("Missing API Key")
    except AgenticCoreError as e:
        # Must catch as base class
        assert e.code == "CONFIG_ERROR"
        assert str(e) == "Missing API Key"
        assert isinstance(e, Exception)

# --- TestCase 4: Logging Singleton & Safety ---
def test_logging_setup_idempotency():
    """
    Ensure setup_logging can be called multiple times without duplicate handlers.
    Edge Case: Spamming setup_logging.
    """
    logger = setup_logging()
    initial_handlers = len(logger.handlers)
    
    # Call again
    setup_logging()
    setup_logging()
    
    # Should not increase handler count
    assert len(logger.handlers) == initial_handlers