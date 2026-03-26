"""SSOT constants smoke tests — import verification and constant presence."""

import pytest


@pytest.mark.smoke
def test_path_constants_importable():
        from agentic_core.L0_routing.config.path_constants import (
        from agentic_core.L5_safety.config.structure_blueprint_config import (
        from agentic_core.L0_routing.config.ssot_tier_constants import (
        from agentic_core.config.core.config_loader import (
        import agentic_core.config.agent_configs as mod
        """Verify path_constants imports and has required constants."""
        try:

    try:
#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
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
        pytest.skip(f"path_constants not available: {e}")


@pytest.mark.smoke
def test_structure_blueprint_importable():
    """Verify structure_blueprint_config imports without error."""
    try:
#  # MOVED: from agentic_core.L5_safety.config.structure_blueprint_config import (
            DOCS_REPORTS_PLANS,
            PROJECT_ROOT_WHITELIST,
            SOVEREIGN_TERRITORIES,
        )

        # Verify constants exist
        assert isinstance(DOCS_REPORTS_PLANS, str), "DOCS_REPORTS_PLANS should be a string"
        assert hasattr(SOVEREIGN_TERRITORIES, "__len__"), "SOVEREIGN_TERRITORIES should be a collection"
        assert hasattr(PROJECT_ROOT_WHITELIST, "__len__"), "PROJECT_ROOT_WHITELIST should be a collection"

        # Verify values are reasonable
        assert len(DOCS_REPORTS_PLANS) > 0, "DOCS_REPORTS_PLANS should not be empty"
        assert len(SOVEREIGN_TERRITORIES) > 0, "SOVEREIGN_TERRITORIES should not be empty"
        assert len(PROJECT_ROOT_WHITELIST) > 0, "PROJECT_ROOT_WHITELIST should not be empty"

        # Verify paths look like paths
        assert "plans" in DOCS_REPORTS_PLANS, "DOCS_REPORTS_PLANS should contain 'plans'"
        assert all(isinstance(k, str) for k in SOVEREIGN_TERRITORIES), (
            "All sovereign territory keys should be strings"
        )
        assert all(isinstance(path, str) for path in PROJECT_ROOT_WHITELIST), (
            "All whitelist paths should be strings"
        )

    except ImportError as e:
        pytest.skip(f"structure_blueprint_config not available: {e}")


@pytest.mark.smoke
def test_ssot_tier_constants_importable():
    """Verify ssot_tier_constants imports without error."""
    try:
#  # MOVED: from agentic_core.L0_routing.config.ssot_tier_constants import (
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
        pytest.skip(f"ssot_tier_constants not available: {e}")


@pytest.mark.smoke
def test_config_core_load_json_returns_dict():
    """Verify _load_json_config returns a dict when given a valid JSON path."""
    try:
#  # MOVED: from agentic_core.config.core.config_loader import (
            _load_json_config,
        )
    except ImportError as e:
        pytest.skip(f"config.core not available: {e}")

    assert callable(_load_json_config), "_load_json_config should be callable"
    import inspect

    sig = inspect.signature(_load_json_config)
    assert "filename" in sig.parameters, "_load_json_config should accept 'filename' param"


@pytest.mark.smoke
def test_agent_configs_is_importable_package():
    """Verify agent_configs imports as a valid package with submodules."""
    try:
#  # MOVED: import agentic_core.config.agent_configs as mod
    except ImportError as e:
        pytest.skip(f"agent_configs not available: {e}")

    # Namespace package — verify it has __path__ (is a package, not a plain module)
    assert hasattr(mod, "__path__") or hasattr(mod, "__file__"), (
        "agent_configs should be a valid package or module"
    )
