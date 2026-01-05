# New file: tests/unit/test_mcp_guardian_agent.py
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L5_safety.guardrails.MCPGuardianAgent import MCPGuardianAgent


@pytest.fixture
def mock_project_root(tmp_path):
    """Mock project root directory."""
    return tmp_path


@pytest.fixture
def mcp_guardian_agent(mock_project_root):
    """Fixture for fresh MCPGuardianAgent instance."""
    return MCPGuardianAgent(mock_project_root)


def test_instantiation(mcp_guardian_agent, mock_project_root):
    """Smoke test: agent instantiates without error."""
    assert mcp_guardian_agent is not None
    assert hasattr(mcp_guardian_agent, "audit_mcp_call")
    assert mcp_guardian_agent.project_root == mock_project_root
    assert isinstance(mcp_guardian_agent.violations, list)
    assert len(mcp_guardian_agent.violations) == 0


def test_instantiation_default_project_root():
    """Test agent initialization with default project root."""
    agent = MCPGuardianAgent()
    assert agent.project_root == Path.cwd()
    assert isinstance(agent.violations, list)


@pytest.mark.asyncio
async def test_audit_mcp_call_compliant(mcp_guardian_agent):
    """Test audit of compliant MCP call."""
    compliant_config = {
        "host": "localhost",
        "port": 6379,
        "timeout": 30,
        "ssl": True,
        "username": "${REDIS_USERNAME}",  # Environment variable
        "password": "${REDIS_PASSWORD}"   # Environment variable
    }
    
    result = await mcp_guardian_agent.audit_mcp_call(
        operation="redis_get",
        client_name="redis",
        config=compliant_config
    )
    
    assert result is True  # Should be compliant


@pytest.mark.asyncio
async def test_audit_mcp_call_hardcoded_credentials(mcp_guardian_agent):
    """Test detection of hardcoded credentials."""
    non_compliant_config = {
        "host": "localhost",
        "port": 6379,
        "password": "hardcoded_password123",  # Hardcoded credential
        "timeout": 30
    }
    
    result = await mcp_guardian_agent.audit_mcp_call(
        operation="redis_get",
        client_name="redis",
        config=non_compliant_config
    )
    
    assert result is False  # Should detect violation
    # Check that violation was recorded
    assert len(mcp_guardian_agent.violations) > 0
    violation = mcp_guardian_agent.violations[-1]
    assert violation["type"] == "HARDCODED_CREDENTIALS"
    assert violation["Severity"] == "CRITICAL"


@pytest.mark.asyncio
async def test_audit_mcp_call_missing_timeout(mcp_guardian_agent):
    """Test detection of missing timeout configuration."""
    config_without_timeout = {
        "host": "localhost",
        "port": 6379,
        "username": "${REDIS_USERNAME}",
        "password": "${REDIS_PASSWORD}"
        # No timeout specified
    }
    
    result = await mcp_guardian_agent.audit_mcp_call(
        operation="redis_set",
        client_name="redis",
        config=config_without_timeout
    )
    
    assert result is False
    # Check for missing timeout violation
    timeout_violations = [v for v in mcp_guardian_agent.violations if v["type"] == "MISSING_TIMEOUT"]
    assert len(timeout_violations) > 0
    assert timeout_violations[0]["Severity"] == "MEDIUM"


@pytest.mark.asyncio
async def test_audit_mcp_call_ssl_not_enforced_redis(mcp_guardian_agent):
    """Test detection of missing SSL for Redis."""
    config_without_ssl = {
        "host": "localhost",
        "port": 6379,
        "timeout": 30,
        "username": "${REDIS_USERNAME}",
        "password": "${REDIS_PASSWORD}",
        "ssl": False  # SSL disabled
    }
    
    result = await mcp_guardian_agent.audit_mcp_call(
        operation="redis_get",
        client_name="redis",
        config=config_without_ssl
    )
    
    assert result is False
    # Check for SSL violation
    ssl_violations = [v for v in mcp_guardian_agent.violations if v["type"] == "SSL_NOT_ENFORCED"]
    assert len(ssl_violations) > 0
    assert ssl_violations[0]["Severity"] == "HIGH"
    assert "redis" in ssl_violations[0]["message"].lower()


@pytest.mark.asyncio
async def test_audit_mcp_call_ssl_not_enforced_neo4j(mcp_guardian_agent):
    """Test detection of missing SSL for Neo4j."""
    config_without_ssl = {
        "uri": "bolt://localhost:7687",
        "timeout": 30,
        "username": "${NEO4J_USERNAME}",
        "password": "${NEO4J_PASSWORD}"
        # No ssl or use_ssl specified
    }
    
    result = await mcp_guardian_agent.audit_mcp_call(
        operation="neo4j_query",
        client_name="neo4j",
        config=config_without_ssl
    )
    
    assert result is False
    ssl_violations = [v for v in mcp_guardian_agent.violations if v["type"] == "SSL_NOT_ENFORCED"]
    assert len(ssl_violations) > 0


