"""
Phase 4 — Wave 3 Tests: Versioned ML cache policy + default parity.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L4_state.config.versioned_configs import MLCacheConfig, get_ml_cache_config

pytestmark = pytest.mark.unit_min_deps

# Prior behavior constants (locked by parity test)
_PRIOR_DEFAULT_TTL = 3600
_PRIOR_MAX_ENTRIES = 1000
_PRIOR_EVICTION_MODE = "lru"


class TestMLCacheConfig:
    def test_ml_cache_config_has_required_fields(self):
        cfg = MLCacheConfig()
        assert hasattr(cfg, "version")
        assert hasattr(cfg, "default_ttl_seconds")
        assert hasattr(cfg, "max_entries")
        assert hasattr(cfg, "eviction_mode")

    def test_ml_cache_config_has_canonical_bytes(self):
        cfg = MLCacheConfig()
        b = cfg.canonical_bytes()
        assert isinstance(b, bytes)
        assert len(b) > 0

    def test_ml_cache_config_has_config_hash(self):
        cfg = MLCacheConfig()
        h = cfg.config_hash
        assert len(h) == 64

    def test_canonical_bytes_deterministic(self):
        cfg = MLCacheConfig()
        assert cfg.canonical_bytes() == cfg.canonical_bytes()

    def test_config_hash_stable(self):
        cfg1 = MLCacheConfig()
        cfg2 = MLCacheConfig()
        assert cfg1.config_hash == cfg2.config_hash

    def test_config_hash_changes_with_ttl(self):
        cfg1 = MLCacheConfig(default_ttl_seconds=3600)
        cfg2 = MLCacheConfig(default_ttl_seconds=7200)
        assert cfg1.config_hash != cfg2.config_hash

    def test_config_hash_changes_with_max_entries(self):
        cfg1 = MLCacheConfig(max_entries=1000)
        cfg2 = MLCacheConfig(max_entries=500)
        assert cfg1.config_hash != cfg2.config_hash

    def test_config_hash_changes_with_eviction_mode(self):
        cfg1 = MLCacheConfig(eviction_mode="lru")
        cfg2 = MLCacheConfig(eviction_mode="fifo")
        assert cfg1.config_hash != cfg2.config_hash

    def test_get_ml_cache_config_returns_singleton(self):
        cfg1 = get_ml_cache_config()
        cfg2 = get_ml_cache_config()
        assert cfg1 is cfg2

    def test_ml_cache_ttl_comes_from_versioned_config(self):
        """
        TTL must be read from MLCacheConfig, not hardcoded.
        Verify the config field is the source of truth.
        """
        cfg = MLCacheConfig(default_ttl_seconds=7200)
        assert cfg.default_ttl_seconds == 7200
        assert cfg.config_hash != MLCacheConfig().config_hash

    def test_default_cache_config_matches_prior_behavior(self):
        """
        Parity lock: default MLCacheConfig values must match prior hardcoded behavior.
        Changing these defaults is a breaking change requiring a version bump.
        """
        cfg = MLCacheConfig()
        assert cfg.default_ttl_seconds == _PRIOR_DEFAULT_TTL, (
            f"Default TTL changed: expected {_PRIOR_DEFAULT_TTL}, got {cfg.default_ttl_seconds}"
        )
        assert cfg.max_entries == _PRIOR_MAX_ENTRIES, (
            f"Default max_entries changed: expected {_PRIOR_MAX_ENTRIES}, got {cfg.max_entries}"
        )
        assert cfg.eviction_mode == _PRIOR_EVICTION_MODE, (
            f"Default eviction_mode changed: expected {_PRIOR_EVICTION_MODE!r}, got {cfg.eviction_mode!r}"
        )

    def test_canonical_bytes_sorted_keys(self):
        """canonical_bytes must use sorted keys (determinism guarantee)."""
        import json

        cfg = MLCacheConfig()
        raw = cfg.canonical_bytes().decode()
        doc = json.loads(raw)
        keys = list(doc.keys())
        assert keys == sorted(keys), f"canonical_bytes keys not sorted: {keys}"


class TestMLCacheConfigStaticAudit:
    """
    Static AST audit: versioned_configs.py must define MLCacheConfig
    and must not contain any hardcoded TTL literal that bypasses the config.
    Scope: versioned_configs.py only (narrow, as specified).
    """

    _TARGET = (
        Path(__file__).resolve().parents[2] / "agentic_core" / "L4_state" / "config" / "versioned_configs.py"
    )

    def test_ml_cache_config_class_present_in_versioned_configs(self):
        src = self._TARGET.read_text(encoding="utf-8")
        tree = ast.parse(src)
        class_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        assert "MLCacheConfig" in class_names, "MLCacheConfig class not found in versioned_configs.py"

    def test_get_ml_cache_config_function_present(self):
        src = self._TARGET.read_text(encoding="utf-8")
        assert "get_ml_cache_config" in src

    def test_default_ttl_field_present_in_class(self):
        """Verify default_ttl_seconds field is declared in MLCacheConfig."""
        src = self._TARGET.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "MLCacheConfig":
                class_src = ast.unparse(node)
                assert "default_ttl_seconds" in class_src
                return
        pytest.fail("MLCacheConfig class not found in AST")

    def test_no_banned_hardcoded_ttl_outside_config_class(self):
        """
        Verify that the integer literal 3600 does not appear as a standalone
        assignment outside the MLCacheConfig class body in versioned_configs.py.
        This ensures TTL is not duplicated as a module-level magic constant.
        """
        src = self._TARGET.read_text(encoding="utf-8")
        tree = ast.parse(src)

        # Collect all Constant nodes that are 3600 outside MLCacheConfig
        ml_cache_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "MLCacheConfig":
                ml_cache_node = node
                break

        # Get line range of MLCacheConfig
        if ml_cache_node is None:
            pytest.fail("MLCacheConfig not found")

        ml_lines = set(range(ml_cache_node.lineno, ml_cache_node.end_lineno + 1))

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value == 3600:
                if node.lineno not in ml_lines:
                    pytest.fail(
                        f"Hardcoded TTL literal 3600 found outside MLCacheConfig "
                        f"at line {node.lineno} in versioned_configs.py"
                    )
