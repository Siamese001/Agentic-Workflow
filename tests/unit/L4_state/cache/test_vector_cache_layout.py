"""Tests for vector cache layout SSOT.

Location: tests/unit/L4_state/cache/test_vector_cache_layout.py
"""
from pathlib import Path

import pytest

from agentic_core.L4_state.contracts.vector_cache_layout import (
    VECTOR_CACHE_LAYOUT,
    LEGACY_VECTOR_CACHE_LAYOUT,
    VectorCacheLayout,
    get_sqlite_cache_path,
    get_chroma_cache_path,
    validate_cache_layout,
)


class TestVectorCacheLayout:
    """Test VectorCacheLayout dataclass."""

    def test_default_layout_paths(self):
        """Canonical layout should have correct default paths."""
        assert VECTOR_CACHE_LAYOUT.base_dir == Path("artifacts/cache/l2")
        assert VECTOR_CACHE_LAYOUT.sqlite_filename == "l2_cache.db"
        assert VECTOR_CACHE_LAYOUT.chroma_subdir == "chroma"

    def test_sqlite_path_property(self):
        """sqlite_path property should return correct path."""
        layout = VectorCacheLayout(base_dir=Path("/tmp/cache"))
        assert layout.sqlite_path == Path("/tmp/cache/l2_cache.db")

    def test_chroma_path_property(self):
        """chroma_path property should return correct path."""
        layout = VectorCacheLayout(base_dir=Path("/tmp/cache"))
        assert layout.chroma_path == Path("/tmp/cache/chroma")

    def test_custom_filename(self):
        """Custom sqlite filename should be respected."""
        layout = VectorCacheLayout(
            base_dir=Path("/tmp/cache"),
            sqlite_filename="custom.db"
        )
        assert layout.sqlite_path == Path("/tmp/cache/custom.db")

    def test_frozen_immutable(self):
        """Layout should be frozen (immutable)."""
        layout = VectorCacheLayout(base_dir=Path("/tmp/cache"))
        with pytest.raises(AttributeError):
            layout.base_dir = Path("/other")


class TestLegacyLayout:
    """Test legacy layout for backward compatibility."""

    def test_legacy_paths(self):
        """Legacy layout should use artifacts/gptcache."""
        assert LEGACY_VECTOR_CACHE_LAYOUT.base_dir == Path("artifacts/gptcache")


class TestPathHelpers:
    """Test path helper functions."""

    def test_get_sqlite_cache_path(self):
        """get_sqlite_cache_path should return correct path."""
        path = get_sqlite_cache_path("/tmp/cache")
        assert path == Path("/tmp/cache/l2_cache.db")

    def test_get_chroma_cache_path(self):
        """get_chroma_cache_path should return correct path."""
        path = get_chroma_cache_path("/tmp/cache")
        assert path == Path("/tmp/cache/chroma")


class TestValidation:
    """Test cache layout validation."""

    def test_validate_nonexistent_dir(self):
        """Validation should report non-existent base dir."""
        result = validate_cache_layout("/nonexistent/path/xyz123")
        assert result["base_dir_exists"] is False
        assert result["valid"] is False

    def test_validate_empty_dir(self, tmp_path):
        """Validation should report empty dir as invalid (no cache files)."""
        result = validate_cache_layout(tmp_path)
        assert result["base_dir_exists"] is True
        assert result["sqlite_exists"] is False
        assert result["chroma_exists"] is False
        assert result["valid"] is False  # No cache files yet

    def test_validate_with_sqlite(self, tmp_path):
        """Validation should detect SQLite file."""
        sqlite_file = tmp_path / "l2_cache.db"
        sqlite_file.write_text("")  # Create empty file
        result = validate_cache_layout(tmp_path)
        assert result["sqlite_exists"] is True
        assert result["valid"] is True

    def test_validate_with_chroma(self, tmp_path):
        """Validation should detect Chroma directory."""
        chroma_dir = tmp_path / "chroma"
        chroma_dir.mkdir()
        result = validate_cache_layout(tmp_path)
        assert result["chroma_exists"] is True
        assert result["valid"] is True
