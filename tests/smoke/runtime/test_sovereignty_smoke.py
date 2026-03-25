"""Runtime sovereignty smoke tests — import verification."""
import pytest

@pytest.mark.smoke
def test_sovereignty_bootstrap_importable():
    """Verify sovereignty_bootstrap module imports without error."""
    try:
        from agentic_core.runtime.sovereignty_bootstrap import (
            SovereigntyBootstrap,
            get_hierarchy_validator,
            initialize_determinism_engine,
            start_execution_trace,
        )

        # Verify class and functions exist and are callable
        assert SovereigntyBootstrap is not None
        assert callable(get_hierarchy_validator)
        assert callable(initialize_determinism_engine)
        assert callable(start_execution_trace)

    except ImportError as e:
        pytest.fail(f"Failed to import sovereignty_bootstrap: {e}")

@pytest.mark.smoke
def test_boundary_validator_importable():
    """Verify boundary_validator module imports without error."""
    try:
        from agentic_core.runtime.boundary_validator import (
            assert_no_apps_imports,
            validate_layer_direction,
            check_runtime_boundaries,
        )

        # Verify functions exist and are callable
        assert callable(assert_no_apps_imports)
        assert callable(validate_layer_direction)
        assert callable(check_runtime_boundaries)

    except ImportError as e:
        pytest.fail(f"Failed to import boundary_validator: {e}")

@pytest.mark.smoke
def test_sovereignty_exceptions_importable():
    """Verify sovereignty_exceptions module imports without error."""
    try:
        from agentic_core.runtime.sovereignty_exceptions import (
            SovereigntyViolationError,
            IsolationViolationError,
            CapabilityTokenError,
            DeterminismViolationError,
        )

        # Verify exception classes exist
        assert SovereigntyViolationError is not None
        assert IsolationViolationError is not None
        assert CapabilityTokenError is not None
        assert DeterminismViolationError is not None

        # Verify they are exception classes
        assert issubclass(SovereigntyViolationError, Exception)
        assert issubclass(IsolationViolationError, Exception)
        assert issubclass(CapabilityTokenError, Exception)
        assert issubclass(DeterminismViolationError, Exception)

    except ImportError as e:
        pytest.fail(f"Failed to import sovereignty_exceptions: {e}")

@pytest.mark.smoke
def test_runtime_state_importable():
    """Verify runtime.state module imports without error."""
    try:
        # Just verify the module can be imported
        import agentic_core.runtime.state
        assert True

    except ImportError as e:
        pytest.fail(f"Failed to import runtime.state: {e}")

@pytest.mark.smoke
def test_runtime_tools_importable():
    """Verify runtime.tools module imports without error."""
    try:
        # Just verify the module can be imported
        import agentic_core.runtime.tools
        assert True

    except ImportError as e:
        pytest.fail(f"Failed to import runtime.tools: {e}")
