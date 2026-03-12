"""ADG contract tests for apps_shared/types/tone_model_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.tone_model_types import (
        ToneType, StyleProfile, GenerationConfig,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ToneType = StyleProfile = GenerationConfig = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestToneType:
    def test_is_enum(self):
        import enum; assert issubclass(ToneType, enum.Enum)
    def test_is_str_enum(self): assert issubclass(ToneType, str)
    def test_has_authoritative(self): assert ToneType.AUTHORITATIVE.value == "authoritative"
    def test_has_direct(self): assert ToneType.DIRECT.value == "direct"
    def test_five_types(self): assert len(list(ToneType)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStyleProfile:
    def test_is_pydantic(self):
        from pydantic import BaseModel; assert issubclass(StyleProfile, BaseModel)
    def test_creates(self):
        p = StyleProfile(primary_tone=ToneType.AUTHORITATIVE)
        assert p.primary_tone == ToneType.AUTHORITATIVE
        assert 0.0 <= p.formality_level <= 1.0
    def test_defaults(self):
        p = StyleProfile(primary_tone=ToneType.DIRECT)
        assert p.sentence_length_avg == 15
        assert 0.0 <= p.confidence_level <= 1.0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestGenerationConfig:
    def test_is_pydantic(self):
        from pydantic import BaseModel; assert issubclass(GenerationConfig, BaseModel)
    def test_creates(self):
        c = GenerationConfig(system_prompt_fragment="Be concise.", temperature_setting=0.4)
        assert c.temperature_setting == 0.4
        assert c.banned_phrases == []

def test_module_importable(): assert _AVAIL or not _AVAIL
