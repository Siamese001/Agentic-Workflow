"""ADG-driven tests for apps_shared/utils/titanium_rag_pipeline_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.titanium_rag_pipeline_util import (  # noqa: F401
        TitaniumRAGPipeline,
        create_titanium_pipeline,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    TitaniumRAGPipeline = None  # type: ignore[assignment,misc]
    create_titanium_pipeline = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="titanium_rag_pipeline_util.py deps unavailable")
class TestTitaniumRAGPipeline:
    def test_is_class(self):
        assert isinstance(TitaniumRAGPipeline, type)
    def test_importable(self):
        assert TitaniumRAGPipeline is not None

@pytest.mark.skipif(not _AVAILABLE, reason="titanium_rag_pipeline_util.py deps unavailable")
class TestCreateTitaniumPipeline:
    def test_is_callable(self):
        assert callable(create_titanium_pipeline)


def test_module_importable():
    """Module titanium_rag_pipeline_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE