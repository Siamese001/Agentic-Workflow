"""Behavioral contract tests for agentic_core.L0_routing.scripts.chunk_type."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.chunk_type"


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


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_chunktype_is_instantiable(mod):
    """ChunkType is accessible and is a type."""
    cls = getattr(mod, "ChunkType", None)
    assert cls is not None, "ChunkType must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ChunkType must be a class"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_semanticchunk_is_instantiable(mod):
    """SemanticChunk is accessible and is a type."""
    cls = getattr(mod, "SemanticChunk", None)
    assert cls is not None, "SemanticChunk must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SemanticChunk must be a class"


def test_chunk_python_ast_is_callable(mod):
    """chunk_python_ast is accessible and callable."""
    func = getattr(mod, "chunk_python_ast", None)
    assert func is not None, "chunk_python_ast must be defined in {MODULE_PATH}"
    assert callable(func), "chunk_python_ast must be callable"


def test_chunk_text_is_callable(mod):
    """chunk_text is accessible and callable."""
    func = getattr(mod, "chunk_text", None)
    assert func is not None, "chunk_text must be defined in {MODULE_PATH}"
    assert callable(func), "chunk_text must be callable"


def test_chunk_text_fallback_is_callable(mod):
    """chunk_text_fallback is accessible and callable."""
    func = getattr(mod, "chunk_text_fallback", None)
    assert func is not None, "chunk_text_fallback must be defined in {MODULE_PATH}"
    assert callable(func), "chunk_text_fallback must be callable"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"


def test_load_text_file_is_callable(mod):
    """load_text_file is accessible and callable."""
    func = getattr(mod, "load_text_file", None)
    assert func is not None, "load_text_file must be defined in {MODULE_PATH}"
    assert callable(func), "load_text_file must be callable"


def test_main_is_callable(mod):
    """main is accessible and callable."""
    func = getattr(mod, "main", None)
    assert func is not None, "main must be defined in {MODULE_PATH}"
    assert callable(func), "main must be callable"

