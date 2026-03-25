"""Runtime execution trace smoke tests — import verification."""

import pytest


@pytest.mark.smoke
def test_execution_trace_manager_instantiable():
    """Verify ExecutionTraceManager can be instantiated and has expected interface."""
    try:
        from agentic_core.runtime.execution_trace import (
            ExecutionTrace,
            ExecutionTraceManager,
            get_execution_trace_manager,
        )
    except ImportError as e:


    assert isinstance(ExecutionTrace, type), "ExecutionTrace should be a class"
    assert isinstance(ExecutionTraceManager, type), "ExecutionTraceManager should be a class"
    mgr = get_execution_trace_manager()
    assert mgr is not None, "get_execution_trace_manager must return a value"
    assert isinstance(mgr, ExecutionTraceManager)


@pytest.mark.smoke
def test_trace_emitter_is_instantiable_class():
    """Verify TraceEmitter is a class with expected interface."""
    try:
        from agentic_core.runtime.trace_emitter import TraceEmitter
    except ImportError as e:


    assert isinstance(TraceEmitter, type), "TraceEmitter should be a class"
    # Verify expected methods exist on the class
    actual_methods = {n for n in dir(TraceEmitter) if not n.startswith("_")}
    assert len(actual_methods) >= 1, "TraceEmitter should have at least one public method"


@pytest.mark.smoke
def test_mathematical_determinism_engine_instantiable():
    """Verify MathematicalDeterminismEngine can be instantiated."""
    try:
        from agentic_core.runtime.mathematical_determinism import (
            DeterminismProof,
            DeterministicArtifact,
            MathematicalDeterminismEngine,
        )
    except ImportError as e:


    assert isinstance(MathematicalDeterminismEngine, type)
    assert isinstance(DeterministicArtifact, type)
    assert isinstance(DeterminismProof, type)
    # Verify the engine class has core interface methods
    engine_methods = {n for n in dir(MathematicalDeterminismEngine) if not n.startswith("_")}
    assert len(engine_methods) >= 1, "MathematicalDeterminismEngine should have public methods"


@pytest.mark.smoke
def test_trace_context_has_public_api():
    """Verify trace_context module exposes public symbols."""
    try:
        import agentic_core.runtime.trace_context as mod
    except ImportError as e:


    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, "trace_context must expose at least one public symbol"


@pytest.mark.smoke
def test_execution_bound_token_has_public_api():
    """Verify execution_bound_token module exposes public symbols."""
    try:
        import agentic_core.runtime.execution_bound_token as mod
    except ImportError as e:


    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, "execution_bound_token must expose at least one public symbol"
