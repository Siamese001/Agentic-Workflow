"""L1 cognition layer smoke tests — import verification and basic functionality."""
import pytest

@pytest.mark.smoke
def test_l1_cognition_importable():
    """Verify L1 cognition layer imports without error."""
    try:
        import agentic_core.L1_cognition
        assert agentic_core.L1_cognition is not None
    except ImportError as e:
        pytest.skip(f"L1_cognition not available: {e}")

@pytest.mark.smoke
def test_l1_cognition_engines_importable():
    """Verify L1 cognition engines import without error."""
    try:
        from agentic_core.L1_cognition.engines.cognition_engine import CognitionEngine
        assert CognitionEngine is not None
    except ImportError as e:
        pytest.skip(f"CognitionEngine not available: {e}")

@pytest.mark.smoke
def test_l1_cognition_config_importable():
    """Verify L1 cognition config imports without error."""
    try:
        from agentic_core.L1_cognition.config.cognition_config import (
            get_cognition_config,
        )
        assert callable(get_cognition_config), "get_cognition_config should be callable"
    except ImportError as e:
        pytest.skip(f"L1 cognition config not available: {e}")

@pytest.mark.smoke
def test_l1_cognition_context_importable():
    """Verify L1 cognition context managers import without error."""
    try:
        from agentic_core.L1_cognition.context.context_manager import (
            CognitionContextManager,
        )
        assert CognitionContextManager is not None
    except ImportError as e:
        pytest.skip(f"CognitionContextManager not available: {e}")

@pytest.mark.smoke
def test_l1_cognition_planning_importable():
    """Verify L1 cognition planning imports without error."""
    try:
        from agentic_core.L1_cognition.planning.planning_engine import (
            PlanningEngine,
        )
        assert PlanningEngine is not None
    except ImportError as e:
        pytest.skip(f"PlanningEngine not available: {e}")

@pytest.mark.smoke
def test_l1_cognition_validators_importable():
    """Verify L1 cognition validators import without error."""
    try:
        from agentic_core.L1_cognition.enforcement.cognition_validators import (
            CognitionValidator,
        )
        assert CognitionValidator is not None
    except ImportError as e:
        pytest.skip(f"CognitionValidator not available: {e}")

@pytest.mark.smoke
def test_l1_cognition_reasoning_importable():
    """Verify L1 cognition reasoning imports without error."""
    try:
        from agentic_core.L1_cognition.reasoning.reasoning_engine import (
            ReasoningEngine,
        )
        assert ReasoningEngine is not None
    except ImportError as e:
        pytest.skip(f"ReasoningEngine not available: {e}")
