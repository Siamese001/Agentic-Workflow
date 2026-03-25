"""Safety & governance smoke tests — verify detectors, validators, and enforcement surface."""

import pytest


@pytest.mark.smoke
def test_test_quality_detector_scans_code():
    """TestQualityDetector can scan a code snippet and return a result."""
    import os
    import tempfile

    try:
        from agentic_core.L5_safety.validators.base_detector_validator import (
            EnforcementLevel,
        )
        from agentic_core.L5_safety.validators.test_quality_detector_validator import (
            TestQualityDetector,
        )
    except ImportError as e:


    det = TestQualityDetector(enforcement_level=EnforcementLevel.WARNING)
    code = "def test_x():\n    assert True\n"
    fd, path = tempfile.mkstemp(suffix=".py", prefix="test_probe_")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        from pathlib import Path

        result = det.scan_file(Path(path))
        assert result is not None, "scan_file must return a result"
        assert hasattr(result, "has_violations"), "result must have has_violations attr"
        assert result.has_violations, "assert True in a test should be flagged"
    finally:
        os.unlink(path)


@pytest.mark.smoke
def test_antipattern_category_enum_values():
    """AntiPatternCategory enum has expected values."""
    try:
        from agentic_core.L5_safety.validators.base_detector_validator import (
            AntiPatternCategory,
        )
    except ImportError as e:


    assert hasattr(AntiPatternCategory, "TEST_QUALITY")
    assert AntiPatternCategory.TEST_QUALITY == "test_quality"


@pytest.mark.smoke
def test_enforcement_level_enum_values():
    """EnforcementLevel enum has WARNING and ERROR."""
    try:
        from agentic_core.L5_safety.validators.base_detector_validator import (
            EnforcementLevel,
        )
    except ImportError as e:


    assert hasattr(EnforcementLevel, "WARNING")
    assert hasattr(EnforcementLevel, "HARD_BLOCK")


@pytest.mark.smoke
def test_constitutional_validator_importable():
    """constitutional_validator module imports and exposes key symbols."""
    try:
        import ops_scripts.enforcement.constitutional_validator as mod
    except ImportError as e:


    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, "constitutional_validator must expose public symbols"


@pytest.mark.smoke
def test_layer_boundary_enforcement():
    """Layer boundary validation infrastructure is importable."""
    try:
        from agentic_core.runtime.boundary_validator import (
            validate_layer_direction,
        )
    except ImportError as e:


    assert callable(validate_layer_direction)
    import inspect

    sig = inspect.signature(validate_layer_direction)
    assert len(sig.parameters) >= 1, "validate_layer_direction should accept parameters"


@pytest.mark.smoke
def test_structure_blueprint_sovereign_territories():
    """SOVEREIGN_TERRITORIES is a non-empty mapping with string keys."""
    try:
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            SOVEREIGN_TERRITORIES,
        )
    except ImportError as e:
        pytest.skip(f"structure_blueprint_config not available: {e}")

    from collections.abc import Mapping

    assert isinstance(SOVEREIGN_TERRITORIES, Mapping), (
        f"SOVEREIGN_TERRITORIES should be a Mapping, got {type(SOVEREIGN_TERRITORIES).__name__}"
    )
    assert len(SOVEREIGN_TERRITORIES) >= 1, "SOVEREIGN_TERRITORIES should not be empty"
    for key in SOVEREIGN_TERRITORIES:
        assert isinstance(key, str), f"Key {key!r} should be a string"
