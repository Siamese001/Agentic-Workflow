"""Behavioral contract tests for agentic_core.evaluation.retrieval.__init__."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.evaluation.retrieval.__init__"


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


def test_chunkentry_is_instantiable(mod):
    """ChunkEntry is accessible and is a type."""
    cls = getattr(mod, "ChunkEntry", None)
    assert cls is not None, "ChunkEntry must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ChunkEntry must be a class"


def test_chunkmanifest_is_instantiable(mod):
    """ChunkManifest is accessible and is a type."""
    cls = getattr(mod, "ChunkManifest", None)
    assert cls is not None, "ChunkManifest must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ChunkManifest must be a class"


def test_chunkmanifestregistry_is_instantiable(mod):
    """ChunkManifestRegistry is accessible and is a type."""
    cls = getattr(mod, "ChunkManifestRegistry", None)
    assert cls is not None, "ChunkManifestRegistry must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ChunkManifestRegistry must be a class"


def test_completenesschangepackage_is_instantiable(mod):
    """CompletenessChangePackage is accessible and is a type."""
    cls = getattr(mod, "CompletenessChangePackage", None)
    assert cls is not None, "CompletenessChangePackage must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CompletenessChangePackage must be a class"


def test_completenessragproposer_is_instantiable(mod):
    """CompletenessRAGProposer is accessible and is a type."""
    cls = getattr(mod, "CompletenessRAGProposer", None)
    assert cls is not None, "CompletenessRAGProposer must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CompletenessRAGProposer must be a class"


def test_completenessreranker_is_instantiable(mod):
    """CompletenessReranker is accessible and is a type."""
    cls = getattr(mod, "CompletenessReranker", None)
    assert cls is not None, "CompletenessReranker must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CompletenessReranker must be a class"


def test_completenessrerankerconfig_is_instantiable(mod):
    """CompletenessRerankerConfig is accessible and is a type."""
    cls = getattr(mod, "CompletenessRerankerConfig", None)
    assert cls is not None, "CompletenessRerankerConfig must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CompletenessRerankerConfig must be a class"


def test_completenessscorerconfig_is_instantiable(mod):
    """CompletenessScorerConfig is accessible and is a type."""
    cls = getattr(mod, "CompletenessScorerConfig", None)
    assert cls is not None, "CompletenessScorerConfig must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CompletenessScorerConfig must be a class"


def test_latechunkingmode_is_callable(mod):
    """LateChunkingMode is accessible and callable."""
    func = getattr(mod, "LateChunkingMode", None)
    assert func is not None, "LateChunkingMode must be defined in {MODULE_PATH}"
    assert callable(func), "LateChunkingMode must be callable"


def test_build_late_chunk_manifests_for_corpus_is_callable(mod):
    """build_late_chunk_manifests_for_corpus is accessible and callable."""
    func = getattr(mod, "build_late_chunk_manifests_for_corpus", None)
    assert func is not None, "build_late_chunk_manifests_for_corpus must be defined in {MODULE_PATH}"
    assert callable(func), "build_late_chunk_manifests_for_corpus must be callable"


def test_make_profile_is_callable(mod):
    """make_profile is accessible and callable."""
    func = getattr(mod, "make_profile", None)
    assert func is not None, "make_profile must be defined in {MODULE_PATH}"
    assert callable(func), "make_profile must be callable"


def test_segment_document_is_callable(mod):
    """segment_document is accessible and callable."""
    func = getattr(mod, "segment_document", None)
    assert func is not None, "segment_document must be defined in {MODULE_PATH}"
    assert callable(func), "segment_document must be callable"

