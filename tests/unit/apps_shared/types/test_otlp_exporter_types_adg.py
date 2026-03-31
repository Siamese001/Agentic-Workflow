"""ADG contract tests for apps_shared/types/otlp_exporter_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module otlp_exporter_types must be importable."""
    import apps_shared.types.otlp_exporter_types  # noqa: F401

    assert apps_shared.types.otlp_exporter_types is not None