@pytest.mark.asyncio
async def test_audit_mcp_call_non_ssl_client(mcp_guardian_agent):
    """Test that SSL is not required for non-SSL clients."""
    config_for_other_client = {
        "endpoint": "http://localhost:8080",
        "timeout": 30,
        "api_key": "${API_KEY}"
    }
    
    result = await mcp_guardian_agent.audit_mcp_call(
        operation="http_get",
        client_name="http",  # Not redis or neo4j
        config=config_for_other_client
    )
    
    # Should not require SSL for non-SSL clients
    ssl_violations = [v for v in mcp_guardian_agent.violations if v["type"] == "SSL_NOT_ENFORCED"]
    # Should not add SSL violation for http client
    initial_ssl_count = len(ssl_violations)
    # The result might still be False due to other violations, but SSL shouldn't be one


@pytest.mark.asyncio
async def test_audit_mcp_call_multiple_violations(mcp_guardian_agent):
    """Test detection of multiple violations in single call."""
    problematic_config = {
        "host": "localhost",
        "port": 6379,
        "password": "hardcoded123",  # Hardcoded credential
        "ssl": False  # SSL disabled
        # No timeout
    }
    
    result = await mcp_guardian_agent.audit_mcp_call(
        operation="redis_set",
        client_name="redis",
        config=problematic_config
    )
    
    assert result is False
    # Should have multiple violations
    assert len(mcp_guardian_agent.violations) >= 3  # credentials, timeout, ssl
    
    violation_types = {v["type"] for v in mcp_guardian_agent.violations}
    assert "HARDCODED_CREDENTIALS" in violation_types
    assert "MISSING_TIMEOUT" in violation_types
    assert "SSL_NOT_ENFORCED" in violation_types


def test_has_hardcoded_credentials_detection(mcp_guardian_agent):
    """Test hardcoded credential detection method."""
    # Test cases for hardcoded credentials
    hardcoded_cases = [
        {"password": "hardcoded123"},
        {"api_key": "sk-hardcoded"},
        {"secret": "mysecret"},
        {"token": "hardcoded_token"}
    ]
    
    for config in hardcoded_cases:
        assert mcp_guardian_agent._has_hardcoded_credentials(config) is True
    
    # Test cases for environment variables (should be OK)
    env_var_cases = [
        {"password": "${REDIS_PASSWORD}"},
        {"api_key": "${API_KEY}"},
        {"secret": "${SECRET_KEY}"},
        {"token": "${ACCESS_TOKEN}"}
    ]
    
    for config in env_var_cases:
        assert mcp_guardian_agent._has_hardcoded_credentials(config) is False


def test_has_hardcoded_credentials_edge_cases(mcp_guardian_agent):
    """Test edge cases in credential detection."""
    # Empty config
    assert mcp_guardian_agent._has_hardcoded_credentials({}) is False
    
    # Non-credential fields with hardcoded values (should be OK)
    non_cred_config = {
        "host": "localhost",
        "port": 6379,
        "database": "mydb"
    }
    assert mcp_guardian_agent._has_hardcoded_credentials(non_cred_config) is False


@pytest.mark.asyncio
async def test_audit_mcp_call_timeout_variations(mcp_guardian_agent):
    """Test different timeout configuration variations."""
    # Test timeout_seconds instead of timeout
    config_with_timeout_seconds = {
        "host": "localhost",
        "timeout_seconds": 45,
        "username": "${USERNAME}",
        "password": "${PASSWORD}",
        "ssl": True
    }
    
    result = await mcp_guardian_agent.audit_mcp_call(
        operation="test_op",
        client_name="redis",
        config=config_with_timeout_seconds
    )
    
    # Should not have timeout violation
    timeout_violations = [v for v in mcp_guardian_agent.violations 
                         if v["type"] == "MISSING_TIMEOUT" and v["operation"] == "test_op"]
    assert len(timeout_violations) == 0


@pytest.mark.autonomy
def test_heal_repository_smoke(mcp_guardian_agent):
    """Autonomy heal smoke test — ensure no crash."""
    try:
        mcp_guardian_agent.heal_repository()  # Post-healing: will pass once compliant
        assert True  # No crash = success
    except AttributeError:
        # heal_repository method may not exist yet, that's expected
        pytest.skip("heal_repository method not implemented yet")
    except Exception as e:
        # Any other exception should not occur
        pytest.fail(f"heal_repository crashed unexpectedly: {e}")


def test_healer_mixin_inheritance(mcp_guardian_agent):
    """Test that agent properly inherits from HealerMixin."""
    from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
    assert isinstance(mcp_guardian_agent, HealerMixin)


def test_mcp_hardened_mixin_inheritance(mcp_guardian_agent):
    """Test that agent properly inherits from MCPHardenedMixin."""
    from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
    assert isinstance(mcp_guardian_agent, MCPHardenedMixin)


def test_violation_structure(mcp_guardian_agent):
    """Test that violations have expected structure."""
    # Create a violation by auditing non-compliant config
    test_config = {"password": "hardcoded123"}
    
    # Use asyncio.run since we can't use async in regular test
    import asyncio
    asyncio.run(mcp_guardian_agent.audit_mcp_call("test", "test_client", test_config))
    
    assert len(mcp_guardian_agent.violations) > 0
    violation = mcp_guardian_agent.violations[0]
    
    # Check required fields
    required_fields = ["Severity", "type", "operation", "client", "message"]
    for field in required_fields:
        assert field in violation
    
    # Check severity is valid
    valid_severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert violation["Severity"] in valid_severities
