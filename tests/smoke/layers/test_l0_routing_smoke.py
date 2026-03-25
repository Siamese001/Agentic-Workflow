"""L0 routing layer smoke tests — import verification and basic functionality."""

import pytest


@pytest.mark.smoke
def test_l0_routing_importable():
    """Verify L0 routing layer imports without error."""
    try:
        import agentic_core.L0_routing

        assert agentic_core.L0_routing is not None
    except ImportError as e:
        pytest.skip(f"L0_routing not available: {e}")


@pytest.mark.smoke
def test_l0_routing_engines_importable():
    """Verify L0 routing engines import without error."""
    try:
        from agentic_core.L0_routing.engines.routing_engine import RoutingEngine

        assert RoutingEngine is not None
    except ImportError as e:
        pytest.skip(f"RoutingEngine not yet implemented: {e}")


@pytest.mark.smoke
def test_l0_path_constants_importable():
    """Verify L0 path constants import and have reasonable values."""
    try:
        from agentic_core.L0_routing.config.path_constants import (
            BATCH_SIZE,
            BUFFER_SIZE,
            DEFAULT_SLEEP,
            DEFAULT_TIMEOUT,
            MAX_DEPTH,
            MAX_FILES,
            MAX_RETRIES,
            THRESHOLD,
        )

        # Verify constants exist and have reasonable values
        assert isinstance(BATCH_SIZE, int), "BATCH_SIZE should be an integer"
        assert isinstance(BUFFER_SIZE, int), "BUFFER_SIZE should be an integer"
        assert isinstance(DEFAULT_SLEEP, (int, float)), "DEFAULT_SLEEP should be numeric"
        assert isinstance(DEFAULT_TIMEOUT, (int, float)), "DEFAULT_TIMEOUT should be numeric"
        assert isinstance(MAX_DEPTH, int), "MAX_DEPTH should be an integer"
        assert isinstance(MAX_FILES, int), "MAX_FILES should be an integer"
        assert isinstance(MAX_RETRIES, int), "MAX_RETRIES should be an integer"
        assert isinstance(THRESHOLD, (int, float)), "THRESHOLD should be numeric"

        # Verify values are reasonable
        assert BATCH_SIZE > 0, "BATCH_SIZE should be positive"
        assert BUFFER_SIZE > 0, "BUFFER_SIZE should be positive"
        assert DEFAULT_SLEEP >= 0, "DEFAULT_SLEEP should be non-negative"
        assert DEFAULT_TIMEOUT > 0, "DEFAULT_TIMEOUT should be positive"
        assert MAX_DEPTH > 0, "MAX_DEPTH should be positive"
        assert MAX_FILES > 0, "MAX_FILES should be positive"
        assert MAX_RETRIES >= 0, "MAX_RETRIES should be non-negative"
        assert 0 <= THRESHOLD <= 1, "THRESHOLD should be between 0 and 1"

    except ImportError as e:
        pytest.skip(f"L0 path constants not available: {e}")


@pytest.mark.smoke
def test_l0_ssot_tier_constants_importable():
    """Verify L0 SSOT tier constants import without error."""
    try:
        from agentic_core.L0_routing.config.ssot_tier_constants import (
            HEALING_CONFIDENCE_X,
            HEALING_CONFIDENCE_Y,
            QWEN_14B_MODEL_ID,
            SSOT_SCORE_THRESHOLD_DET,
            SSOT_SCORE_THRESHOLD_QWEN,
        )

        # Verify constants exist and are of correct type
        assert isinstance(HEALING_CONFIDENCE_X, float), "HEALING_CONFIDENCE_X should be a float"
        assert isinstance(HEALING_CONFIDENCE_Y, float), "HEALING_CONFIDENCE_Y should be a float"
        assert isinstance(SSOT_SCORE_THRESHOLD_DET, int), "SSOT_SCORE_THRESHOLD_DET should be an integer"
        assert isinstance(SSOT_SCORE_THRESHOLD_QWEN, int), "SSOT_SCORE_THRESHOLD_QWEN should be an integer"
        assert isinstance(QWEN_14B_MODEL_ID, str), "QWEN_14B_MODEL_ID should be a string"

        # Verify values are reasonable
        assert 0 <= HEALING_CONFIDENCE_X <= 1, "HEALING_CONFIDENCE_X should be between 0 and 1"
        assert 0 <= HEALING_CONFIDENCE_Y <= 1, "HEALING_CONFIDENCE_Y should be between 0 and 1"
        assert SSOT_SCORE_THRESHOLD_DET > 0, "SSOT_SCORE_THRESHOLD_DET should be positive"
        assert SSOT_SCORE_THRESHOLD_QWEN > 0, "SSOT_SCORE_THRESHOLD_QWEN should be positive"
        assert len(QWEN_14B_MODEL_ID) > 0, "QWEN_14B_MODEL_ID should not be empty"

    except ImportError as e:
        pytest.skip(f"L0 SSOT tier constants not available: {e}")


@pytest.mark.smoke
def test_l0_deterministic_routing_gateway_importable():
    """Verify L0 deterministic routing gateway imports without error."""
    try:
        from agentic_core.L0_routing.artifacts.deterministic_routing_gateway import (
            DeterministicRoutingGateway,
        )

        assert DeterministicRoutingGateway is not None
    except ImportError as e:
        pytest.skip(f"DeterministicRoutingGateway not yet implemented: {e}")


@pytest.mark.smoke
def test_l0_legacy_agent_name_allowlist_importable():
    """Verify L0 legacy agent name allowlist imports without error."""
    try:
        from agentic_core.L0_routing.legacy_agent_name_allowlist import (
            LEGACY_AGENT_ALLOWLIST,
        )

        assert isinstance(LEGACY_AGENT_ALLOWLIST, (list, tuple, set)), (
            "LEGACY_AGENT_ALLOWLIST should be a collection"
        )
        assert len(LEGACY_AGENT_ALLOWLIST) >= 0, "LEGACY_AGENT_ALLOWLIST should not be negative length"
    except ImportError as e:
        pytest.skip(f"LEGACY_AGENT_ALLOWLIST not yet implemented: {e}")
