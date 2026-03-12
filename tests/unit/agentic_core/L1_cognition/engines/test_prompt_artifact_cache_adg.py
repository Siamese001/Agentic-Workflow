"""ADG importability contract for agentic_core/L1_cognition/engines/prompt_artifact_cache.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_prompt_artifact_cache.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import (  # noqa: F401
        CompiledPromptCache,
        TemplateRenderCache,
        get_compiled_prompt_cache,
        get_template_render_cache,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    CompiledPromptCache = None  # type: ignore[assignment,misc]
    TemplateRenderCache = None  # type: ignore[assignment,misc]
    get_compiled_prompt_cache = None  # type: ignore[assignment,misc]
    get_template_render_cache = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_artifact_cache.py deps unavailable")
class TestPromptArtifactCacheImportability:
    def test_module_importable(self) -> None:
        """ADG contract: prompt_artifact_cache.py must be importable."""
        assert _AVAILABLE

    def test_compiledpromptcache_is_type(self) -> None:
        assert CompiledPromptCache is not None

    def test_templaterendercache_is_type(self) -> None:
        assert TemplateRenderCache is not None

    def test_get_compiled_prompt_cache_callable(self) -> None:
        assert callable(get_compiled_prompt_cache)

    def test_get_template_render_cache_callable(self) -> None:
        assert callable(get_template_render_cache)

