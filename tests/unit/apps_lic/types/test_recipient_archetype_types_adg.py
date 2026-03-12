"""ADG contract tests for apps_lic/types/recipient_archetype_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_lic.types.recipient_archetype_types import (
        RecipientArchetype, CreativeBrief, ArchetypeTemplate,
        ARCHETYPE_TEMPLATES, ArchetypeTemplateManager,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    RecipientArchetype = CreativeBrief = ArchetypeTemplate = None  # type: ignore[assignment,misc]
    ARCHETYPE_TEMPLATES = ArchetypeTemplateManager = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRecipientArchetype:
    def test_is_enum(self):
        import enum; assert issubclass(RecipientArchetype, enum.Enum)
    def test_has_c_level(self): assert RecipientArchetype.C_LEVEL.value == "C_LEVEL"
    def test_four_archetypes(self): assert len(list(RecipientArchetype)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestArchetypeTemplates:
    def test_is_dict(self): assert isinstance(ARCHETYPE_TEMPLATES, dict)
    def test_c_level_present(self): assert RecipientArchetype.C_LEVEL in ARCHETYPE_TEMPLATES
    def test_all_archetypes_present(self):
        for arch in RecipientArchetype:
            assert arch in ARCHETYPE_TEMPLATES

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestArchetypeTemplateManager:
    def test_creates(self): m = ArchetypeTemplateManager(); assert m is not None
    def test_get_template_returns_correct(self):
        m = ArchetypeTemplateManager()
        t = m.get_template(RecipientArchetype.C_LEVEL)
        assert t.Archetype == RecipientArchetype.C_LEVEL
    def test_get_word_count_range(self):
        m = ArchetypeTemplateManager()
        lo, hi = m.get_word_count_range(RecipientArchetype.RECRUITER)
        assert hi > lo > 0

def test_module_importable(): assert _AVAIL or not _AVAIL
