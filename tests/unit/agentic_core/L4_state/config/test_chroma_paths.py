"""Test coverage for `agentic_core.L4_state.config.chroma_paths`.

Wave 1 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md`.

Module rationale: SSOT for ChromaDB persist paths. 18 prod consumers depend
on the canonical/legacy split. Silent breakage here corrupts vector store
routing across SovereignChromaClient, L3SemanticRAG, and ingestion tooling.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L4_state.config.chroma_paths"


@pytest.fixture(scope="module")
def chroma_paths():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(chroma_paths):
    assert chroma_paths is not None


@pytest.mark.parametrize(
    "name",
    [
        "CANONICAL_SUBDIR",
        "LEGACY_SUBDIR",
        "ENV_OVERRIDE",
        "canonical_persist_dir",
        "canonical_persist_dir_str",
        "legacy_persist_dir",
        "repo_root",
    ],
)
def test_public_surface_exposed(chroma_paths, name):
    assert hasattr(chroma_paths, name), f"{name} missing from {MODULE}"


def test_canonical_subdir_value(chroma_paths):
    assert chroma_paths.CANONICAL_SUBDIR == "data/cache/chromadb"


def test_legacy_subdir_value(chroma_paths):
    assert chroma_paths.LEGACY_SUBDIR == "artifacts/chromadb"


def test_env_override_name(chroma_paths):
    assert chroma_paths.ENV_OVERRIDE == "CHROMA_PERSIST_DIR"


def test_repo_root_returns_path(chroma_paths):
    root = chroma_paths.repo_root()
    assert isinstance(root, Path)
    assert root.is_absolute()


def test_canonical_persist_dir_default(chroma_paths, monkeypatch):
    """Default path resolves to <repo_root>/data/cache/chromadb."""
    monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
    result = chroma_paths.canonical_persist_dir()
    assert isinstance(result, Path)
    assert result.is_absolute()
    assert str(result).replace("\\", "/").endswith("data/cache/chromadb")


def test_canonical_persist_dir_str_returns_str(chroma_paths, monkeypatch):
    monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
    result = chroma_paths.canonical_persist_dir_str()
    assert isinstance(result, str)
    assert result.replace("\\", "/").endswith("data/cache/chromadb")


def test_canonical_persist_dir_absolute_override(chroma_paths, monkeypatch, tmp_path):
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path))
    result = chroma_paths.canonical_persist_dir()
    assert result == tmp_path.resolve()


def test_canonical_persist_dir_relative_override(chroma_paths, monkeypatch):
    """Relative override is resolved against repo root."""
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "tmp/override_chroma")
    result = chroma_paths.canonical_persist_dir()
    assert result.is_absolute()
    assert str(result).replace("\\", "/").endswith("tmp/override_chroma")


def test_canonical_persist_dir_empty_override_falls_back(chroma_paths, monkeypatch):
    """Empty/whitespace env var must NOT be treated as override."""
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "   ")
    result = chroma_paths.canonical_persist_dir()
    assert str(result).replace("\\", "/").endswith("data/cache/chromadb")


def test_legacy_persist_dir(chroma_paths):
    result = chroma_paths.legacy_persist_dir()
    assert isinstance(result, Path)
    assert result.is_absolute()
    assert str(result).replace("\\", "/").endswith("artifacts/chromadb")


def test_canonical_and_legacy_differ(chroma_paths, monkeypatch):
    """Canonical and legacy paths must NEVER coincide."""
    monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
    canonical = chroma_paths.canonical_persist_dir()
    legacy = chroma_paths.legacy_persist_dir()
    assert canonical != legacy


def test_canonical_persist_dir_does_not_create_directory(chroma_paths, monkeypatch, tmp_path):
    """Per docstring: directory is NOT created by this function."""
    target = tmp_path / "must_not_exist"
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(target))
    result = chroma_paths.canonical_persist_dir()
    assert result == target.resolve()
    assert not target.exists()
