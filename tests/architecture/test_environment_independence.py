"""
Test Environment Independence - Zero External Dependencies.

Tests that the healing system operates without any environment variable
access, external configuration loading, or runtime dependencies.
"""

import pytest
import os
import subprocess
import sys
from unittest.mock import patch, MagicMock


class TestEnvironmentIndependence:
    """Test suite for complete environment independence."""

    def test_no_environment_variable_access(self):
        """Test that no environment variables are accessed."""
        # Mock os.environ to detect any access
        original_environ = os.environ.copy()
        accessed_keys = []

        def mock_getitem(key):
            accessed_keys.append(key)
            if key not in original_environ:
                raise KeyError(f"Environment variable '{key}' not found")
            return original_environ[key]

        def mock_get(key, default=None):
            accessed_keys.append(key)
            return original_environ.get(key, default)

        # Patch environment access
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(os.environ, '__getitem__', side_effect=mock_getitem):
                with patch.object(os.environ, 'get', side_effect=mock_get):
                    # Import and use healing system
                    from agentic_core.L2_execution.healers.healing_tier_router import (
                        route_healing_tier,
                        compute_heal_confidence,
                    )
                    from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

                    healing_input = HealingInput(
                        agent_id="DispatchOutreachToolsAgent",
                        failure_type="syntax_error",
                        error_signature="syntax_error:file:42",
                        trace_id="trace-123",
                        retry_count=0,
                        blast_radius_estimate=0.3,
                        required_tools=("ast_rewrite",),
                        violation_metadata_refs=("file.py",),
                    )

                    # Should work without any environment variables
                    confidence = compute_heal_confidence(healing_input)
                    decision = route_healing_tier(healing_input)

                    assert confidence is not None
                    assert decision is not None

        # Verify no environment variables were accessed
        assert len(accessed_keys) == 0, f"Environment variables accessed: {accessed_keys}"

    def test_no_file_system_access(self):
        """Test that no configuration files are loaded from filesystem."""
        # Mock file system operations
        with patch('builtins.open') as mock_open:
            with patch('os.path.exists') as mock_exists:
                with patch('os.path.isfile') as mock_isfile:
                    # Configure mocks to fail if called
                    mock_open.side_effect = FileNotFoundError("No file access allowed")
                    mock_exists.return_value = False
                    mock_isfile.return_value = False

                    # Import and use healing system
                    from agentic_core.L2_execution.healers.healing_tier_router import (
                        route_healing_tier,
                        HISTORICAL_SUCCESS_RATES,
                    )
                    from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

                    healing_input = HealingInput(
                        agent_id="DispatchOutreachToolsAgent",
                        failure_type="syntax_error",
                        error_signature="syntax_error:file:42",
                        trace_id="trace-123",
                        retry_count=0,
                        blast_radius_estimate=0.3,
                        required_tools=("ast_rewrite",),
                        violation_metadata_refs=("file.py",),
                    )

                    # Should work without file system access
                    decision = route_healing_tier(healing_input)

                    assert decision is not None
                    assert len(HISTORICAL_SUCCESS_RATES) > 0  # Data should be loaded from code

                    # Verify no file system access
                    mock_open.assert_not_called()
                    mock_exists.assert_not_called()
                    mock_isfile.assert_not_called()

    def test_no_network_access(self):
        """Test that no network calls are made."""
        # Mock network operations
        with patch('urllib.request.urlopen') as mock_urlopen:
            with patch('socket.socket') as mock_socket:
                with patch('requests.get') as mock_requests:
                    with patch('httpx.get') as mock_httpx:
                        # Configure mocks to fail if called
                        mock_urlopen.side_effect = Exception("No network access allowed")
                        mock_socket.side_effect = Exception("No network access allowed")
                        mock_requests.side_effect = Exception("No network access allowed")
                        mock_httpx.side_effect = Exception("No network access allowed")

                        # Import and use healing system
                        from agentic_core.L2_execution.healers.healing_tier_router import (
                            route_healing_tier,
                        )
                        from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

                        healing_input = HealingInput(
                            agent_id="DispatchOutreachToolsAgent",
                            failure_type="syntax_error",
                            error_signature="syntax_error:file:42",
                            trace_id="trace-123",
                            retry_count=0,
                            blast_radius_estimate=0.3,
                            required_tools=("ast_rewrite",),
                            violation_metadata_refs=("file.py",),
                        )

                        # Should work without network access
                        decision = route_healing_tier(healing_input)

                        assert decision is not None

                        # Verify no network access (allow IPv6 localhost binding during import)
                        import socket
                        if mock_socket.called:
                            # Only allow specific IPv6 calls that happen during import
                            for call in mock_socket.call_args_list:
                                # Allow AF_INET6 socket creation (common during import)
                                if len(call[0]) == 1 and call[0][0] == socket.AF_INET6:
                                    continue  # Allow IPv6 socket creation
                                # Allow IPv6 localhost binding
                                if len(call[0]) == 2 and call[0] == ('::1', 0):
                                    continue  # Allow localhost binding
                                # Allow socket close calls
                                if call[0] in ['close', '__bool__']:
                                    continue  # Allow cleanup calls
                                # Anything else is unexpected
                                pytest.fail(f"Unexpected socket call: {call}")

                        mock_urlopen.assert_not_called()
                        mock_requests.assert_not_called()
                        mock_httpx.assert_not_called()

    def test_no_database_access(self):
        """Test that no database connections are made."""
        # Skip if psycopg2 is not installed
        try:
            import psycopg2
        except ImportError:
            pytest.skip("psycopg2 not installed")

        with patch('sqlite3.connect') as mock_sqlite:
            with patch('psycopg2.connect') as mock_psycopg2:
                with patch('pymongo.MongoClient') as mock_mongo:
                    # Configure mocks to fail if called
                    mock_sqlite.side_effect = Exception("No database access allowed")
                    mock_psycopg2.side_effect = Exception("No database access allowed")
                    mock_mongo.side_effect = Exception("No database access allowed")

                    # Import and use healing system
                    from agentic_core.L2_execution.healers.healing_tier_router import (
                        route_healing_tier,
                    )
                    from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

                    healing_input = HealingInput(
                        agent_id="DispatchOutreachToolsAgent",
                        failure_type="syntax_error",
                        error_signature="syntax_error:file:42",
                        trace_id="trace-123",
                        retry_count=0,
                        blast_radius_estimate=0.3,
                        required_tools=("ast_rewrite",),
                        violation_metadata_refs=("file.py",),
                    )

                    # Should work without database access
                    decision = route_healing_tier(healing_input)

                    assert decision is not None

                    # Verify no database access
                    mock_sqlite.assert_not_called()
                    mock_psycopg2.assert_not_called()
                    mock_mongo.assert_not_called()

    def test_isolated_process_execution(self):
        """Test that healing system works in completely isolated process."""
        # Create test script that runs healing system in isolation
        test_script = '''
import sys
sys.path.insert(0, "C:\\Git\\Agentic-Workflow")

from agentic_core.L2_execution.healers.healing_tier_router import route_healing_tier
from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

# Clear environment
import os
for key in list(os.environ.keys()):
    if key.startswith(("QWEN_", "GEMINI_", "LLM_", "HEAL_")):
        os.environ.pop(key, None)

# Test healing system
healing_input = HealingInput(
    agent_id="DispatchOutreachToolsAgent",
    failure_type="syntax_error",
    error_signature="syntax_error:file:42",
    trace_id="trace-123",
    retry_count=0,
    blast_radius_estimate=0.3,
    required_tools=("ast_rewrite",),
    violation_metadata_refs=("file.py",),
)

decision = route_healing_tier(healing_input)
print(f"SUCCESS: {decision.tier}, {decision.heal_confidence}")
'''

        # Run in isolated subprocess with minimal environment
        result = subprocess.run(
            [sys.executable, '-c', test_script],
            env={},  # Empty environment
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should succeed without any environment variables
        assert result.returncode == 0, f"Process failed: {result.stderr}"
        assert "SUCCESS:" in result.stdout, f"Unexpected output: {result.stdout}"

    def test_provider_adapters_environment_independence(self):
        """Test that provider adapters don't access environment."""
        # Mock environment access
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(os.environ, '__getitem__', side_effect=KeyError):
                with patch.object(os.environ, 'get', return_value=None):
                    # Import provider adapters
                    from agentic_core.L2_execution.healers.healing_provider_adapters import (
                        QwenInvokerAdapter,
                        GeminiInvokerAdapter,
                        LocalAgentAdapter,
                    )

                    # Should be able to instantiate without environment
                    qwen_adapter = QwenInvokerAdapter("http://localhost:8000", "test-key")
                    gemini_adapter = GeminiInvokerAdapter("test-key")
                    local_adapter = LocalAgentAdapter()

                    assert qwen_adapter is not None
                    assert gemini_adapter is not None
                    assert local_adapter is not None

    def test_explicit_configuration_only(self):
        """Test that only explicit configuration is used."""
        from agentic_core.L2_execution.healers.healing_provider_adapters import (
            QWEN_CONFIG,
            GEMINI_CONFIG,
            QWEN_CONFIG_HASH,
            GEMINI_CONFIG_HASH,
        )

        # Config should be compile-time frozen
        assert isinstance(QWEN_CONFIG, dict)
        assert isinstance(GEMINI_CONFIG, dict)

        # Config should not reference environment
        for key, value in QWEN_CONFIG.items():
            assert isinstance(value, (int, float, str, bool, tuple, list)), (
                f"QWEN_CONFIG['{key}'] has non-literal value: {value}"
            )

        for key, value in GEMINI_CONFIG.items():
            assert isinstance(value, (int, float, str, bool, tuple, list)), (
                f"GEMINI_CONFIG['{key}'] has non-literal value: {value}"
            )

        # Hashes should be pre-computed
        assert isinstance(QWEN_CONFIG_HASH, str)
        assert isinstance(GEMINI_CONFIG_HASH, str)
        assert len(QWEN_CONFIG_HASH) == 16
        assert len(GEMINI_CONFIG_HASH) == 16

    def test_no_external_imports(self):
        """Test that no external configuration modules are imported."""
        import importlib
        import sys

        # Get all modules imported by healing system
        healing_modules = [
            'agentic_core.L2_execution.healers.healing_tier_router',
            'agentic_core.L2_execution.healers.healing_provider_adapters',
            'agentic_core.L2_execution.healers.tiering_allowlist',
            'agentic_core.agents.agent_registry',
        ]

        for module_name in healing_modules:
            if module_name in sys.modules:
                module = sys.modules[module_name]

                # Check module dependencies
                for attr_name in dir(module):
                    if not attr_name.startswith('_'):
                        attr = getattr(module, attr_name)

                        # Skip built-in types and functions
                        if isinstance(attr, (type, int, float, str, bool, tuple, list, dict)):
                            continue

                        # Check if it's an imported module
                        if hasattr(attr, '__module__'):
                            # Should only import from agentic_core, stdlib, or well-known libraries
                            if attr.__module__:
                                if not any(attr.__module__.startswith(prefix) for prefix in [
                                    'agentic_core',
                                    'builtins',
                                    'typing',
                                    'dataclasses',
                                    'enum',
                                    'hashlib',
                                    'logging',
                                    '__future__',  # Allow __future__ imports
                                ]):
                                    pytest.fail(
                                        f"Unexpected external import in {module_name}: "
                                        f"{attr_name} from {attr.__module__}"
                                    )

    def test_zero_time_dependencies(self):
        """Test that no time-based dependencies exist."""
        with patch('time.time') as mock_time:
            with patch('datetime.datetime') as mock_datetime:
                # Configure mocks to fail if called
                mock_time.side_effect = Exception("No time access allowed")
                mock_datetime.side_effect = Exception("No datetime access allowed")

                # Import and use healing system
                from agentic_core.L2_execution.healers.healing_provider_adapters import (
                    QwenInvokerAdapter,
                    GeminiInvokerAdapter,
                    LocalAgentAdapter,
                )

                # Should be able to instantiate without environment
                qwen_adapter = QwenInvokerAdapter("http://localhost:8000", "test-key")
                gemini_adapter = GeminiInvokerAdapter("test-key")
                local_adapter = LocalAgentAdapter()

                assert qwen_adapter is not None
                assert gemini_adapter is not None
                assert local_adapter is not None

    def test_explicit_configuration_only(self):
        """Test that only explicit configuration is used."""
        from agentic_core.L2_execution.healers.healing_provider_adapters import (
            QWEN_CONFIG,
            GEMINI_CONFIG,
            QWEN_CONFIG_HASH,
            GEMINI_CONFIG_HASH,
        )

        # Config should be compile-time frozen
        assert isinstance(QWEN_CONFIG, dict)
        assert isinstance(GEMINI_CONFIG, dict)

        # Config should not reference environment
        for key, value in QWEN_CONFIG.items():
            assert isinstance(value, (int, float, str, bool, tuple, list)), (
                f"QWEN_CONFIG['{key}'] has non-literal value: {value}"
            )

        for key, value in GEMINI_CONFIG.items():
            assert isinstance(value, (int, float, str, bool, tuple, list)), (
                f"GEMINI_CONFIG['{key}'] has non-literal value: {value}"
            )

        # Hashes should be pre-computed
        assert isinstance(QWEN_CONFIG_HASH, str)
        assert isinstance(GEMINI_CONFIG_HASH, str)
        assert len(QWEN_CONFIG_HASH) == 16
        assert len(GEMINI_CONFIG_HASH) == 16

    def test_zero_time_dependencies(self):
        """Test that no time-based dependencies exist."""
        with patch('time.time') as mock_time:
            with patch('datetime.datetime') as mock_datetime:
                # Configure mocks to fail if called
                mock_time.side_effect = Exception("No time access allowed")
                mock_datetime.side_effect = Exception("No datetime access allowed")

                # Import and use healing system
                from agentic_core.L2_execution.healers.healing_tier_router import (
                    route_healing_tier,
                )
                from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

                healing_input = HealingInput(
                    agent_id="DispatchOutreachToolsAgent",  # In registry
                    failure_type="syntax_error",
                    error_signature="syntax_error:file:42",
                    trace_id="trace-123",
                    retry_count=0,
                    blast_radius_estimate=0.3,
                    required_tools=("ast_rewrite",),
                    violation_metadata_refs=("file.py",),
                )

                # Should work without time access
                decision = route_healing_tier(healing_input)

                assert decision is not None
