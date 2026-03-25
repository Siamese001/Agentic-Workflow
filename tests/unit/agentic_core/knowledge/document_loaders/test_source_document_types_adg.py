"""Behavioral contract tests for agentic_core.knowledge.document_loaders.source_document_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.knowledge.document_loaders.source_document_types"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api(mod):
    """Module exposes expected public symbols."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{MODULE_PATH} must expose at least one public symbol"


def test_baseentity_is_instantiable(mod):
    """BaseEntity is accessible and is a type."""
    cls = getattr(mod, "BaseEntity", None)
    assert cls is not None, "BaseEntity must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BaseEntity must be a class"


def test_knowledgechunk_is_instantiable(mod):
    """KnowledgeChunk is accessible and is a type."""
    cls = getattr(mod, "KnowledgeChunk", None)
    assert cls is not None, "KnowledgeChunk must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "KnowledgeChunk must be a class"


def test_sourcedocument_is_instantiable(mod):
    """SourceDocument is accessible and is a type."""
    cls = getattr(mod, "SourceDocument", None)
    assert cls is not None, "SourceDocument must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SourceDocument must be a class"


def test_field_is_callable(mod):
    """Field is accessible and callable."""
    func = getattr(mod, "Field", None)
    assert func is not None, "Field must be defined in {MODULE_PATH}"
    assert callable(func), "Field must be callable"

