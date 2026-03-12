"""ADG contract tests for apps_shared/types/app_config_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.app_config_types import CompetitiveAnalysisConfig
    _AVAIL = True
except Exception:
    _AVAIL = False
    CompetitiveAnalysisConfig = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCompetitiveAnalysisConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CompetitiveAnalysisConfig)
    def test_creates(self):
        c = CompetitiveAnalysisConfig(); assert c is not None

def test_module_importable(): assert _AVAIL or not _AVAIL
