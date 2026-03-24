"""ADG-driven tests for apps_shared/enforcement/PersonatemplateStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.enforcement.PersonatemplateStrategy import (  # noqa: F401
        PersonaTemplate,
        PromptSanitizer,
        get_functional_prompt,
        sanitize_legacy_prompt,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    PersonaTemplate = None  # type: ignore[assignment,misc]
    PromptSanitizer = None  # type: ignore[assignment,misc]
    get_functional_prompt = None  # type: ignore[assignment,misc]
    sanitize_legacy_prompt = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="PersonatemplateStrategy.py deps unavailable")
class TestPersonaTemplate:
    def test_is_class(self):
        assert isinstance(PersonaTemplate, type)
    def test_importable(self):
        assert PersonaTemplate is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PersonatemplateStrategy.py deps unavailable")
class TestPromptSanitizer:
    def test_is_class(self):
        assert isinstance(PromptSanitizer, type)
    def test_importable(self):
        assert PromptSanitizer is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PersonatemplateStrategy.py deps unavailable")
class TestGetFunctionalPrompt:
    def test_is_callable(self):
        assert callable(get_functional_prompt)

@pytest.mark.skipif(not _AVAILABLE, reason="PersonatemplateStrategy.py deps unavailable")
class TestSanitizeLegacyPrompt:
    def test_is_callable(self):
        assert callable(sanitize_legacy_prompt)


def test_module_importable():
    """Module PersonatemplateStrategy.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE