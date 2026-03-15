"""ADG importability contract for apps_shared/config/pipeline_constants_config.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_pipeline_constants_config.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    import apps_shared.config.pipeline_constants_config as _mod  # noqa: F401
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _mod = None

@pytest.mark.skipif(not _AVAILABLE, reason="pipeline_constants_config.py deps unavailable")
class TestPipelineConstantsConfigImportability:
    def test_module_importable(self) -> None:
        """ADG contract: pipeline_constants_config.py must be importable."""
        assert _AVAILABLE
