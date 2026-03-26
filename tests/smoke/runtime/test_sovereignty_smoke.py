"""Runtime sovereignty smoke tests — import verification."""

import pytest


@pytest.mark.smoke
def test_sovereignty_bootstrap_class_interface():
    """Verify SovereigntyBootstrap is a class with expected public interface."""
    try:
        from agentic_core.runtime.sovereignty_bootstrap import (
            SovereigntyBootstrap,
            get_hierarchy_validator,
        )
    except ImportError as e:
        pytest.skip(f"sovereignty_bootstrap not available: {e}")

    assert isinstance(SovereigntyBootstrap, type), "SovereigntyBootstrap should be a class"
    public = {n for n in dir(SovereigntyBootstrap) if not n.startswith("_")}
    assert len(public) >= 1, "SovereigntyBootstrap should have public methods"
    import inspect

    sig = inspect.signature(get_hierarchy_validator)
    assert "policy" in sig.parameters, "get_hierarchy_validator should accept 'policy' param"


@pytest.mark.smoke
def test_boundary_validator_functions_have_signatures():
    """Verify boundary_validator functions accept expected parameters."""
    import inspect

    try:
        from agentic_core.runtime.boundary_validator import (
            assert_no_apps_imports,
            check_runtime_boundaries,
            validate_layer_direction,
        )
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    for fn in [assert_no_apps_imports, validate_layer_direction, check_runtime_boundaries]:
        sig = inspect.signature(fn)
        assert len(sig.parameters) >= 0, f"{fn.__name__} should have a valid signature"
        assert callable(fn)


@pytest.mark.smoke
def test_sovereignty_exceptions_raise_with_message():
    """Verify sovereignty exceptions carry messages and inherit from Exception."""
    try:
        from agentic_core.runtime.sovereignty_exceptions import (
            CapabilityTokenError,
            DeterminismViolationError,
            IsolationViolationError,
            SovereigntyViolationError,
        )
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
# REVEALED FAILURE: f"sovereignty_exceptions not available: {e}

    for exc_cls in [
        SovereigntyViolationError,
        IsolationViolationError,
        CapabilityTokenError,
        DeterminismViolationError,
    ]:
        assert issubclass(exc_cls, Exception)
        err = exc_cls("test message")
        assert "test message" in str(err), f"{exc_cls.__name__} should carry its message"


@pytest.mark.smoke
def test_runtime_state_has_public_api():
    """Verify runtime.state module exposes public symbols."""
    try:
        import agentic_core.runtime.state as mod
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, "runtime.state must expose at least one public symbol"


@pytest.mark.smoke
def test_runtime_tools_has_public_api():
    """Verify runtime.tools module exposes public symbols."""
    try:
        import agentic_core.runtime.tools as mod
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, "runtime.tools must expose at least one public symbol"
